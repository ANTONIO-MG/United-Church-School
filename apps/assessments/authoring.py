"""Educator-facing authoring + marking for assessments.

* **Per-question builder** — create an assessment and add/edit/delete questions,
  choosing per question whether it is *auto-marked* (you define the key: correct
  choices, accepted answers) or *manually marked* (you write a rubric and grade
  it later). If a question isn't flagged manual it defaults to the builder/auto
  path. Total marks auto-sync to the sum of question marks.
* **Marking queue** — the promptable manual path: submitted attempts that have
  answered manual questions surface here; the educator is shown each response
  next to its rubric and awards marks + feedback, which re-grades the attempt.
"""

from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from core.errors import note
from core.roles import role_flags
from core.scoping import taught_module_qs

from . import models
from .marking import _assessment_questions, _has_response, grade_attempt, pending_manual_count


# ---------------------------------------------------------------------------
# access
# ---------------------------------------------------------------------------
def _is_staff_admin(request):
    return role_flags(request)['is_admin_staff']


def _managed_modules(request):
    """Subjects the user may author for (all for staff/admin, taught for educators)."""
    return taught_module_qs(request.user)


def _can_manage(request, assessment):
    """Staff always; an educator only for a paper on a module they teach.

    A paper with no module yet belongs to nobody but staff — refusing is the
    safe answer, and it keeps a half-built assessment from raising here.
    """
    if _is_staff_admin(request):
        return True
    person = getattr(request.user, 'profile', None)
    offering = assessment.module
    return bool(person and offering
                and offering.educators.filter(pk=person.pk).exists())


def _guard(request):
    flags = role_flags(request)
    return flags['is_admin_staff'] or flags['is_educator']


# ---------------------------------------------------------------------------
# builder
# ---------------------------------------------------------------------------
@login_required
def manage(request):
    """Educator's assessments list + entry to the builder."""
    if not _guard(request):
        return HttpResponseForbidden()
    modules = _managed_modules(request)
    assessments = (models.Assessment.objects.filter(module__in=modules)
                   .select_related('module').order_by('-created_at'))
    return render(request, 'assessments/manage.html', {
        'page_title': 'Manage assessments', 'assessments': assessments, 'modules': modules,
    })


@login_required
def create(request):
    """Create a new assessment (then jump into the question builder)."""
    if not _guard(request):
        return HttpResponseForbidden()
    modules = _managed_modules(request)
    if request.method == 'POST':
        module = modules.filter(pk=request.POST.get('module')).first()
        if not module:
            note('ASMT-2001', request)
            messages.error(request, 'Choose a subject you teach.')
            return redirect('assessments:create')
        assessment = models.Assessment.objects.create(
            module=module,
            title=request.POST.get('title', 'Untitled assessment').strip()[:200] or 'Untitled assessment',
            kind=request.POST.get('kind', models.Assessment.KIND_QUIZ),
            component=request.POST.get('component', ''),
            total_marks=0,
            pass_mark_pct=_int(request.POST.get('pass_mark_pct'), 50),
            time_limit_minutes=_int(request.POST.get('time_limit_minutes'), 0),
            attempts_allowed=_int(request.POST.get('attempts_allowed'), 1),
            # Always starts as a draft. Publishing now goes through
            # Assessment.transition_to, which refuses to open a paper that has
            # no questions in it — a form field could previously set any state.
            status=models.Assessment.STATUS_DRAFT,
            created_by=request.user,
        )
        models.Section.objects.create(assessment=assessment, title='Questions', order=0)
        messages.success(request, 'Assessment created — now add questions.')
        return redirect('assessments:builder', assessment_id=assessment.id)

    return render(request, 'assessments/create.html', {
        'page_title': 'New assessment', 'modules': modules,
        'kinds': models.Assessment.KIND_CHOICES, 'components': models.Assessment.COMPONENT_CHOICES,
    })


