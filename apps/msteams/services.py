"""High-level Teams live-classroom operations, called from the LMS.

This is the seam the rest of the app uses — views never touch Graph directly.
Everything degrades gracefully: when Teams isn't configured, meeting creation
falls back to the in-app (Jitsi) room so nothing breaks.
"""

import logging

from django.conf import settings
from django.utils import timezone

from . import graph

logger = logging.getLogger('apps')


def teams_active():
    """True when Teams is the selected provider AND Graph is configured."""
    return getattr(settings, 'MEETING_PROVIDER', 'teams') == 'teams' and graph.is_configured()


def host_can_use_teams(user):
    """Only admins / staff / educators host on Microsoft Teams (with their MS
    credentials). Students — including student↔student and small student group
    calls — always use Jitsi."""
    if user is None or not getattr(user, 'is_authenticated', False):
        return False
    if user.is_staff or user.is_superuser:
        return True
    prof = getattr(user, 'profile', None)
    return bool(prof and prof.user_type in ('admin', 'staff', 'educator'))


def should_use_teams(host):
    """Route by initiator: staff/educator/admin → Teams (when active); else Jitsi."""
    return teams_active() and host_can_use_teams(host)


def organizer_upn_for(user):
    """The Microsoft UPN that should own meetings for ``user``.

    Order: an explicit per-profile override (``profile.ms_upn`` if present) →
    the account e-mail → the configured default organizer. Returns '' if none.
    """
    if user is not None:
        prof = getattr(user, 'profile', None)
        upn = getattr(prof, 'ms_upn', '') if prof else ''
        if upn:
            return upn
        if getattr(user, 'email', ''):
            return user.email
    return getattr(settings, 'MS_GRAPH_DEFAULT_ORGANIZER', '') or ''


def create_class_meeting(*, host, title, start=None, end=None, module=None, group=None,
                         description='', record=True):
    """Create a live class session and return its :class:`MeetingRoom`.

    Uses Microsoft Teams when active (organiser = the host's licensed account);
    otherwise falls back to the in-app Jitsi room. The room is auto-linked to
    ``module``/``group`` so it surfaces on the right course/module.
    """
    from apps.communication.models import MeetingRoom

    start = start or timezone.now()
    room = MeetingRoom(
        title=title or 'Live session',
        description=description or '',
        host=host,
        group=group,
        module=module,
        scheduled_start=start,
        scheduled_end=end,
        requires_login=False,   # students join anonymously via the link
    )

    if should_use_teams(host):
        organizer = organizer_upn_for(host)
        if organizer:
            created = graph.create_online_meeting(
                organizer,
                subject=title or 'Live session',
                start_iso=_iso(start),
                end_iso=_iso(end or start + timezone.timedelta(hours=1)),
                allow_recording=record,
            )
            if created:
                room.provider = MeetingRoom.PROVIDER_TEAMS
                room.organizer_upn = organizer
                room.teams_meeting_id = created['id']
                room.teams_join_url = created['join_url']
            else:
                logger.warning('msteams: Graph meeting creation failed; falling back to in-app room')
                room.provider = MeetingRoom.PROVIDER_JITSI
        else:
            logger.warning('msteams: no organiser UPN for %s; falling back to in-app room', host)
            room.provider = MeetingRoom.PROVIDER_JITSI
    else:
        room.provider = MeetingRoom.PROVIDER_JITSI

    room.save()
    return room


def _iso(dt):
    """Graph wants an ISO-8601 timestamp with an offset."""
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt, timezone.get_current_timezone())
    return dt.isoformat()


