"""The daily register flow.

1. :func:`open_registers` — on a school day, one register per active class with
   learners, everyone pre-marked **present**, and the class teacher is given a
   task + notification: "Take the register — mark who is absent".
2. The teacher marks the exceptions and submits (:func:`save_marks`,
   :func:`submit_register`). Parents of absent learners are told, once a day.
3. :func:`auto_submit_open` — registers nobody submitted are closed at the end
   of the day with everyone not marked otherwise kept present.

:func:`run_daily` is the scheduler entry point that does 1 and 3.
"""

import logging
from datetime import datetime, timedelta

from django.db import transaction
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone

from .calendar import CLOSE_AT, OPEN_AT, SCHOOL_TZ, is_school_day, local_now, local_today, week_start
from .models import AttendanceMark, DailyRegister, cohort_label

logger = logging.getLogger(__name__)

#: The Department rule quoted in the UCS parent code of conduct: a learner
#: absent for this many consecutive school days is removed from the enrolment
#: register.
CONSECUTIVE_ABSENCE_LIMIT = 10


# ---------------------------------------------------------------------------
# Who is in a class, and who takes its register
# ---------------------------------------------------------------------------
def cohort_learners(cohort):
    from apps.accounts.models import Person
    return (Person.objects
            .filter(programme_enrolments__cohort=cohort, programme_enrolments__is_active=True,
                    user_type='student', user__is_active=True)
            .select_related('user').distinct()
            .order_by('first_name', 'last_name'))


def register_takers(cohort):
    """Who takes this class's register: the class teacher; failing that the
    grade's subject educators; failing that the school's admin/staff."""
    from apps.accounts.models import Person
    if cohort.class_teacher_id:
        return [cohort.class_teacher]
    educators = list(Person.objects.filter(
        taught_modules__programme=cohort.programme, taught_modules__is_active=True,
        user__is_active=True).distinct())
    if educators:
        return educators
    return list(Person.objects.filter(
        Q(user_type__in=('admin', 'staff')) | Q(user__is_staff=True), user__is_active=True).distinct())


def active_cohorts():
    from apps.learning.models import Cohort
    return (Cohort.objects.filter(is_active=True, programme__is_active=True,
                                  enrolments__is_active=True)
            .select_related('programme', 'class_teacher').distinct()
            .order_by('programme__grade', 'code'))


def _is_admin_staff(user):
    from core.roles import role_of_user
    return role_of_user(user) in ('admin', 'staff')


def cohorts_for(user):
    """The classes whose register this user may take (all, for admin/staff)."""
    cohorts = active_cohorts()
    if _is_admin_staff(user):
        return cohorts
    person = getattr(user, 'profile', None)
    if person is None:
        return cohorts.none()
    return [c for c in cohorts if any(p.pk == person.pk for p in register_takers(c))]


def can_take(user, register):
    """May this user see and mark this register?"""
    if not getattr(user, 'is_authenticated', False):
        return False
    if _is_admin_staff(user):
        return True
    person = getattr(user, 'profile', None)
    if person is None or person.user_type != 'educator':
        return False
    return any(p.pk == person.pk for p in register_takers(register.cohort))


def can_edit(user, register, today=None):
    """Staff may edit any register; a teacher their own, within the same week."""
    if not can_take(user, register):
        return False
    if _is_admin_staff(user):
        return True
    today = today or local_today()
    return week_start(register.date) == week_start(today) and register.date <= today


# ---------------------------------------------------------------------------
# Opening
# ---------------------------------------------------------------------------
def ensure_register(cohort, day):
    """The register for ``cohort`` on ``day``, with a present mark for every
    learner (learners who joined since it opened are added). ``(register, created)``."""
    register, created = DailyRegister.objects.get_or_create(cohort=cohort, date=day)
    have = set(register.marks.values_list('learner_id', flat=True))
    AttendanceMark.objects.bulk_create([
        AttendanceMark(register=register, learner=learner, status=AttendanceMark.PRESENT)
        for learner in cohort_learners(cohort) if learner.pk not in have
    ])
    return register, created


def open_registers(day=None, *, force=False, notify_teachers=True, cohorts=None):
    """Open today's (or ``day``'s) register for every class. Idempotent.

    Returns the registers that were newly created. Does nothing on a day that is
    not a school day unless ``force``.
    """
    day = day or local_today()
    if not force and not is_school_day(day):
        return []
    created_regs = []
    for cohort in (cohorts if cohorts is not None else active_cohorts()):
        if not cohort_learners(cohort).exists():
            continue
        with transaction.atomic():
            register, created = ensure_register(cohort, day)
        if created:
            created_regs.append(register)
            if notify_teachers:
                _ask_teachers(register)
    return created_regs


