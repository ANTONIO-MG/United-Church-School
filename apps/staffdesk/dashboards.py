"""Query helpers behind the staff desk's three dashboards.

* :func:`operations` — ``/staff/``, the admin team's morning screen.
* :func:`student_360` — ``/staff/students/<person_id>/``, one student on one page.
* :func:`teaching` — ``/staff/teaching/``, an educator's own desk.

The rules the whole module follows:

* **Cheap by construction.** Every number is an aggregate or a ``LIMIT``-ed
  query; nothing walks a table in Python. The operations page must stay fast
  with thousands of students, so no panel may scale with the user count.
* **Never break the page.** Each panel is built inside :func:`_panel`, which
  logs and swallows an exception, so a missing table or a bad row costs that
  one panel (it renders its empty state), not the dashboard.
* **Every panel says where to act.** Each one carries the URL of the page that
  fixes what it shows, resolved by :func:`_url` so a page another app has not
  built yet degrades to its fallback instead of a ``NoReverseMatch``.
"""

import logging
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db.models import Avg, Count, DecimalField, ExpressionWrapper, F, Max, Min, Q, Sum
from django.db.models.functions import NullIf
from django.urls import NoReverseMatch, reverse
from django.utils import timezone

from core.utils import display_name as _display_name

logger = logging.getLogger(__name__)

ZERO = Decimal('0')

#: A student counts as inactive after this long without signing in or studying.
INACTIVE_AFTER = timedelta(days=7)
#: A module can be nudged at most once in this window.
NUDGE_COOLDOWN = timedelta(hours=24)
#: Average recent mark (percent) below which a student is "falling behind".
LOW_SCORE_PCT = 50
#: How far back "recent" scores reach.
RECENT_SCORES = timedelta(days=30)


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------
def _panel(name, build, default=None):
    """Run one panel's builder; on any failure log it and return ``default``."""
    try:
        return build()
    except Exception as exc:
        logger.exception('staffdesk dashboard: %s panel failed', name)
        from core.errors import report
        report('DESK-9004', exc, context={'panel': name})
        return default


def _url(*candidates, fallback='#'):
    """The first of ``candidates`` that reverses — ``'name'`` or ``('name', args)``."""
    for candidate in candidates:
        name, args = (candidate, ()) if isinstance(candidate, str) else candidate
        try:
            return reverse(name, args=args)
        except NoReverseMatch:
            continue
    return fallback


def display_name(user):
    """The profile's name when the account has none of its own, else ``core.utils.display_name``."""
    if user is not None and not (user.get_full_name() or '').strip():
        person = getattr(user, 'profile', None)
        full = f"{getattr(person, 'first_name', '')} {getattr(person, 'last_name', '')}".strip()
        if full:
            return full
    return _display_name(user)


def _pct(part, whole):
    try:
        return round((part or 0) * 100 / whole) if whole else None
    except Exception:
        return None


def _day_bounds(day):
    """Aware ``[start, end)`` datetimes of a local date."""
    from datetime import datetime, time
    tz = timezone.get_current_timezone()
    start = timezone.make_aware(datetime.combine(day, time.min), tz)
    return start, start + timedelta(days=1)


def _score_pct():
    """``score`` as a percentage of the assessment's marks (NULL when it has none)."""
    return ExpressionWrapper(
        F('score') * 100 / NullIf(F('assessment__total_marks'), 0),
        output_field=DecimalField(max_digits=9, decimal_places=2))


def _invoice_models():
    from apps.finance import models as finance
    return finance.Invoice, finance.InvoicePayment


def open_invoice_filter():
    """Invoices that still ask for money: issued, not paid, not cancelled."""
    Invoice, _ = _invoice_models()
    return ~Q(status__in=[Invoice.STATUS_DRAFT, Invoice.STATUS_PAID, Invoice.STATUS_CANCELLED])


def balance_of(invoices):
    """Outstanding on an invoice queryset — two aggregates, never a loop."""
    _, InvoicePayment = _invoice_models()
    billed = invoices.aggregate(t=Sum('total'))['t'] or ZERO
    paid = (InvoicePayment.objects
            .filter(invoice__in=invoices, status=InvoicePayment.STATUS_COMPLETED)
            .aggregate(t=Sum('amount'))['t'] or ZERO)
    return max(billed - paid, ZERO)


