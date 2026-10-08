"""HTML views for assessments.

* ``index``  — the list of assessments available to the user (students get a
  Take button; educators/staff see everything).
* ``take``   — the test-taking player: sections → questions, resume-in-progress,
  a client-side timer, attempt-limit + availability-window enforcement.
* ``submit`` — persist answers, auto-mark objective questions (``marking``) and
  record the :class:`AssessmentAttempt` (which recomputes the report-card grade
  ).
* ``result`` — score + per-question review.

Same-origin + login-protected, so normal session auth + CSRF apply.
"""

import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from core.roles import role_flags
from core.scoping import children_of, is_scoped, taught_module_qs, viewing_child

from . import models, proctoring
from .marking import _assessment_questions, grade_attempt


# ---------------------------------------------------------------------------
# access helpers
# ---------------------------------------------------------------------------
def _is_staff_like(request):
    flags = role_flags(request)
    return flags['is_admin_staff'] or flags['is_educator']


def _can_access(user, assessment):
    """Whether ``user`` is on the module this paper belongs to.

    A paper with no module is refused rather than raising: an assessment can be
    half-built (imported against a topic, or created before an offering was
    picked), and a candidate meeting one should be turned away, not shown a 500.
    """
    from apps.learning.access import is_staff_like
    if is_staff_like(user):          # admin and staff open every paper in the school
        return True
    person = getattr(user, 'profile', None)
    offering = assessment.module
    if person is None or offering is None:
        return False
    return (offering.students.filter(pk=person.pk).exists()
            or offering.educators.filter(pk=person.pk).exists())


def _within_window(assessment):
    now = timezone.now()
    if assessment.available_from and now < assessment.available_from:
        return False
    if assessment.available_to and now > assessment.available_to:
        return False
    return True


# ---------------------------------------------------------------------------
# list
# ---------------------------------------------------------------------------
@login_required
def index(request):
    """The assessments this user is concerned with.

    Learners see the open ones in their own modules; educators the ones they
    set; **a parent sees their child's** — the same list the child sees, with the
    child's results, but read-only (no Take button: sitting the assessment is the
    learner's to do).
    """
    is_staff = _is_staff_like(request)
    child = viewing_child(request)
    qs = models.Assessment.objects.select_related('module').order_by('-created_at')

    if child is not None:
        person = getattr(child, 'profile', None)
        module_ids = list(person.selected_modules.values_list('id', flat=True)) if person else []
        qs = qs.filter(status='open', module_id__in=module_ids)
    elif not is_staff:
        person = getattr(request.user, 'profile', None)
        module_ids = list(person.selected_modules.values_list('id', flat=True)) if person else []
        qs = qs.filter(status='open', module_id__in=module_ids)
    elif is_scoped(request.user):
        # An educator sets and marks work for their own modules only.
        qs = qs.filter(module__in=taught_module_qs(request.user))

    # Best finished attempt per assessment — the learner's own, or the child's.
    best = {}
    if not is_staff:
        for att in (models.AssessmentAttempt.objects
                    .filter(student=child or request.user, assessment__in=qs,
                            status__in=['submitted', 'marked'])
                    .order_by('assessment_id', '-score')):
            best.setdefault(att.assessment_id, att)

    name = (child.get_full_name() or child.get_username()) if child else ''
    return render(request, 'assessments/index.html', {
        'page_title': f'{name}’s Assessments' if child else 'Assessments',
        'assessments': qs[:100],
        'is_staff': is_staff, 'best': best,
        'child': child, 'read_only': child is not None,
        'children': children_of(request.user) if child else None,
    })


