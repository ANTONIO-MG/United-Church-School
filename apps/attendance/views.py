"""Daily register pages.

* ``/attendance/``                    — today's registers: the teacher's classes
                                        (admin/staff: every grade).
* ``/attendance/register/<id>/``      — take / edit one register.
* ``/attendance/reports/``            — staff: monthly grid per class, flags, CSV.
* ``/attendance/learner/<person>/``   — staff/teacher: one learner's record.
* ``/attendance/my/``                 — a learner's own record; a parent's child's.
"""

import csv
from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from core.roles import role_flags

from . import services
from .calendar import is_school_day, local_today
from .models import AttendanceMark, DailyRegister, cohort_label


def _require_teach(request):
    flags = role_flags(request)
    if not (flags['is_admin_staff'] or flags['is_educator']):
        raise PermissionDenied
    return flags


def _require_staff(request):
    flags = role_flags(request)
    if not flags['is_admin_staff']:
        raise PermissionDenied
    return flags


def _parse_date(value, default):
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        return default


@login_required
def index(request):
    flags = _require_teach(request)
    today = local_today()
    day = _parse_date(request.GET.get('date'), today)
    if day > today:
        day = today
    cohorts = list(services.cohorts_for(request.user))
    school_day = is_school_day(day)
    # The job opens registers at 06:30; a teacher who gets here first (or a
    # school where cron is not running yet) should not find an empty page.
    if day == today and school_day and cohorts:
        services.open_registers(day, notify_teachers=False, cohorts=cohorts)
    registers = (DailyRegister.objects.filter(date=day, cohort__in=cohorts)
                 .select_related('cohort__programme', 'cohort__class_teacher', 'submitted_by'))
    rows = [{'register': r, 'counts': r.counts(), 'can_edit': services.can_edit(request.user, r, today)}
            for r in registers]
    return render(request, 'attendance/index.html', {
        'page_title': 'Daily register',
        'day': day, 'today': today, 'is_today': day == today, 'school_day': school_day,
        'rows': rows, 'has_classes': bool(cohorts),
        'prev_day': day - timedelta(days=1), 'next_day': day + timedelta(days=1) if day < today else None,
        'flags': flags,
    })