def _ask_teachers(register):
    """Give the register taker(s) a task and a notification."""
    label = register.cohort_label
    url = register.get_absolute_url()
    title = f'Take the register for {label} — mark who is absent'
    body = (f'Everyone in {label} is marked present for {register.date:%A %d %B}. '
            f'Open the register, mark who is absent (or late), and submit it.')
    takers = [p for p in register_takers(register.cohort) if p.user_id]
    try:
        from apps.tasks.models import Task
        due = datetime.combine(register.date, CLOSE_AT, tzinfo=SCHOOL_TZ)
        task = None
        for person in takers:
            task = Task.objects.create(
                title=title[:200], description=f'{body}\n\n{url}',
                assign_to=Task.ASSIGN_USER, assignee=person, priority='high', due_date=due,
                programme=register.cohort.programme)
            if register.task_id is None:
                register.task = task
                register.save(update_fields=['task'])
    except Exception:   # pragma: no cover - the register matters more than the to-do
        logger.exception('attendance: could not create the register task')
    try:
        from apps.communication.services import notify
        for person in takers:
            notify(person.user, title=title, body=body, verb='attendance', level='warning',
                   url=url, category='tasks')
    except Exception:   # pragma: no cover
        logger.exception('attendance: could not notify the register taker')


# ---------------------------------------------------------------------------
# Marking and submitting
# ---------------------------------------------------------------------------
def save_marks(register, changes, by=None):
    """Apply ``{mark_id: (status, reason)}``. Unknown ids / statuses are ignored."""
    valid = {s for s, _ in AttendanceMark.STATUS_CHOICES}
    marks = {m.pk: m for m in register.marks.all()}
    changed = 0
    for mark_id, (status, reason) in changes.items():
        mark = marks.get(mark_id)
        if mark is None or status not in valid:
            continue
        reason = (reason or '').strip()[:200] if status != AttendanceMark.PRESENT else ''
        if mark.status != status or mark.reason != reason:
            mark.status, mark.reason = status, reason
            mark.marked_by = by
            mark.save(update_fields=['status', 'reason', 'marked_by', 'updated_at'])
            changed += 1
    return changed


def submit_register(register, by=None, *, auto=False):
    """Close the register; everyone not marked otherwise stays present."""
    if register.is_open:
        register.submitted_at = timezone.now()
        register.submitted_by = by
        register.auto_submitted = auto
    register.status = DailyRegister.STATUS_SUBMITTED
    register.save(update_fields=['status', 'submitted_at', 'submitted_by', 'auto_submitted'])
    _close_task(register)
    notify_parents_of_absence(register)
    return register


def _close_task(register):
    if not register.task_id:
        return
    try:
        from apps.tasks.models import Task, TaskAssignment
        Task.objects.filter(title=register.task.title, due_date=register.task.due_date,
                            assign_to=Task.ASSIGN_USER, status='open').update(status='closed')
        TaskAssignment.objects.filter(
            task__title=register.task.title, task__due_date=register.task.due_date,
        ).exclude(status=TaskAssignment.STATUS_COMPLETED).update(
            status=TaskAssignment.STATUS_COMPLETED, progress=100, completed_at=timezone.now())
    except Exception:   # pragma: no cover
        logger.exception('attendance: could not close the register task')


def notify_parents_of_absence(register):
    """Tell the linked parents of every absent learner — once per learner per day."""
    from apps.accounts.models import ParentLink
    try:
        from apps.communication.services import notify
    except Exception:   # pragma: no cover
        return 0
    sent = 0
    marks = (register.marks.filter(status=AttendanceMark.ABSENT, parents_notified_at__isnull=True)
             .select_related('learner__user'))
    for mark in marks:
        # Already told today through another register (a learner in two classes)?
        if AttendanceMark.objects.filter(learner=mark.learner, register__date=register.date,
                                         parents_notified_at__isnull=False).exists():
            mark.parents_notified_at = timezone.now()
            mark.save(update_fields=['parents_notified_at'])
            continue
        name = str(mark.learner)
        reason = f' Reason given: {mark.reason}.' if mark.reason else ''
        url = reverse('attendance:my') + f'?student={mark.learner.user_id}'
        for link in ParentLink.objects.filter(student_id=mark.learner.user_id).select_related('parent'):
            try:
                notify(link.parent, title=f'{name} was marked absent today',
                       body=(f'{name} was marked absent from {register.cohort_label} on '
                             f'{register.date:%A %d %B}.{reason} If this is unexpected, please '
                             f'contact the school.'),
                       verb='attendance', level='warning', url=url, email=True)
                sent += 1
            except Exception:   # pragma: no cover
                logger.exception('attendance: could not notify parent %s', link.parent_id)
        mark.parents_notified_at = timezone.now()
        mark.save(update_fields=['parents_notified_at'])
    return sent


