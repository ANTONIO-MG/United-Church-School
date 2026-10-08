"""Views for the tasks app.

* ``my_tasks`` — the assignments belonging to the current user.
* ``all_tasks`` — tasks the user created / can manage (staff & educators).
* ``task_detail`` — task meta + every assignment; assignees update progress,
  staff grade.
* CRUD for staff/educators; the assignment fan-out happens in the signal.
"""

from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from core.branding import t
from core.scoping import children_of, viewing_child

from . import forms, models
from .scoping import can_manage_task, manageable_tasks


def _can_manage(user):
    profile = getattr(user, 'profile', None)
    return bool(user.is_active and (user.is_staff or getattr(profile, 'user_type', '') in ('staff', 'admin', 'educator')))


manage_required = user_passes_test(lambda u: u.is_active and (u.is_staff or getattr(getattr(u, 'profile', None), 'user_type', '') in ('staff', 'admin', 'educator')))


def _save_form(request, form_class, instance, template, *, list_url, page_title,
               extra_context=None):
    # ``user`` lets the form narrow every target dropdown to this person's
    # audience — and re-validate the POST against the same querysets.
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=instance, user=request.user)
        if form.is_valid():
            obj = form.save(commit=False)
            if not obj.pk and hasattr(obj, 'created_by') and not obj.created_by_id:
                obj.created_by = request.user
            obj.save()
            form.save_m2m()
            messages.success(request, t('messages.saved', '{name} saved successfully.', name=page_title))
            return redirect(obj.get_absolute_url() if hasattr(obj, 'get_absolute_url') else list_url)
        messages.error(request, t('messages.form_errors', 'Please correct the errors highlighted below.'))
    else:
        form = form_class(instance=instance, user=request.user)
    context = {'form': form, 'object': instance, 'page_title': page_title}
    if extra_context:
        context.update(extra_context)
    return render(request, template, context)


def _to_decimal(value, default=None):
    if value in (None, ''):
        return default
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return default


# ===========================================================================
# Lists
# ===========================================================================
@login_required
def my_tasks(request):
    """The signed-in user's own tasks — or, for a parent, their child's.

    A parent is assigned no work themselves, so showing them their own (empty)
    list would be useless. The page becomes a read-only view of the child's:
    what has been set, what is done, what is overdue.
    """
    child = viewing_child(request)
    owner = child or request.user
    assignments = (models.TaskAssignment.objects
                   .filter(user=owner)
                   .select_related('task', 'task__lesson', 'task__assessment'))
    name = (child.get_full_name() or child.get_username()) if child else ''
    return render(request, 'tasks/my-tasks.html', {
        'page_title': f'{name}’s Tasks' if child else 'My Tasks',
        'assignments': assignments,
        'child': child,
        'children': children_of(request.user) if child else None,
        'read_only': child is not None,
    })


@login_required
@manage_required
def all_tasks(request):
    tasks = manageable_tasks(
        request.user,
        models.Task.objects.select_related('created_by').prefetch_related('assignments'),
    )
    return render(request, 'tasks/all-tasks.html', {
        'page_title': 'All Tasks', 'tasks': tasks,
    })


# ===========================================================================
# Detail
# ===========================================================================
@login_required
def task_detail(request, pk):
    task = get_object_or_404(
        models.Task.objects.prefetch_related('assignments__user'), pk=pk)
    my_assignment = task.assignments.filter(user=request.user).first()
    # Managing needs the task to be in this user's audience; being assigned it is
    # enough to view it. A parent may look at whatever their child was assigned,
    # but only ever read-only. None of the three → 404 (never confirm a task they
    # can't reach).
    can_manage = _can_manage(request.user) and can_manage_task(request.user, task)
    child_assignment = None
    if not can_manage and my_assignment is None:
        child_assignment = task.assignments.filter(
            user__in=children_of(request.user)).select_related('user').first()
        if child_assignment is None:
            from django.http import Http404
            raise Http404

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'progress' and my_assignment:
            form = forms.AssignmentProgressForm(request.POST, instance=my_assignment)
            if form.is_valid():
                form.save()
                messages.success(request, t('messages.saved', '{name} saved successfully.', name='Progress'))
            else:
                messages.error(request, t('messages.form_errors', 'Please correct the errors highlighted below.'))
            return redirect('orgtasks:task-detail', pk=task.pk)
        if action == 'grade' and can_manage:
            assignment = get_object_or_404(
                models.TaskAssignment, pk=request.POST.get('assignment_id'), task=task)
            assignment.score = _to_decimal(request.POST.get('score'), assignment.score)
            assignment.status = request.POST.get('status', assignment.status)
            assignment.feedback = request.POST.get('feedback', assignment.feedback)
            assignment.save()
            messages.success(request, t('messages.saved', '{name} saved successfully.', name='Grade'))
            return redirect('orgtasks:task-detail', pk=task.pk)

    # A parent sees only their own child's row, not the rest of the class.
    assignments = task.assignments.select_related('user')
    if child_assignment is not None:
        assignments = assignments.filter(pk=child_assignment.pk)

    return render(request, 'tasks/task-detail.html', {
        'page_title': task.title, 'task': task,
        'assignments': assignments,
        'my_assignment': my_assignment, 'can_manage': can_manage,
        'child_assignment': child_assignment,
        'progress_form': forms.AssignmentProgressForm(instance=my_assignment) if my_assignment else None,
        'status_choices': models.TaskAssignment.STATUS_CHOICES,
    })


# ===========================================================================
# CRUD (staff / educators)
# ===========================================================================
@login_required
@manage_required
def add_task(request):
    return _save_form(request, forms.TaskForm, None, 'tasks/task-form.html',
                      list_url='orgtasks:all-tasks', page_title='Add Task')


@login_required
@manage_required
def edit_task(request, pk):
    # Scoped lookup: an educator editing someone else's task gets a 404.
    task = get_object_or_404(manageable_tasks(request.user), pk=pk)
    return _save_form(request, forms.TaskForm, task, 'tasks/task-form.html',
                      list_url='orgtasks:all-tasks', page_title='Edit Task')


@login_required
@manage_required
@require_POST
def delete_task(request, pk):
    task = get_object_or_404(manageable_tasks(request.user), pk=pk)
    task.delete()
    messages.success(request, t('messages.deleted', '{name} deleted.', name='Task'))
    return redirect('orgtasks:all-tasks')


@login_required
@require_POST
def assignment_update(request, pk):
    assignment = get_object_or_404(models.TaskAssignment, pk=pk, user=request.user)
    form = forms.AssignmentProgressForm(request.POST, instance=assignment)
    if form.is_valid():
        form.save()
        messages.success(request, t('messages.saved', '{name} saved successfully.', name='Progress'))
    else:
        messages.error(request, t('messages.form_errors', 'Please correct the errors highlighted below.'))
    return redirect('orgtasks:task-detail', pk=assignment.task_id)