# ---------------------------------------------------------------------------
# After-class sync: transcript → recap, recording, attendance
# ---------------------------------------------------------------------------
def sync_meeting(meeting, *, use_claude=False, force=False):
    """Pull a finished Teams meeting's artifacts and file them into the LMS.

    Fetches the transcript (→ recap), the recording URL and the attendance
    report; stores the recap as an :class:`AiReport` linked to the meeting, posts
    it to the class feed, and reconciles attendance. Idempotent — skips meetings
    already synced unless ``force``. Returns True if it did work.
    """
    from . import graph, recap as recap_mod

    if not meeting.is_teams or not meeting.teams_meeting_id or not meeting.organizer_upn:
        return False
    if meeting.artifacts_synced_at and not force:
        return False
    if not graph.is_configured():
        return False

    organizer, mid = meeting.organizer_upn, meeting.teams_meeting_id
    updated = []

    # 1) Recording URL (content lives in the organiser's OneDrive/SharePoint).
    recs = graph.list_recordings(organizer, mid)
    if recs:
        url = recs[0].get('recordingContentUrl') or recs[0].get('@microsoft.graph.downloadUrl') or ''
        if url:
            meeting.recording_url = url
            updated.append('recording_url')

    # 2) Transcript → recap.
    cues = []
    for tr in graph.list_transcripts(organizer, mid):
        content = graph.get_transcript_content(organizer, mid, tr.get('id'))
        cues += recap_mod.parse_vtt(content)
    if cues:
        data = (recap_mod.claude_recap if use_claude else recap_mod.extractive_recap)(
            cues, title=meeting.title)
        _file_recap(meeting, data, recap_mod.to_markdown(data, title=meeting.title))

    # 3) Attendance report → reconcile into the ClassSession.
    _reconcile_attendance(meeting, organizer, mid, graph)

    meeting.artifacts_synced_at = timezone.now()
    updated.append('artifacts_synced_at')
    meeting.save(update_fields=updated)
    return True


def _file_recap(meeting, data, markdown):
    """Store the recap as an AiReport + post it to the module's class feed."""
    try:
        from apps.ai_assistant.models import AiReport
        AiReport.objects.update_or_create(
            linked_ref=f'meeting:{meeting.pk}',
            defaults={
                'kind': AiReport.KIND_MEETING_RECAP,
                'title': f'Class recap — {meeting.title}',
                'module': meeting.module,
                'created_by': meeting.host,
                'content': markdown,
                'data': {k: data.get(k) for k in
                         ('key_points', 'action_items', 'decisions', 'questions', 'timeline', 'speakers')},
                'used_llm': data.get('engine') == 'claude',
                'status': AiReport.STATUS_FINAL,
            },
        )
    except Exception:  # pragma: no cover
        logger.exception('msteams: could not file recap')

    # Post to the class feed (a Discussion on the module) so students see it.
    if meeting.module_id:
        try:
            from apps.communication.models import Discussion
            Discussion.objects.get_or_create(
                title=f'Class recap — {meeting.title}',
                module=meeting.module,
                defaults={'author': meeting.host, 'body': markdown[:4000],
                          'course': getattr(meeting.module, 'course', None)},
            )
        except Exception:  # pragma: no cover
            logger.exception('msteams: could not post recap to the feed')


def _parse_graph_dt(value):
    """Parse a Graph ISO-8601 timestamp into an aware datetime (None on junk)."""
    if not value:
        return None
    from datetime import datetime, timezone as dt_timezone
    try:
        # Graph returns "…Z"; fromisoformat only learned to accept that in 3.11.
        parsed = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    except (TypeError, ValueError):
        return None
    if timezone.is_naive(parsed):
        # Graph timestamps are UTC. (django.utils.timezone.utc was removed in 5.0.)
        parsed = parsed.replace(tzinfo=dt_timezone.utc)
    return parsed


