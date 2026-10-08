"""Signal handlers for the tasks app.

* When a :class:`Task` is saved, fan its target out into one
  :class:`TaskAssignment` per resolved user (``get_or_create`` so existing
  progress is never wiped).
* When a **lesson or assessment** is saved, keep the task that delivers it in
  step (:mod:`apps.tasks.activities`) — so a deadline set on the content shows
  up in the task list and the calendar by itself.
* Record task create/update/delete in the shared
  :class:`apps.accounts.models.ActivityLog` audit trail.

Connected in :meth:`apps.tasks.apps.TasksConfig.ready`.
"""

import logging

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Task, TaskAssignment

logger = logging.getLogger('apps')

# Guard against the obvious loop: syncing an activity saves a Task, whose own
# post_save must not turn round and re-sync the activity.
_syncing = set()


def _log(action, description):
    try:
        from apps.accounts.models import ActivityLog
        ActivityLog.objects.create(action=action, description=description)
    except Exception:  # pragma: no cover
        logger.exception('tasks: failed to write ActivityLog')


@receiver(post_save, sender=Task)
def fan_out_assignments(sender, instance, created, **kwargs):
    """Create a TaskAssignment for every user the task targets.

    Uses ``get_or_create`` so re-saving a task (e.g. editing the due date)
    never deletes assignments a user has already started.
    """
    for user in instance.resolve_users():
        TaskAssignment.objects.get_or_create(task=instance, user=user)
    _log('create' if created else 'update',
         f"Task {'created' if created else 'updated'}: {instance.title}")


@receiver(post_delete, sender=Task)
def log_task_delete(sender, instance, **kwargs):
    _log('delete', f'Task deleted: {instance.title}')


def sync_activity_task(sender, instance, **kwargs):
    """A lesson/assessment was saved — refresh the task that delivers it.

    Deliberately best-effort: a problem building the task must never stop an
    educator saving their lesson.
    """
    key = (sender.__name__, instance.pk)
    if key in _syncing:
        return
    _syncing.add(key)
    try:
        from . import activities
        activities.sync_task_for(instance)
    except Exception:  # pragma: no cover - tracking never blocks authoring
        logger.exception('tasks: could not sync task for %s %s', sender.__name__, instance.pk)
    finally:
        _syncing.discard(key)


def record_activity_progress(sender, instance, **kwargs):
    """A learner sat a quiz / studied a lesson — move the delivering task along."""
    try:
        from apps.assessments.models import AssessmentAttempt
        from . import activities
        if isinstance(instance, AssessmentAttempt):
            activities.record_attempt(instance)
        else:
            activities.record_study(instance)
    except Exception:  # pragma: no cover - never break submitting work
        logger.exception('tasks: could not record progress from %s %s',
                         sender.__name__, instance.pk)


def connect_activity_signals():
    """Wire the lesson/assessment hooks (called from ``TasksConfig.ready``).

    Two directions:

    * **content → task** — publishing a lesson/assessment creates or refreshes
      the task that delivers it;
    * **doing → task** — an attempt or study session moves that task's
      assignment along, so the learner's task list reflects real work rather
      than needing a second manual update.
    """
    from apps.assessments.models import Assessment, AssessmentAttempt
    from apps.learning.models import Lesson, StudySession

    for model in (Lesson, Assessment):
        post_save.connect(sync_activity_task, sender=model,
                          dispatch_uid=f'tasks.sync_activity_task.{model.__name__}')
    for model in (AssessmentAttempt, StudySession):
        post_save.connect(record_activity_progress, sender=model,
                          dispatch_uid=f'tasks.record_activity_progress.{model.__name__}')
