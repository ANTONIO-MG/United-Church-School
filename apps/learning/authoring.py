"""Lesson authoring — the block-based lesson creator.

Educators/staff build a lesson from ordered :class:`~apps.learning.models.LessonBlock`
rows (text, media, embedded pages, quizzes, live sessions, references…) in a
single-page editor. The editor talks to these views over ``fetch`` returning
``JsonResponse`` (the same lightweight pattern the module builder + chat use — no
DRF needed). Blocks are reordered by drag-and-drop, media is uploaded per block,
quizzes reuse the ``assessments`` engine and live sessions reuse a Jitsi
``MeetingRoom``. Finally the lesson is published to a module / class / individuals.
"""

import json

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import F, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from core.errors import note
from core.scoping import is_scoped, taught_module_qs

from . import models

User = get_user_model()


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def _staff_like(user):
    person = getattr(user, 'profile', None)
    return bool(user.is_staff or (person and person.user_type in ('admin', 'staff', 'educator')))


def _can_author(user):
    """Role gate: may this person author lessons *at all*?

    Says nothing about **which** lesson — that is enforced where the object is
    looked up (:func:`editable_lessons` and the ``_get_*`` helpers below), so
    every endpoint gets the check for free rather than relying on 20-odd call
    sites each remembering it.
    """
    return user.is_authenticated and _staff_like(user)


def editable_lessons(user):
    """The lessons this user may edit: everything for admin/staff, and for an
    educator the modules they teach plus whatever they authored themselves."""
    qs = models.Lesson.objects.all()
    if not is_scoped(user):
        return qs
    return qs.filter(Q(module__in=taught_module_qs(user)) | Q(created_by=user)).distinct()


def _body(request):
    """Parse a JSON request body (falls back to POST form data)."""
    if request.content_type and 'application/json' in request.content_type:
        try:
            return json.loads(request.body or '{}')
        except (ValueError, TypeError):
            return {}
    return request.POST


def _get_lesson(request, lesson_id):
    """The lesson, if this user may edit it — otherwise a 404.

    Scoping lives here because every lesson-bound authoring endpoint funnels
    through it.
    """
    return get_object_or_404(
        editable_lessons(request.user).select_related('module'), pk=lesson_id)


def _get_block(request, block_id):
    """A block of a lesson this user may edit (404 otherwise)."""
    return get_object_or_404(
        models.LessonBlock.objects.select_related('lesson')
        .filter(lesson__in=editable_lessons(request.user)), pk=block_id)


def _get_section(request, section_id):
    """A section of a lesson this user may edit (404 otherwise)."""
    return get_object_or_404(
        models.LessonSection.objects.select_related('lesson')
        .filter(lesson__in=editable_lessons(request.user)), pk=section_id)


def _deny():
    return JsonResponse({'ok': False, 'error': 'forbidden'}, status=403)


def _ai_enabled():
    """Whether the editor should offer its AI panel (never let this 500 the page)."""
    try:
        from apps.ai_assistant import generate
        return generate.is_enabled()
    except Exception:  # pragma: no cover
        return False


# ---------------------------------------------------------------------------
# lesson-level: list · create · editor · meta · publish · delete
# ---------------------------------------------------------------------------
@login_required
def lesson_manage(request):
    """Author's dashboard — the lessons this educator/staff can edit."""
    if not _can_author(request.user):
        note('LRN-2002', request)
        messages.error(request, 'You do not have permission to author lessons.')
        return redirect('learning:lessons')
    # Educators see lessons in the modules they teach or authored themselves.
    qs = (editable_lessons(request.user)
          .select_related('module', 'created_by').order_by('-updated_at'))
    from apps.assessments.models import Assessment
    assessments = (Assessment.objects.filter(module__in=taught_module_qs(request.user))
                   .select_related('module').order_by('-id')[:100])
    return render(request, 'learning/lesson_manage.html', {
        'page_title': 'Lesson creator', 'lessons': qs[:200], 'assessments': assessments,
    })