@login_required
def builder(request, assessment_id):
    """The per-question builder for one assessment."""
    assessment = get_object_or_404(models.Assessment.objects.select_related('module'), pk=assessment_id)
    if not _can_manage(request, assessment):
        return HttpResponseForbidden()

    section = _default_section(assessment)
    questions = section.questions.prefetch_related('choices').order_by('order')

    editing = None
    edit_id = request.GET.get('edit')
    if edit_id:
        editing = questions.filter(pk=edit_id).first()

    return render(request, 'assessments/builder.html', {
        'page_title': f'Build: {assessment.title}',
        'assessment': assessment, 'questions': questions,
        'question_types': models.Question.TYPE_CHOICES,
        'editing': editing, 'editing_ctx': _edit_context(editing) if editing else None,
        'proctor_actions': models.Assessment.ACTION_CHOICES,
    })


@login_required
def status_change(request, assessment_id):
    """Move an assessment along its lifecycle (Draft → Review → Open → Closed).

    The legal moves live on the model (``Assessment.STATUS_TRANSITIONS``), so an
    illegal one is refused here whether it arrives from the builder's buttons or
    a hand-crafted POST.
    """
    assessment = get_object_or_404(models.Assessment, pk=assessment_id)
    if not _can_manage(request, assessment):
        return HttpResponseForbidden()
    if request.method != 'POST':
        return redirect('assessments:builder', assessment_id=assessment.id)

    from django.core.exceptions import ValidationError
    try:
        assessment.transition_to(request.POST.get('status', ''), by=request.user)
        messages.success(request, f'Assessment is now {assessment.get_status_display().lower()}.')
    except ValidationError as exc:
        messages.error(request, '; '.join(exc.messages))
    return redirect('assessments:builder', assessment_id=assessment.id)


@login_required
def proctoring_save(request, assessment_id):
    """Save the exam-integrity ("focus guard") settings from the builder."""
    assessment = get_object_or_404(models.Assessment, pk=assessment_id)
    if not _can_manage(request, assessment):
        return HttpResponseForbidden()
    if request.method != 'POST':
        return redirect('assessments:builder', assessment_id=assessment.id)

    assessment.proctoring_enabled = request.POST.get('proctoring_enabled') == 'on'
    assessment.proctor_warn_limit = max(0, min(50, _int(request.POST.get('proctor_warn_limit'), 3)))
    action = request.POST.get('proctor_action')
    if action in dict(models.Assessment.ACTION_CHOICES):
        assessment.proctor_action = action
    assessment.proctor_block_copy = request.POST.get('proctor_block_copy') == 'on'
    assessment.proctor_require_fullscreen = request.POST.get('proctor_require_fullscreen') == 'on'
    assessment.proctor_blur_content = request.POST.get('proctor_blur_content') == 'on'
    assessment.proctor_grace_seconds = max(1, min(60, _int(request.POST.get('proctor_grace_seconds'), 3)))
    assessment.save(update_fields=[
        'proctoring_enabled', 'proctor_warn_limit', 'proctor_action', 'proctor_block_copy',
        'proctor_require_fullscreen', 'proctor_blur_content', 'proctor_grace_seconds', 'updated_at'])

    messages.success(request, 'Exam integrity settings saved.'
                     if assessment.proctoring_enabled else 'Exam integrity monitoring turned off.')
    return redirect('assessments:builder', assessment_id=assessment.id)


@login_required
def question_save(request, assessment_id):
    """Add or update a question from the builder form."""
    assessment = get_object_or_404(models.Assessment, pk=assessment_id)
    if not _can_manage(request, assessment):
        return HttpResponseForbidden()
    if request.method != 'POST':
        return redirect('assessments:builder', assessment_id=assessment.id)

    section = _default_section(assessment)
    qid = request.POST.get('question_id')
    question = section.questions.filter(pk=qid).first() if qid else models.Question(section=section)

    question.type = request.POST.get('type', 'mcq')
    question.text = request.POST.get('text', '').strip()
    question.marks = _dec(request.POST.get('marks'), Decimal('1'))
    question.marking_mode = (models.Question.MARKING_MANUAL
                             if request.POST.get('marking_mode') == 'manual'
                             else models.Question.MARKING_AUTO)
    question.guidance = request.POST.get('guidance', '').strip() if question.marking_mode == 'manual' else ''
    if not qid:
        question.order = section.questions.count()
    question.marking = {}
    if question.media is None and 'media' in request.FILES:
        question.media = request.FILES['media']
    question.save()

    # Rebuild the answer key/content for the question's type (used for rendering
    # + auto-grading; ignored by the marker when the question is manual).
    _rebuild_question_key(question, request.POST)

    _sync_total_marks(assessment)
    messages.success(request, 'Question saved.')
    return redirect('assessments:builder', assessment_id=assessment.id)


