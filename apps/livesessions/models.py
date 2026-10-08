"""Live-session settings, after-class pipeline state, and the reminder ledger.

Three models, each answering one question:

* :class:`LiveSessionSettings` — *how should sessions behave?* A single row an
  admin edits in the Django admin. Credentials stay in the environment; only
  behaviour lives here, so switching recording off or renaming the OneDrive root
  never means a deploy.
* :class:`SessionArtifact` — *how far has this finished session got?* One row per
  :class:`~apps.communication.models.MeetingRoom`, carrying the state machine
  that runs recording → OneDrive → transcript → summary → YouTube → published,
  plus the retry bookkeeping that makes the whole chain resumable.
* :class:`SessionReminder` — *who has already been reminded, and at what lead?*
  The ledger that stops the 30-minute job from re-sending the 24-hour reminder
  every time it ticks.
"""

from django.conf import settings as django_settings
from django.db import models
from django.utils import timezone

from core import validators as v
from core.storage import files_storage


# ===========================================================================
# Settings (one row, edited in the admin)
# ===========================================================================
class LiveSessionSettings(models.Model):
    """Platform-wide behaviour for live sessions. Exactly one row.

    Everything here has a working default, so the feature behaves sensibly
    before anybody opens the page. :meth:`load` is the only way the rest of the
    app reads it — it creates the row on first use and never raises, because a
    missing settings row must not be able to take the calendar down.
    """

    # --- Recording ---------------------------------------------------------
    auto_record = models.BooleanField(
        default=True,
        help_text='Start recording automatically when the host joins a session.')
    publish_recordings = models.BooleanField(
        default=True,
        help_text='Publish finished recordings as past sessions students can re-watch.')

    # --- OneDrive filing ---------------------------------------------------
    onedrive_root = models.CharField(
        max_length=120, default='UCS Sessions',
        help_text='Top folder in the organiser’s OneDrive. Sessions are filed under '
                  '<root>/<institution>/<programme>/<module>/<date + title>/.')
    onedrive_owner_upn = models.CharField(
        max_length=255, blank=True,
        help_text='UPN whose OneDrive holds the whole tree. Blank = each session is '
                  'filed in its own organiser’s drive.')
    keep_teams_copy = models.BooleanField(
        default=False,
        help_text='Leave the original recording where Teams put it as well as filing a copy. '
                  'Off = the recording is moved, so there is one copy, in one place.')

    # --- YouTube -----------------------------------------------------------
    PRIVACY_UNLISTED = 'unlisted'
    PRIVACY_PRIVATE = 'private'
    PRIVACY_PUBLIC = 'public'
    PRIVACY_CHOICES = [(PRIVACY_UNLISTED, 'Unlisted'), (PRIVACY_PRIVATE, 'Private'),
                       (PRIVACY_PUBLIC, 'Public')]

    youtube_enabled = models.BooleanField(
        default=False,
        help_text='Upload finished recordings to YouTube and stream them in the platform. '
                  'Needs YOUTUBE_* credentials in the environment.')
    youtube_privacy = models.CharField(max_length=8, choices=PRIVACY_CHOICES, default=PRIVACY_UNLISTED)
    youtube_daily_quota = models.PositiveIntegerField(
        default=10000,
        help_text='Your project’s daily YouTube Data API quota. An upload costs 1600 units, '
                  'so the default cap allows about six a day before uploads must wait.')

    # --- Thumbnails --------------------------------------------------------
    thumbnail_background = models.ImageField(
        upload_to='sessions/backgrounds/', blank=True, null=True, storage=files_storage,
        validators=v.validate_image,
        help_text='Background image the session details are drawn on top of. '
                  'Blank = a plain brand-coloured panel. Best at 1280×720.')
    thumbnail_text_colour = models.CharField(max_length=9, default='#FFFFFF')
    thumbnail_accent_colour = models.CharField(max_length=9, default='#C9A84C')

    # --- Reminders ---------------------------------------------------------
    reminder_leads = models.CharField(
        max_length=100, default='1440,30',
        help_text='Minutes before a session to remind people, comma-separated. '
                  'Default 1440,30 = 24 hours and 30 minutes.')
    reminder_email = models.BooleanField(default=True, help_text='Also send reminders by e-mail.')

    # --- AI follow-up ------------------------------------------------------
    ai_followup_enabled = models.BooleanField(
        default=True,
        help_text='After each session, have the Claude admin layer write the full summary, '
                  'the next session’s agenda and the action items. Runs as a background '
                  'job on the admin account only.')

    # --- Microsoft calendar ------------------------------------------------
    create_calendar_events = models.BooleanField(
        default=True,
        help_text='Also create a real Outlook/Teams calendar event for the organiser and '
                  'any staff invitees. Needs the Calendars.ReadWrite application permission.')

    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(django_settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                   null=True, blank=True, related_name='+')

    class Meta:
        verbose_name = 'Live session settings'
        verbose_name_plural = 'Live session settings'

    def __str__(self):
        return 'Live session settings'

    def save(self, *args, **kwargs):
        # One row, always pk=1 — so a second "Add" in the admin edits the same
        # settings instead of quietly creating a rival set nothing reads.
        #
        # Pinning the pk is not enough on its own: a freshly constructed
        # instance still has ``_state.adding`` set, so Django would issue an
        # INSERT and hit the primary-key constraint rather than overwriting.
        # Clearing it turns the write into an update-then-insert, which is the
        # upsert this model actually wants.
        self.pk = 1
        self._state.adding = False
        kwargs['force_insert'] = False
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        """The settings row, created on first use. Never raises."""
        try:
            obj, _ = cls.objects.get_or_create(pk=1)
            return obj
        except Exception:       # pragma: no cover - a broken row must not 500 the calendar
            return cls()

    # --- Derived -----------------------------------------------------------
    @property
    def lead_minutes(self):
        """``reminder_leads`` as a sorted list of ints, longest lead first."""
        leads = set()
        for chunk in (self.reminder_leads or '').split(','):
            chunk = chunk.strip()
            if chunk.isdigit() and int(chunk) > 0:
                leads.add(int(chunk))
        return sorted(leads, reverse=True) or [1440, 30]

    @property
    def youtube_live(self):
        """True only when YouTube is switched on *and* credentials are present."""
        from . import youtube
        return bool(self.youtube_enabled and youtube.is_configured())


