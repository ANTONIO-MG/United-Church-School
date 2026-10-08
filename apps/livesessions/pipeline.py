"""The after-class chain: finished meeting → filed, summarised, playable session.

Run by the ``run_session_pipeline`` job every few minutes. Each tick advances
every non-terminal :class:`~apps.livesessions.models.SessionArtifact` by **one**
step and stops. That shape is deliberate:

* Teams publishes a recording somewhere between two minutes and several hours
  after a call ends, so step 2 is a poll, not a wait.
* A YouTube upload may have to sit until tomorrow's quota, so step 5 has to be
  resumable across days.
* Any step can fail transiently. Storing the state means a failure parks one
  session and the other forty carry on.

The states, in order::

    waiting → polling → filing → summarising → uploading → published
                  ↘ skipped (nothing was recorded / publishing is off)
                  ↘ failed  (same step failed MAX_ATTEMPTS times)

Students are never blocked on the end of the chain: as soon as ``filing`` puts an
anonymous OneDrive link on the record the session is watchable, and the YouTube
id simply replaces it later.
"""

import logging

from django.utils import timezone

from apps.msteams import graph, onedrive

logger = logging.getLogger('apps')


# ---------------------------------------------------------------------------
# Entry points
# ---------------------------------------------------------------------------
def artifact_for(meeting):
    """Get-or-create the pipeline row for a session."""
    from .models import SessionArtifact
    artifact, _ = SessionArtifact.objects.get_or_create(meeting=meeting)
    return artifact


def enqueue_finished_sessions():
    """Open a pipeline row for every Teams session that has ended. Returns the count."""
    from apps.communication.models import MeetingRoom
    from .models import SessionArtifact

    ended = (MeetingRoom.objects
             .filter(provider=MeetingRoom.PROVIDER_TEAMS, is_active=True,
                     scheduled_end__lt=timezone.now())
             .exclude(teams_meeting_id='')
             .exclude(artifact__isnull=False))
    opened = 0
    for meeting in ended.iterator():
        SessionArtifact.objects.get_or_create(
            meeting=meeting, defaults={'state': SessionArtifact.STATE_POLLING})
        opened += 1
    return opened


def run(limit=25):
    """Advance up to ``limit`` pending sessions by one step each.

    Returns a short human summary, which the scheduler records as the job's
    output — so ``run_scheduled_jobs --list`` says what actually happened rather
    than just "ok".
    """
    from .models import SessionArtifact

    opened = enqueue_finished_sessions()
    pending = (SessionArtifact.objects
               .exclude(state__in=[SessionArtifact.STATE_PUBLISHED,
                                   SessionArtifact.STATE_FAILED,
                                   SessionArtifact.STATE_SKIPPED])
               .select_related('meeting', 'meeting__module', 'meeting__host')
               .order_by('last_attempt_at', 'created_at')[:limit])

    advanced, failed = 0, 0
    for artifact in pending:
        try:
            if step(artifact):
                advanced += 1
        except Exception as exc:          # one bad session must not stop the rest
            logger.exception('livesessions: pipeline step failed for %s', artifact.meeting)
            artifact.record_failure(exc)
            failed += 1
    return (f'{opened} opened, {advanced} advanced, {failed} failed '
            f'({len(pending)} examined)')


def step(artifact):
    """Advance one session by exactly one state. True if anything changed."""
    from .models import SessionArtifact

    handlers = {
        SessionArtifact.STATE_WAITING: _step_waiting,
        SessionArtifact.STATE_POLLING: _step_polling,
        SessionArtifact.STATE_FILING: _step_filing,
        SessionArtifact.STATE_SUMMARISING: _step_summarising,
        SessionArtifact.STATE_UPLOADING: _step_uploading,
    }
    handler = handlers.get(artifact.state)
    return bool(handler and handler(artifact))