def _graph_attendance_rows(organizer, mid, graph):
    """Flatten every attendance report for a meeting into one entry per attendee.

    Teams files a **separate report per session** — if the organiser stops and
    restarts the meeting, or it recurs, a participant appears in more than one.
    Their seconds are summed and the earliest join kept, so someone who drops
    and rejoins is credited for all their time rather than only the last stretch.

    Returns a list of ``{'record', 'seconds', 'first_join'}``. The raw Graph
    record is carried through because identity resolution needs the display name
    as well as the address — see :mod:`apps.livesessions.identity`.
    """
    from apps.livesessions import identity as ident

    merged = {}
    for report in graph.list_attendance_reports(organizer, mid):
        for record in graph.get_attendance_records(organizer, mid, report.get('id')):
            seconds = int(record.get('totalAttendanceInSeconds') or 0)
            if seconds <= 0:
                continue
            first_join = None
            for interval in (record.get('attendanceIntervals') or []):
                joined = _parse_graph_dt(interval.get('joinDateTime'))
                if joined and (first_join is None or joined < first_join):
                    first_join = joined

            # One attendee may be reported under several spellings across
            # reports; the strongest key they offer is what merges them.
            keys = ident.keys_for_record(record)
            key = keys[0] if keys else ident.label_for_record(record).casefold()

            bucket = merged.setdefault(key, {'record': record, 'seconds': 0, 'first_join': None})
            bucket['seconds'] += seconds
            if first_join and (bucket['first_join'] is None or first_join < bucket['first_join']):
                bucket['first_join'] = first_join
    return list(merged.values())


def _reconcile_attendance(meeting, organizer, mid, graph):
    """Reconcile the class register against the Graph attendance report.

    Graph is **authoritative for time**: it reports exactly how long each person
    was in the call, whereas the platform's own heartbeat can only see how long
    the launch page stayed open. So the reported seconds replace the accrued
    ones, and the status is then re-derived against the session's
    ``min_attendance_pct`` — attending 12 minutes of a 60-minute class does not
    become "present" just because Graph saw the person.

    Graph is **not** authoritative for identity. Students join anonymously, so an
    attendance record carries whatever they typed into Teams' name box. Resolving
    that is :mod:`apps.livesessions.identity`'s job: it matches against a roster
    bounded by the session's own audience and by everyone who clicked through
    from the platform, trying e-mail, then Microsoft UPN, then a remembered alias, then
    the name — and refusing anything ambiguous rather than guessing.

    Whatever it cannot resolve is left on the session for an educator to attach
    to an account, and that answer is remembered for every future session.
    Manual educator marks are never overwritten.
    """
    session = getattr(meeting, 'class_session', None)
    if session is None:
        return 0

    from apps.communication import services as comm
    from apps.communication.models import Attendance
    from apps.livesessions import identity as ident
    from apps.livesessions.models import SessionJoin

    rows = _graph_attendance_rows(organizer, mid, graph)
    if not rows:
        return 0

    index, ambiguous = ident.build_index(meeting)
    joins = {j.user_id: j for j in SessionJoin.objects.filter(meeting=meeting)}

    applied, unresolved = 0, []
    for row in rows:
        user, key = ident.resolve(row['record'], index)
        if user is None:
            unresolved.append({
                'label': ident.label_for_record(row['record']),
                'seconds': row['seconds'],
                'keys': ident.keys_for_record(row['record']),
            })
            continue

        comm.apply_measured_attendance(
            session, user, seconds=row['seconds'], first_seen=row['first_join'],
            source=Attendance.SOURCE_TEAMS, authoritative=True)
        applied += 1

        join = joins.get(user.pk)
        if join is not None:
            join.matched_identity = key
            join.matched_seconds = row['seconds']
            join.save(update_fields=['matched_identity', 'matched_seconds'])

    _store_unresolved(meeting, unresolved)

    if ambiguous:
        logger.info('msteams: %s — %s name(s) were ambiguous within the roster and left unmatched',
                    meeting, len(ambiguous))
    logger.info('msteams: reconciled attendance for %s — %s of %s reported attendees matched',
                meeting, applied, len(rows))
    return applied


def _store_unresolved(meeting, unresolved):
    """Park the attendees we could not name, for the educator to resolve.

    Kept on the session's pipeline row rather than raised as an error: an
    unmatched attendee is a normal, expected outcome of anonymous joining, not a
    failure. The register is still correct for everyone it did match.
    """
    try:
        from apps.livesessions.models import SessionArtifact
        artifact, _ = SessionArtifact.objects.get_or_create(meeting=meeting)
        artifact.unresolved_attendees = unresolved
        artifact.save(update_fields=['unresolved_attendees', 'updated_at'])
    except Exception:   # pragma: no cover - never let bookkeeping break the sync
        logger.exception('msteams: could not store the unresolved attendees for %s', meeting)
