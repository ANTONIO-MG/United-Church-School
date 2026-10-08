"""Everything that lands on a calendar, from every app, in one shape.

The platform grew two calendars. ``myhub.events_feed`` aggregated the practice
diary, the academic dates, task deadlines, lessons, assessments and meetings into
a FullCalendar feed; the live-session work then added a month grid of its own that
knew only about sessions and academic dates. Two aggregations meant two answers
to "what is on my calendar this week", and only one of them knew about audience
scoping.

So there is now one aggregation — this module — and both surfaces render from it.
A source is added here once and appears everywhere: the month grid, the day view,
the events page, the JSON feed and the exported ``.ics``.

Every entry is a :class:`CalendarEntry`, which is deliberately flat and dumb: a
title, a span, a kind, a colour and a link. Sources do their own permission
scoping *before* returning — the live-session source defers to
:mod:`apps.livesessions.audience`, the academic source to the reader's
institutions, personal reminders to their owner — so a caller can render whatever
it is handed without re-checking anything.
"""

import logging
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta

from django.urls import reverse
from django.utils import timezone

logger = logging.getLogger('apps')


# ---------------------------------------------------------------------------
# The shape
# ---------------------------------------------------------------------------
#: Every source, with the label, colour and icon it draws in. Ordered as they
#: should appear in a legend: what you attend, then what you owe, then context.
KINDS = {
    'session':   ('Live session', '#20c997', 'camera-video'),
    'assessment': ('Assessment',  '#dc3545', 'ui-checks'),
    'academic':  ('Academic date', '#C00000', 'mortarboard'),
    'task':      ('Task',         '#198754', 'check2-square'),
    'lesson':    ('Lesson',       '#0dcaf0', 'journal-richtext'),
    'event':     ('Event',        '#3a87ad', 'calendar-event'),
    'reminder':  ('Reminder',     '#6f42c1', 'bell'),
    'external':  ('From your calendar', '#8E8E93', 'calendar2-week'),
}


@dataclass
class CalendarEntry:
    """One dated thing, from any app, ready to render."""

    title: str
    start: datetime
    kind: str = 'event'
    end: datetime = None
    all_day: bool = False
    url: str = ''
    location: str = ''
    detail: str = ''
    colour: str = ''
    uid: str = ''
    #: True when this blocks out time for the free-slot finder.
    busy: bool = False
    meta: dict = field(default_factory=dict)

    def __post_init__(self):
        label, colour, icon = KINDS.get(self.kind, KINDS['event'])
        self.colour = self.colour or colour
        self.meta.setdefault('label', label)
        self.meta.setdefault('icon', icon)

    @property
    def label(self):
        return self.meta.get('label', '')

    @property
    def icon(self):
        return self.meta.get('icon', 'calendar-event')

    @property
    def local_start(self):
        return timezone.localtime(self.start) if self.start else None

    @property
    def is_past(self):
        return bool(self.start and self.start < timezone.now())


# ---------------------------------------------------------------------------
# The aggregate
# ---------------------------------------------------------------------------
#: Source name → the callable that produces its entries.
def entries_for(user, start, end, *, kinds=None, limit_per_source=500):
    """Every calendar entry ``user`` may see between ``start`` and ``end``.

    ``kinds`` optionally restricts which sources run — the exported ``.ics``
    uses it to leave out the events it imported in the first place, which would
    otherwise loop straight back into the calendar they came from.
    """
    wanted = set(kinds) if kinds else set(KINDS)
    collected = []

    for name, source in (
        ('session', _sessions),
        ('academic', _academic_dates),
        ('event', _events),
        ('task', _tasks),
        ('lesson', _lessons),
        ('assessment', _assessments),
        ('external', _external),
    ):
        if name not in wanted:
            continue
        try:
            collected.extend(source(user, start, end, limit_per_source) or [])
        except Exception:       # one broken source must never blank the calendar
            logger.exception('calendar: source %r failed', name)

    collected.sort(key=lambda entry: (entry.start or timezone.now()))
    return collected


def group_by_day(entries):
    """``{date: [entry, ...]}`` in the reader's own time zone."""
    grouped = {}
    for entry in entries:
        if not entry.start:
            continue
        grouped.setdefault(timezone.localtime(entry.start).date(), []).append(entry)
    return grouped