# ---------------------------------------------------------------------------
# Steps
# ---------------------------------------------------------------------------
def _step_waiting(artifact):
    """Nothing to do until the session is actually over."""
    from .models import LiveSessionSettings, SessionArtifact

    meeting = artifact.meeting
    if not meeting.has_ended:
        return False
    conf = LiveSessionSettings.load()
    if not (conf.publish_recordings and meeting.publish_recording):
        artifact.advance(SessionArtifact.STATE_SKIPPED)
        return True
    artifact.advance(SessionArtifact.STATE_POLLING)
    return True


def _step_polling(artifact):
    """Ask Graph whether Teams has published the recording yet."""
    from .models import SessionArtifact

    meeting = artifact.meeting
    if not (meeting.is_teams and meeting.teams_meeting_id and meeting.organizer_upn):
        artifact.advance(SessionArtifact.STATE_SKIPPED)
        return True
    if not graph.is_configured():
        return False        # dormant install — try again when it is switched on

    recordings = graph.list_recordings(meeting.organizer_upn, meeting.teams_meeting_id)
    transcripts = graph.list_transcripts(meeting.organizer_upn, meeting.teams_meeting_id)
    if recordings or transcripts:
        artifact.advance(SessionArtifact.STATE_FILING)
        return True

    # Give up eventually — a class nobody recorded will never produce artifacts,
    # and polling it forever crowds out the sessions that will.
    ended = meeting.scheduled_end or meeting.scheduled_start
    if ended and (timezone.now() - ended).total_seconds() > artifact.POLL_GIVE_UP_HOURS * 3600:
        logger.info('livesessions: no artifacts for %s after %sh — skipping',
                    meeting, artifact.POLL_GIVE_UP_HOURS)
        artifact.advance(SessionArtifact.STATE_SKIPPED,
                         last_error='Teams published no recording or transcript.')
        return True
    return False


def _step_filing(artifact):
    """Build the OneDrive folder and move the recording + transcript into it."""
    from .models import SessionArtifact

    meeting = artifact.meeting
    folder = onedrive.ensure_session_folder(meeting)
    if not folder:
        artifact.record_failure('Could not create the OneDrive session folder.')
        return False

    artifact.folder_id = folder['folder_id']
    artifact.folder_path = folder['path']
    artifact.folder_web_url = folder['web_url']
    artifact.drive_owner_upn = folder['owner_upn']

    # A week-pinned session files into that week's buckets (Recordings / Session
    # summaries); a session with no week keeps the flat dated folder as before.
    rec_folder = folder
    if meeting.week_id:
        rec_folder = onedrive.ensure_subfolder(folder, 'Recordings') or folder

    organizer, mid = meeting.organizer_upn, meeting.teams_meeting_id

    # 1) The recording.
    recordings = graph.list_recordings(organizer, mid)
    if recordings and not artifact.recording_item_id:
        item = onedrive.file_recording(meeting, rec_folder, recordings[0])
        if item and item.get('id'):
            artifact.recording_item_id = item['id']
            artifact.recording_web_url = item.get('webUrl', '')
            artifact.recording_bytes = int(item.get('size') or 0)
            artifact.recording_filed_at = timezone.now()
            artifact.recording_share_url = onedrive.anonymous_link(folder, item['id'])
            meeting.recording_url = artifact.recording_share_url or artifact.recording_web_url
            meeting.save(update_fields=['recording_url', 'updated_at'])

    # 2) The Microsoft transcript, verbatim, next to the video.
    if not artifact.transcript_item_id:
        vtt = _transcript_text(organizer, mid)
        if vtt:
            item = onedrive.put_text(rec_folder, f'{onedrive.artifact_stem(meeting)}-transcript.vtt',
                                     vtt, 'text/vtt')
            if item:
                artifact.transcript_item_id = item.get('id', '')
                artifact.transcript_web_url = item.get('webUrl', '')

    # 3) The thumbnail — generated here so it exists before YouTube needs it.
    _ensure_thumbnail(artifact, folder)

    artifact.advance(SessionArtifact.STATE_SUMMARISING)
    return True