# ===========================================================================
# After-class pipeline state
# ===========================================================================
class SessionArtifact(models.Model):
    """Everything produced by one finished session, and how far along it is.

    The pipeline is deliberately a *stored* state machine rather than a chain of
    calls: Teams can take anything from minutes to hours to publish a recording,
    YouTube quota can defer an upload to tomorrow, and any step can fail on a
    transient network error. Storing the state means each tick of the scheduler
    resumes exactly where the last one stopped, and a failure parks one session
    without holding up the rest.
    """

    STATE_WAITING = 'waiting'          # session has not ended yet
    STATE_POLLING = 'polling'          # ended; waiting for Teams to publish artifacts
    STATE_FILING = 'filing'            # moving recording/transcript into OneDrive
    STATE_SUMMARISING = 'summarising'  # transcript → recap → AI follow-up
    STATE_UPLOADING = 'uploading'      # queued for / mid YouTube upload
    STATE_PUBLISHED = 'published'      # available to students as a past session
    STATE_FAILED = 'failed'            # gave up after MAX_ATTEMPTS
    STATE_SKIPPED = 'skipped'          # nothing was recorded, or publishing is off
    STATE_CHOICES = [
        (STATE_WAITING, 'Waiting for the session to end'),
        (STATE_POLLING, 'Waiting for Teams artifacts'),
        (STATE_FILING, 'Filing to OneDrive'),
        (STATE_SUMMARISING, 'Summarising'),
        (STATE_UPLOADING, 'Uploading to YouTube'),
        (STATE_PUBLISHED, 'Published'),
        (STATE_FAILED, 'Failed'),
        (STATE_SKIPPED, 'Skipped'),
    ]

    #: Teams can be slow; give up polling for artifacts after this long.
    POLL_GIVE_UP_HOURS = 48
    #: Consecutive failures of one step before the row is parked as failed.
    MAX_ATTEMPTS = 8

    meeting = models.OneToOneField('communication.MeetingRoom', on_delete=models.CASCADE,
                                   related_name='artifact')
    state = models.CharField(max_length=12, choices=STATE_CHOICES, default=STATE_WAITING, db_index=True)

    # --- OneDrive ---
    folder_id = models.CharField(max_length=255, blank=True)
    folder_path = models.CharField(max_length=500, blank=True,
                                   help_text='Human-readable path of the session folder.')
    folder_web_url = models.URLField(max_length=1000, blank=True)
    drive_owner_upn = models.CharField(max_length=255, blank=True)

    recording_item_id = models.CharField(max_length=255, blank=True)
    recording_web_url = models.URLField(max_length=1000, blank=True)
    recording_share_url = models.URLField(max_length=1000, blank=True,
                                          help_text='Anonymous view link, for students who are not in the tenant.')
    recording_bytes = models.BigIntegerField(default=0)
    recording_filed_at = models.DateTimeField(null=True, blank=True)

    transcript_item_id = models.CharField(max_length=255, blank=True)
    transcript_web_url = models.URLField(max_length=1000, blank=True)
    summary_item_id = models.CharField(max_length=255, blank=True)
    summary_web_url = models.URLField(max_length=1000, blank=True)
    thumbnail_item_id = models.CharField(max_length=255, blank=True)

    # --- YouTube ---
    youtube_video_id = models.CharField(max_length=40, blank=True, db_index=True)
    youtube_uploaded_at = models.DateTimeField(null=True, blank=True)
    youtube_error = models.CharField(max_length=300, blank=True)

    # --- AI follow-up (Claude, admin account, background) ---
    ai_followup_done = models.BooleanField(default=False)
    ai_report_id = models.PositiveIntegerField(null=True, blank=True,
                                               help_text='The ai_assistant.AiReport holding the full write-up.')

    # --- Bookkeeping ---
    #: Graph attendance records that could not be resolved to an account, as
    #: ``[{'label', 'seconds', 'keys'}]``. Anonymous joining makes these normal,
    #: not exceptional — an educator attaches each one to a candidate on the
    #: register and the answer is remembered as a TeamsIdentityAlias.
    unresolved_attendees = models.JSONField(default=list, blank=True)

    announced_at = models.DateTimeField(
        null=True, blank=True,
        help_text='When the audience was told the recording is up. Stops a second '
                  'announcement when the YouTube id lands after the OneDrive link.')
    attempts = models.PositiveIntegerField(default=0)
    last_error = models.TextField(blank=True)
    last_attempt_at = models.DateTimeField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Session artifact'

    def __str__(self):
        return f'{self.meeting} — {self.get_state_display()}'

    # --- State transitions -------------------------------------------------
    def advance(self, state, **fields):
        """Move to ``state``, clear the failure counter, and save."""
        self.state = state
        self.attempts = 0
        self.last_error = ''
        self.last_attempt_at = timezone.now()
        if state == self.STATE_PUBLISHED and not self.published_at:
            self.published_at = timezone.now()
        for key, value in fields.items():
            setattr(self, key, value)
        self.save()
        return self

    def record_failure(self, error):
        """Count a failed attempt; park the row once :attr:`MAX_ATTEMPTS` is hit.

        Parking matters: without it a session whose recording Teams never
        publishes would be retried by every tick of the scheduler forever, and
        the log would be nothing but that one session.
        """
        self.attempts += 1
        self.last_error = str(error)[:2000]
        self.last_attempt_at = timezone.now()
        if self.attempts >= self.MAX_ATTEMPTS:
            self.state = self.STATE_FAILED
        self.save(update_fields=['attempts', 'last_error', 'last_attempt_at', 'state', 'updated_at'])
        return self

    @property
    def is_terminal(self):
        return self.state in (self.STATE_PUBLISHED, self.STATE_FAILED, self.STATE_SKIPPED)

    @property
    def watch_url(self):
        """Where the platform should send someone who wants to re-watch.

        YouTube first — it is the only one that plays for a student who has no
        Microsoft account — then the anonymous OneDrive share link, then
        whatever Graph originally reported.
        """
        if self.youtube_video_id:
            return f'https://www.youtube.com/watch?v={self.youtube_video_id}'
        return self.recording_share_url or self.recording_web_url or self.meeting.recording_url or ''

    @property
    def embed_url(self):
        """A URL that can be dropped straight into an ``<iframe>``, or ''."""
        if self.youtube_video_id:
            return f'https://www.youtube-nocookie.com/embed/{self.youtube_video_id}'
        if self.recording_share_url:
            # OneDrive share links embed by appending the action, not by rewriting
            # the host — the link already carries its own sharing token.
            return f'{self.recording_share_url}&action=embedview' if '?' in self.recording_share_url \
                else f'{self.recording_share_url}?action=embedview'
        return ''

    @property
    def is_watchable(self):
        return bool(self.watch_url)


