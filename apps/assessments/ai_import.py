"""AI route for assessments: upload a PDF (mock exam / test / quiz with a memo)
→ Claude drafts a full assessment with sections, questions, mark allocations and
answer keys. The draft is saved in ``draft`` status and opened in the existing
question builder for a human to review and publish — same downstream flow as the
manual ``create``. The AI never publishes.

Auto-markable question types get a machine key (correct choices / accepted
answers); subjective types get the model answer as marking guidance for the
manual marking queue.
"""

from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from core.errors import note
from django.shortcuts import redirect, render

from apps.ai_assistant import generate

from . import models
from .authoring import _guard, _managed_modules

_AUTO_TYPES = {'mcq', 'multi', 'tf', 'short', 'fill'}

ASSESSMENT_SCHEMA = {
    'type': 'object',
    'additionalProperties': False,
    'properties': {
        'title': {'type': 'string'},
        'instructions': {'type': 'string'},
        'pass_mark_pct': {'type': 'integer'},
        'sections': {
            'type': 'array',
            'items': {
                'type': 'object',
                'additionalProperties': False,
                'properties': {
                    'title': {'type': 'string'},
                    'instructions': {'type': 'string'},
                    'questions': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'additionalProperties': False,
                            'properties': {
                                'type': {'type': 'string',
                                         'enum': ['mcq', 'multi', 'tf', 'short', 'fill',
                                                  'long', 'essay']},
                                'text': {'type': 'string'},
                                'marks': {'type': 'number'},
                                'choices': {
                                    'type': 'array',
                                    'items': {
                                        'type': 'object',
                                        'additionalProperties': False,
                                        'properties': {
                                            'text': {'type': 'string'},
                                            'is_correct': {'type': 'boolean'},
                                        },
                                        'required': ['text', 'is_correct'],
                                    },
                                },
                                'accepted_answers': {'type': 'array', 'items': {'type': 'string'}},
                                'model_answer': {'type': 'string'},
                            },
                            'required': ['type', 'text', 'marks'],
                        },
                    },
                },
                'required': ['title', 'questions'],
            },
        },
    },
    'required': ['title', 'sections'],
}

ASSESSMENT_SYSTEM = (
    'You are an assessment author digitising school test and exam papers (South African CAPS, '
    'Grade 1 to Grade 12). Papers range from simple objective class quizzes to written '
    'examination papers with a scenario or source followed by a REQUIRED list of '
    'parts (a), (b), (c)… each carrying its own mark allocation in a mark table, often with a '
    'communication-skills mark and a stated TOTAL.\n\n'
    'Rules:\n'
    '- Preserve every question and its EXACT mark allocation from the paper. Do not invent, '
    'merge, split or re-weight questions.\n'
    '- Pick the closest type: mcq (one correct choice), multi (several correct), tf '
    '(true/false), fill (fill in the blank), short (one-line answer), long or essay (extended '
    'written answer). Extended "required" parts are almost always long or essay.\n'
    '- For mcq/multi/tf give the choices with is_correct flags; for fill/short give '
    'accepted_answers. For long/essay leave those empty.\n'
    '- model_answer holds the marking guidance/rubric/worked solution. If a separate memo or '
    'solution document is provided, base model_answer on it (quote the key marking points and '
    'their marks). If no memo is provided, write a concise model answer yourself and prefix it '
    'with "[AI-generated — verify against the official memo]".\n'
    '- Put scenario text and standing instructions in the section "instructions" field; group '
    'parts under sections that mirror the paper. Include any communication-skills mark as its '
    'own question.'
)

ASSESSMENT_INSTRUCTION = (
    'Digitise this paper into an assessment draft matching the schema. Keep every required '
    'part and its marks exactly. The first document is the question paper; any further document '
    'is its memo/solution — use it for the model answers. Set the pass mark percentage the '
    'paper implies (else 50).'
)


def _dec(value, default='1'):
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal(default)