def _step_summarising(artifact):
    """Recap the transcript, reconcile attendance, and publish to the schedule."""
    from apps.msteams import services as teams_services
    from .models import LiveSessionSettings, SessionArtifact

    meeting = artifact.meeting

    # The existing after-class sync already does the three things it does well:
    # transcript → recap AiReport, recap → class feed, Graph attendance → register.
    try:
        teams_services.sync_meeting(meeting, force=True)
    except Exception:
        logger.exception('livesessions: sync_meeting failed for %s', meeting)

    # File the recap into the week's "Session summaries" bucket (a session with no
    # week keeps it in the flat session folder).
    if not artifact.summary_item_id and artifact.folder_id:
        folder = folder_ref(artifact)
        if folder and meeting.week_id:
            folder = onedrive.ensure_subfolder(folder, 'Session summaries') or folder
        markdown = recap_markdown(meeting)
        if markdown and folder:
            item = onedrive.put_text(folder, f'{onedrive.artifact_stem(meeting)}-summary.md',
                                     markdown, 'text/markdown')
            if item:
                artifact.summary_item_id = item.get('id', '')
                artifact.summary_web_url = item.get('webUrl', '')

    publish_to_schedule(artifact)
    notify_one_on_one_attendance(meeting)

    # Tell people now, not after YouTube: the OneDrive link already plays, and a
    # student who missed Tuesday's class should not wait on an upload queue.
    _announce_recording(artifact)

    conf = LiveSessionSettings.load()
    if conf.youtube_live and artifact.recording_item_id and not artifact.youtube_video_id:
        artifact.advance(SessionArtifact.STATE_UPLOADING)
    else:
        artifact.advance(SessionArtifact.STATE_PUBLISHED)
    return True


def _step_uploading(artifact):
    """Push the recording to YouTube, when today's quota allows it."""
    from . import youtube
    from .models import LiveSessionSettings, SessionArtifact

    conf = LiveSessionSettings.load()
    if not conf.youtube_live:
        artifact.advance(SessionArtifact.STATE_PUBLISHED)
        _announce_recording(artifact)
        return True

    if not youtube.quota_available():
        # Not a failure: there is simply no room today. Leave the row where it
        # is so tomorrow's first tick picks it up, and do not count an attempt.
        logger.info('livesessions: YouTube quota exhausted — %s stays queued', artifact.meeting)
        return False

    folder = folder_ref(artifact)
    if not folder or not artifact.recording_item_id:
        artifact.advance(SessionArtifact.STATE_PUBLISHED)
        _announce_recording(artifact)
        return True

    blob = graph.download_item(folder['drive_id'], artifact.recording_item_id)
    if not blob:
        artifact.record_failure('Could not download the recording from OneDrive.')
        return False

    meeting = artifact.meeting
    video_id, error = youtube.upload(
        video_bytes=blob,
        title=_video_title(meeting),
        description=_video_description(meeting),
        privacy=conf.youtube_privacy,
        thumbnail_bytes=_thumbnail_bytes(meeting),
        tags=_video_tags(meeting),
    )
    if error:
        artifact.youtube_error = error[:300]
        artifact.record_failure(error)
        return False

    artifact.youtube_video_id = video_id
    artifact.youtube_uploaded_at = timezone.now()
    artifact.youtube_error = ''
    artifact.advance(SessionArtifact.STATE_PUBLISHED)
    publish_to_schedule(artifact)       # re-run so the material points at YouTube
    _announce_recording(artifact)
    return True