@login_required
def lesson_create(request):
    """Create a shell lesson, then jump straight into the block editor."""
    if not _can_author(request.user):
        messages.error(request, 'You do not have permission to author lessons.')
        return redirect('learning:lessons')

    person = getattr(request.user, 'profile', None)
    # Only the modules this author may teach — and the POST is resolved against
    # the same queryset, so a hand-typed id can't file a lesson elsewhere.
    modules = (taught_module_qs(request.user).filter(is_active=True)
                .select_related('programme').order_by('programme__name', 'order', 'name'))

    if request.method == 'POST':
        title = (request.POST.get('title') or '').strip() or 'Untitled lesson'
        module_id = request.POST.get('module') or None
        module = modules.filter(pk=module_id).first() if module_id else modules.first()
        if module is None:
            note('LRN-4001', request)
            messages.error(request, 'Create a subject first — a lesson must belong to one.')
            return redirect('learning:lesson-manage')
        lesson = models.Lesson.objects.create(
            title=title, module=module, created_by=request.user,
            author_name=(request.user.get_full_name() or request.user.get_username()),
            author_role=(getattr(person, 'get_user_type_display', lambda: '')() if person else ''),
            estimated_minutes=int(request.POST.get('estimated_minutes') or 30),
        )
        return redirect('learning:lesson-editor', lesson_id=lesson.pk)

    return render(request, 'learning/lesson_create.html', {
        'page_title': 'New lesson', 'modules': modules,
    })


@login_required
def lesson_editor(request, lesson_id):
    """The single-page block editor for a lesson."""
    lesson = _get_lesson(request, lesson_id)
    if not _can_author(request.user):
        note('LRN-2002', request, action='edit')
        messages.error(request, 'You do not have permission to edit this lesson.')
        return redirect('learning:lessons')

    ensure_body_flow(lesson)
    blocks = [b.to_dict() for b in lesson.blocks.all().order_by('order', 'id')]
    sections = [_section_dict(s) for s in lesson.sections.prefetch_related('blocks__assessment')]
    # Existing quizzes in this module the author can attach instead of making a new one.
    from apps.assessments.models import Assessment
    quizzes = Assessment.objects.filter(module=lesson.module).order_by('-id')[:50]
    audience = audience_options(request.user, lesson)

    from . import styles
    return render(request, 'learning/lesson_editor.html', {
        'page_title': f'Edit · {lesson.title}',
        'lesson': lesson,
        'blocks_json': json.dumps(blocks),
        'sections_json': json.dumps(sections),
        'style_fonts': sorted(styles.FIELDS['font_family']['values']),
        'style_borders': sorted(styles.BORDERS),
        'style_shadows': sorted(styles.SHADOWS),
        'block_types': models.LessonBlock.TYPE_CHOICES,
        'section_types': models.LessonSection.TYPE_CHOICES,
        'modules': audience['modules'],
        'programmes': audience['programmes'],
        'students': audience['students'],
        'quizzes': quizzes,
        'block_style_fields': json.dumps(sorted(styles.ALLOWED_KEYS)),
        'attachments': lesson.resources.all(),
        'ai_enabled': _ai_enabled(),
        'references_json': json.dumps(lesson.references or []),
        'status_choices': models.Lesson.STATUS_CHOICES,
        'visibility_choices': models.Lesson.VISIBILITY_CHOICES,
        'target_module_ids': list(lesson.target_modules.values_list('id', flat=True)),
        'target_programme_ids': list(lesson.target_programmes.values_list('id', flat=True)),
        'target_user_ids': list(lesson.target_users.values_list('id', flat=True)),
    })


@login_required
@require_POST
def lesson_meta_save(request, lesson_id):
    """Autosave the lesson's title / author / references / settings."""
    lesson = _get_lesson(request, lesson_id)
    if not _can_author(request.user):
        return _deny()
    data = _body(request)
    for field in ('title', 'subtitle', 'author_name', 'author_role', 'author_bio'):
        if field in data:
            setattr(lesson, field, (data.get(field) or '')[:2000])
    if 'estimated_minutes' in data:
        try:
            lesson.estimated_minutes = max(1, int(data.get('estimated_minutes') or 30))
        except (ValueError, TypeError):
            pass
    if 'references' in data and isinstance(data['references'], list):
        # Sanitise to a clean list of dicts.
        refs = []
        for r in data['references'][:100]:
            if isinstance(r, dict) and (r.get('text') or r.get('url')):
                refs.append({'text': str(r.get('text', ''))[:500], 'url': str(r.get('url', ''))[:500],
                             'authors': str(r.get('authors', ''))[:300], 'year': str(r.get('year', ''))[:20]})
        lesson.references = refs
    lesson.save()
    return JsonResponse({'ok': True, 'saved_at': timezone.now().isoformat()})