def auto_submit_open(now=None):
    """Submit registers still open after the end of their school day."""
    now = now or local_now()
    qs = DailyRegister.objects.filter(status=DailyRegister.STATUS_OPEN).filter(
        Q(date__lt=now.date()) | (Q(date=now.date()) if now.time() >= CLOSE_AT else Q(pk__in=[])))
    done = 0
    for register in qs.select_related('cohort__programme'):
        submit_register(register, by=None, auto=True)
        done += 1
    return done


def run_daily(now=None):
    """Scheduler entry point ('daily-register')."""
    now = now or local_now()
    opened = []
    if now.time() >= OPEN_AT and now.time() < CLOSE_AT:
        opened = open_registers(now.date())
    closed = auto_submit_open(now)
    return f'opened {len(opened)} register(s), auto-submitted {closed}'


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------
def learner_summary(person, start=None, end=None):
    """Days present / absent / late / excused and the attendance %."""
    marks = AttendanceMark.objects.filter(learner=person)
    if start:
        marks = marks.filter(register__date__gte=start)
    if end:
        marks = marks.filter(register__date__lte=end)
    counts = {s: 0 for s, _ in AttendanceMark.STATUS_CHOICES}
    for status in marks.values_list('status', flat=True):
        counts[status] += 1
    total = sum(counts.values())
    attended = counts[AttendanceMark.PRESENT] + counts[AttendanceMark.LATE]
    counts['total'] = total
    counts['pct'] = round(attended * 100 / total, 1) if total else None
    counts['streak'] = consecutive_absences(person)
    return counts


def consecutive_absences(person):
    """The learner's current run of consecutive school days marked absent."""
    streak = 0
    for status in (AttendanceMark.objects.filter(learner=person)
                   .order_by('-register__date').values_list('status', flat=True)[:200]):
        if status != AttendanceMark.ABSENT:
            break
        streak += 1
    return streak


def flagged_learners(limit=CONSECUTIVE_ABSENCE_LIMIT, cohorts=None):
    """``[(person, streak, since_date)]`` for learners absent ``limit``+ days in a row."""
    from apps.accounts.models import Person
    since = local_today() - timedelta(days=limit * 2 + 30)
    candidates = (AttendanceMark.objects.filter(status=AttendanceMark.ABSENT, register__date__gte=since))
    if cohorts is not None:
        candidates = candidates.filter(register__cohort__in=cohorts)
    ids = candidates.values_list('learner_id', flat=True).distinct()
    out = []
    for person in Person.objects.filter(pk__in=ids).select_related('user'):
        streak = consecutive_absences(person)
        if streak >= limit:
            dates = list(AttendanceMark.objects.filter(learner=person)
                         .order_by('-register__date').values_list('register__date', flat=True)[:streak])
            out.append((person, streak, dates[-1] if dates else None))
    out.sort(key=lambda row: -row[1])
    return out


def month_grid(cohort, first_day, last_day):
    """``(days, rows)`` — rows are ``{'learner', 'cells': [code|''], 'summary'}``."""
    registers = {r.date: r for r in DailyRegister.objects.filter(
        cohort=cohort, date__gte=first_day, date__lte=last_day)}
    days = sorted(set(registers) | set(_school_days(first_day, last_day)))
    marks = {}
    for m in AttendanceMark.objects.filter(register__in=registers.values()).values(
            'learner_id', 'register__date', 'status'):
        marks[(m['learner_id'], m['register__date'])] = m['status']
    learner_ids = {lid for lid, _ in marks}
    learners = list(cohort_learners(cohort))
    from apps.accounts.models import Person
    extra = Person.objects.filter(pk__in=learner_ids - {p.pk for p in learners})
    learners += list(extra)
    rows = []
    for learner in learners:
        cells, counts = [], {s: 0 for s, _ in AttendanceMark.STATUS_CHOICES}
        for day in days:
            status = marks.get((learner.pk, day))
            cells.append(AttendanceMark.CODES.get(status, '') if status else '')
            if status:
                counts[status] += 1
        total = sum(counts.values())
        attended = counts[AttendanceMark.PRESENT] + counts[AttendanceMark.LATE]
        counts['total'] = total
        counts['pct'] = round(attended * 100 / total, 1) if total else None
        rows.append({'learner': learner, 'cells': cells, 'summary': counts})
    return days, rows


def _school_days(first, last):
    from .calendar import school_days_between
    return school_days_between(first, min(last, local_today()))