# ===========================================================================
# Identity — who actually walked into the call
# ===========================================================================
class SessionJoin(models.Model):
    """One identified hand-off from the platform into a live session.

    Microsoft gives us no supported way to pre-fill an anonymous attendee's
    display name, so what Teams reports is whatever the student typed into its
    "Enter your name" box — a nickname, a phone keyboard's autocorrect, or
    nothing useful at all. Matching that back to a candidate on e-mail alone
    misses most of a class.

    So the platform stops relying on Teams for identity. Every student reaches the call
    through :func:`apps.livesessions.views.session_join`, which is behind the
    login gate: at that moment we know exactly who they are, and we write it
    down. This row is the authoritative answer to "who went into this session",
    and the Graph attendance report is then matched *against* it rather than
    interpreted on its own.

    Clicking is not attending — the row starts no clock and marks nobody
    present. Presence is still measured, by the Graph report and the page
    heartbeat. This only settles identity.
    """

    meeting = models.ForeignKey('communication.MeetingRoom', on_delete=models.CASCADE,
                                related_name='joins')
    user = models.ForeignKey(django_settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='session_joins')

    # Snapshots, taken at the moment of the hand-off. Stored rather than derived
    # because a candidate who marries in June must still match the register of a
    # class they attended in March under their previous surname.
    display_name = models.CharField(max_length=200, blank=True,
                                    help_text='The name we asked them to enter in Teams.')
    email = models.EmailField(blank=True)

    first_clicked_at = models.DateTimeField(auto_now_add=True)
    last_clicked_at = models.DateTimeField(auto_now=True)
    click_count = models.PositiveIntegerField(default=1)

    #: The Graph identity this hand-off was resolved to, once the report arrives.
    matched_identity = models.CharField(max_length=255, blank=True)
    matched_seconds = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['meeting', 'display_name']
        constraints = [
            models.UniqueConstraint(fields=['meeting', 'user'], name='uniq_session_join_per_user'),
        ]
        indexes = [models.Index(fields=['meeting', 'user'], name='livesess_join_meet_user')]
        verbose_name = 'Session join'

    def __str__(self):
        return f'{self.display_name or self.user} → {self.meeting}'

    @property
    def is_matched(self):
        return bool(self.matched_identity)