def audience_options(user, lesson):
    """The students, modules and programmes this educator may assign a lesson to.

    An educator authors **only for their own audience**: the students enrolled
    in the modules they teach, and the programmes those modules belong to.
    Admin/staff see everyone.
    """
    from apps.learning.models import Programme, ProgrammeModule

    if is_scoped(user):
        # Always include the lesson's own module so the author can still reach a
        # lesson handed to them, even if it sits outside their teaching list.
        modules = ProgrammeModule.objects.filter(
            Q(pk__in=taught_module_qs(user).values('pk')) | Q(pk=lesson.module_id))
    else:
        modules = ProgrammeModule.objects.filter(is_active=True)

    modules = modules.select_related('programme').order_by('programme__name', 'order', 'name')
    students = (User.objects.filter(is_active=True, profile__module_enrolments__programme_module__in=modules)
                .select_related('profile')
                .distinct().order_by('first_name', 'last_name', 'username')[:1000])
    programmes = Programme.objects.filter(modules__in=modules).distinct().order_by('name')
    return {'modules': modules, 'students': students, 'programmes': programmes}


@login_required
@require_POST
def lesson_publish(request, lesson_id):
    """Set status + who the lesson is available to.

    The editor offers three audience buttons — **Student** (named individuals),
    **Programme** (everyone registered for it) and **Module** — which map onto the
    lesson's ``visibility`` plus the matching target M2M.
    """
    lesson = _get_lesson(request, lesson_id)
    if not _can_author(request.user):
        return _deny()
    data = _body(request)

    status = data.get('status')
    if status in dict(models.Lesson.STATUS_CHOICES):
        lesson.status = status
    visibility = data.get('visibility')
    if visibility in dict(models.Lesson.VISIBILITY_CHOICES):
        lesson.visibility = visibility
    for dtf in ('publish_at', 'expire_at'):
        if dtf in data:
            val = data.get(dtf) or None
            setattr(lesson, dtf, val)
    lesson.save()

    # Targeting — only ever within what this author is allowed to reach.
    allowed = audience_options(request.user, lesson)
    if 'target_modules' in data:
        ids = [int(i) for i in (data.get('target_modules') or []) if str(i).isdigit()]
        lesson.target_modules.set(allowed['modules'].filter(pk__in=ids))
    if 'target_programmes' in data:
        ids = [int(i) for i in (data.get('target_programmes') or []) if str(i).isdigit()]
        lesson.target_programmes.set(allowed['programmes'].filter(pk__in=ids))
    if 'target_users' in data:
        ids = [int(i) for i in (data.get('target_users') or []) if str(i).isdigit()]
        lesson.target_users.set(User.objects.filter(pk__in=ids, id__in=[u.id for u in allowed['students']]))

    return JsonResponse({'ok': True, 'status': lesson.status, 'is_live': lesson.is_live,
                         'visibility': lesson.visibility})


# ---------------------------------------------------------------------------
# sections — the collapsible panels an author drops into the body
#
# A section is created *through* a block: adding a "Dropdown section" element to
# the flow makes both the LessonSection (which owns progress, gating and timing)
# and the anchor LessonBlock that positions it. Everything the editor needs about
# a section therefore rides along on the block payload.
# ---------------------------------------------------------------------------
def _section_dict(section):
    return {
        'id': section.pk, 'title': section.title, 'summary': section.summary,
        'order': section.order, 'section_type': section.section_type,
        'resolved_type': section.resolved_type, 'type_label': section.type_label,
        'type_icon': section.type_icon, 'type_tone': section.type_tone,
        'duration_minutes': section.duration_minutes, 'minutes': section.minutes,
        'duration_label': section.duration_label,
        'is_required': section.is_required, 'requires_previous': section.requires_previous,
        'open_by_default': section.open_by_default,
    }