# ---------------------------------------------------------------------------
# 1 · Operations dashboard
# ---------------------------------------------------------------------------
def operations(user):
    """Everything ``/staff/`` shows, one dict per panel."""
    now = timezone.now()
    return {
        'people': _panel('people', lambda: _ops_people(now), {}),
        'money': _panel('money', _ops_money, {}),
        'risk': _panel('risk', _ops_risk, {}),
        'marking': _panel('marking', _ops_marking, {}),
        'sessions': _panel('sessions', _ops_sessions, {}),
        'jobs': _panel('jobs', lambda: _ops_jobs(now), {}),
        'errors': _panel('errors', _ops_errors, {}),
        'broadcasts': _panel('broadcasts', _ops_broadcasts, {}),
        'activity': _panel('activity', lambda: _activity(), []),
        'activity_url': _url('staffdesk:ops-audit', 'staffdesk:audit'),
        'actions': quick_actions(),
    }


def quick_actions():
    return [
        {'label': 'Send notification', 'icon': 'bi-megaphone',
         'url': _url('communication:announcement-compose')},
        {'label': 'New invoice', 'icon': 'bi-receipt', 'url': _url('finance:invoice-new')},
        {'label': 'Schedule session', 'icon': 'bi-camera-video', 'url': _url('livesessions:session-create')},
        {'label': 'Create task', 'icon': 'bi-check2-square', 'url': _url('orgtasks:add-task')},
        {'label': 'Enrol member', 'icon': 'bi-person-plus', 'url': _url('accounts:manage-members')},
    ]


def _ops_people(now):
    User = get_user_model()
    students = User.objects.filter(is_active=True, profile__user_type='student')
    counts = students.aggregate(
        total=Count('id'),
        active_week=Count('id', filter=Q(last_login__gte=now - timedelta(days=7))),
        new_week=Count('id', filter=Q(date_joined__gte=now - timedelta(days=7))),
        new_month=Count('id', filter=Q(date_joined__gte=now - timedelta(days=30))),
    )
    recent = list(User.objects.filter(date_joined__gte=now - timedelta(days=30))
                  .select_related('profile').order_by('-date_joined')[:6])
    counts['recent'] = [{'user': u, 'name': display_name(u), 'person': getattr(u, 'profile', None),
                         'role': getattr(getattr(u, 'profile', None), 'user_type', '') or ''}
                        for u in recent]
    counts['url'] = _url('staffdesk:students', 'accounts:manage-members')
    return counts


def _ops_money():
    Invoice, InvoicePayment = _invoice_models()
    today = timezone.localdate()
    overdue = Invoice.objects.filter(open_invoice_filter(), due_date__lt=today, total__gt=0)
    collected = (InvoicePayment.objects
                 .filter(status=InvoicePayment.STATUS_COMPLETED, paid_at__date__gte=today.replace(day=1))
                 .exclude(invoice__status=Invoice.STATUS_CANCELLED)
                 .aggregate(t=Sum('amount'), n=Count('id')))
    return {
        'overdue_count': overdue.count(),
        'overdue_amount': balance_of(overdue),
        'collected_month': collected['t'] or ZERO,
        'payments_month': collected['n'] or 0,
        'url': _url('finance:invoices'),
        'overview_url': _url('finance:money-overview'),
    }


def _ops_risk():
    from apps.analytics.models import RiskFlag
    open_flags = RiskFlag.objects.filter(resolved=False)
    top = list(open_flags.select_related('student', 'student__profile', 'module__programme__institution')
               .order_by('-score', '-created_at')[:5])
    return {
        'students': open_flags.values('student_id').distinct().count(),
        'high': open_flags.filter(score__gte=70).values('student_id').distinct().count(),
        'top': [{'flag': f, 'name': display_name(f.student),
                 'person_id': getattr(getattr(f.student, 'profile', None), 'pk', None),
                 'reasons': (f.reasons or [])[:2] if isinstance(f.reasons, list) else []}
                for f in top],
        'url': _url('staffdesk:academic-risk', 'staffdesk:at-risk', 'staffdesk:risk', 'analytics:dashboard'),
    }


