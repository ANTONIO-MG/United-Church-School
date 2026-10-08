"""Creating, updating and cancelling a live session — everything in one place.

Scheduling a session is not one action, it is eight, and they have to happen in
an order that survives any of them failing:

1. create the Teams meeting (or fall back to the in-app room),
2. record who it is for,
3. open the attendance register,
4. draw the thumbnail,
5. put it on the organiser's Outlook calendar and invite the staff,
6. file it on the module's schedule as an upcoming session,
7. tell the audience,
8. open the pipeline row that will collect the recording afterwards.

Only (1) can fail in a way that changes what the session *is*; everything after
it is best-effort and logged, because a session that exists with no thumbnail is
fine and a session that could not be created because a thumbnail failed is not.
"""

import logging

from django.utils import timezone

logger = logging.getLogger('apps')


def create_session(*, host, title, start, end, audience, description='', session_kind='class',
                   institution=None, programme=None, cohort=None, module=None, week=None,
                   calendar_event=None, invitees=(), record=None, publish_recording=None,
                   group=None, notify=True):
    """Schedule a live session and return the :class:`MeetingRoom`.

    ``invitees`` is an iterable of ``User`` objects invited by name — required
    for a private/one-on-one session, optional (and additive) for the rest.
    """
    from apps.communication.models import MeetingParticipant, MeetingRoom
    from apps.msteams import services as teams
    from .models import LiveSessionSettings

    conf = LiveSessionSettings.load()
    record = conf.auto_record if record is None else bool(record)
    publish = conf.publish_recordings if publish_recording is None else bool(publish_recording)

    meeting = teams.create_class_meeting(
        host=host, title=title, start=start, end=end, module=module, group=group,
        description=description, record=record,
    )

    meeting.audience = audience
    meeting.session_kind = session_kind
    meeting.institution = institution
    meeting.programme = programme
    meeting.cohort = cohort
    meeting.week = week
    meeting.calendar_event = calendar_event
    meeting.record_automatically = record
    meeting.publish_recording = publish
    meeting.save(update_fields=[
        'audience', 'session_kind', 'institution', 'programme', 'cohort', 'week',
        'calendar_event', 'record_automatically', 'publish_recording', 'updated_at'])

    MeetingParticipant.objects.get_or_create(
        meeting=meeting, user=host, defaults={'role': 'host', 'rsvp': 'yes'})
    for user in invitees or ():
        if user and user.pk != getattr(host, 'pk', None):
            MeetingParticipant.objects.get_or_create(meeting=meeting, user=user)

    ensure_class_session(meeting)
    ensure_thumbnail(meeting, conf=conf)
    ensure_calendar_event(meeting, conf=conf)
    publish_upcoming_to_schedule(meeting)
    open_pipeline(meeting)

    if notify:
        try:
            from .reminders import announce_new_session
            announce_new_session(meeting)
        except Exception:
            logger.exception('livesessions: could not announce %s', meeting)
    return meeting


def update_session(meeting, *, fields=None, reschedule=False):
    """Persist edits and push the ones Microsoft needs to know about.

    ``reschedule`` re-sends the times to Graph. It is a separate flag rather than
    an inference, because changing a title should not risk bouncing a meeting
    that people already have in their calendars.
    """
    from apps.msteams import graph

    if fields:
        meeting.save(update_fields=list(fields) + ['updated_at'])
    else:
        meeting.save()

    if meeting.is_teams and meeting.teams_meeting_id and meeting.organizer_upn:
        payload = {'subject': meeting.title}
        if reschedule and meeting.scheduled_start:
            payload['startDateTime'] = _iso(meeting.scheduled_start)
            if meeting.scheduled_end:
                payload['endDateTime'] = _iso(meeting.scheduled_end)
        graph.update_online_meeting(meeting.organizer_upn, meeting.teams_meeting_id, **payload)

        if meeting.teams_calendar_event_id and reschedule and meeting.scheduled_start:
            graph.update_calendar_event(
                meeting.organizer_upn, meeting.teams_calendar_event_id,
                subject=meeting.title,
                start={'dateTime': _iso(meeting.scheduled_start), 'timeZone': 'UTC'},
                end={'dateTime': _iso(meeting.scheduled_end or meeting.scheduled_start),
                     'timeZone': 'UTC'},
            )

    ensure_thumbnail(meeting, force=True)
    publish_upcoming_to_schedule(meeting)
    return meeting