def ensure_body_flow(lesson):
    """Make sure every section of ``lesson`` has an anchor block in the body.

    The 0013 migration does this for existing content; this is the runtime
    safety net for anything created since by a path that made a section directly
    (an import, a fixture, the admin). Without an anchor a section would exist in
    the database but never appear on the page. Returns how many were added.
    """
    orphans = list(lesson.sections.filter(anchor_block__isnull=True).order_by('order', 'id'))
    if not orphans:
        return 0
    next_order = lesson.blocks.filter(section__isnull=True).count()
    for index, section in enumerate(orphans):
        models.LessonBlock.objects.create(
            lesson=lesson, section=None, holds_section=section,
            block_type=models.LessonBlock.TYPE_SECTION,
            order=next_order + index,
            data={'title': section.title, 'summary': section.summary},
        )
    return len(orphans)


def _new_section_block(lesson, *, order, title=''):
    """Create a section plus the anchor block that places it in the body."""
    count = lesson.sections.count()
    section = models.LessonSection.objects.create(
        lesson=lesson, order=count,
        title=(title or f'Section {count + 1}')[:200],
    )
    return models.LessonBlock.objects.create(
        lesson=lesson, section=None, holds_section=section,
        block_type=models.LessonBlock.TYPE_SECTION, order=order,
        data={'title': section.title, 'summary': ''},
    )


@login_required
@require_POST
def section_add(request, lesson_id):
    """Add a dropdown section to the end of the lesson body."""
    lesson = _get_lesson(request, lesson_id)
    if not _can_author(request.user):
        return _deny()
    data = _body(request)
    block = _new_section_block(
        lesson, order=lesson.blocks.filter(section__isnull=True).count(),
        title=data.get('title') or '')
    lesson.save(update_fields=['updated_at'])
    return JsonResponse({'ok': True, 'block': block.to_dict(),
                         'section': _section_dict(block.holds_section)})


@login_required
@require_POST
def section_save(request, section_id):
    section = _get_section(request, section_id)
    if not _can_author(request.user):
        return _deny()
    data = _body(request)
    if 'title' in data:
        section.title = (data.get('title') or 'Untitled section')[:200]
    if 'summary' in data:
        section.summary = (data.get('summary') or '')[:300]
    if data.get('section_type') in dict(models.LessonSection.TYPE_CHOICES):
        section.section_type = data['section_type']
    if 'duration_minutes' in data:
        try:
            section.duration_minutes = max(0, int(data.get('duration_minutes') or 0))
        except (TypeError, ValueError):
            pass
    for flag in ('is_required', 'requires_previous', 'open_by_default'):
        if flag in data:
            setattr(section, flag, bool(data[flag]))
    section.save()
    # Keep the anchor block's cached title in step so the body reads correctly
    # without a round-trip to the section table.
    anchor = models.LessonBlock.objects.filter(holds_section=section).first()
    if anchor is not None:
        anchor.data = {**(anchor.data or {}), 'title': section.title,
                       'summary': section.summary}
        anchor.save(update_fields=['data', 'updated_at'])
    section.lesson.save(update_fields=['updated_at'])
    return JsonResponse({'ok': True, 'section': _section_dict(section)})


@login_required
@require_POST
def section_delete(request, section_id):
    """Remove a section from the body.

    By default its contents are *kept* — they move up into the main flow where
    the section used to sit, so nothing an author wrote is silently destroyed.
    Pass ``keep_blocks: false`` to delete the section with everything in it.
    """
    section = _get_section(request, section_id)
    if not _can_author(request.user):
        return _deny()
    lesson = section.lesson
    anchor = models.LessonBlock.objects.filter(holds_section=section).first()
    at = anchor.order if anchor else lesson.blocks.filter(section__isnull=True).count()

    if _body(request).get('keep_blocks', True):
        # Splice the children into the body at the section's own position.
        children = list(section.blocks.order_by('order', 'id'))
        shift = max(0, len(children) - 1)
        if shift:
            (models.LessonBlock.objects
             .filter(lesson=lesson, section__isnull=True, order__gt=at)
             .update(order=F('order') + shift))
        for offset, child in enumerate(children):
            child.section = None
            child.order = at + offset
            child.save(update_fields=['section', 'order'])
    else:
        section.blocks.all().delete()

    section.delete()          # cascades to the anchor block (OneToOne)
    _renumber_body(lesson)
    for index, remaining in enumerate(lesson.sections.all()):
        if remaining.order != index:
            remaining.order = index
            remaining.save(update_fields=['order'])
    return JsonResponse({'ok': True})