def _marking_counts(modules=None):
    """``(count, oldest_submitted_at)`` of work waiting for a human mark."""
    from apps.assessments.models import AssessmentAttempt, AssignmentSubmission
    attempts = AssessmentAttempt.objects.filter(status=AssessmentAttempt.STATUS_SUBMITTED)
    assignments = AssignmentSubmission.objects.filter(status='submitted')
    if modules is not None:
        attempts = attempts.filter(assessment__module__in=modules)
        assignments = assignments.filter(assessment__module__in=modules)
    a = attempts.aggregate(n=Count('id'), oldest=Min('submitted_at'),
                           flagged=Count('id', filter=Q(integrity_flagged=True)))
    b = assignments.aggregate(n=Count('id'), oldest=Min('submitted_at'))
    oldest = min([d for d in (a['oldest'], b['oldest']) if d], default=None)
    return {'attempts': a['n'], 'assignments': b['n'], 'total': a['n'] + b['n'],
            'flagged': a['flagged'], 'oldest': oldest,
            'oldest_days': (timezone.now() - oldest).days if oldest else None}


def _ops_marking():
    data = _marking_counts()
    data['url'] = _url('assessments:marking-queue')
    return data


def _ops_sessions():
    from apps.communication.models import MeetingRoom
    today = timezone.localdate()
    start, _ = _day_bounds(today)
    end = start + timedelta(days=2)
    rows = list(MeetingRoom.objects.filter(is_active=True, scheduled_start__gte=start, scheduled_start__lt=end)
                .select_related('host', 'module__programme__institution')
                .order_by('scheduled_start')[:12])
    tomorrow = today + timedelta(days=1)
    return {
        'days': [{'label': 'today', 'rows': [m for m in rows if timezone.localdate(m.scheduled_start) == today]},
                 {'label': 'tomorrow',
                  'rows': [m for m in rows if timezone.localdate(m.scheduled_start) == tomorrow]}],
        'url': _url('livesessions:calendar'),
        'create_url': _url('livesessions:session-create'),
    }


def _ops_jobs(now):
    """Failing, stuck and overdue scheduler jobs, measured against their intervals."""
    from apps.scheduler.jobs import JOBS, LOCK_STALE_AFTER
    from apps.scheduler.models import JobRun

    states = {row.name: row for row in JobRun.objects.all()[:200]}
    problems, healthy = [], 0
    for job in JOBS:
        if not job.enabled:
            continue
        state = states.get(job.name)
        issue = None
        if state is None or not state.last_started_at:
            issue = 'Never run'
        elif state.consecutive_failures:
            issue = f'Failing ×{state.consecutive_failures}'
        elif state.locked_at and (now - state.locked_at).total_seconds() > LOCK_STALE_AFTER:
            issue = 'Stuck'
        elif (now - state.last_started_at).total_seconds() > job.every * 2 + 300:
            issue = 'Overdue'
        if issue:
            problems.append({'name': job.name, 'issue': issue, 'state': state,
                             'is_failure': issue.startswith('Failing') or issue == 'Stuck'})
        else:
            healthy += 1
    problems.sort(key=lambda p: (not p['is_failure'], p['name']))
    last_tick = max((s.last_started_at for s in states.values() if s.last_started_at), default=None)
    return {'problems': problems[:6], 'problem_count': len(problems), 'healthy': healthy,
            'total': healthy + len(problems), 'last_tick': last_tick,
            'failing': sum(1 for p in problems if p['is_failure']),
            'url': _url('staffdesk:ops-jobs', 'staffdesk:jobs', fallback='/staff/jobs/')}


def _ops_errors():
    from apps.diagnostics.models import ErrorEvent
    unresolved = ErrorEvent.objects.filter(status__in=[ErrorEvent.STATUS_OPEN, ErrorEvent.STATUS_ACKNOWLEDGED])
    day_ago = timezone.now() - timedelta(days=1)
    counts = unresolved.aggregate(n=Count('id'), today=Count('id', filter=Q(last_seen__gte=day_ago)))
    return {'count': counts['n'], 'today': counts['today'],
            'latest': list(unresolved.order_by('-last_seen')[:4]),
            'url': _url('diagnostics:log')}


def _ops_broadcasts():
    from apps.communication.models import Announcement, Notification
    latest = list(Announcement.objects.filter(sent_at__isnull=False)
                  .select_related('sender').order_by('-sent_at')[:5])
    reads = {row['announcement_id']: row for row in
             Notification.objects.filter(announcement_id__in=[a.pk for a in latest])
             .values('announcement_id').annotate(n=Count('id'), read=Count('id', filter=Q(is_read=True)))}
    rows = []
    for a in latest:
        stats = reads.get(a.pk, {'n': 0, 'read': 0})
        rows.append({'a': a, 'reached': stats['n'] or a.recipient_count, 'read': stats['read'],
                     'read_pct': _pct(stats['read'], stats['n'])})
    return {'rows': rows, 'url': _url('communication:announcements'),
            'compose_url': _url('communication:announcement-compose')}