class TeamsIdentityAlias(models.Model):
    """A Teams identity that is known to belong to a particular person.

    The point of this table is that a correction only has to be made **once**.
    When an educator resolves "Tebza 📱" on Tuesday's register to Thabo Mokoena,
    that answer is written here, and every future session matches him
    automatically — including the ones where he types the same nickname again.

    Without it, the same handful of students would need correcting by hand every
    single week, which is exactly the chore the register is meant to remove.
    """

    SOURCE_MANUAL = 'manual'        # an educator resolved it on the register
    SOURCE_INFERRED = 'inferred'    # matched confidently and remembered
    SOURCE_CHOICES = [(SOURCE_MANUAL, 'Resolved by a person'),
                      (SOURCE_INFERRED, 'Matched automatically')]

    person = models.ForeignKey('accounts.Person', on_delete=models.CASCADE,
                               related_name='teams_aliases')
    #: Lower-cased, whitespace-collapsed. The form the matcher looks up.
    identity = models.CharField(max_length=255, unique=True, db_index=True)
    #: What it looked like before normalisation, so a human can recognise it.
    raw = models.CharField(max_length=255, blank=True)
    source = models.CharField(max_length=8, choices=SOURCE_CHOICES, default=SOURCE_MANUAL)
    created_by = models.ForeignKey(django_settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                   null=True, blank=True, related_name='+')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['identity']
        verbose_name = 'Teams identity alias'
        verbose_name_plural = 'Teams identity aliases'

    def __str__(self):
        return f'{self.raw or self.identity} → {self.person}'