# ---------------------------------------------------------------------------
# Publishing to the module schedule
# ---------------------------------------------------------------------------
def publish_to_schedule(artifact):
    """Put the recording on the module's schedule as a past session.

    A :class:`~apps.learning.models.ModuleMaterial` of kind ``recording`` is what
    the schedule, the Documents tab and the search all already understand, so the
    recording appears everywhere a document does without a second surface having
    to be built. Idempotent — re-running updates the same row.
    """
    meeting = artifact.meeting
    if not meeting.module_id or not artifact.is_watchable:
        return None

    from apps.learning.models import ModuleMaterial

    phase = phase_for(meeting)
    if phase is None:
        return None

    material, _created = ModuleMaterial.objects.update_or_create(
        phase=phase,
        kind=ModuleMaterial.KIND_RECORDING,
        meeting=meeting,
        defaults={
            'week': meeting.week if meeting.week_id and meeting.week.phase_id == phase.pk else None,
            'title': f'Recording — {meeting.title}',
            'description': meeting.description or '',
            'url': artifact.watch_url,
        },
    )
    return material


def phase_for(meeting):
    """Which preparation block this recording belongs under.

    The week the session was scheduled against is the best answer; failing that,
    the block the session date falls inside; failing that, the module's most
    recent block. A recording filed in roughly the right place beats one that is
    not filed at all.
    """
    if meeting.week_id:
        return meeting.week.phase
    phases = list(meeting.module.phases.filter(is_active=True).order_by('order', 'id'))
    if not phases:
        return None
    when = (meeting.scheduled_start or timezone.now()).date()
    for phase in phases:
        starts, ends = phase.starts_on, phase.ends_on or phase.assessment_date
        if starts and ends and starts <= when <= ends:
            return phase
    return phases[-1]


# ---------------------------------------------------------------------------
# Attendance for one-on-one sessions
# ---------------------------------------------------------------------------
def notify_one_on_one_attendance(meeting):
    """E-mail the attendee their own attendance record for a 1:1.

    For a class the register belongs to the educator and the module. For a
    one-on-one there is no class — the "report" is one person's, so it goes to
    that person rather than into a roll nobody will read.
    """
    if not meeting.is_one_on_one:
        return False
    session = getattr(meeting, 'class_session', None)
    if session is None:
        return False

    from apps.communication import services as comm
    from apps.communication.models import Attendance

    invitee = meeting.participants.exclude(role='host').select_related('user').first()
    if invitee is None or invitee.user is None:
        return False

    record = Attendance.objects.filter(session=session, student=invitee.user).first()
    if record is None:
        return False

    comm.notify(
        invitee.user, category='meetings', level='info',
        verb='session attendance',
        title=f'Your session record — {meeting.title}',
        body=(f'You attended {record.minutes_attended} minute(s) of '
              f'“{meeting.title}” ({record.get_status_display()}). '
              f'The recording and notes are on the session page.'),
        url=meeting.get_absolute_url(), meeting=meeting, email=True,
    )
    return True


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def folder_ref(artifact):
    """Rebuild the ``{'drive_id', 'folder_id', ...}`` dict from stored ids.

    The pipeline is resumed from the database on a later tick — often a later
    process — so the folder handle has to be reconstituted rather than carried.
    """
    if not artifact.folder_id or not artifact.drive_owner_upn:
        return None
    drive_id = graph.get_drive_id(artifact.drive_owner_upn)
    if not drive_id:
        return None
    return {'drive_id': drive_id, 'folder_id': artifact.folder_id,
            'path': artifact.folder_path, 'web_url': artifact.folder_web_url,
            'owner_upn': artifact.drive_owner_upn}


def _transcript_text(organizer, meeting_id):
    """Every transcript for the meeting, concatenated as VTT."""
    chunks = []
    for transcript in graph.list_transcripts(organizer, meeting_id):
        content = graph.get_transcript_content(organizer, meeting_id, transcript.get('id'))
        if content:
            chunks.append(content)
    return '\n\n'.join(chunks)