def _renumber_body(lesson):
    """Compact the top-level flow so ``order`` stays 0..n-1 and contiguous."""
    for index, block in enumerate(lesson.blocks.filter(section__isnull=True)
                                  .order_by('order', 'id')):
        if block.order != index:
            block.order = index
            block.save(update_fields=['order'])


@login_required
@require_POST
def section_reorder(request, lesson_id):
    """Legacy endpoint: sections now move by moving their anchor block, so this
    only keeps ``LessonSection.order`` consistent with the body order."""
    lesson = _get_lesson(request, lesson_id)
    if not _can_author(request.user):
        return _deny()
    order = [int(i) for i in (_body(request).get('order') or []) if str(i).isdigit()]
    by_id = {s.pk: s for s in lesson.sections.all()}
    for index, sid in enumerate(order):
        section = by_id.get(sid)
        if section and section.order != index:
            section.order = index
            section.save(update_fields=['order'])
    lesson.save(update_fields=['updated_at'])
    return JsonResponse({'ok': True})


@login_required
@require_POST
def block_move(request, block_id):
    """Move a block into a section (or back out to the body) at a given position
    — the drop half of the editor's drag-and-drop."""
    block = _get_block(request, block_id)
    if not _can_author(request.user):
        return _deny()
    data = _body(request)
    section_id = data.get('section_id')
    section = None
    if section_id:
        section = models.LessonSection.objects.filter(pk=section_id, lesson=block.lesson).first()
    # A section block is always part of the body: nesting one inside another
    # would make the flow (and the gating rules) ambiguous.
    if block.is_section:
        section = None
    block.section = section
    block.save(update_fields=['section', 'updated_at'])

    # Re-number the destination group so ``order`` stays contiguous.
    order = [int(i) for i in (data.get('order') or []) if str(i).isdigit()]
    if order:
        by_id = {b.pk: b for b in block.lesson.blocks.all()}
        for index, bid in enumerate(order):
            sibling = by_id.get(bid)
            if sibling and sibling.order != index:
                sibling.order = index
                sibling.save(update_fields=['order'])
    block.lesson.save(update_fields=['updated_at'])
    return JsonResponse({'ok': True, 'block': block.to_dict()})


# ---------------------------------------------------------------------------
# lesson attachments (PDFs · images · text files …)
# ---------------------------------------------------------------------------
_KIND_BY_EXT = {
    'pdf': 'pdf', 'doc': 'word', 'docx': 'word', 'ppt': 'ppt', 'pptx': 'ppt',
    'txt': 'text', 'md': 'text', 'csv': 'text', 'rtf': 'text',
    'png': 'image', 'jpg': 'image', 'jpeg': 'image', 'gif': 'image', 'webp': 'image', 'svg': 'image',
    'mp3': 'audio', 'wav': 'audio', 'm4a': 'audio',
    'mp4': 'video', 'webm': 'video', 'mov': 'video',
}


def _resource_dict(resource):
    url = ''
    if resource.file:
        try:
            url = resource.file.url
        except Exception:
            url = ''
    return {'id': resource.pk, 'kind': resource.kind, 'title': resource.title,
            'url': url or resource.url, 'kind_label': resource.get_kind_display()}


@login_required
@require_POST
def attachment_add(request, lesson_id):
    """Attach one or more documents to the lesson (multipart, ``files``)."""
    lesson = _get_lesson(request, lesson_id)
    if not _can_author(request.user):
        return _deny()
    uploads = request.FILES.getlist('files') or ([request.FILES['file']] if 'file' in request.FILES else [])
    if not uploads:
        return JsonResponse({'ok': False, 'error': 'no-file'}, status=400)
    created = []
    order = lesson.resources.count()
    for upload in uploads:
        ext = upload.name.rsplit('.', 1)[-1].lower() if '.' in upload.name else ''
        resource = models.LessonResource.objects.create(
            lesson=lesson, kind=_KIND_BY_EXT.get(ext, 'download'),
            title=upload.name[:200], file=upload, order=order)
        created.append(_resource_dict(resource))
        order += 1
    lesson.save(update_fields=['updated_at'])
    return JsonResponse({'ok': True, 'attachments': created})


