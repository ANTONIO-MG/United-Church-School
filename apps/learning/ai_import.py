"""AI route for lessons — Claude drafts a full lesson from a **source document**
or from a **written brief**.

Both routes end in the same place: a ``draft`` Lesson whose content is grouped
into :class:`~apps.learning.models.LessonSection` tear-drops, opened in the
normal block editor for a human to review, edit and publish. The AI never
publishes anything itself, and it only authors block types it can produce from
text (heading, rich text, callout, table, reference, divider) — media, quizzes
and live sessions are added by the human afterwards.

The same document→draft logic backs class/document importing elsewhere in the
hub, so improvements here apply to both.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from core.errors import note
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.ai_assistant import generate

from . import models
from .authoring import _can_author

# JSON schema Claude must return — mirrors Lesson + LessonSection + LessonBlock.
# Structured outputs require additionalProperties:false on every object.
BLOCK_SCHEMA = {
    'type': 'object',
    'additionalProperties': False,
    'properties': {
        'block_type': {'type': 'string',
                       'enum': ['heading', 'text', 'callout', 'table', 'reference', 'divider']},
        'heading_text': {'type': 'string'},
        'heading_level': {'type': 'integer', 'enum': [2, 3, 4]},
        'html': {'type': 'string'},
        'callout_variant': {'type': 'string', 'enum': ['info', 'tip', 'warning', 'danger']},
        'table_caption': {'type': 'string'},
        'table_headers': {'type': 'array', 'items': {'type': 'string'}},
        # Each row is one string with cells separated by " | " (kept flat rather
        # than nested arrays so the schema's constraint grammar stays small).
        'table_rows': {'type': 'array', 'items': {'type': 'string'}},
        'reference_text': {'type': 'string'},
        'reference_authors': {'type': 'string'},
        'reference_year': {'type': 'string'},
        'reference_url': {'type': 'string'},
    },
    'required': ['block_type'],
}

LESSON_SCHEMA = {
    'type': 'object',
    'additionalProperties': False,
    'properties': {
        'title': {'type': 'string'},
        'subtitle': {'type': 'string'},
        'estimated_minutes': {'type': 'integer'},
        'intro_blocks': {'type': 'array', 'items': BLOCK_SCHEMA},
        'sections': {
            'type': 'array',
            'items': {
                'type': 'object',
                'additionalProperties': False,
                'properties': {
                    'title': {'type': 'string'},
                    'summary': {'type': 'string'},
                    'section_type': {'type': 'string',
                                     'enum': ['reading', 'video', 'quiz', 'assessment',
                                              'live', 'interactive', 'resources']},
                    'duration_minutes': {'type': 'integer'},
                    'requires_previous': {'type': 'boolean'},
                    'blocks': {'type': 'array', 'items': BLOCK_SCHEMA},
                },
                'required': ['title', 'blocks'],
            },
        },
        'references': {
            'type': 'array',
            'items': {
                'type': 'object',
                'additionalProperties': False,
                'properties': {
                    'text': {'type': 'string'},
                    'authors': {'type': 'string'},
                    'year': {'type': 'string'},
                    'url': {'type': 'string'},
                },
                'required': ['text'],
            },
        },
    },
    'required': ['title', 'subtitle', 'estimated_minutes', 'sections', 'references'],
}

LESSON_SYSTEM = (
    'You are an instructional designer building a structured online lesson. The lesson is '
    'presented to learners as a stack of collapsible sections — each one labelled with its '
    'kind and its expected duration — so your job is to break the material into a clear, '
    'well-sequenced set of sections and write the content inside each. Produce an '
    'introduction, then the core content as headed sections with explanatory prose, tables '
    'where the material is tabular, and callouts for key definitions or warnings. Rewrite and '
    'organise the material for learners — never merely copy a source verbatim. Rich text goes '
    'in the "html" field as simple HTML (<p>, <ul>, <li>, <strong>, <em>, <h4> only). Keep any '
    'real references you find.'
)

_SHARED_RULES = (
    'Put a short welcome/overview in intro_blocks (one text block is enough). Then produce 4–8 '
    'sections. Give each section a specific title, a one-line summary, a section_type (use '
    '"reading" unless the content is genuinely a quiz, assessment, live class or interactive '
    'activity) and a realistic duration_minutes. Inside a section use text blocks for prose, '
    'table blocks for tabular data and callout blocks for key points — do not repeat the '
    'section title as a heading block. In a table block, put each row in table_rows as one '
    'string with cells separated by " | " (a vertical bar), matching the order of '
    'table_headers. Set requires_previous to true only where a section genuinely depends on '
    'the one before it.'
)

LESSON_INSTRUCTION = (
    'Turn this document into a lesson draft that fits the required schema. ' + _SHARED_RULES
    + ' Estimate the total reading time in minutes.'
)

PROMPT_INSTRUCTION = (
    'Write a complete lesson from the brief above, fitting the required schema. Cover the '
    'topic properly — teach it, with worked explanations and examples, not just an outline. '
    + _SHARED_RULES + ' Estimate the total study time in minutes.'
)


def _block_data(raw):
    """Map one AI block onto the ``data`` JSON a :class:`LessonBlock` stores.

    Returns ``(block_type, data)``, or ``(None, None)`` for a type we do not
    author from text.
    """
    block_type = raw.get('block_type')
    if block_type == 'heading':
        return block_type, {'text': raw.get('heading_text', ''), 'level': raw.get('heading_level', 2)}
    if block_type == 'text':
        return block_type, {'html': raw.get('html', '')}
    if block_type == 'callout':
        return block_type, {'html': raw.get('html', ''), 'variant': raw.get('callout_variant', 'info')}
    if block_type == 'table':
        headers = raw.get('table_headers') or []
        # Rows arrive as " | "-delimited strings; split back into cells.
        rows = [[c.strip() for c in str(r).split('|')] for r in (raw.get('table_rows') or [])]
        return block_type, {
            'caption': raw.get('table_caption', ''),
            'has_header': bool(headers),
            'headers': headers or (rows[0] if rows else ['Column 1', 'Column 2']),
            'rows': rows or [['', '']],
        }
    if block_type == 'reference':
        return block_type, {
            'text': raw.get('reference_text', ''), 'authors': raw.get('reference_authors', ''),
            'year': raw.get('reference_year', ''), 'url': raw.get('reference_url', ''),
        }
    if block_type == 'divider':
        return block_type, {}
    return None, None


def build_lesson_draft(data, module, user, *, source=''):
    """Create a draft Lesson + its sections and blocks from the model's JSON."""
    lesson = models.Lesson.objects.create(
        title=(data.get('title') or 'Untitled lesson')[:200],
        subtitle=(data.get('subtitle') or '')[:255],
        module=module,
        created_by=user,
        status='draft',
        estimated_minutes=int(data.get('estimated_minutes') or 20),
        author_name=(user.get_full_name() or user.get_username()),
        references=[r for r in (data.get('references') or []) if r.get('text')],
    )

    order = 0

    def add_blocks(raws, section):
        nonlocal order
        for raw in (raws or []):
            block_type, block_data = _block_data(raw)
            if block_type is None:
                continue  # skip block types the AI route does not author
            models.LessonBlock.objects.create(
                lesson=lesson, section=section, block_type=block_type,
                order=order, data=block_data)
            order += 1

    # Intro blocks sit above the accordion; everything else lives in a tear-drop.
    add_blocks(data.get('intro_blocks'), None)

    sections = data.get('sections') or []
    if not sections and data.get('blocks'):
        # Tolerate a flat response (an older/looser model reply) — one section.
        sections = [{'title': lesson.title, 'blocks': data['blocks']}]

    for index, raw_section in enumerate(sections):
        section_type = raw_section.get('section_type')
        section = models.LessonSection.objects.create(
            lesson=lesson, order=index,
            title=(raw_section.get('title') or f'Section {index + 1}')[:200],
            summary=(raw_section.get('summary') or '')[:300],
            section_type=(section_type if section_type in dict(models.LessonSection.TYPE_CHOICES)
                          else models.LessonSection.TYPE_AUTO),
            duration_minutes=max(0, int(raw_section.get('duration_minutes') or 0)),
            requires_previous=bool(raw_section.get('requires_previous')),
            open_by_default=(index == 0),
        )
        add_blocks(raw_section.get('blocks'), section)

    return lesson