def cancel_session(meeting, *, by=None, reason=''):
    """Cancel a session: tear down the Microsoft side and tell the audience."""
    from apps.communication import services as comm
    from apps.msteams import graph
    from .audience import recipients_for

    if meeting.is_teams and meeting.organizer_upn:
        if meeting.teams_calendar_event_id:
            graph.delete_calendar_event(meeting.organizer_upn, meeting.teams_calendar_event_id)
        if meeting.teams_meeting_id:
            graph.delete_online_meeting(meeting.organizer_upn, meeting.teams_meeting_id)

    meeting.is_active = False
    meeting.save(update_fields=['is_active', 'updated_at'])

    body = f'“{meeting.title}” has been cancelled.'
    if reason:
        body += f' {reason}'
    for user in recipients_for(meeting).iterator():
        comm.notify(user, actor=by, category='meetings', level='warning',
                    verb='session cancelled', title=f'Cancelled: {meeting.title}',
                    body=body, meeting=meeting, email=True)
    return meeting


# ---------------------------------------------------------------------------
# The steps
# ---------------------------------------------------------------------------
def ensure_class_session(meeting):
    """Open the attendance register for a module session.

    Only module sessions get one: a platform-wide briefing has no roster to take
    a register against, and creating an empty one would put a meaningless 0%
    attendance row on everybody's record.
    """
    from apps.communication.models import ClassSession

    if not meeting.module_id or getattr(meeting, 'class_session', None) is not None:
        return None
    start = meeting.scheduled_start or timezone.now()
    session, _ = ClassSession.objects.get_or_create(
        meeting=meeting,
        defaults={
            'module': meeting.module,
            'title': meeting.title,
            'session_date': timezone.localtime(start).date(),
            'starts_at': meeting.scheduled_start,
            'ends_at': meeting.scheduled_end,
            'created_by': meeting.host,
        },
    )
    return session


def ensure_thumbnail(meeting, *, conf=None, force=False):
    """Draw and store the session card. Returns True if one was written."""
    from django.core.files.base import ContentFile
    from . import thumbnails

    if meeting.thumbnail and not force:
        return False
    blob = thumbnails.render(meeting, conf=conf)
    if not blob:
        return False
    try:
        meeting.thumbnail.save(thumbnails.filename_for(meeting), ContentFile(blob), save=True)
        return True
    except Exception:
        logger.exception('livesessions: could not save the thumbnail for %s', meeting)
        return False


def ensure_calendar_event(meeting, *, conf=None):
    """Put the session on the organiser's Outlook calendar and invite the staff.

    Only licensed people go on the Microsoft invite — see
    :func:`apps.msteams.graph.create_calendar_event` for why students must not.
    """
    from apps.msteams import graph, services as teams
    from .models import LiveSessionSettings

    conf = conf or LiveSessionSettings.load()
    if not conf.create_calendar_events or not meeting.is_teams or meeting.teams_calendar_event_id:
        return None
    if not meeting.organizer_upn or not meeting.scheduled_start:
        return None

    attendees = []
    for participant in meeting.participants.exclude(user=meeting.host).select_related('user'):
        user = participant.user
        if user is None or not teams.host_can_use_teams(user):
            continue
        upn = teams.organizer_upn_for(user)
        if upn:
            attendees.append((upn, user.get_full_name() or user.get_username()))

    event = graph.create_calendar_event(
        meeting.organizer_upn,
        subject=meeting.title,
        start_iso=_iso(meeting.scheduled_start),
        end_iso=_iso(meeting.scheduled_end or meeting.scheduled_start),
        body_html=_event_body(meeting),
        attendees=attendees,
        join_url=meeting.teams_join_url,
    )
    if event and event.get('id'):
        meeting.teams_calendar_event_id = event['id']
        meeting.save(update_fields=['teams_calendar_event_id', 'updated_at'])
        return event
    return None