@login_required
@require_POST
def attachment_delete(request, resource_id):
    resource = get_object_or_404(
        models.LessonResource.objects.filter(lesson__in=editable_lessons(request.user)),
        pk=resource_id)
    if not _can_author(request.user):
        return _deny()
    resource.delete()
    return JsonResponse({'ok': True})


@login_required
@require_POST
def lesson_delete(request, lesson_id):
    lesson = _get_lesson(request, lesson_id)
    if not _can_author(request.user):
        return _deny()
    lesson.delete()
    messages.success(request, 'Lesson deleted.')
    return JsonResponse({'ok': True, 'redirect': reverse('learning:lesson-manage')})


# ---------------------------------------------------------------------------
# block CRUD + reorder + media upload
# ---------------------------------------------------------------------------
@login_required
@require_POST
def block_add(request, lesson_id):
    lesson = _get_lesson(request, lesson_id)
    if not _can_author(request.user):
        return _deny()
    data = _body(request)
    block_type = data.get('block_type') or models.LessonBlock.TYPE_TEXT
    if block_type not in dict(models.LessonBlock.TYPE_CHOICES):
        return JsonResponse({'ok': False, 'error': 'bad-type'}, status=400)

    section = _section_for(lesson, data.get('section_id'))
    # A "dropdown section" element creates the section it anchors, and always
    # sits in the body — sections don't nest.
    if block_type == models.LessonBlock.TYPE_SECTION:
        block = _new_section_block(
            lesson, order=lesson.blocks.filter(section__isnull=True).count(),
            title=(data.get('title') or ''))
        lesson.save(update_fields=['updated_at'])
        return JsonResponse({'ok': True, 'block': block.to_dict(),
                             'section': _section_dict(block.holds_section)})

    # Append to the end of whichever group it was dropped into.
    next_order = lesson.blocks.filter(section=section).count()
    block = models.LessonBlock.objects.create(
        lesson=lesson, section=section, block_type=block_type, order=next_order,
        data=_default_data(block_type), style=_default_style(block_type),
    )
    lesson.save(update_fields=['updated_at'])
    return JsonResponse({'ok': True, 'block': block.to_dict()})


def _section_for(lesson, section_id):
    """Resolve a section id from the editor to a section of ``lesson`` (or None)."""
    if not section_id:
        return None
    return models.LessonSection.objects.filter(pk=section_id, lesson=lesson).first()


def _default_data(block_type):
    return {
        models.LessonBlock.TYPE_HEADING: {'text': 'Section heading', 'level': 2},
        models.LessonBlock.TYPE_TEXT: {'html': ''},
        models.LessonBlock.TYPE_CALLOUT: {'html': '', 'variant': 'info'},
        models.LessonBlock.TYPE_REFERENCE: {'text': '', 'url': '', 'authors': '', 'year': ''},
        models.LessonBlock.TYPE_EMBED: {'url': '', 'title': '', 'height': 480, 'mode': 'iframe'},
        models.LessonBlock.TYPE_VIDEO: {'url': '', 'provider': 'file', 'caption': ''},
        models.LessonBlock.TYPE_AUDIO: {'url': '', 'caption': ''},
        models.LessonBlock.TYPE_IMAGE: {'url': '', 'caption': '', 'alt': ''},
        models.LessonBlock.TYPE_FILE: {'title': '', 'description': ''},
        models.LessonBlock.TYPE_TABLE: {
            'caption': '', 'has_header': True,
            'headers': ['Column 1', 'Column 2'],
            'rows': [['', ''], ['', '']],
        },
        # A diagram is a labelled image: base picture (uploaded ``media`` or
        # ``url``) plus positioned ``labels`` [{n, x, y, text}] where x/y are
        # percentages of the image dimensions.
        models.LessonBlock.TYPE_DIAGRAM: {'url': '', 'alt': '', 'caption': '', 'labels': []},
    }.get(block_type, {})


def _default_style(block_type):
    """Sensible opening formatting so a new element looks deliberate.

    Authors then adjust it in the Format panel; these are only starting points.
    """
    return {
        models.LessonBlock.TYPE_HEADING: {'font_weight': '700', 'margin_top': '18px',
                                          'margin_bottom': '8px'},
        models.LessonBlock.TYPE_IMAGE: {'align': 'center', 'width': '100%'},
        models.LessonBlock.TYPE_VIDEO: {'align': 'center', 'width': '100%'},
        models.LessonBlock.TYPE_CALLOUT: {'padding': '16px', 'radius': '10px'},
    }.get(block_type, {})