def recap_markdown(meeting):
    """The recap ``sync_meeting`` filed, as markdown."""
    try:
        from apps.ai_assistant.models import AiReport
        report = (AiReport.objects.filter(linked_ref=f'meeting:{meeting.pk}')
                  .order_by('-created_at').first())
        return getattr(report, 'content', '') or ''
    except Exception:
        return ''


def _ensure_thumbnail(artifact, folder):
    """Draw the session card if it is missing, save it locally and to OneDrive."""
    from django.core.files.base import ContentFile
    from . import thumbnails

    meeting = artifact.meeting
    blob = _thumbnail_bytes(meeting)
    if blob is None:
        blob = thumbnails.render(meeting)
        if not blob:
            return
        try:
            meeting.thumbnail.save(thumbnails.filename_for(meeting), ContentFile(blob), save=True)
        except Exception:
            logger.warning('livesessions: could not store the thumbnail for %s', meeting, exc_info=True)

    if folder and not artifact.thumbnail_item_id:
        item = onedrive.put_bytes(folder, f'{onedrive.artifact_stem(meeting)}-thumbnail.jpg',
                                  blob, 'image/jpeg')
        if item:
            artifact.thumbnail_item_id = item.get('id', '')


def _thumbnail_bytes(meeting):
    """The stored thumbnail's bytes, or None if there isn't one."""
    if not meeting.thumbnail:
        return None
    try:
        with meeting.thumbnail.open('rb') as fh:
            return fh.read()
    except Exception:
        return None


def _video_title(meeting):
    """``UCS GR10 | MATH — Week 3: Functions`` — searchable, and unique per class."""
    bits = [meeting.title]
    if meeting.module_id:
        bits.insert(0, meeting.module.label)
    elif meeting.resolved_programme is not None:
        bits.insert(0, meeting.resolved_programme.label)
    return ' — '.join(b for b in bits if b)[:100]


def _video_description(meeting):
    """The session details, so the YouTube page stands alone if it is opened directly."""
    lines = []
    if meeting.description:
        lines += [meeting.description.strip(), '']
    for label, value in (
        ('School', getattr(meeting.resolved_institution, 'display_name', '')),
        ('Grade', getattr(meeting.resolved_programme, 'label', '')),
        ('Subject', meeting.module.display_name if meeting.module_id else ''),
        ('Covers', meeting.week.display_title if meeting.week_id else ''),
        ('Prepares for', meeting.calendar_event.title if meeting.calendar_event_id else ''),
        ('Held', f'{timezone.localtime(meeting.scheduled_start):%A %d %B %Y, %H:%M}'
                 if meeting.scheduled_start else ''),
    ):
        if value:
            lines.append(f'{label}: {value}')
    lines += ['', 'Recorded on United Church School. This video is unlisted and intended for '
                  'learners registered for this subject.']
    return '\n'.join(lines)


def _video_tags(meeting):
    tags = []
    institution = meeting.resolved_institution
    programme = meeting.resolved_programme
    if institution is not None:
        tags.append(institution.code)
    if programme is not None:
        tags.append(programme.code)
    if meeting.module_id:
        tags += [meeting.module.code, meeting.module.display_name]
    return [t for t in tags if t]


def _announce_recording(artifact):
    """Tell the session's audience the recording is up — once."""
    from apps.communication import services as comm
    from .audience import recipients_for

    meeting = artifact.meeting
    if artifact.announced_at or not artifact.is_watchable:
        return 0
    url = meeting.get_absolute_url()
    sent = 0
    for user in recipients_for(meeting).iterator():
        if comm.notify(user, category='meetings', level='success',
                       verb='recording available',
                       title=f'Recording available — {meeting.title}',
                       body='The recording, transcript and summary for this session are now '
                            'on its page. You can watch it in full whenever suits you.',
                       url=url, meeting=meeting, email=False):
            sent += 1
    artifact.announced_at = timezone.now()
    artifact.save(update_fields=['announced_at', 'updated_at'])
    return sent