@login_required
def register_detail(request, pk):
    _require_teach(request)
    register = get_object_or_404(DailyRegister.objects.select_related('cohort__programme'), pk=pk)
    if not services.can_take(request.user, register):
        raise PermissionDenied
    editable = services.can_edit(request.user, register)
    if request.method == 'POST':
        if not editable:
            messages.error(request, 'This register can no longer be changed — ask the office.')
            return redirect(register.get_absolute_url())
        changes = {}
        for mark in register.marks.all():
            status = request.POST.get(f'status_{mark.pk}')
            if status:
                changes[mark.pk] = (status, request.POST.get(f'reason_{mark.pk}', ''))
        by = getattr(request.user, 'profile', None)
        services.save_marks(register, changes, by=by)
        if request.POST.get('action') == 'submit' or not register.is_open:
            services.submit_register(register, by=by)
            counts = register.counts()
            messages.success(request, f'Register for {register.cohort_label} saved: '
                                      f'{counts["present"]} present, {counts["absent"]} absent, '
                                      f'{counts["late"]} late, {counts["excused"]} excused.')
            return redirect('attendance:index')
        messages.success(request, 'Saved. The register is still open — submit it when you are done.')
        return redirect(register.get_absolute_url())
    marks = register.marks.select_related('learner__user', 'marked_by')
    return render(request, 'attendance/register.html', {
        'page_title': f'Register · {register.cohort_label}',
        'register': register, 'marks': marks, 'editable': editable,
        'counts': register.counts(), 'statuses': AttendanceMark.STATUS_CHOICES,
    })


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------
def _month_bounds(value):
    today = local_today()
    try:
        year, month = (int(x) for x in (value or '').split('-'))
        first = date(year, month, 1)
    except (TypeError, ValueError):
        first = today.replace(day=1)
    last = (first.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
    return first, last


@login_required
def reports(request):
    _require_staff(request)
    cohorts = list(services.active_cohorts())
    cohort = None
    cid = request.GET.get('cohort')
    if cid and cid.isdigit():
        cohort = next((c for c in cohorts if c.pk == int(cid)), None)
    if cohort is None and cohorts:
        cohort = cohorts[0]
    first, last = _month_bounds(request.GET.get('month'))
    days, rows = services.month_grid(cohort, first, last) if cohort else ([], [])
    prev_month = (first - timedelta(days=1)).replace(day=1)
    next_month = last + timedelta(days=1)
    return render(request, 'attendance/reports.html', {
        'page_title': 'Attendance',
        'cohorts': [(c, cohort_label(c)) for c in cohorts], 'cohort': cohort,
        'cohort_name': cohort_label(cohort) if cohort else '',
        'first': first, 'days': days, 'rows': rows,
        'prev_month': prev_month, 'next_month': next_month if next_month <= local_today() else None,
        'flagged': services.flagged_learners(),
        'limit': services.CONSECUTIVE_ABSENCE_LIMIT,
        'open_today': DailyRegister.objects.filter(date=local_today(), status=DailyRegister.STATUS_OPEN)
                      .select_related('cohort__programme'),
    })


@login_required
def reports_csv(request):
    _require_staff(request)
    from apps.learning.models import Cohort
    cohort = get_object_or_404(Cohort, pk=request.GET.get('cohort') or 0)
    first, last = _month_bounds(request.GET.get('month'))
    days, rows = services.month_grid(cohort, first, last)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = (
        f'attachment; filename="attendance-{cohort.programme.code}-{cohort.code}-{first:%Y-%m}.csv"')
    writer = csv.writer(response)
    writer.writerow(['Learner'] + [d.isoformat() for d in days]
                    + ['Present', 'Absent', 'Late', 'Excused', 'Attendance %'])
    for row in rows:
        s = row['summary']
        writer.writerow([str(row['learner'])] + row['cells']
                        + [s['present'], s['absent'], s['late'], s['excused'],
                           '' if s['pct'] is None else s['pct']])
    return response


def _record_context(person, *, title):
    today = local_today()
    year_start = date(today.year, 1, 1)
    month_start = today.replace(day=1)
    marks = (AttendanceMark.objects.filter(learner=person)
             .exclude(status=AttendanceMark.PRESENT)
             .select_related('register__cohort__programme').order_by('-register__date')[:60])
    return {
        'page_title': title, 'learner': person,
        'year': services.learner_summary(person, year_start, today),
        'month': services.learner_summary(person, month_start, today),
        'exceptions': marks, 'limit': services.CONSECUTIVE_ABSENCE_LIMIT,
        'today': today,
    }


@login_required
def learner_record(request, person_id):
    from apps.accounts.models import Person
    _require_teach(request)
    person = get_object_or_404(Person, pk=person_id)
    if not role_flags(request)['is_admin_staff']:
        mine = services.cohorts_for(request.user)
        if not person.programme_enrolments.filter(cohort__in=mine).exists():
            raise PermissionDenied
    return render(request, 'attendance/record.html',
                  _record_context(person, title=f'Attendance · {person}'))


@login_required
def my_attendance(request):
    flags = role_flags(request)
    if flags['is_parent']:
        from core.scoping import viewing_child
        child = viewing_child(request)
        if child is None:
            return render(request, 'attendance/record.html',
                          {'page_title': 'Attendance', 'learner': None, 'no_child': True})
        person = child.profile
        return render(request, 'attendance/record.html',
                      _record_context(person, title=f"{person}'s attendance"))
    if flags['is_student']:
        person = request.user.profile
        return render(request, 'attendance/record.html', _record_context(person, title='My attendance'))
    return redirect('attendance:index')