def build_assessment_draft(data, module, kind, user):
    """Create a draft Assessment + Sections + Questions + Choices from ``data``."""
    assessment = models.Assessment.objects.create(
        module=module,
        title=(data.get('title') or 'Untitled assessment')[:200],
        kind=kind,
        total_marks=0,
        pass_mark_pct=int(data.get('pass_mark_pct') or 50),
        status='draft',
        created_by=user,
    )

    total = Decimal('0')
    for s_order, sec in enumerate(data.get('sections') or []):
        section = models.Section.objects.create(
            assessment=assessment,
            title=(sec.get('title') or 'Section')[:200],
            instructions=sec.get('instructions', ''),
            order=s_order,
        )
        for q_order, q in enumerate(sec.get('questions') or []):
            qtype = q.get('type', 'short')
            marks = _dec(q.get('marks'), '1')
            total += marks
            is_auto = qtype in _AUTO_TYPES
            marking = {}
            if qtype in ('short', 'fill'):
                marking = {'keywords': [a for a in (q.get('accepted_answers') or []) if a]}
            question = models.Question.objects.create(
                section=section,
                type=qtype,
                text=q.get('text', ''),
                marks=marks,
                order=q_order,
                marking=marking,
                marking_mode='auto' if is_auto else 'manual',
                guidance=q.get('model_answer', ''),
            )
            if qtype in ('mcq', 'multi', 'tf'):
                for c_order, ch in enumerate(q.get('choices') or []):
                    models.Choice.objects.create(
                        question=question,
                        text=ch.get('text', ''),
                        is_correct=bool(ch.get('is_correct')),
                        order=c_order,
                    )

    assessment.total_marks = total
    assessment.save(update_fields=['total_marks'])
    return assessment


@login_required
def assessment_ai_import(request):
    """Upload a PDF paper and let Claude draft the assessment, then open the builder."""
    if not _guard(request):
        return HttpResponseForbidden()
    modules = _managed_modules(request)

    if request.method == 'POST':
        if not generate.is_enabled():
            note('AI-7001', request)
            messages.error(request, 'AI authoring is not enabled on this server.')
            return redirect('assessments:manage')
        module = modules.filter(pk=request.POST.get('module')).first()
        kind = request.POST.get('kind') if request.POST.get('kind') in dict(models.Assessment.KIND_CHOICES) else models.Assessment.KIND_QUIZ
        upload = request.FILES.get('pdf')
        if module is None:
            messages.error(request, 'Choose a subject you teach.')
            return redirect('assessments:ai-import')
        if upload is None:
            note('AI-1001', request)
            messages.error(request, 'Attach a PDF exam/quiz to generate from.')
            return redirect('assessments:ai-import')
        # Optional separate memo/solution — PDF sent to Claude natively; a
        # workbook/doc (.xlsx/.docx/.txt/.csv/.md) is extracted to text first.
        from apps.ai_assistant import docextract
        memo = request.FILES.get('memo')
        extra_docs, extra_text = [], None
        if memo is not None:
            if memo.name.lower().endswith('.pdf'):
                extra_docs.append((memo.read(), memo.name))
            elif docextract.supported_memo(memo.name):
                extra_text = docextract.extract_text(memo)
                if not extra_text.strip():
                    note('AI-8001', request)
                    messages.error(request, 'Could not read the memo file — check it opens, or export it to PDF.')
                    return redirect('assessments:ai-import')
            else:
                messages.error(request, 'Memo must be a PDF, Excel (.xlsx), Word (.docx) or text file.')
                return redirect('assessments:ai-import')
        try:
            data = generate.generate_from_pdf(
                upload.read(), upload.name,
                system=ASSESSMENT_SYSTEM, schema=ASSESSMENT_SCHEMA, instruction=ASSESSMENT_INSTRUCTION,
                extra_docs=extra_docs, extra_text=extra_text)
            assessment = build_assessment_draft(data, module, kind, request.user)
        except generate.GenerationError as exc:
            messages.error(request, str(exc))
            return redirect('assessments:ai-import')
        messages.success(
            request, 'Draft created from your PDF — review the questions and marks, then publish.')
        return redirect('assessments:builder', assessment_id=assessment.id)

    return render(request, 'assessments/ai_import.html', {
        'page_title': 'AI assessment from PDF', 'modules': modules,
        'kinds': models.Assessment.KIND_CHOICES, 'ai_enabled': generate.is_enabled(),
    })