def busy_spans(user, start, end):
    """``(start, end)`` pairs for everything that occupies ``user``'s time.

    Used by the free-slot finder. Only genuinely blocking entries count — an
    assessment closing date is a deadline, not a meeting, and an imported event
    marked *free* by its own calendar is not busy either.
    """
    spans = []
    for entry in entries_for(user, start, end, kinds=('session', 'external')):
        if not entry.busy or not entry.start:
            continue
        spans.append((entry.start, entry.end or entry.start + timedelta(hours=1)))
    return spans


# ---------------------------------------------------------------------------
# Sources
# ---------------------------------------------------------------------------
def _sessions(user, start, end, limit):
    """Live sessions, scoped by :mod:`apps.livesessions.audience`.

    This is the source the old myhub feed got wrong: it showed only sessions the
    user hosted or was individually invited to, so a module class never appeared
    on the calendar of the students it was for.
    """
    from .audience import visible_sessions

    entries = []
    query = (visible_sessions(user)
             .filter(scheduled_start__gte=start, scheduled_start__lte=end)
             .select_related('module', 'host', 'artifact')
             .order_by('scheduled_start')[:limit])
    for meeting in query:
        entries.append(CalendarEntry(
            kind='session',
            title=meeting.title,
            start=meeting.scheduled_start,
            end=meeting.scheduled_end,
            url=meeting.get_absolute_url(),
            detail=meeting.audience_label,
            uid=f'session-{meeting.pk}@ucs-lms',
            busy=True,
            meta={'live': meeting.is_live_now,
                  'module': meeting.module.label if meeting.module_id else '',
                  'watchable': bool(getattr(meeting, 'artifact', None)
                                    and meeting.artifact.is_watchable)},
        ))
    return entries


def _academic_dates(user, start, end, limit):
    """The institution's published dates — tests, exams, deadlines, holidays."""
    from apps.learning.models import CalendarEvent
    from core.roles import role_of_user

    query = (CalendarEvent.objects
             .filter(start__gte=start, start__lte=end)
             .select_related('calendar__institution', 'programme', 'programme_module'))

    person = getattr(user, 'profile', None)
    if role_of_user(user) not in ('admin', 'staff'):
        query = query.filter(is_published=True)
        # Scoped to the institutions they are actually registered with, so a
        # learner is not shown another school's exam timetable. Someone with no
        # enrolment yet sees every published date rather than a blank calendar.
        institution_ids = list(person.programme_enrolments
                               .values_list('programme__institution_id', flat=True)) if person else []
        if institution_ids:
            query = query.filter(calendar__institution_id__in=institution_ids)

    return [CalendarEntry(
        kind='academic',
        title=f'{event.get_kind_display()} · {event.label}',
        start=event.start,
        end=event.end,
        all_day=event.all_day,
        colour=event.colour,
        detail=event.description,
        location=event.location,
        uid=f'academic-{event.pk}@ucs-lms',
    ) for event in query.order_by('start')[:limit]]


def _events(user, start, end, limit):
    """The practice's own diary and the reader's personal reminders."""
    from django.db.models import Q

    from apps.myhub.models import Event

    if not getattr(user, 'is_authenticated', False):
        query = Event.objects.filter(owner__isnull=True)
    else:
        query = Event.objects.filter(Q(owner__isnull=True) | Q(owner=user))

    entries = []
    for event in query.filter(start__gte=start, start__lte=end).order_by('start')[:limit]:
        is_reminder = event.category == Event.CATEGORY_REMINDER
        entries.append(CalendarEntry(
            kind='reminder' if is_reminder else 'event',
            title=event.title,
            start=event.start,
            end=event.end,
            all_day=event.all_day,
            location=event.location,
            detail=event.description,
            colour='' if is_reminder else (event.color or ''),
            url=reverse('myhub:event-detail', args=[event.pk]),
            uid=f'event-{event.pk}@ucs-lms',
            busy=not is_reminder,
        ))
    return entries


def _tasks(user, start, end, limit):
    """Task deadlines, styled and linked as whatever the task delivers."""
    if not getattr(user, 'is_authenticated', False):
        return []
    from apps.tasks.models import TaskAssignment

    query = (TaskAssignment.objects
             .filter(user=user, task__due_date__gte=start, task__due_date__lte=end)
             .exclude(status=TaskAssignment.STATUS_COMPLETED)
             .select_related('task')
             .order_by('task__due_date')[:limit])
    return [CalendarEntry(
        kind='task',
        title=assignment.task.title,
        start=assignment.task.due_date,
        url=assignment.task.get_absolute_url(),
        detail='Due',
        uid=f'task-{assignment.task_id}@ucs-lms',
    ) for assignment in query]


