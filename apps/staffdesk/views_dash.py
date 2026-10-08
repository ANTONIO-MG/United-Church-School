"""The staff desk's dashboards: operations, Student 360 and the educator desk.

Views stay thin — every number comes from :mod:`apps.staffdesk.dashboards`.
"""

from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from core.errors import note
from core.roles import role_of_user
from core.scoping import taught_module_qs

from . import dashboards as dash
from .access import staff_required, teaching_required
from .dashboards import display_name


# ---------------------------------------------------------------------------
# Operations
# ---------------------------------------------------------------------------
@staff_required
def home(request):
    """``/staff/`` — what needs the admin team's attention today."""
    return render(request, 'staffdesk/dash/home.html', {
        'page_title': 'Operations',
        'ops': dash.operations(request.user),
        'today': timezone.localdate(),
    })


# ---------------------------------------------------------------------------
# Student 360
# ---------------------------------------------------------------------------
ROLE_FILTERS = [('student', 'Students'), ('parent', 'Parents'), ('educator', 'Educators'), ('', 'Everyone')]


@staff_required
def students(request):
    """Search everyone (students by default) and open their 360 page."""
    query = (request.GET.get('q') or '').strip()
    role = request.GET.get('role', 'student')
    if role not in {value for value, _label in ROLE_FILTERS}:
        role = 'student'
    page = Paginator(dash.search_students(query, role), 40).get_page(request.GET.get('page'))
    return render(request, 'staffdesk/dash/students.html', {
        'page_title': 'Student 360', 'page': page, 'query': query, 'role': role,
        'role_filters': ROLE_FILTERS,
    })


@staff_required
def student_detail(request, person_id):
    """``/staff/students/<person_id>/`` — one person, everything about them."""
    from apps.accounts.models import Person
    person = get_object_or_404(Person.objects.select_related('user', 'contact'), pk=person_id)
    return render(request, 'staffdesk/dash/student.html', {
        'page_title': display_name(person.user),
        'person': person, 'student': person.user,
        'd': dash.student_360(person),
        'now': timezone.now(),
    })


# ---------------------------------------------------------------------------
# Educator desk
# ---------------------------------------------------------------------------
def _educator_for(request):
    """The educator whose desk is shown: yourself, or ``?educator=`` for admin/staff."""
    from apps.accounts.models import Person
    own = getattr(request.user, 'profile', None)
    if role_of_user(request.user) not in ('admin', 'staff'):
        return own
    requested = (request.GET.get('educator') or '').strip()
    if requested.isdigit():
        found = Person.objects.select_related('user').filter(user_id=int(requested)).first()
        if found is not None:
            return found
    return own


def _educator_choices():
    from django.db.models import Q

    from apps.accounts.models import Person
    return list(Person.objects.filter(Q(user_type='educator') | Q(taught_modules__isnull=False),
                                      user__is_active=True)
                .select_related('user').distinct().order_by('first_name', 'last_name')[:300])


@teaching_required
def teaching(request):
    """``/staff/teaching/`` — an educator's modules, queue, stragglers and sessions."""
    person = _educator_for(request)
    is_admin_staff = role_of_user(request.user) in ('admin', 'staff')
    viewing_other = bool(person and person.user_id != request.user.pk)
    return render(request, 'staffdesk/dash/teaching.html', {
        'page_title': 'Teaching' if not viewing_other else f'Teaching · {display_name(person.user)}',
        'educator': person,
        'educator_name': display_name(person.user) if person else '',
        'viewing_other': viewing_other,
        'is_admin_staff': is_admin_staff,
        'educators': _educator_choices() if is_admin_staff else [],
        't': dash.teaching(person) if person else {},
        'inactive_days': dash.INACTIVE_AFTER.days,
        'low_score': dash.LOW_SCORE_PCT,
    })


@require_POST
@teaching_required
def nudge(request, module_id):
    """Notify a module's inactive students — once per module per 24 hours.

    Educators may only nudge modules they teach; admin and staff any module.
    """
    from apps.learning.models import ProgrammeModule

    module = get_object_or_404(ProgrammeModule, pk=module_id)
    if not taught_module_qs(request.user).filter(pk=module.pk).exists():
        return HttpResponseForbidden('You do not teach this subject.')

    back = reverse('staffdesk:teaching')
    educator = (request.POST.get('educator') or '').strip()
    if educator.isdigit() and role_of_user(request.user) in ('admin', 'staff'):
        back += f'?educator={educator}'

    allowed, next_at = dash.can_nudge(module)
    if not allowed:
        note('DESK-4001', request, module=module.pk)
        messages.warning(request, f'{module.display_name} was already nudged in the last 24 hours. '
                                  f'You can nudge again after {timezone.localtime(next_at):%a %H:%M}.')
        return redirect(back)

    sent = dash.send_nudge(module, request.user)
    if sent is None:
        note('DESK-4001', request, module=module.pk)
        messages.warning(request, f'{module.display_name} was already nudged in the last 24 hours.')
    elif sent.recipients:
        messages.success(request, f'Nudged {sent.recipients} inactive student{"s" if sent.recipients != 1 else ""} '
                                  f'on {module.display_name}.')
    else:
        messages.info(request, f'Nobody on {module.display_name} needed a nudge — everyone has been active.')
    return redirect(back)