def publish_upcoming_to_schedule(meeting):
    """Show the session on the module's schedule before it happens.

    The same :class:`~apps.learning.models.ModuleMaterial` row is later switched
    to a recording by the pipeline, so a student watching the schedule sees one
    item change from "live session" to "recording" rather than two appearing.
    """
    if not meeting.module_id:
        return None
    from apps.learning.models import ModuleMaterial
    from .pipeline import phase_for

    phase = phase_for(meeting)
    if phase is None:
        return None
    material, _ = ModuleMaterial.objects.update_or_create(
        phase=phase, kind=ModuleMaterial.KIND_LIVE, meeting=meeting,
        defaults={
            'week': meeting.week if meeting.week_id and meeting.week.phase_id == phase.pk else None,
            'title': meeting.title,
            'description': meeting.description or '',
            'url': '',
        },
    )
    return material


def open_pipeline(meeting):
    """Create the after-class pipeline row up front, in ``waiting``."""
    from .models import SessionArtifact
    if not meeting.is_teams:
        return None
    artifact, _ = SessionArtifact.objects.get_or_create(
        meeting=meeting, defaults={'state': SessionArtifact.STATE_WAITING})
    return artifact


# ---------------------------------------------------------------------------
# Free/busy — "when can I actually book this?"
# ---------------------------------------------------------------------------
def busy_blocks(day, *, hosts=None):
    """Every session on ``day``, as ``(start, end, meeting)``, in order.

    This is what the calendar's free-slot strip is drawn from. It deliberately
    ignores audience: a slot is occupied whether or not the person looking is
    allowed to see what occupies it.
    """
    from datetime import datetime, time
    from apps.communication.models import MeetingRoom

    start = timezone.make_aware(datetime.combine(day, time.min), timezone.get_current_timezone())
    end = start + timezone.timedelta(days=1)
    qs = (MeetingRoom.objects
          .filter(is_active=True, scheduled_start__lt=end, scheduled_end__gt=start)
          .select_related('host', 'module'))
    if hosts:
        qs = qs.filter(host__in=hosts)
    return [(m.scheduled_start, m.scheduled_end, m) for m in qs.order_by('scheduled_start')]


def free_slots(day, *, hosts=None, open_from=8, open_to=20, minimum_minutes=30,
               for_user=None):
    """The gaps on ``day`` that are long enough to hold a session.

    Returns ``(start, end)`` pairs between ``open_from`` and ``open_to`` local
    time. Overlapping sessions are merged first, so two classes running at once
    do not produce a phantom gap between them.

    ``for_user`` also subtracts that person's *own* connected calendar — the
    lecture already in their Google diary is real busy time, and a free-slot
    finder that cannot see it will happily book straight over it.
    """
    from datetime import datetime, time

    tz = timezone.get_current_timezone()
    window_start = timezone.make_aware(datetime.combine(day, time(hour=open_from)), tz)
    window_end = timezone.make_aware(datetime.combine(day, time(hour=open_to)), tz)

    spans = [(start, end or start + timezone.timedelta(hours=1))
             for start, end, _meeting in busy_blocks(day, hosts=hosts) if start]
    if for_user is not None:
        from . import sources
        spans += sources.busy_spans(for_user, window_start, window_end)

    blocks = [(max(start, window_start), min(end, window_end)) for start, end in spans]
    blocks = [b for b in blocks if b[1] > b[0]]
    blocks.sort()

    merged = []
    for start, end in blocks:
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))

    gaps, cursor = [], window_start
    for start, end in merged:
        if (start - cursor).total_seconds() >= minimum_minutes * 60:
            gaps.append((cursor, start))
        cursor = max(cursor, end)
    if (window_end - cursor).total_seconds() >= minimum_minutes * 60:
        gaps.append((cursor, window_end))
    return gaps


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def _iso(moment):
    if timezone.is_naive(moment):
        moment = timezone.make_aware(moment, timezone.get_current_timezone())
    return moment.isoformat()


def _event_body(meeting):
    from django.conf import settings as django_settings
    site = (getattr(django_settings, 'SITE_URL', '') or '').rstrip('/')
    link = f'{site}{meeting.get_join_url()}' if site else meeting.get_join_url()
    rows = [f'<p>{meeting.description}</p>' if meeting.description else '',
            f'<p><strong>Audience:</strong> {meeting.audience_label}</p>',
            f'<p><a href="{link}">Open this session on United Church School</a></p>']
    return ''.join(r for r in rows if r)