def _modules_for(user):
    from apps.learning.models import ProgrammeModule
    return (ProgrammeModule.objects.filter(is_active=True)
            .select_related('programme').order_by('programme__name', 'order', 'name'))


@login_required
def lesson_ai_import(request):
    """Draft a lesson with Claude — from an uploaded document, a written brief, or both."""
    if not _can_author(request.user):
        messages.error(request, 'You do not have permission to author lessons.')
        return redirect('learning:lessons')

    modules = _modules_for(request.user)

    if request.method == 'POST':
        if not generate.is_enabled():
            note('AI-7001', request)
            messages.error(request, 'AI authoring is not enabled on this server.')
            return redirect('learning:lesson-manage')
        module = modules.filter(pk=request.POST.get('module')).first()
        upload = request.FILES.get('pdf')
        prompt = (request.POST.get('prompt') or '').strip()
        if module is None:
            messages.error(request, 'Choose a subject for the lesson.')
            return redirect('learning:lesson-ai-import')
        if upload is None and not prompt:
            note('AI-1001', request)
            messages.error(request, 'Attach a document, describe the lesson you want, or do both.')
            return redirect('learning:lesson-ai-import')
        try:
            if upload is not None:
                data = generate.generate_from_pdf(
                    upload.read(), upload.name,
                    system=LESSON_SYSTEM, schema=LESSON_SCHEMA,
                    instruction=LESSON_INSTRUCTION, extra_prompt=prompt,
                    # The lesson grammar is too large to compile (it times out),
                    # so the schema goes in the prompt instead.
                    constrain=False)
            else:
                data = generate.generate_from_prompt(
                    prompt, system=LESSON_SYSTEM, schema=LESSON_SCHEMA,
                    instruction=PROMPT_INSTRUCTION, constrain=False)
            lesson = build_lesson_draft(data, module, request.user)
        except generate.GenerationError as exc:
            messages.error(request, str(exc))
            return redirect('learning:lesson-ai-import')
        messages.success(
            request, 'Draft lesson created — review, edit and publish it below. '
                     'Nothing is visible to learners until you publish.')
        return redirect('learning:lesson-editor', lesson_id=lesson.pk)

    return render(request, 'learning/lesson_ai_import.html', {
        'page_title': 'Build a lesson with AI', 'modules': modules,
        'ai_enabled': generate.is_enabled(),
    })


