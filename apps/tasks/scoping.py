"""Which tasks a user may manage — shared by the list view, the detail view and
the sidebar counters so all three agree.

Admin/staff manage everything. An educator manages a task when it is *theirs* in
any of the senses that matter: they created it, or it is aimed at a module,
programme or individual student inside their teaching audience. That
last clause is what stops a task quietly disappearing from its own author's list
after an admin re-targets it, and equally stops an educator browsing work set by
somebody else for a class they have nothing to do with.
"""

from django.db.models import Q

from core.scoping import (
    is_scoped, taught_people, taught_programmes, taught_module_qs,
)

from . import models


def manageable_tasks(user, queryset=None):
    """The tasks ``user`` may see on the management side."""
    qs = models.Task.objects.all() if queryset is None else queryset
    if not is_scoped(user):
        return qs
    if not getattr(user, 'is_authenticated', False):
        return qs.none()
    return qs.filter(
        Q(created_by=user)
        | Q(module__in=taught_module_qs(user))
        | Q(programme__in=taught_programmes(user))
        | Q(assignee__in=taught_people(user))
    ).distinct()


def can_manage_task(user, task):
    """Whether ``user`` may edit/grade this specific task."""
    return manageable_tasks(user).filter(pk=task.pk).exists()