@login_required
@require_POST
def block_save(request, block_id):
    block = _get_block(request, block_id)
    if not _can_author(request.user):
        return _deny()
    data = _body(request)
    if isinstance(data.get('data'), dict):
        block.data = data['data']
    if 'style' in data:
        # Whitelisted on the way in as well as the way out — an unrecognised
        # property never even reaches the database.
        from . import styles
        block.style = styles.clean(data.get('style'))
    if 'track' in data:
        block.track = bool(data['track'])
    block.save(update_fields=['data', 'style', 'track', 'updated_at'])

    # A section block's title is edited in the body; mirror it onto the section
    # itself so the player's contents/timing use the same words.
    if block.is_section:
        section = block.holds_section
        section.title = ((block.data or {}).get('title') or section.title)[:200]
        section.summary = ((block.data or {}).get('summary') or '')[:300]
        section.save(update_fields=['title', 'summary', 'updated_at'])

    block.lesson.save(update_fields=['updated_at'])
    return JsonResponse({'ok': True, 'block': block.to_dict()})


@login_required
@require_POST
def block_delete(request, block_id):
    block = _get_block(request, block_id)
    if not _can_author(request.user):
        return _deny()
    lesson, section = block.lesson, block.section
    # Deleting a section block takes its section — and everything inside it —
    # with it, which is what removing the panel from the page means. Use the
    # section-delete endpoint to keep the contents.
    block.delete()
    # Compact ordering within the group the block came from.
    for index, sibling in enumerate(lesson.blocks.filter(section=section)
                                    .order_by('order', 'id')):
        if sibling.order != index:
            sibling.order = index
            sibling.save(update_fields=['order'])
    return JsonResponse({'ok': True})


@login_required
@require_POST
def block_reorder(request, lesson_id):
    lesson = _get_lesson(request, lesson_id)
    if not _can_author(request.user):
        return _deny()
    data = _body(request)
    order = data.get('order') or []
    by_id = {b.pk: b for b in lesson.blocks.all()}
    for i, bid in enumerate(order):
        b = by_id.get(int(bid)) if str(bid).isdigit() else None
        if b and b.order != i:
            b.order = i
            b.save(update_fields=['order'])
    lesson.save(update_fields=['updated_at'])
    return JsonResponse({'ok': True})


@login_required
@require_POST
def block_upload(request, block_id):
    """Upload media for an image/video/audio/file block (multipart)."""
    block = _get_block(request, block_id)
    if not _can_author(request.user):
        return _deny()
    upload = request.FILES.get('file')
    if not upload:
        return JsonResponse({'ok': False, 'error': 'no-file'}, status=400)
    block.media = upload
    data = dict(block.data or {})
    data['filename'] = upload.name
    data['size'] = upload.size
    data['content_type'] = getattr(upload, 'content_type', '')
    if not data.get('title'):
        data['title'] = upload.name
    block.data = data
    block.save(update_fields=['media', 'data', 'updated_at'])
    return JsonResponse({'ok': True, 'block': block.to_dict()})


# ---------------------------------------------------------------------------
# interactive blocks: quiz (assessments) · live session (meeting)
# ---------------------------------------------------------------------------
@login_required
@require_POST
def attach_quiz(request, lesson_id):
    """Attach a quiz/test block. Either create a fresh assessment (and jump to the
    question builder) or link an existing one in the module."""
    lesson = _get_lesson(request, lesson_id)
    if not _can_author(request.user):
        return _deny()
    from apps.assessments.models import Assessment, Section
    data = _body(request)

    existing_id = data.get('assessment_id')
    if existing_id:
        assessment = Assessment.objects.filter(pk=existing_id, module=lesson.module).first()
        if assessment is None:
            return JsonResponse({'ok': False, 'error': 'not-found'}, status=404)
        builder = False
    else:
        kind = data.get('kind') if data.get('kind') in ('quiz', 'test') else 'quiz'
        assessment = Assessment.objects.create(
            module=lesson.module, lesson=lesson, kind=kind,
            title=(data.get('title') or f'{lesson.title} — {kind.title()}')[:200],
            pass_mark_pct=int(data.get('pass_mark_pct') or 50),
            created_by=request.user,
        )
        Section.objects.get_or_create(assessment=assessment, order=0, defaults={'title': 'Questions'})
        builder = True

    section = _section_for(lesson, data.get('section_id'))
    block = models.LessonBlock.objects.create(
        lesson=lesson, section=section,
        block_type=models.LessonBlock.TYPE_QUIZ,
        order=lesson.blocks.filter(section=section).count(), assessment=assessment,
        data={'title': assessment.title},
    )
    return JsonResponse({
        'ok': True, 'block': block.to_dict(),
        'builder_url': reverse('assessments:builder', args=[assessment.pk]) if builder else '',
        'assessment_title': assessment.title,
    })