# ===========================================================================
# External calendars — import and export
# ===========================================================================
class CalendarSubscription(models.Model):
    """An outside calendar a user has pointed the platform at.

    Deliberately an **iCalendar feed URL**, not an OAuth connection. Google
    ("secret address in iCal format"), Microsoft 365 / Outlook ("publish this
    calendar") and Apple all hand out such a link from their own settings, and a
    feed needs no consent screen, no per-user token refresh, no API quota and no
    verification review. It also cannot write to the person's calendar, which is
    the correct authority for something the platform only needs to *read*.

    The events are imported read-only, as busy time. That matters most for
    educators: :func:`apps.livesessions.services.free_slots` consults them, so
    "when can I book this class?" accounts for the lesson the teacher already has
    in their own diary.
    """

    PROVIDER_GOOGLE = 'google'
    PROVIDER_MICROSOFT = 'microsoft'
    PROVIDER_APPLE = 'apple'
    PROVIDER_OTHER = 'other'
    PROVIDER_CHOICES = [
        (PROVIDER_GOOGLE, 'Google Calendar'),
        (PROVIDER_MICROSOFT, 'Microsoft 365 / Outlook'),
        (PROVIDER_APPLE, 'Apple iCloud'),
        (PROVIDER_OTHER, 'Other (any .ics feed)'),
    ]

    STATUS_PENDING = 'pending'
    STATUS_OK = 'ok'
    STATUS_FAILED = 'failed'
    STATUS_CHOICES = [(STATUS_PENDING, 'Not synced yet'), (STATUS_OK, 'Syncing'),
                      (STATUS_FAILED, 'Failing')]

    user = models.ForeignKey(django_settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='calendar_subscriptions')
    name = models.CharField(max_length=120, help_text='What to call it on your calendar.')
    url = models.URLField(max_length=1000,
                          help_text='The private iCalendar (.ics) address from your calendar app.')
    provider = models.CharField(max_length=10, choices=PROVIDER_CHOICES, default=PROVIDER_OTHER)
    colour = models.CharField(max_length=9, default='#8E8E93')
    is_active = models.BooleanField(default=True)
    #: Whether these events block out time when looking for a free slot.
    blocks_time = models.BooleanField(
        default=True,
        help_text='Count these events as busy when someone looks for a free slot to book.')

    last_synced_at = models.DateTimeField(null=True, blank=True)
    last_status = models.CharField(max_length=8, choices=STATUS_CHOICES, default=STATUS_PENDING)
    last_error = models.CharField(max_length=300, blank=True)
    event_count = models.PositiveIntegerField(default=0)
    consecutive_failures = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['user', 'name']
        constraints = [
            models.UniqueConstraint(fields=['user', 'url'], name='uniq_calendar_feed_per_user'),
        ]
        verbose_name = 'Calendar subscription'

    def __str__(self):
        return f'{self.name} ({self.user})'

    @property
    def is_healthy(self):
        return self.last_status != self.STATUS_FAILED

    @property
    def safe_url(self):
        """The URL with its query string hidden.

        A Google "secret address" is a bearer credential: anyone holding the
        whole link can read that person's diary. So it is never rendered back to
        a page in full, not even to its owner.
        """
        from urllib.parse import urlparse
        try:
            parsed = urlparse(self.url)
            return f'{parsed.scheme}://{parsed.netloc}{parsed.path[:40]}…'
        except Exception:
            return '(hidden)'


class ExternalEvent(models.Model):
    """One occurrence imported from a :class:`CalendarSubscription`.

    Occurrences, not rules: recurrence is expanded at import time inside a fixed
    window (see :mod:`apps.livesessions.ics`), so rendering a month never has to
    evaluate an RRULE. Each sync replaces the window wholesale, which keeps a
    deleted or moved meeting from lingering.
    """

    subscription = models.ForeignKey(CalendarSubscription, on_delete=models.CASCADE,
                                     related_name='events')
    uid = models.CharField(max_length=255, blank=True)
    title = models.CharField(max_length=300)
    start = models.DateTimeField(db_index=True)
    end = models.DateTimeField(null=True, blank=True)
    all_day = models.BooleanField(default=False)
    location = models.CharField(max_length=300, blank=True)
    #: False for an event marked TRANSPARENT — shown, but not treated as busy.
    busy = models.BooleanField(default=True)

    class Meta:
        ordering = ['start']
        indexes = [models.Index(fields=['subscription', 'start'], name='livesess_ext_sub_start')]
        verbose_name = 'Imported calendar event'

    def __str__(self):
        return f'{self.title} · {self.start:%Y-%m-%d %H:%M}'