@login_required
def question_delete(request, question_id):
    question = get_object_or_404(models.Question.objects.select_related('section__assessment'), pk=question_id)
    assessment = question.section.assessment
    if not _can_manage(request, assessment):
        return HttpResponseForbidden()
    if request.method == 'POST':
        question.delete()
        _sync_total_marks(assessment)
        messages.success(request, 'Question removed.')
    return redirect('assessments:builder', assessment_id=assessment.id)


# ---------------------------------------------------------------------------
# marking queue (promptable manual marking)
# ---------------------------------------------------------------------------
@login_required
def marking_queue(request):
    """Attempts with answered manual questions awaiting an educator's mark."""
    if not _guard(request):
        return HttpResponseForbidden()
    modules = _managed_modules(request)
    attempts = (models.AssessmentAttempt.objects
                .filter(assessment__module__in=modules, status=models.AssessmentAttempt.STATUS_SUBMITTED)
                .select_related('assessment', 'student').order_by('submitted_at'))
    rows = [{'attempt': a, 'pending': pending_manual_count(a)} for a in attempts]
    rows = [r for r in rows if r['pending']]

    # Attempts the focus guard flagged. These need a human look even when every
    # question was auto-marked, so they would otherwise never surface anywhere.
    flagged = (models.AssessmentAttempt.objects
               .filter(assessment__module__in=modules, integrity_flagged=True)
               .exclude(status=models.AssessmentAttempt.STATUS_IN_PROGRESS)
               .select_related('assessment', 'student')
               .order_by('-submitted_at', '-created_at')[:50])

    return render(request, 'assessments/marking_queue.html', {
        'page_title': 'Marking queue', 'rows': rows, 'flagged': flagged,
    })


@login_required
def mark_attempt(request, public_id):
    """Grade the manual answers of one attempt, prompted by each question's rubric."""
    attempt = get_object_or_404(
        models.AssessmentAttempt.objects.select_related('assessment', 'student'), public_id=public_id)
    if not _can_manage(request, attempt.assessment):
        return HttpResponseForbidden()

    answers = {a.question_id: a for a in attempt.answers.prefetch_related('selected_choices')}
    manual_rows = []
    for question in _assessment_questions(attempt.assessment):
        if question.is_auto_marked:
            continue
        answer = answers.get(question.id)
        if answer is None or not _has_response(answer):
            continue
        manual_rows.append({'question': question, 'answer': answer})

    if request.method == 'POST':
        for row in manual_rows:
            question, answer = row['question'], row['answer']
            awarded = _dec(request.POST.get(f'marks_{answer.id}'), Decimal('0'))
            awarded = max(Decimal('0'), min(awarded, Decimal(str(question.marks))))
            answer.awarded_marks = awarded
            answer.feedback = request.POST.get(f'feedback_{answer.id}', '').strip()
            answer.marked = True
            answer.marked_by = request.user
            answer.is_correct = awarded >= Decimal(str(question.marks))
            answer.save()
        grade_attempt(attempt)  # recompute score / status, and fire the grade signal
        if attempt.status == attempt.STATUS_MARKED:
            # Tell the student once the last hand-marked answer is in.
            from apps.communication.auto import queue_result
            queue_result(attempt, marker=request.user)
        messages.success(request, 'Marks saved.')
        return redirect('assessments:marking-queue')

    # A row imported as ``ai_assisted`` can be offered a rubric suggestion. The
    # flag only decides whether the *button* appears — nothing is requested, and
    # certainly nothing marked, until the teacher asks for it.
    from . import proctoring, rubric_marking
    can_suggest = rubric_marking.is_enabled()
    for row in manual_rows:
        row['can_suggest'] = can_suggest and rubric_marking.wants_suggestion(row['question'])
        row['rubric'] = rubric_marking.rubric_of(row['question'])

    return render(request, 'assessments/mark_attempt.html', {
        'page_title': f'Mark — {attempt.student}', 'attempt': attempt, 'rows': manual_rows,
        'integrity': proctoring.summary(attempt),
    })