def _activity(person=None, limit=10):
    from apps.accounts.models import ActivityLog
    qs = ActivityLog.objects.select_related('actor__user', 'target_user__user')
    if person is not None:
        qs = qs.filter(Q(actor=person) | Q(target_user=person))
    return list(qs.order_by('-timestamp')[:limit])


# ---------------------------------------------------------------------------
# 2 · Student 360
# ---------------------------------------------------------------------------
def search_students(query='', role='student'):
    """People for the Student 360 picker, newest first (a queryset to paginate)."""
    from apps.accounts.models import Person
    qs = (Person.objects.select_related('user')
          .prefetch_related('programme_enrolments__programme__institution'))
    if role:
        qs = qs.filter(user_type=role)
    query = (query or '').strip()
    if query:
        terms = Q()
        for word in query.split()[:4]:
            terms &= (Q(first_name__icontains=word) | Q(last_name__icontains=word)
                      | Q(user__email__icontains=word) | Q(user__first_name__icontains=word)
                      | Q(user__last_name__icontains=word) | Q(phone__icontains=word))
        qs = qs.filter(terms)
    return qs.order_by('-user__date_joined', '-pk')


def student_360(person):
    """Every panel of one student's page. ``person`` is an ``accounts.Person``."""
    user = person.user
    return {
        'contact': _panel('contact', lambda: _contact(person), {}),
        'enrolments': _panel('enrolments', lambda: _enrolments(person), {}),
        'grades': _panel('grades', lambda: _grades(user), []),
        'attempts': _panel('attempts', lambda: _attempts(user), {}),
        'attendance': _panel('attendance', lambda: _attendance(user), {}),
        'tasks': _panel('tasks', lambda: _tasks(user), {}),
        'money': _panel('money', lambda: _student_money(user), {}),
        'shop': _panel('shop', lambda: _shop(user), {}),
        'notifications': _panel('notifications', lambda: _notifications(user), {}),
        'activity': _panel('activity', lambda: _activity(person, limit=12), []),
        'parents': _panel('parents', lambda: _parents(user), []),
        'risk': _panel('risk', lambda: _student_risk(user), []),
        'actions': _student_actions(person),
        'parent_links_url': _url('staffdesk:ops-parent-links'),
    }


def _student_actions(person):
    user = person.user
    return {
        'notify': _url('communication:announcement-compose') + f'?user={user.pk}',
        'message': _url(('communication:chat-direct', [user.pk])),
        'invoice': _url('finance:invoice-new') + f'?customer={user.pk}',
        'profile': _url(('accounts:profile', [person.pk])),
        'statement': _url(('finance:statement-for', [user.pk])),
        'payments': _url(('finance:student-payments', [person.pk])),
        'enrol': _url(('accounts:member-enrol', [person.pk])),
    }


def _contact(person):
    contact = getattr(person, 'contact', None)
    return {'phone': (getattr(contact, 'primary_phone', '') or person.phone or ''),
            'city': ', '.join(p for p in (getattr(contact, 'suburb', ''), getattr(contact, 'city', ''),
                                          getattr(contact, 'province', '')) if p)}


def _enrolments(person):
    from apps.learning.models import ModuleEnrolment
    programmes = list(person.programme_enrolments.select_related('programme__institution', 'cohort')
                      .order_by('-is_active', '-created_at'))
    modules = list(ModuleEnrolment.objects.filter(person=person)
                   .select_related('programme_module__programme__institution', 'programme_module__module')
                   .order_by('programme_module__programme_id', 'programme_module__order'))
    counts = {}
    for row in modules:
        counts[row.status] = counts.get(row.status, 0) + 1
    return {'programmes': programmes, 'modules': modules, 'counts': counts}


def _grades(user):
    from apps.reports.models import Grade
    return list(Grade.objects.filter(student=user)
                .select_related('module__programme__institution', 'module__module')
                .order_by('module__code'))


def _attempts(user):
    from apps.assessments.models import AssessmentAttempt
    qs = AssessmentAttempt.objects.filter(student=user)
    rows = list(qs.exclude(status=AssessmentAttempt.STATUS_IN_PROGRESS)
                .select_related('assessment__module')
                .annotate(pct=_score_pct()).order_by('-submitted_at', '-created_at')[:10])
    stats = qs.filter(status=AssessmentAttempt.STATUS_MARKED).annotate(pct=_score_pct()).aggregate(
        avg=Avg('pct'), n=Count('id'), passed=Count('id', filter=Q(passed=True)))
    return {'rows': rows, 'avg': stats['avg'], 'marked': stats['n'], 'passed': stats['passed'],
            'waiting': qs.filter(status=AssessmentAttempt.STATUS_SUBMITTED).count()}