# Appending to an existing lesson only needs the section list, so the schema is
# a trimmed LESSON_SCHEMA — smaller prompt, tighter output.
EXTEND_SCHEMA = {
    'type': 'object',
    'additionalProperties': False,
    'properties': {'sections': LESSON_SCHEMA['properties']['sections']},
    'required': ['sections'],
}


@login_required
@require_POST
def lesson_ai_extend(request, lesson_id):
    """Draft extra sections into an **existing** lesson from a written brief.

    Used by the editor's "Build with AI" panel. New sections are appended after
    whatever the author already has, so nothing they wrote is overwritten — they
    then edit, reorder or delete them like any other section.
    """
    lesson = get_object_or_404(models.Lesson, pk=lesson_id)
    if not _can_author(request.user):
        return JsonResponse({'ok': False, 'error': 'forbidden'}, status=403)
    if not generate.is_enabled():
        return JsonResponse({'ok': False, 'error': 'AI authoring is not enabled on this server.'}, status=400)

    prompt = (request.POST.get('prompt') or '').strip()
    if not prompt:
        return JsonResponse({'ok': False, 'error': 'Describe the sections you want.'}, status=400)

    # A lesson sits under a topic on the new spine, or a module on the legacy
    # one — either way, tell the model where it is so the material fits.
    placement = lesson.topic.label if lesson.topic_id else getattr(lesson.module, 'name', 'this course')
    context = (f'You are adding to an existing lesson titled "{lesson.title}" '
               f'({lesson.subtitle}) in "{placement}". '
               f'Its current sections are: '
               + (', '.join(s.title for s in lesson.sections.all()) or '(none yet)') + '. '
               'Do not repeat material those sections already cover.\n\n')
    try:
        data = generate.generate_from_prompt(
            context + prompt, system=LESSON_SYSTEM, schema=EXTEND_SCHEMA,
            instruction=PROMPT_INSTRUCTION, constrain=False)
    except generate.GenerationError as exc:
        return JsonResponse({'ok': False, 'error': str(exc)}, status=502)

    order = lesson.sections.count()
    block_order = lesson.blocks.count()
    created = []
    for raw_section in (data.get('sections') or []):
        section_type = raw_section.get('section_type')
        section = models.LessonSection.objects.create(
            lesson=lesson, order=order,
            title=(raw_section.get('title') or f'Section {order + 1}')[:200],
            summary=(raw_section.get('summary') or '')[:300],
            section_type=(section_type if section_type in dict(models.LessonSection.TYPE_CHOICES)
                          else models.LessonSection.TYPE_AUTO),
            duration_minutes=max(0, int(raw_section.get('duration_minutes') or 0)),
            requires_previous=bool(raw_section.get('requires_previous')),
        )
        for raw_block in (raw_section.get('blocks') or []):
            block_type, block_data = _block_data(raw_block)
            if block_type is None:
                continue
            models.LessonBlock.objects.create(
                lesson=lesson, section=section, block_type=block_type,
                order=block_order, data=block_data)
            block_order += 1
        created.append(section.title)
        order += 1

    if not created:
        return JsonResponse({'ok': False, 'error': 'The AI returned no usable sections. Try a more specific brief.'},
                            status=502)
    lesson.save(update_fields=['updated_at'])
    return JsonResponse({'ok': True, 'sections': created})