def _lessons(user, start, end, limit):
    """Lessons publishing inside the window, for the reader's own modules."""
    person = getattr(user, 'profile', None)
    if person is None:
        return []
    from apps.learning.models import Lesson

    module_ids = list(person.module_enrolments.values_list('programme_module_id', flat=True))
    if not module_ids:
        return []
    query = (Lesson.objects
             .filter(module_id__in=module_ids, publish_at__gte=start, publish_at__lte=end)
             .order_by('publish_at')[:limit])
    return [CalendarEntry(
        kind='lesson',
        title=lesson.title,
        start=lesson.publish_at,
        url=lesson.get_absolute_url(),
        detail='Lesson released',
        uid=f'lesson-{lesson.pk}@ucs-lms',
    ) for lesson in query]


def _assessments(user, start, end, limit):
    """Assessment closing dates for the reader's own modules."""
    person = getattr(user, 'profile', None)
    if person is None:
        return []
    from apps.assessments.models import Assessment

    module_ids = list(person.module_enrolments.values_list('programme_module_id', flat=True))
    if not module_ids:
        return []
    query = (Assessment.objects
             .filter(module_id__in=module_ids, available_to__gte=start, available_to__lte=end)
             .order_by('available_to')[:limit])

    entries = []
    for assessment in query:
        try:
            url = reverse('assessments:take', args=[assessment.pk])
        except Exception:
            url = ''
        entries.append(CalendarEntry(
            kind='assessment',
            title=assessment.title,
            start=assessment.available_to,
            url=url,
            detail='Closes',
            uid=f'assessment-{assessment.pk}@ucs-lms',
        ))
    return entries


def _external(user, start, end, limit):
    """Events imported from the reader's own Google / Outlook / Apple calendar."""
    if not getattr(user, 'is_authenticated', False):
        return []
    from .models import ExternalEvent

    query = (ExternalEvent.objects
             .filter(subscription__user=user, subscription__is_active=True,
                     start__gte=start, start__lte=end)
             .select_related('subscription')
             .order_by('start')[:limit])
    return [CalendarEntry(
        kind='external',
        title=event.title,
        start=event.start,
        end=event.end,
        all_day=event.all_day,
        location=event.location,
        colour=event.subscription.colour,
        detail=event.subscription.name,
        uid=f'ext-{event.pk}@ucs-lms',
        busy=bool(event.busy and event.subscription.blocks_time),
    ) for event in query]


# ---------------------------------------------------------------------------
# Adapters for the surfaces that had their own shapes
# ---------------------------------------------------------------------------
def as_fullcalendar(entries):
    """FullCalendar's JSON shape, as ``myhub:events-feed`` has always returned."""
    return [{
        'title': f'{_emoji(entry.kind)} {entry.title}'.strip(),
        'start': entry.start.isoformat() if entry.start else None,
        'end': entry.end.isoformat() if entry.end else None,
        'allDay': entry.all_day,
        'color': entry.colour,
        'url': entry.url,
    } for entry in entries if entry.start]


def as_items(entries):
    """The dict shape ``myhub:events`` renders its list from."""
    return [{
        'title': entry.title,
        'when': entry.start,
        'category': entry.label,
        'color': entry.colour,
        'icon': entry.icon,
        'url': entry.url,
        'location': entry.location,
        'detail_url': entry.url,
    } for entry in entries if entry.start]


_EMOJI = {'session': '🎥', 'academic': '🎓', 'task': '✅', 'lesson': '📘',
          'assessment': '📝', 'reminder': '🔔', 'event': '', 'external': '🗓'}


def _emoji(kind):
    return _EMOJI.get(kind, '')


def window_around(anchor=None, *, before=30, after=180):
    """A sensible default window: a month back, six months on."""
    anchor = anchor or timezone.now()
    if isinstance(anchor, date) and not isinstance(anchor, datetime):
        anchor = timezone.make_aware(datetime.combine(anchor, datetime.min.time()),
                                     timezone.get_current_timezone())
    return anchor - timedelta(days=before), anchor + timedelta(days=after)