def _attendance(user):
    from apps.communication.models import Attendance
    counts = Attendance.objects.filter(student=user).aggregate(
        total=Count('id'),
        present=Count('id', filter=Q(status__in=[Attendance.STATUS_PRESENT, Attendance.STATUS_LATE])),
        excused=Count('id', filter=Q(status=Attendance.STATUS_EXCUSED)),
        late=Count('id', filter=Q(status=Attendance.STATUS_LATE)))
    countable = counts['total'] - counts['excused']
    counts['rate'] = _pct(counts['present'], countable)
    counts['recent'] = list(Attendance.objects.filter(student=user)
                            .select_related('session__module').order_by('-session__session_date')[:6])
    return counts


def _tasks(user):
    from apps.tasks.models import TaskAssignment
    now = timezone.now()
    open_qs = TaskAssignment.objects.filter(user=user).exclude(status=TaskAssignment.STATUS_COMPLETED)
    counts = open_qs.aggregate(open=Count('id'), overdue=Count('id', filter=Q(task__due_date__lt=now)))
    counts['done'] = TaskAssignment.objects.filter(user=user, status=TaskAssignment.STATUS_COMPLETED).count()
    counts['rows'] = list(open_qs.select_related('task').order_by(F('task__due_date').asc(nulls_last=True))[:8])
    counts['now'] = now
    return counts


def _student_money(user):
    Invoice, InvoicePayment = _invoice_models()
    issued = Invoice.objects.filter(customer=user).exclude(status=Invoice.STATUS_DRAFT)
    live = issued.exclude(status=Invoice.STATUS_CANCELLED)
    billed = live.aggregate(t=Sum('total'))['t'] or ZERO
    paid = (InvoicePayment.objects.filter(invoice__in=live, status=InvoicePayment.STATUS_COMPLETED)
            .aggregate(t=Sum('amount'))['t'] or ZERO)
    today = timezone.localdate()
    overdue = live.filter(open_invoice_filter(), due_date__lt=today, total__gt=0)
    return {
        'billed': billed, 'paid': paid, 'balance': billed - paid,
        'overdue_count': overdue.count(),
        'invoices': list(issued.prefetch_related('payments').order_by('-issue_date', '-id')[:8]),
        'payments': list(InvoicePayment.objects.filter(invoice__customer=user)
                         .select_related('invoice').order_by('-paid_at')[:6]),
    }


def _shop(user):
    from apps.shop.models import Booking, Order
    orders = list(Order.objects.filter(buyer=user, checked_out=True)
                  .annotate(n_items=Count('items')).order_by('-created_at')[:6])
    bookings = list(Booking.objects.filter(student=user)
                    .exclude(status=Booking.STATUS_EXPIRED)
                    .select_related('educator__user', 'product').order_by('-start')[:6])
    return {'orders': orders, 'bookings': bookings}


def _notifications(user):
    from apps.communication.models import Notification
    counts = Notification.objects.filter(recipient=user).aggregate(
        total=Count('id'), read=Count('id', filter=Q(is_read=True)),
        month=Count('id', filter=Q(created_at__gte=timezone.now() - timedelta(days=30))))
    counts['rate'] = _pct(counts['read'], counts['total'])
    counts['recent'] = list(Notification.objects.filter(recipient=user).order_by('-created_at')[:6])
    return counts


def _parents(user):
    from apps.accounts.models import ParentLink
    return list(ParentLink.objects.filter(student=user).select_related('parent__profile'))


def _student_risk(user):
    from apps.analytics.models import RiskFlag
    return list(RiskFlag.objects.filter(student=user, resolved=False).select_related('module')[:3])


# ---------------------------------------------------------------------------
# 3 · Educator dashboard
# ---------------------------------------------------------------------------
def educator_modules(person):
    """The offerings ``person`` teaches, each with its live student count."""
    from apps.learning.models import ModuleEnrolment, ProgrammeModule
    live = [ModuleEnrolment.STATUS_TRIAL, ModuleEnrolment.STATUS_ACTIVE]
    return list(ProgrammeModule.objects.filter(educators=person, is_active=True)
                .select_related('programme__institution', 'module')
                .annotate(n_students=Count('enrolments', filter=Q(enrolments__status__in=live), distinct=True))
                .order_by('programme__institution__code', 'programme__code', 'order', 'id'))