@login_required
@require_POST
def suggest_marks(request, answer_id):
    """Rubric suggestion for one answer, as JSON for the marking page.

    Deliberately per-answer and on demand: a teacher asks for help with the one
    they are looking at. Nothing is written — the response is a suggestion the
    page shows beside the answer, and the teacher still types the mark.
    """
    from . import rubric_marking

    answer = get_object_or_404(
        models.Answer.objects.select_related('question', 'attempt__assessment'), pk=answer_id)
    if not _can_manage(request, answer.attempt.assessment):
        return HttpResponseForbidden()

    try:
        suggestion = rubric_marking.suggest(answer)
    except rubric_marking.SuggestionError as exc:
        return JsonResponse({'ok': False, 'error': str(exc)}, status=400)

    return JsonResponse({
        'ok': True,
        'suggested': str(suggestion['suggested']),
        'total': str(suggestion['total']),
        'overall': suggestion['overall'],
        'rows': [{**row, 'marks': str(row['marks']), 'awarded': str(row['awarded'])}
                 for row in suggestion['rows']],
    })


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def _default_section(assessment):
    section = assessment.sections.order_by('order').first()
    if section is None:
        section = models.Section.objects.create(assessment=assessment, title='Questions', order=0)
    return section


def _rebuild_question_key(question, post):
    """(Re)create choices / accepted-answer key for a question from the form."""
    question.choices.all().delete()
    qtype = question.type
    if qtype in ('mcq', 'multi'):
        for i, line in enumerate(_lines(post.get('choices', ''))):
            correct = line.startswith('*')
            text = line[1:].strip() if correct else line
            if text:
                models.Choice.objects.create(question=question, text=text[:400], is_correct=correct, order=i)
    elif qtype == 'tf':
        answer = (post.get('tf_answer') or 'true').lower()
        models.Choice.objects.create(question=question, text='True', is_correct=(answer == 'true'), order=0)
        models.Choice.objects.create(question=question, text='False', is_correct=(answer == 'false'), order=1)
    elif qtype in ('fill', 'short'):
        accepted = _lines(post.get('accepted', ''))
        if accepted:
            question.marking = {'keywords': accepted}
            question.save(update_fields=['marking'])


def _edit_context(question):
    """Reconstruct the builder form values for an existing question."""
    choices_text = ''
    tf_answer = 'true'
    accepted = ''
    if question.type in ('mcq', 'multi'):
        choices_text = '\n'.join(
            (('*' if c.is_correct else '') + c.text) for c in question.choices.all())
    elif question.type == 'tf':
        correct = question.choices.filter(is_correct=True, text='True').exists()
        tf_answer = 'true' if correct else 'false'
    elif question.type in ('fill', 'short'):
        accepted = '\n'.join(question.marking.get('keywords', []) if isinstance(question.marking, dict) else [])
    return {'choices_text': choices_text, 'tf_answer': tf_answer, 'accepted': accepted}


def _sync_total_marks(assessment):
    total = sum((q.marks for q in _assessment_questions(assessment)), Decimal('0'))
    assessment.total_marks = total or Decimal('0')
    assessment.save(update_fields=['total_marks'])


def _lines(text):
    return [ln.strip() for ln in (text or '').splitlines() if ln.strip()]


def _int(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _dec(value, default):
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return default
