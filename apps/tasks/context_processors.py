"""Context processor exposing task summary stats to every template.

Scoped by role: admin/staff see all tasks; educators see the tasks in their
teaching audience (:func:`apps.tasks.scoping.manageable_tasks` — the same rule
the list view uses, so the sidebar badge always matches the page it links to);
students/parents see only the tasks assigned to them. ``my_pending`` /
``my_completed`` are always the current user's own assignments."""

from django.utils import timezone

from core.roles import role_flags

from . import models
from .scoping import manageable_tasks
from core.request_cache import cached_per_request


def _build_task_stats(request):
    try:
        flags = role_flags(request)
        user = getattr(request, 'user', None)
        tasks = models.Task.objects.all()
        if user is not None and user.is_authenticated:
            if flags['is_admin_staff']:
                pass  # see everything
            elif flags['is_educator']:
                tasks = manageable_tasks(user, tasks)
            else:
                # students/parents: only tasks assigned to them.
                tasks = tasks.filter(assignments__user=user).distinct()
        stats = {
            'tasks_total': tasks.count(),
            'open_tasks': tasks.filter(status='open').count(),
            'overdue_tasks': tasks.filter(
                status='open', due_date__lt=timezone.now()).count(),
            'my_pending': 0,
            'my_completed': 0,
        }
        if user is not None and user.is_authenticated:
            mine = models.TaskAssignment.objects.filter(user=user)
            stats['my_pending'] = mine.exclude(
                status=models.TaskAssignment.STATUS_COMPLETED).count()
            stats['my_completed'] = mine.filter(
                status=models.TaskAssignment.STATUS_COMPLETED).count()
        return {'task_stats': stats}
    except Exception:
        return {'task_stats': {}}


def task_stats(request):
    """Cached for the life of the request — these are nav badges, and this
    processor runs once per template rendered in a response, not once per
    response."""
    return cached_per_request(request, 'task_stats', lambda: _build_task_stats(request))