# ---------------------------------------------------------------------------
# take
# ---------------------------------------------------------------------------
@login_required
def take(request, assessment_id):
    assessment = get_object_or_404(models.Assessment.objects.select_related('module'), pk=assessment_id)
    if not _can_access(request.user, assessment):
        return HttpResponseForbidden('You are not enrolled for this assessment.')

    is_staff = _is_staff_like(request)
    if not is_staff and (assessment.status != 'open' or not _within_window(assessment)):
        from core.errors import note
        note('ASMT-4003', request, assessment=assessment.pk, status=assessment.status)
        messages.error(request, 'This assessment is not currently open.')
        return redirect('assessments:index')

    attempt = _get_or_create_attempt(request.user, assessment)
    if attempt is None:
        messages.warning(request, 'You have used all your attempts for this assessment.')
        return redirect('assessments:index')

    # An attempt the focus guard ended cannot be reopened — finalise it with
    # whatever was answered so reloading the page is not a way back in.
    if attempt.terminated_at and attempt.status == models.AssessmentAttempt.STATUS_IN_PROGRESS:
        grade_attempt(attempt)
        messages.error(request, 'This attempt was ended because you left the assessment window '
                                'too many times. It has been submitted as it stood.')
        return redirect('assessments:result', public_id=attempt.public_id)

    sections = assessment.sections.prefetch_related('questions__choices').order_by('order')
    existing = {a.question_id: a for a in attempt.answers.prefetch_related('selected_choices')}
    # For resume: {question_id: [selected choice ids]} and {question_id: "text"}.
    selected_map = {str(qid): list(a.selected_choices.values_list('id', flat=True))
                    for qid, a in existing.items()}
    text_map = {str(qid): (a.response or {}).get('text', '') for qid, a in existing.items()}

    # Educators previewing their own assessment are not proctored.
    guard = proctoring.client_config(assessment, attempt)
    if is_staff:
        guard['enabled'] = False

    return render(request, 'assessments/take.html', {
        'page_title': assessment.title, 'assessment': assessment,
        'attempt': attempt, 'sections': sections,
        'selected_map': json.dumps(selected_map), 'text_map': json.dumps(text_map),
        'time_limit': assessment.time_limit_minutes,
        'guard_json': json.dumps(guard), 'guard': guard,
    })


@login_required
@require_POST
def proctor_event(request, public_id):
    """Report one integrity event for an in-progress attempt (focus guard).

    The browser says only *what happened*; the tally, the limit and any
    decision to end the attempt are computed in
    :mod:`apps.assessments.proctoring` so a tampered client cannot lower its
    own warning count.
    """
    attempt = get_object_or_404(
        models.AssessmentAttempt.objects.select_related('assessment'),
        public_id=public_id, student=request.user)
    if attempt.status != models.AssessmentAttempt.STATUS_IN_PROGRESS:
        return JsonResponse({'ok': False, 'error': 'not-in-progress'}, status=409)
    if not proctoring.is_active(attempt.assessment):
        return JsonResponse({'ok': True, 'action': '', 'warnings': 0})

    detail = {'ua': request.META.get('HTTP_USER_AGENT', '')[:200]}
    if request.POST.get('detail'):
        detail['note'] = request.POST['detail'][:200]
    state = proctoring.record(
        attempt, request.POST.get('kind') or '',
        seconds_away=request.POST.get('seconds') or 0, detail=detail)
    state['ok'] = True
    return JsonResponse(state)


def _get_or_create_attempt(user, assessment):
    """Resume an in-progress attempt, or start a new one if attempts remain."""
    attempts = models.AssessmentAttempt.objects.filter(assessment=assessment, student=user)
    in_progress = attempts.filter(status=models.AssessmentAttempt.STATUS_IN_PROGRESS).order_by('-attempt_no').first()
    if in_progress:
        return in_progress
    finished = attempts.exclude(status=models.AssessmentAttempt.STATUS_IN_PROGRESS)
    allowed = assessment.attempts_allowed  # 0 = unlimited
    if allowed and finished.count() >= allowed:
        return None
    last = attempts.order_by('-attempt_no').first()
    next_no = (last.attempt_no + 1) if last else 1
    return models.AssessmentAttempt.objects.create(
        assessment=assessment, student=user, attempt_no=next_no,
        status=models.AssessmentAttempt.STATUS_IN_PROGRESS, started_at=timezone.now())