@login_required
@require_POST
def module_live_schedule(request, module_id):
    """Schedule a live class for a module: provision a Teams/Jitsi room and back
    it with a ClassSession so joining auto-records attendance. Educators/staff only."""
    from datetime import datetime, timedelta

    from django.utils import timezone
    from apps.learning.models import ProgrammeModule
    from apps.communication.models import ClassSession
    from apps.msteams import services as teams

    module = get_object_or_404(ProgrammeModule, pk=module_id)
    person = getattr(request.user, 'profile', None)
    may_host = (request.user.is_staff
                or (person and (person.user_type in ('admin', 'staff')
                                or module.educators.filter(pk=person.pk).exists())))
    if not may_host:
        note('LRN-2002', request, action='schedule-live')
        messages.error(request, 'You cannot schedule live classes for this subject.')
        return redirect('learning:module-profile', pk=module.pk, tab='live')

    title = (request.POST.get('title') or f'{module.name} — live class').strip()[:200]
    try:
        sdate = datetime.strptime(request.POST.get('session_date', ''), '%Y-%m-%d').date()
        stime = datetime.strptime(request.POST.get('start_time', ''), '%H:%M').time()
    except ValueError:
        messages.error(request, 'Enter a valid date and start time.')
        return redirect('learning:module-profile', pk=module.pk, tab='live')
    start = timezone.make_aware(datetime.combine(sdate, stime), timezone.get_current_timezone())
    try:
        minutes = max(15, int(request.POST.get('duration') or 60))
    except ValueError:
        minutes = 60
    end = start + timedelta(minutes=minutes)

    meeting = teams.create_class_meeting(
        host=request.user, title=title, module=module, start=start, end=end)
    ClassSession.objects.create(
        module=module, title=title, session_date=sdate, starts_at=start, ends_at=end,
        meeting=meeting, created_by=request.user)
    messages.success(request, f'Live class scheduled ({meeting.get_provider_display()}).')
    return redirect('learning:module-profile', pk=module.pk, tab='live')


@login_required
@require_POST
def attach_meeting(request, lesson_id):
    """Attach a live online-class block for the lesson's module.

    Provisions the room through :func:`apps.msteams.services.create_class_meeting`,
    so it becomes a **Microsoft Teams** meeting when Teams is configured (organiser
    = the educator's licensed account) and falls back to an in-app **Jitsi** room
    otherwise — transparent to the learner, who always joins via the in-app link.
    """
    from django.utils.dateparse import parse_datetime

    lesson = _get_lesson(request, lesson_id)
    if not _can_author(request.user):
        return _deny()
    from apps.msteams import services as teams
    data = _body(request)
    start = parse_datetime(data.get('scheduled_start') or '') if data.get('scheduled_start') else None
    meeting = teams.create_class_meeting(
        host=request.user,
        title=(data.get('title') or f'{lesson.title} — live class')[:200],
        description=data.get('description', '') or '',
        start=start,
        module=lesson.module,
    )
    block = models.LessonBlock.objects.create(
        lesson=lesson, section=_section_for(lesson, data.get('section_id')),
        block_type=models.LessonBlock.TYPE_MEETING,
        order=lesson.blocks.count(), meeting=meeting,
        data={'title': meeting.title, 'provider': meeting.provider},
    )
    d = block.to_dict()
    d['join_url'] = meeting.get_join_url()
    d['provider'] = meeting.provider
    return JsonResponse({'ok': True, 'block': d})
