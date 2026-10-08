"""Keep a :class:`~apps.tasks.models.Task` in step with the activity it delivers.

A lesson or an assessment with a deadline *is* a piece of work someone has to
do — so it should appear in the task list and on the calendar without an educator
having to create a second object by hand. This module is the bridge: when a
lesson or assessment is published with a date, :func:`sync_task_for` creates (or
updates) the one task that points at it.

Design notes:

* **One task per activity.** Found by the activity FK, never by title, so
  renaming the lesson doesn't orphan its task or spawn a duplicate.
* **Idempotent.** Re-saving an activity updates the existing task in place;
  ``fan_out_assignments`` then tops up assignments with ``get_or_create``, so
  progress a learner has already made is never reset.
* **Unpublishing closes, it does not delete.** Deleting would take submissions
  and grades with it. An activity that goes back to draft simply closes its task.
* **Best-effort.** Every entry point is wrapped by the caller in the signal
  module — a failure here must never block saving a lesson.
"""

import logging

from . import models

logger = logging.getLogger('apps')


def _target_from_lesson(lesson):
    """Map a lesson's own audience onto the task's ``assign_to`` + target FK.

    Mirrors the three audience buttons in the lesson editor (individual /
    programme / module) so the task reaches exactly the people the lesson does.
    Individual targeting can't be expressed by a single ``assignee`` FK when
    several students are named, so it falls back to the lesson's module and
    lets the lesson's own visibility rules do the filtering at open time.
    """
    from apps.learning.models import Lesson

    if lesson.visibility == Lesson.VIS_PROGRAMME:
        programme = lesson.target_programmes.first() or getattr(lesson.module, 'programme', None)
        if programme:
            return {'assign_to': models.Task.ASSIGN_PROGRAMME, 'programme': programme,
                    'module': None, 'assignee': None}
    if lesson.visibility == Lesson.VIS_INDIVIDUAL:
        targets = list(lesson.target_users.all()[:2])
        if len(targets) == 1:
            person = getattr(targets[0], 'profile', None)
            if person is not None:
                return {'assign_to': models.Task.ASSIGN_USER, 'assignee': person,
                        'module': None, 'programme': None}
    module = lesson.target_modules.first() or lesson.module
    return {'assign_to': models.Task.ASSIGN_SUBJECT, 'module': module,
            'programme': None, 'assignee': None}


def _lesson_plan(lesson):
    """``(should_exist, field_values)`` for a lesson's task."""
    from apps.learning.models import Lesson

    live = lesson.status in (Lesson.STATUS_PUBLISHED, Lesson.STATUS_SCHEDULED)
    values = {
        'title': lesson.title,
        'description': lesson.subtitle or '',
        'due_date': lesson.expire_at or lesson.publish_at,
        'status': 'open' if live else 'closed',
        'created_by': lesson.created_by,
        **_target_from_lesson(lesson),
    }
    return live, values


def _assessment_plan(assessment):
    """``(should_exist, field_values)`` for an assessment's task."""
    from apps.assessments.models import Assessment

    live = assessment.status in (Assessment.STATUS_OPEN, Assessment.STATUS_SCHEDULED)
    values = {
        'title': assessment.title,
        'description': assessment.description or '',
        'due_date': getattr(assessment, 'available_to', None),
        'max_score': assessment.total_marks,
        'status': 'open' if live else 'closed',
        'created_by': getattr(assessment, 'created_by', None),
        'assign_to': models.Task.ASSIGN_SUBJECT,
        'module': assessment.module,
        'programme': None, 'assignee': None,
    }
    return live, values


def sync_task_for(activity):
    """Create/update the task delivering ``activity``; return it (or ``None``).

    ``None`` means "nothing to track" — an unpublished activity that never had a
    task. An activity that *had* one keeps it, closed.
    """
    from apps.assessments.models import Assessment
    from apps.learning.models import Lesson

    if isinstance(activity, Lesson):
        link, (live, values) = {'lesson': activity}, _lesson_plan(activity)
    elif isinstance(activity, Assessment):
        link, (live, values) = {'assessment': activity}, _assessment_plan(activity)
    else:
        return None

    task = models.Task.objects.filter(**link).first()
    if task is None:
        if not live:
            return None          # never published → nothing to track
        task = models.Task(**link)

    for field, value in values.items():
        # Don't blank a deadline someone set by hand on the task itself.
        if field == 'due_date' and value is None and task.due_date:
            continue
        if field == 'created_by' and value is None and task.created_by_id:
            continue
        setattr(task, field, value)
    task.save()                  # post_save fans the assignments out
    return task


# ---------------------------------------------------------------------------
# Progress flowing back: doing the activity progresses the task
# ---------------------------------------------------------------------------
def _apply(assignment, *, progress, complete, score=None):
    """Move a :class:`TaskAssignment` forward — never backward.

    Progress and completion only ever ratchet up: re-opening a lesson after
    finishing it, or a weaker later attempt at a quiz, must not undo work already
    banked.
    """
    changed = False
    progress = max(0, min(100, int(round(progress))))
    if progress > assignment.progress:
        assignment.progress, changed = progress, True
    if score is not None and (assignment.score is None or score > float(assignment.score)):
        assignment.score, changed = round(score, 2), True
    if complete and assignment.status != models.TaskAssignment.STATUS_COMPLETED:
        assignment.status, changed = models.TaskAssignment.STATUS_COMPLETED, True
    elif not complete and assignment.status == models.TaskAssignment.STATUS_NOT_STARTED:
        assignment.status, changed = models.TaskAssignment.STATUS_IN_PROGRESS, True
    if changed:
        assignment.save()        # stamps submitted_at / completed_at
    return changed


def record_attempt(attempt):
    """An assessment attempt was saved — reflect it on the delivering task."""
    from apps.assessments.models import AssessmentAttempt

    complete = attempt.status in (AssessmentAttempt.STATUS_SUBMITTED,
                                  AssessmentAttempt.STATUS_MARKED)
    total = float(attempt.assessment.total_marks or 0)
    pct = (float(attempt.score or 0) / total * 100.0) if total else 0.0

    updated = 0
    for task in models.Task.objects.filter(assessment=attempt.assessment):
        assignment = models.TaskAssignment.objects.filter(
            task=task, user=attempt.student).first()
        if assignment is None:
            continue
        # The task's own max_score may differ from the assessment's total, so
        # rescale rather than copying the raw mark across.
        score = float(task.max_score) * pct / 100.0 if task.max_score else None
        updated += bool(_apply(assignment, progress=100 if complete else 50,
                               complete=complete, score=score))
    return updated


def record_study(session):
    """A study session moved — reflect it on the task delivering that lesson."""
    from apps.learning.models import StudySession

    complete = session.status in (StudySession.STATUS_COMPLETED, StudySession.STATUS_SUBMITTED)
    updated = 0
    for task in models.Task.objects.filter(lesson=session.lesson):
        assignment = models.TaskAssignment.objects.filter(
            task=task, user=session.student).first()
        if assignment is None:
            continue
        updated += bool(_apply(assignment,
                               progress=100 if complete else session.completion_pct,
                               complete=complete))
    return updated