# ===========================================================================
# Reminder ledger
# ===========================================================================
class SessionReminder(models.Model):
    """One reminder actually sent, for one person, at one lead time.

    The unique constraint is the whole point: the reminder job runs every few
    minutes and re-examines the same upcoming sessions each time, so "have I
    already sent this?" has to be a database question, not an in-memory one.
    """

    meeting = models.ForeignKey('communication.MeetingRoom', on_delete=models.CASCADE,
                                related_name='reminders_sent')
    recipient = models.ForeignKey(django_settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                  related_name='session_reminders')
    lead_minutes = models.PositiveIntegerField()
    sent_at = models.DateTimeField(auto_now_add=True)
    emailed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-sent_at']
        constraints = [
            models.UniqueConstraint(fields=['meeting', 'recipient', 'lead_minutes'],
                                    name='uniq_session_reminder_per_lead'),
        ]
        indexes = [models.Index(fields=['meeting', 'lead_minutes'], name='livesess_rem_meet_lead')]

    def __str__(self):
        return f'{self.recipient} · {self.meeting} · {self.lead_minutes}m'


# ---------------------------------------------------------------------------
# Imported YouTube content — existing channel playlists / past-session videos
# linked to a module + cohort so students can watch them in the platform.
#
# Mapping is per *playlist* (chosen model): a staff member points a playlist at
# an institution → programme → module → cohort once, and every video in it is
# surfaced for that module+cohort wherever the placement flags say. Scanning
# (see apps/livesessions/youtube.py + the scan_youtube command) only upserts the
# raw metadata; it never touches a mapping a human has set.

class YouTubePlaylist(models.Model):
    """A playlist read off the channel, plus where its videos should appear."""

    youtube_id = models.CharField(max_length=64, unique=True)
    title = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)
    thumbnail_url = models.URLField(max_length=500, blank=True)
    item_count = models.PositiveIntegerField(default=0)

    # Mapping — blank until a staff member assigns it.
    institution = models.ForeignKey('learning.Institution', null=True, blank=True,
                                    on_delete=models.SET_NULL, related_name='youtube_playlists')
    programme = models.ForeignKey('learning.Programme', null=True, blank=True,
                                  on_delete=models.SET_NULL, related_name='youtube_playlists')
    programme_module = models.ForeignKey('learning.ProgrammeModule', null=True, blank=True,
                                         on_delete=models.SET_NULL, related_name='youtube_playlists')
    cohort = models.ForeignKey('learning.Cohort', null=True, blank=True,
                               on_delete=models.SET_NULL, related_name='youtube_playlists')

    # Where mapped videos appear.
    show_past_sessions = models.BooleanField(default=True)
    show_my_programme = models.BooleanField(default=True)
    show_schedule = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    last_scanned_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title or self.youtube_id

    @property
    def is_mapped(self):
        return bool(self.programme_module_id and self.cohort_id)

    @property
    def url(self):
        return f'https://www.youtube.com/playlist?list={self.youtube_id}'


class YouTubeVideo(models.Model):
    """One video inside a scanned playlist. Inherits its playlist's mapping; may
    optionally be attached to a specific lesson for the lesson player."""

    youtube_id = models.CharField(max_length=32, unique=True)
    playlist = models.ForeignKey(YouTubePlaylist, on_delete=models.CASCADE, related_name='videos')
    title = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)
    thumbnail_url = models.URLField(max_length=500, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    position = models.PositiveIntegerField(default=0)

    # Optional per-video attachment to a lesson (surfaced in the lesson player).
    lesson = models.ForeignKey('learning.Lesson', null=True, blank=True,
                               on_delete=models.SET_NULL, related_name='youtube_videos')
    is_hidden = models.BooleanField(default=False)   # a staff member can hide one video

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['position', '-published_at']
        indexes = [models.Index(fields=['playlist', 'position'])]

    def __str__(self):
        return self.title or self.youtube_id

    @property
    def watch_url(self):
        return f'https://www.youtube.com/watch?v={self.youtube_id}'

    @property
    def embed_url(self):
        return f'https://www.youtube-nocookie.com/embed/{self.youtube_id}'