def _live_enrolments(modules):
    """``{module_id: [user_id, …]}`` for students with live (trial/paid) access."""
    from apps.learning.models import ModuleEnrolment
    out = {}
    rows = (ModuleEnrolment.objects
            .filter(programme_module__in=modules,
                    status__in=[ModuleEnrolment.STATUS_TRIAL, ModuleEnrolment.STATUS_ACTIVE],
                    person__user__is_active=True, person__user_type='student')
            .values_list('programme_module_id', 'person__user_id'))
    for module_id, user_id in rows:
        out.setdefault(module_id, []).append(user_id)
    return out


def last_seen(user_ids):
    """``{user_id: datetime|None}`` — the later of last sign-in and last study."""
    if not user_ids:
        return {}
    User = get_user_model()
    seen = {}
    for pk, login in User.objects.filter(pk__in=user_ids).values_list('pk', 'last_login'):
        seen[pk] = login
    try:
        from apps.learning.models import StudySession
        for pk, studied in (StudySession.objects.filter(student_id__in=user_ids)
                            .values('student_id').annotate(t=Max('updated_at')).values_list('student_id', 't')):
            if studied and (seen.get(pk) is None or studied > seen[pk]):
                seen[pk] = studied
    except Exception:
        logger.exception('staffdesk: study-session recency failed')
    return seen


def inactive_students(module, now=None):
    """Users on ``module`` with live access who have gone quiet for :data:`INACTIVE_AFTER`."""
    now = now or timezone.now()
    user_ids = _live_enrolments([module]).get(module.pk, [])
    seen = last_seen(user_ids)
    cutoff = now - INACTIVE_AFTER
    quiet = [pk for pk in user_ids if seen.get(pk) is None or seen[pk] < cutoff]
    return list(get_user_model().objects.filter(pk__in=quiet))


def last_nudge(module):
    from .models import Nudge
    return Nudge.objects.filter(module=module).order_by('-sent_at').first()


def can_nudge(module, now=None):
    """``(allowed, next_allowed_at)`` under the once-per-:data:`NUDGE_COOLDOWN` rule."""
    now = now or timezone.now()
    latest = last_nudge(module)
    if latest and latest.sent_at > now - NUDGE_COOLDOWN:
        return False, latest.sent_at + NUDGE_COOLDOWN
    return True, None


def send_nudge(module, actor):
    """Notify each inactive student on ``module``; returns the :class:`Nudge` row.

    The row is written *before* sending, inside a lock on the module, so a
    double click (or two teachers on one subject) cannot both get through.
    """
    from django.db import transaction

    from apps.communication.services import notify
    from apps.learning.models import ProgrammeModule

    from .models import Nudge

    recipients = inactive_students(module)
    if not recipients:
        # Nothing to send, so nothing to rate-limit: an unsaved row says "0".
        return Nudge(module=module, sent_by=actor, recipients=0)

    with transaction.atomic():
        ProgrammeModule.objects.select_for_update().filter(pk=module.pk).first()
        allowed, _next = can_nudge(module)
        if not allowed:
            return None
        nudge = Nudge.objects.create(module=module, sent_by=actor)

    url = _url(('learning:module-feed', [module.pk]))
    teacher = display_name(actor)
    sent = 0
    for student in recipients:
        try:
            note = notify(
                student,
                title=f'{module.display_name} misses you',
                body=(f"It's been a little while since you studied {module.display_name}. "
                      f'Pick up where you left off — even 20 minutes today keeps you on track. — {teacher}'),
                url=url, actor=actor, category='deadlines', email=True)
            sent += 1 if note is not None else 0
        except Exception as exc:
            logger.exception('staffdesk nudge: notify failed for user %s', student.pk)
            from core.errors import report
            report('NOTF-9001', exc, context={'nudge_module': module.pk, 'user': student.pk})
    Nudge.objects.filter(pk=nudge.pk).update(recipients=sent)
    nudge.recipients = sent
    return nudge


