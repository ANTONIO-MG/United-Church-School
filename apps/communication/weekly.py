"""The Monday-morning "your week ahead" notification.

One short, personal list per student — what is due, what opens, which classes
are on, what arrived last week and how far away the exam is — so the week starts
with a plan rather than a search. Educators get the teaching version: their
classes this week and what is waiting to be marked.

Sent by the ``weekly-summary`` job, which ticks hourly but only acts on Monday
from 06:00 (SAST). Each person's summary is recorded as an
:class:`~apps.communication.models.AutoNotice` keyed by ISO week, so a second run
on the same Monday sends nothing. Anyone with nothing on their plate is skipped:
an empty list teaches people to ignore the next one.
"""

import logging
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone

from core.errors import report

logger = logging.getLogger('apps')


def _fmt(dt):
    return timezone.localtime(dt).strftime('%a %d %b, %H:%M')


def student_lines(user, now):
    """The bullet lines of one student's week, or [] if nothing is on."""
    from apps.assessments.models import Assessment
    from apps.learning.models import ModuleMaterial
    from apps.livesessions.audience import visible_sessions
    from apps.tasks.models import TaskAssignment

    person = getattr(user, 'profile', None)
    if person is None:
        return []
    week_end = now + timedelta(days=7)
    modules = list(person.module_enrolments.values_list('programme_module_id', flat=True))
    lines = []

    try:
        from apps.myhub.dashboard import exam_countdown
        exam = exam_countdown(user)
        if exam and exam['days_left'] <= 120:
            lines.append(f"⏳ {exam['days_left']} days to {exam['title']}"
                         + (' (date provisional)' if exam['is_provisional'] else ''))
    except Exception:   # pragma: no cover
        pass

    tasks = (TaskAssignment.objects.filter(user=user, task__due_date__gte=now, task__due_date__lte=week_end)
             .exclude(status__in=('completed', 'submitted')).exclude(task__status='closed')
             .select_related('task')
             .order_by('task__due_date')[:6])
    for ta in tasks:
        lines.append(f'📝 {ta.task.title} — due {_fmt(ta.task.due_date)}')

    if modules:
        tests = (Assessment.objects.filter(module_id__in=modules, status=Assessment.STATUS_OPEN)
                 .filter(Q(available_to__isnull=True) | Q(available_to__gte=now))
                 .exclude(attempts__student=user).order_by('available_to')[:5])
        for a in tests:
            closes = f' — closes {_fmt(a.available_to)}' if a.available_to else ''
            lines.append(f'✅ {a.title} is open{closes}')
        opening = (Assessment.objects.filter(module_id__in=modules, status=Assessment.STATUS_SCHEDULED,
                                             available_from__gte=now, available_from__lte=week_end)
                   .order_by('available_from')[:3])
        for a in opening:
            lines.append(f'🗓 {a.title} opens {_fmt(a.available_from)}')

    sessions = (visible_sessions(user).filter(scheduled_start__gte=now, scheduled_start__lte=week_end)
                .order_by('scheduled_start')[:5])
    for m in sessions:
        lines.append(f'🎥 {m.title} — {_fmt(m.scheduled_start)}')

    if modules:
        fresh = (ModuleMaterial.objects.filter(phase__programme_module_id__in=modules, is_published=True,
                                               created_at__gte=now - timedelta(days=7))
                 .filter(Q(available_from__isnull=True) | Q(available_from__lte=now)).count())
        if fresh:
            lines.append(f'📚 {fresh} new item{"s" if fresh != 1 else ""} of material arrived last week')
    return lines


def educator_lines(user, now):
    """An educator's week: their classes, and the marking waiting for them."""
    from apps.assessments.models import AssessmentAttempt
    from apps.livesessions.audience import visible_sessions

    person = getattr(user, 'profile', None)
    if person is None:
        return []
    week_end = now + timedelta(days=7)
    lines = []
    taught = person.taught_modules.values('pk')
    queue = AssessmentAttempt.objects.filter(assessment__module__in=taught,
                                             status=AssessmentAttempt.STATUS_SUBMITTED).count()
    if queue:
        lines.append(f'🖊 {queue} attempt{"s" if queue != 1 else ""} waiting to be marked')
    sessions = (visible_sessions(user).filter(scheduled_start__gte=now, scheduled_start__lte=week_end)
                .filter(Q(host=user) | Q(module__in=taught)).order_by('scheduled_start')[:6])
    for m in sessions:
        lines.append(f'🎥 {m.title} — {_fmt(m.scheduled_start)}')
    return lines