@login_required
@require_POST
def submit(request, public_id):
    attempt = get_object_or_404(
        models.AssessmentAttempt.objects.select_related('assessment'),
        public_id=public_id, student=request.user)
    if attempt.status != models.AssessmentAttempt.STATUS_IN_PROGRESS:
        return redirect('assessments:result', public_id=attempt.public_id)

    for question in _assessment_questions(attempt.assessment):
        field = f'q_{question.id}'
        answer, _ = models.Answer.objects.get_or_create(attempt=attempt, question=question)

        if question.type in ('mcq', 'tf'):
            answer.save()
            choice_id = request.POST.get(field)
            answer.selected_choices.set([choice_id] if choice_id else [])
        elif question.type == 'multi':
            answer.save()
            answer.selected_choices.set(request.POST.getlist(field))
        elif question.type in ('matching', 'ordering'):
            answer.response = {'value': request.POST.get(field, '')}
            answer.save()
        elif question.type == 'schedule':
            # A computation arrives as one input per scoring line. Kept keyed by
            # line index rather than flattened to text, because the marker scores
            # each line on its own and needs to know which is which.
            lines = {}
            for index in range(len(((question.config or {}).get('lines') or []))):
                value = request.POST.get(f'{field}_line_{index}', '')
                if value != '':
                    lines[str(index)] = value
            answer.response = {'lines': lines}
            answer.save()
        elif question.type in ('file_upload', 'project', 'audio_resp', 'video_resp'):
            if field in request.FILES:
                answer.file = request.FILES[field]
            answer.save()
        else:  # fill / short / long / essay / coding / …
            answer.response = {'text': request.POST.get(field, '')}
            answer.save()

    if attempt.started_at:
        attempt.time_spent_seconds = int((timezone.now() - attempt.started_at).total_seconds())
    grade_attempt(attempt)  # score / passed / status, and fires the grade signal
    messages.success(request, 'Your responses have been submitted.')
    return redirect('assessments:result', public_id=attempt.public_id)


# ---------------------------------------------------------------------------
# result / review
# ---------------------------------------------------------------------------
def _solution_for(question):
    """The model answer for one question, shaped for the result page.

    Reads the structure the content-pack importer wrote into ``config``: a
    computation carries ``lines`` (label · authority · expected figure · marks),
    a discussion carries ``rubric`` (the point that earns the mark · authority ·
    marks). Falls back to the free-text ``guidance`` an educator typed by hand.
    """
    config = question.config or {}
    kind = config.get('kind')
    if kind == 'schedule' and config.get('lines'):
        return {'kind': 'schedule', 'lines': config['lines'], 'text': ''}
    if kind == 'rubric' and config.get('rubric'):
        return {'kind': 'rubric', 'rubric': config['rubric'], 'text': ''}
    if question.guidance:
        return {'kind': 'text', 'text': question.guidance}
    return None


@login_required
def result(request, public_id):
    attempt = get_object_or_404(
        models.AssessmentAttempt.objects.select_related('assessment', 'student'), public_id=public_id)
    # The learner who sat it, the staff/educators who set it, and the parent of
    # the learner — results are exactly what a guardian is here to see.
    allowed = (attempt.student_id == request.user.id
               or _is_staff_like(request)
               or children_of(request.user).filter(pk=attempt.student_id).exists())
    if not allowed:
        return HttpResponseForbidden()

    assessment = attempt.assessment
    # The memo opens only once this candidate has committed an answer — see
    # Assessment.solution_released_for. Resolved here, once, rather than being a
    # condition the template could get wrong.
    show_solution = assessment.solution_released_for(request.user)

    questions = _assessment_questions(assessment)
    answers = {a.question_id: a for a in attempt.answers.prefetch_related('selected_choices')}
    rows = []
    for question in questions:
        answer = answers.get(question.id)
        rows.append({
            'question': question, 'answer': answer,
            'choices': list(question.choices.all()),
            'selected': set(answer.selected_choices.values_list('id', flat=True)) if answer else set(),
            # Only ever populated when the memo is released, so a solution
            # cannot reach the page and be hidden with CSS.
            'solution': _solution_for(question) if show_solution else None,
        })

    total = float(assessment.total_marks or 0)
    pct = round(float(attempt.score) / total * 100, 1) if total else 0
    return render(request, 'assessments/result.html', {
        'page_title': f'Result — {assessment.title}',
        'attempt': attempt, 'rows': rows, 'pct': pct,
        'show_solution': show_solution,
        'solution_notes': (assessment.solution_notes or {}) if show_solution else {},
        # The full event log is the educator's; the student sees their tally only.
        'integrity': proctoring.summary(attempt) if _is_staff_like(request) else None,
    })