def teaching(person, *, now=None):
    """Everything ``/staff/teaching/`` shows for the educator ``person``."""
    now = now or timezone.now()
    modules = _panel('modules', lambda: educator_modules(person), [])
    enrolled = _panel('enrolled', lambda: _live_enrolments(modules), {}) if modules else {}
    behind = _panel('behind', lambda: _falling_behind(modules, enrolled, now), {}) if modules else {}

    inactive_by_module = behind.get('inactive_by_module', {}) if behind else {}
    nudges = _panel('nudges', lambda: _nudge_state(modules, now), {}) if modules else {}
    for module in modules:
        module.inactive_count = inactive_by_module.get(module.pk, 0)
        state = nudges.get(module.pk, {})
        module.last_nudge = state.get('last')
        module.can_nudge = state.get('allowed', True)
        module.next_nudge_at = state.get('next')
        module.feed_url = _url(('learning:module-feed', [module.pk]))

    return {
        'modules': modules,
        'student_total': len({uid for ids in enrolled.values() for uid in ids}),
        'marking': _panel('marking', lambda: _teaching_marking(modules), {}) if modules else {},
        'behind': behind,
        'sessions': _panel('sessions', lambda: _teaching_sessions(person, modules, now), []),
        'attendance': _panel('attendance', lambda: _attendance_trend(modules, enrolled), []) if modules else [],
        'submissions': _panel('submissions', lambda: _recent_submissions(modules), []) if modules else [],
        'marking_url': _url('assessments:marking-queue'),
        'calendar_url': _url('livesessions:calendar'),
        'create_session_url': _url('livesessions:session-create'),
        'attendance_url': _url('communication:attendance'),
    }


def _nudge_state(modules, now):
    from .models import Nudge
    latest = {}
    for row in (Nudge.objects.filter(module__in=modules, sent_at__gte=now - timedelta(days=30))
                .order_by('module_id', '-sent_at')):
        latest.setdefault(row.module_id, row)
    out = {}
    for module in modules:
        row = latest.get(module.pk)
        cooling = bool(row and row.sent_at > now - NUDGE_COOLDOWN)
        out[module.pk] = {'last': row, 'allowed': not cooling,
                          'next': (row.sent_at + NUDGE_COOLDOWN) if cooling else None}
    return out


def _teaching_marking(modules):
    from apps.assessments.models import AssessmentAttempt, AssignmentSubmission
    data = _marking_counts(modules)
    rows = []
    for a in (AssessmentAttempt.objects
              .filter(assessment__module__in=modules, status=AssessmentAttempt.STATUS_SUBMITTED)
              .select_related('assessment__module', 'student__profile').order_by('submitted_at')[:6]):
        rows.append({'title': a.assessment.title, 'module': a.assessment.module, 'student': display_name(a.student),
                     'at': a.submitted_at, 'url': _url(('assessments:mark-attempt', [a.public_id])),
                     'flagged': a.integrity_flagged})
    for s in (AssignmentSubmission.objects
              .filter(assessment__module__in=modules, status='submitted')
              .select_related('assessment__module', 'student__profile').order_by('submitted_at')[:6]):
        rows.append({'title': s.assessment.title, 'module': s.assessment.module, 'student': display_name(s.student),
                     'at': s.submitted_at, 'url': _url('assessments:marking-queue'), 'flagged': False})
    rows.sort(key=lambda r: r['at'] or timezone.now())
    data['rows'] = rows[:8]
    return data