def run(now=None, *, force=False):
    """Scheduler entry point. Acts on Mondays from 06:00 local time (or ``force``)."""
    from .models import AutoNotice
    from .services import notify

    now = now or timezone.now()
    local = timezone.localtime(now, timezone.get_fixed_timezone(120))     # SAST
    if not force and (local.weekday() != 0 or local.hour < 6):
        return 'not Monday morning'
    year, week, _ = local.isocalendar()
    done = set(AutoNotice.objects.filter(key__startswith=f'weekly:{year}-{week}:')
               .values_list('key', flat=True))

    sent = skipped = 0
    users = (get_user_model().objects.filter(is_active=True, profile__user_type__in=('student', 'educator'))
             .select_related('profile'))
    for user in users.iterator():
        key = f'weekly:{year}-{week}:{user.pk}'
        if key in done:
            continue
        try:
            educator = user.profile.user_type == 'educator'
            lines = educator_lines(user, now) if educator else student_lines(user, now)
        except Exception as exc:   # pragma: no cover - one odd account never stops the rest
            logger.exception('weekly summary failed for user %s', user.pk)
            report('NOTF-9006', exc, context={'user': user.pk, 'kind': 'weekly'})
            continue
        if not lines:
            skipped += 1
            continue
        title = 'Your teaching week ahead' if educator else 'Your week ahead'
        note = notify(user, title=title, body='\n'.join(lines), verb='weekly summary',
                      url='/myhub/', category='weekly', email=True)
        AutoNotice.objects.create(key=key, kind='weekly', title=title, body='\n'.join(lines),
                                  category='weekly', audience={'users': [user.pk]},
                                  sent_at=now, recipient_count=1 if note else 0,
                                  dropped='' if note else 'opted out')
        sent += 1 if note else 0
    return f'weekly summaries: {sent} sent, {skipped} with nothing on'


#: How long without signing in before a student is nudged, and how long before
#: the same student can be nudged again.
QUIET_DAYS = 7
NUDGE_EVERY_DAYS = 14


def run_reengage(now=None):
    """Nudge students who have not signed in for a week but still have work on.

    Only students with something concrete to come back to (a deadline, an open
    test, a class, new material) are nudged, at most once a fortnight. The
    message is the same personal list as the weekly summary, framed as "here is
    where you left off", which gives a reason to return, not a guilt trip.
    """
    from .models import AutoNotice
    from .services import notify

    now = now or timezone.now()
    quiet_since = now - timedelta(days=QUIET_DAYS)
    recent = set(AutoNotice.objects.filter(kind='reengage', sent_at__gte=now - timedelta(days=NUDGE_EVERY_DAYS))
                 .values_list('audience__users__0', flat=True))
    students = (get_user_model().objects
                .filter(is_active=True, profile__user_type='student', last_login__lt=quiet_since,
                        profile__module_enrolments__isnull=False)
                .exclude(pk__in=[r for r in recent if r is not None])
                .select_related('profile').distinct())
    sent = 0
    for user in students.iterator():
        try:
            lines = student_lines(user, now)
        except Exception as exc:   # pragma: no cover
            logger.exception('re-engagement failed for user %s', user.pk)
            report('NOTF-9006', exc, context={'user': user.pk, 'kind': 're-engagement'})
            continue
        if not lines:
            continue
        days = (now - user.last_login).days
        note = notify(user, title=f"It's been {days} days. Here's where you left off",
                      body='\n'.join(lines), verb='re-engagement', url='/myhub/',
                      category='weekly', email=True)
        AutoNotice.objects.create(key=f'reengage:{user.pk}:{now:%Y%m%d}', kind='reengage',
                                  title='Re-engagement', category='weekly',
                                  audience={'users': [user.pk]}, sent_at=now,
                                  recipient_count=1 if note else 0)
        sent += 1 if note else 0
    return f're-engagement nudges: {sent}'