def _falling_behind(modules, enrolled, now):
    """Students with no activity for a week, low recent marks, or overdue tasks.

    Three grouped queries over the educator's own students — recency, average
    recent mark, overdue task count — joined in Python on ``user_id``.
    """
    from apps.assessments.models import AssessmentAttempt
    from apps.tasks.models import TaskAssignment

    user_ids = sorted({uid for ids in enrolled.values() for uid in ids})
    if not user_ids:
        return {'rows': [], 'count': 0, 'inactive_by_module': {}}
    seen = last_seen(user_ids)
    scores = dict(AssessmentAttempt.objects
                  .filter(student_id__in=user_ids, assessment__module__in=modules,
                          status=AssessmentAttempt.STATUS_MARKED, submitted_at__gte=now - RECENT_SCORES)
                  .annotate(pct=_score_pct()).values('student_id')
                  .annotate(avg=Avg('pct')).values_list('student_id', 'avg'))
    overdue = dict(TaskAssignment.objects
                   .filter(user_id__in=user_ids, task__due_date__lt=now)
                   .exclude(status=TaskAssignment.STATUS_COMPLETED)
                   .values('user_id').annotate(n=Count('id')).values_list('user_id', 'n'))

    cutoff = now - INACTIVE_AFTER
    modules_of = {}
    inactive_by_module = {}
    for module in modules:
        for uid in enrolled.get(module.pk, []):
            modules_of.setdefault(uid, []).append(module)
            if seen.get(uid) is None or seen[uid] < cutoff:
                inactive_by_module[module.pk] = inactive_by_module.get(module.pk, 0) + 1

    flagged = []
    for uid in user_ids:
        when = seen.get(uid)
        quiet = when is None or when < cutoff
        avg = scores.get(uid)
        low = avg is not None and avg < LOW_SCORE_PCT
        late = overdue.get(uid, 0)
        if not (quiet or low or late):
            continue
        reasons = []
        if quiet:
            reasons.append('Never active' if when is None else f'Inactive {(now - when).days}d')
        if low:
            reasons.append(f'Avg {round(avg)}%')
        if late:
            reasons.append(f'{late} overdue task{"s" if late != 1 else ""}')
        severity = (2 if quiet else 0) + (2 if low else 0) + min(late, 3)
        flagged.append({'user_id': uid, 'seen': when, 'avg': avg, 'overdue': late, 'reasons': reasons,
                        'quiet': quiet, 'low': low, 'severity': severity,
                        'modules': modules_of.get(uid, [])})
    flagged.sort(key=lambda r: (-r['severity'], r['seen'] or now - timedelta(days=3650)))
    top = flagged[:15]
    users = {u.pk: u for u in get_user_model().objects.filter(pk__in=[r['user_id'] for r in top])
             .select_related('profile')}
    for row in top:
        user = users.get(row['user_id'])
        row['name'] = display_name(user)
        row['email'] = getattr(user, 'email', '')
        row['person_id'] = getattr(getattr(user, 'profile', None), 'pk', None)
    return {'rows': top, 'count': len(flagged), 'inactive_by_module': inactive_by_module,
            'inactive': sum(1 for r in flagged if r['quiet']),
            'low': sum(1 for r in flagged if r['low']),
            'late': sum(1 for r in flagged if r['overdue'])}


def _teaching_sessions(person, modules, now):
    from apps.communication.models import MeetingRoom
    scope = Q(host=person.user)
    if modules:
        scope |= Q(module__in=modules)
    return list(MeetingRoom.objects.filter(scope, is_active=True, scheduled_start__gte=now - timedelta(hours=2))
                .select_related('module__programme__institution', 'host')
                .order_by('scheduled_start')[:8])


def _attendance_trend(modules, enrolled):
    """Turnout for the educator's last eight class sessions, oldest first."""
    from apps.communication.models import Attendance, ClassSession
    today = timezone.localdate()
    sessions = list(ClassSession.objects.filter(module__in=modules, session_date__lte=today)
                    .select_related('module')
                    .annotate(present=Count('attendance', filter=Q(attendance__status__in=[
                        Attendance.STATUS_PRESENT, Attendance.STATUS_LATE])),
                              excused=Count('attendance', filter=Q(attendance__status=Attendance.STATUS_EXCUSED)))
                    .order_by('-session_date', '-starts_at')[:8])
    rows = []
    for s in reversed(sessions):
        expected = max(len(enrolled.get(s.module_id, [])) - s.excused, 0)
        pct = _pct(s.present, expected)
        rows.append({'session': s, 'present': s.present, 'expected': expected,
                     'pct': min(pct, 100) if pct is not None else None,
                     'url': _url(('communication:attendance-session', [s.pk]))})
    return rows


def _recent_submissions(modules):
    from apps.assessments.models import AssessmentAttempt, AssignmentSubmission
    rows = []
    for a in (AssessmentAttempt.objects
              .filter(assessment__module__in=modules, submitted_at__isnull=False)
              .exclude(status=AssessmentAttempt.STATUS_IN_PROGRESS)
              .select_related('assessment__module', 'student__profile').annotate(pct=_score_pct())
              .order_by('-submitted_at')[:8]):
        rows.append({'title': a.assessment.title, 'module': a.assessment.module, 'student': display_name(a.student),
                     'student_id': a.student_id, 'at': a.submitted_at, 'status': a.status,
                     'pct': a.pct if a.status == AssessmentAttempt.STATUS_MARKED else None})
    for s in (AssignmentSubmission.objects
              .filter(assessment__module__in=modules, submitted_at__isnull=False)
              .select_related('assessment__module', 'student__profile').order_by('-submitted_at')[:8]):
        rows.append({'title': s.assessment.title, 'module': s.assessment.module, 'student': display_name(s.student),
                     'student_id': s.student_id, 'at': s.submitted_at, 'status': s.status, 'pct': None})
    rows.sort(key=lambda r: r['at'], reverse=True)
    return rows[:8]
