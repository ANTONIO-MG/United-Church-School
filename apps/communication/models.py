"""Data models for the communication app.

Three feature areas:

* **Chat** — :class:`ChatGroup` (direct / module / custom) with
  :class:`ChatMembership`, :class:`Message`, :class:`MessageAttachment`
  (images / videos / files), edit history (``is_edited`` / ``edited_at``) and
  @mentions via :class:`MessageMention`. Module-scoped groups have
  their membership kept in sync with enrolment by :mod:`apps.communication.signals`.

* **Meetings** — :class:`MeetingRoom`: a video/audio call or class session with a
  shareable join link and scheduling fields. The actual A/V uses an embedded
  Jitsi Meet room (free, open-source, self-hostable); :class:`MeetingParticipant`
  records the invite list / RSVPs.

* **Notifications** — :class:`Notification` (one per recipient) and
  :class:`Announcement` (a staff/admin broadcast targeting everyone, a user
  category, modules or individuals — optionally also e-mailed).
"""

import uuid

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone

from core import validators as v

from core.storage import files_storage   # exchanged/generated files → file server


def _new_token():
    """Short URL-safe token used for meeting-room slugs / join links."""
    return uuid.uuid4().hex[:12]


#: Characters OneDrive / SharePoint refuse in an item name.
_FORBIDDEN_IN_FOLDER = '"*:<>?/\\|#%'


def _safe_folder_name(name, limit=120):
    """A folder/file name OneDrive will accept, trimmed to ``limit``.

    OneDrive rejects a handful of characters outright and silently mangles
    leading/trailing dots and spaces, so a session titled "Q&A: IAS 12" has to
    be cleaned before it can become a folder.
    """
    cleaned = ''.join(' ' if ch in _FORBIDDEN_IN_FOLDER else ch for ch in str(name or ''))
    cleaned = ' '.join(cleaned.split()).strip(' .')
    return (cleaned[:limit].strip(' .')) or 'Untitled'


# ===========================================================================
# Chat
# ===========================================================================
class ChatGroup(models.Model):
    """A conversation: a 1:1 direct chat, a module group or a custom group."""

    KIND_DIRECT = 'direct'
    KIND_SUBJECT = 'module'
    KIND_CUSTOM = 'custom'
    KIND_CHOICES = [
        (KIND_DIRECT, 'Direct (1:1)'),
        (KIND_SUBJECT, 'Module group'),
        (KIND_CUSTOM, 'Custom group'),
    ]

    kind = models.CharField(max_length=10, choices=KIND_CHOICES, default=KIND_CUSTOM)
    name = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)

    # An auto-managed group is linked from its ProgrammeModule
    # (``ProgrammeModule.chat_group``), so its membership tracks enrolment.

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+',
    )
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return self.display_name

    @property
    def display_name(self):
        if self.name:
            return self.name
        offering = getattr(self, 'programme_module', None)
        if offering is not None:
            return f'Module · {offering}'
        if self.kind == self.KIND_DIRECT:
            from core.utils import display_name
            people = ', '.join(display_name(membership.user) for membership in self.memberships.all()[:2])
            return people or 'Direct chat'
        return f'Chat #{self.pk}'

    @property
    def is_auto_managed(self):
        """True for module groups whose membership tracks enrolment."""
        return self.kind == self.KIND_SUBJECT

    def add_member(self, user, *, role='member', auto=False):
        membership, created = self.memberships.get_or_create(
            user=user, defaults={'role': role, 'is_auto': auto},
        )
        if not created and auto and not membership.is_auto:
            membership.is_auto = True
            membership.save(update_fields=['is_auto'])
        return membership


class ChatMembership(models.Model):
    """A user's membership in a :class:`ChatGroup`."""

    ROLE_CHOICES = [('owner', 'Owner'), ('admin', 'Admin'), ('member', 'Member')]

    group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_memberships')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')

    # True when added automatically because the user is enrolled in the module.
    is_auto = models.BooleanField(default=False)
    muted = models.BooleanField(default=False)
    last_read_at = models.DateTimeField(null=True, blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('group', 'user')
        ordering = ['group', 'user']

    def __str__(self):
        return f'{self.user} in {self.group}'

    @property
    def unread_count(self):
        """Unread messages in this one conversation.

        One query per membership — fine for a single conversation, wrong for a
        list of them. Use :meth:`unread_total_for` when you want the badge.
        """
        qs = self.group.messages.exclude(sender=self.user)
        if self.last_read_at:
            qs = qs.filter(created_at__gt=self.last_read_at)
        return qs.count()

    @classmethod
    def unread_total_for(cls, user):
        """Total unread across every conversation ``user`` is in — in ONE query.

        The obvious loop (``sum(m.unread_count for m in memberships)``) issues a
        COUNT per membership, and this number is rendered in the navbar on every
        single page: it was the platform's most-repeated query. Each membership
        has its own ``last_read_at`` watermark, so the whole thing collapses into
        one aggregate with a per-row condition rather than N round trips.
        """
        from django.db.models import Count, F, Q

        row = (cls.objects
               .filter(user=user)
               .aggregate(total=Count(
                   'group__messages',
                   filter=(~Q(group__messages__sender=user)
                           & (Q(last_read_at__isnull=True)
                              | Q(group__messages__created_at__gt=F('last_read_at')))))))
        return row['total'] or 0


class Message(models.Model):
    """A chat message. Supports text + attachments, replies, editing and @mentions."""

    group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='sent_messages')
    body = models.TextField(blank=True)
    reply_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')

    mentions = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through='MessageMention', related_name='mentioned_in_messages', blank=True,
    )

    is_edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        ordering = ['created_at']
        indexes = [models.Index(fields=['group', 'created_at'])]

    def __str__(self):
        return f'{self.sender}: {self.body[:40]}'

    def mark_edited(self):
        self.is_edited = True
        self.edited_at = timezone.now()


class MessageAttachment(models.Model):
    """A file attached to a :class:`Message` — an image, a video or a generic file."""

    KIND_IMAGE = 'image'
    KIND_VIDEO = 'video'
    KIND_FILE = 'file'
    KIND_CHOICES = [(KIND_IMAGE, 'Image'), (KIND_VIDEO, 'Video'), (KIND_FILE, 'File')]

    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='chat/%Y/%m/', storage=files_storage,
                            validators=v.validate_attachment)
    kind = models.CharField(max_length=10, choices=KIND_CHOICES, default=KIND_FILE)
    original_name = models.CharField(max_length=255, blank=True)
    size = models.PositiveBigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    # Extensions that auto-classify an upload as an image / video.
    IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg'}
    VIDEO_EXTS = {'.mp4', '.webm', '.mov', '.m4v', '.avi', '.mkv', '.ogg'}

    def __str__(self):
        return self.original_name or self.file.name

    @classmethod
    def classify(cls, filename):
        import os
        ext = os.path.splitext(filename or '')[1].lower()
        if ext in cls.IMAGE_EXTS:
            return cls.KIND_IMAGE
        if ext in cls.VIDEO_EXTS:
            return cls.KIND_VIDEO
        return cls.KIND_FILE

    def save(self, *args, **kwargs):
        if self.file and not self.original_name:
            self.original_name = getattr(self.file, 'name', '')
        if self.file and not self.size:
            try:
                self.size = self.file.size
            except (OSError, ValueError):
                self.size = 0
        if (not self.kind or self.kind == self.KIND_FILE) and self.original_name:
            self.kind = self.classify(self.original_name)
        super().save(*args, **kwargs)


class MessageMention(models.Model):
    """Through-table linking a :class:`Message` to a tagged (``@``) user.

    Creating one also creates a :class:`Notification` for that user (see
    :mod:`apps.communication.signals`), so they're alerted they were tagged.
    """

    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='mention_links')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='message_mentions')
    seen = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('message', 'user')

    def __str__(self):
        return f'@{self.user} in message #{self.message_id}'


class ConnectionRequest(models.Model):
    """A request from one user to open 1:1 direct messaging with another.

    Used to gate **student ↔ student** direct chats: two students can only
    exchange direct messages once a request between them is ``accepted``. Chats
    that involve staff/admin/educator/parent — and every course/module/custom
    group chat — are not gated (see
    :func:`apps.communication.services.students_need_connection`).
    """

    STATUS_PENDING = 'pending'
    STATUS_ACCEPTED = 'accepted'
    STATUS_DECLINED = 'declined'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_ACCEPTED, 'Accepted'),
        (STATUS_DECLINED, 'Declined'),
    ]

    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='connection_requests_sent')
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='connection_requests_received')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        # At most one request row per ordered (from, to) pair.
        unique_together = ('from_user', 'to_user')
        ordering = ['-created_at']
        indexes = [models.Index(fields=['to_user', 'status'])]

    def __str__(self):
        return f'{self.from_user} → {self.to_user} ({self.status})'

    def accept(self):
        self.status = self.STATUS_ACCEPTED
        self.responded_at = timezone.now()
        self.save(update_fields=['status', 'responded_at'])

    def decline(self):
        self.status = self.STATUS_DECLINED
        self.responded_at = timezone.now()
        self.save(update_fields=['status', 'responded_at'])


# ===========================================================================
# Meetings (video / audio calls & conferencing)
# ===========================================================================
class MeetingRoom(models.Model):
    """A live class session / video call.

    The live engine is **Microsoft Teams** (``provider='teams'``), created from
    the LMS via Microsoft Graph — see :mod:`apps.msteams` and
    docs/TEAMS_INTEGRATION.md. Students join anonymously via ``teams_join_url``.
    **Jitsi** (``provider='jitsi'``) is kept only as a fallback engine.

    Either way, :meth:`get_join_url` is the in-app launch page (stable link used
    by the calendar, lessons and notifications); the page then sends the attendee
    to :meth:`live_url` (the Teams/Jitsi room).
    """

    PROVIDER_TEAMS = 'teams'
    PROVIDER_JITSI = 'jitsi'
    PROVIDER_CHOICES = [(PROVIDER_TEAMS, 'Microsoft Teams'), (PROVIDER_JITSI, 'Jitsi')]

    # --- Who the session is for -------------------------------------------
    # The audience decides two different things at once: who is *notified* when
    # the session is created, and who may *see it on the calendar*. They are the
    # same set on purpose — a student seeing a session they were never told
    # about is the bug this field exists to prevent.
    AUDIENCE_EVERYONE = 'everyone'          # the whole platform
    AUDIENCE_INSTITUTION = 'institution'    # everyone registered with one institution
    AUDIENCE_PROGRAMME = 'programme'        # everyone on one programme
    AUDIENCE_COHORT = 'cohort'              # one intake of one programme
    AUDIENCE_MODULE = 'module'              # everyone studying one module offering
    AUDIENCE_PRIVATE = 'private'            # named invitees only — includes 1:1
    AUDIENCE_CHOICES = [
        (AUDIENCE_EVERYONE, 'Everyone on the platform'),
        (AUDIENCE_INSTITUTION, 'One institution'),
        (AUDIENCE_PROGRAMME, 'One programme'),
        (AUDIENCE_COHORT, 'One cohort'),
        (AUDIENCE_MODULE, 'One module'),
        (AUDIENCE_PRIVATE, 'Invited people only (incl. one-on-one)'),
    ]

    #: Audiences whose membership is derived from enrolment rather than from the
    #: invite list. Used by both the notifier and the calendar filter.
    DERIVED_AUDIENCES = (AUDIENCE_EVERYONE, AUDIENCE_INSTITUTION,
                         AUDIENCE_PROGRAMME, AUDIENCE_COHORT, AUDIENCE_MODULE)

    # --- What kind of contact time it is ----------------------------------
    KIND_CLASS = 'class'
    KIND_REVISION = 'revision'
    KIND_TEST_REVIEW = 'test_review'
    KIND_CONSULT = 'consult'          # one-on-one
    KIND_WORKSHOP = 'workshop'
    KIND_BRIEFING = 'briefing'
    KIND_CHOICES = [
        (KIND_CLASS, 'Class'),
        (KIND_REVISION, 'Revision'),
        (KIND_TEST_REVIEW, 'Test / exam review'),
        (KIND_CONSULT, 'One-on-one consultation'),
        (KIND_WORKSHOP, 'Workshop'),
        (KIND_BRIEFING, 'Briefing'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=24, unique=True, default=_new_token, editable=False)
    description = models.TextField(blank=True)

    host = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='hosted_meetings')
    # Optional link to a chat group (e.g. a course/module session).
    group = models.ForeignKey(ChatGroup, on_delete=models.SET_NULL, null=True, blank=True, related_name='meetings')
    # Direct link to the module this session belongs to (auto-assigned on create).
    module = models.ForeignKey('learning.ProgrammeModule', on_delete=models.SET_NULL, null=True, blank=True, related_name='meetings')

    scheduled_start = models.DateTimeField(null=True, blank=True)
    scheduled_end = models.DateTimeField(null=True, blank=True)
    is_recurring = models.BooleanField(default=False)
    RECURRENCE_CHOICES = [('', 'None'), ('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')]
    recurrence = models.CharField(max_length=10, choices=RECURRENCE_CHOICES, blank=True)

    requires_login = models.BooleanField(default=True, help_text='If off, anyone with the link can join.')
    is_active = models.BooleanField(default=True)

    # --- Live engine (Microsoft Teams via Graph; Jitsi fallback) ---
    provider = models.CharField(max_length=10, choices=PROVIDER_CHOICES, default=PROVIDER_JITSI)
    teams_meeting_id = models.CharField(max_length=512, blank=True)
    teams_join_url = models.URLField(max_length=1000, blank=True)
    organizer_upn = models.CharField(max_length=255, blank=True,
                                     help_text='Microsoft UPN of the meeting organiser (the licensed educator).')

    # --- Audience / academic placement ------------------------------------
    # ``module`` (above) stays the primary link. These narrow or widen it: a
    # programme-wide briefing has no module, a module class has no cohort, and a
    # one-on-one has neither. ``week`` and ``calendar_event`` are what put the
    # session on the module's schedule next to the right topic or test.
    audience = models.CharField(max_length=12, choices=AUDIENCE_CHOICES, default=AUDIENCE_PRIVATE,
                                db_index=True,
                                help_text='Who this session is for — decides both who is notified '
                                          'and who can see it on the calendar.')
    session_kind = models.CharField(max_length=12, choices=KIND_CHOICES, default=KIND_CLASS)
    institution = models.ForeignKey('learning.Institution', on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='meetings')
    programme = models.ForeignKey('learning.Programme', on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='meetings')
    cohort = models.ForeignKey('learning.Cohort', on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='meetings')
    week = models.ForeignKey('learning.ModuleWeek', on_delete=models.SET_NULL, null=True, blank=True,
                             related_name='meetings',
                             help_text='The week / topic this session covers, if any.')
    calendar_event = models.ForeignKey('learning.CalendarEvent', on_delete=models.SET_NULL,
                                       null=True, blank=True, related_name='meetings',
                                       help_text='The test / exam this session prepares for or reviews.')

    # --- Live-session settings (per session; defaults come from LiveSessionSettings) ---
    record_automatically = models.BooleanField(
        default=True, help_text='Start recording the moment the host joins.')
    publish_recording = models.BooleanField(
        default=True, help_text='Make the recording available as a past session afterwards.')

    # --- Microsoft calendar (the staff-side Outlook/Teams invite) ---
    teams_calendar_event_id = models.CharField(max_length=512, blank=True)

    # --- Thumbnail (background image + session details, drawn by livesessions.thumbnails) ---
    thumbnail = models.ImageField(upload_to='sessions/thumbnails/', blank=True, null=True,
                                  storage=files_storage, validators=v.validate_image)

    # --- After-class artifacts (filled by apps.msteams.services) ---
    recording_url = models.URLField(max_length=1000, blank=True)
    artifacts_synced_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-scheduled_start', '-created_at']
        indexes = [
            # The calendar's only question: "sessions in this window, for this
            # audience". Both the staff view (no audience filter) and every
            # student view (audience + one scope id) are served by walking this
            # index over the requested month.
            models.Index(fields=['audience', 'scheduled_start'], name='comm_meet_aud_start'),
            models.Index(fields=['module', 'scheduled_start'], name='comm_meet_mod_start'),
            models.Index(fields=['scheduled_start'], name='comm_meet_start'),
        ]

    def __str__(self):
        return self.title

    @property
    def is_teams(self):
        return self.provider == self.PROVIDER_TEAMS

    @property
    def room_name(self):
        """The Jitsi room name (kept stable + namespaced to avoid collisions)."""
        return f'UCSHub-{self.slug}'

    @property
    def jitsi_domain(self):
        base = getattr(settings, 'JITSI_BASE_URL', 'https://meet.jit.si').rstrip('/')
        return base.split('//', 1)[-1]

    @property
    def external_url(self):
        """The real A/V room URL — the Teams join link, or the Jitsi room."""
        if self.is_teams and self.teams_join_url:
            return self.teams_join_url
        base = getattr(settings, 'JITSI_BASE_URL', 'https://meet.jit.si').rstrip('/')
        return f'{base}/{self.room_name}'

    # Alias used by the launch page / templates.
    live_url = external_url

    def get_join_url(self):
        """The launch page — the button that actually puts you in the call."""
        return reverse('communication:meeting-room', args=[self.slug])

    def get_absolute_url(self):
        """The session's own page: details, join button, and afterwards the
        recording, transcript, summary and your attendance.

        This is what the calendar, reminders and e-mails link to. The launch page
        above is one button on it, because a link sent 24 hours in advance should
        open something you can read, not something that tries to start a call.
        """
        return reverse('livesessions:session-detail', args=[self.pk])

    @property
    def is_upcoming(self):
        return bool(self.scheduled_start and self.scheduled_start >= timezone.now())

    @property
    def is_live_now(self):
        now = timezone.now()
        start, end = self.scheduled_start, self.scheduled_end
        if not start:
            return False
        return start <= now and (end is None or now <= end)

    @property
    def has_ended(self):
        end = self.scheduled_end
        return bool(end and timezone.now() > end)

    @property
    def duration_minutes(self):
        start, end = self.scheduled_start, self.scheduled_end
        if start and end and end > start:
            return int((end - start).total_seconds() // 60)
        return 60

    @property
    def is_one_on_one(self):
        """A private session with exactly one invitee besides the host.

        Used to decide whether the attendance report goes back to the attendee
        personally rather than into a class register.
        """
        if self.audience != self.AUDIENCE_PRIVATE:
            return False
        return self.participants.exclude(role='host').count() == 1

    # --- Academic placement ------------------------------------------------
    @property
    def resolved_institution(self):
        """The institution this session belongs to, however it was scoped."""
        if self.institution_id:
            return self.institution
        programme = self.resolved_programme
        return getattr(programme, 'institution', None)

    @property
    def resolved_programme(self):
        if self.programme_id:
            return self.programme
        if self.cohort_id:
            return self.cohort.programme
        if self.module_id:
            return self.module.programme
        return None

    @property
    def storage_path_parts(self):
        """Institution → programme → module → (Test N → Week n) → session, as folders.

        This mirrors the UCS LMS OneDrive tree that the ``provision_onedrive``
        command builds, so a recap files itself into the same place. When the
        session is pinned to a week (:attr:`week`), it routes into that week's
        folder — the recording and summary then land in the week's Recordings /
        Session summaries buckets. A session with no week (a general briefing)
        keeps its own dated folder under the module. Levels that do not apply are
        left out, so a platform-wide briefing lands in ``General/`` rather than a
        chain of "None" folders. Segment names match ``provision_onedrive``:
        institution.code, programme.code, module.code, phase.short_label.
        """
        parts = []
        institution = self.resolved_institution
        programme = self.resolved_programme
        parts.append(getattr(institution, 'code', '') or 'General')
        if programme is not None:
            parts.append(getattr(programme, 'code', '') or str(programme))
        if self.module_id:
            parts.append(self.module.code)
        if self.week_id:
            parts.append(self.week.phase.short_label)     # "Test 1"
            parts.append(f'Week {self.week.number}')
        else:
            when = self.scheduled_start or self.created_at or timezone.now()
            parts.append(f'{timezone.localtime(when):%Y-%m-%d} {self.title}'.strip())
        return [_safe_folder_name(part) for part in parts if part]

    @property
    def audience_label(self):
        """A human sentence naming who the session is for."""
        if self.audience == self.AUDIENCE_EVERYONE:
            return 'Everyone'
        if self.audience == self.AUDIENCE_INSTITUTION and self.institution_id:
            return self.institution.label
        if self.audience == self.AUDIENCE_PROGRAMME and self.programme_id:
            return self.programme.label
        if self.audience == self.AUDIENCE_COHORT and self.cohort_id:
            return str(self.cohort)
        if self.audience == self.AUDIENCE_MODULE and self.module_id:
            return self.module.label
        if self.audience == self.AUDIENCE_PRIVATE:
            return 'One-on-one' if self.is_one_on_one else 'Invited people only'
        return self.get_audience_display()

    @property
    def thumbnail_caption_lines(self):
        """The lines drawn onto the thumbnail, top to bottom.

        Programme / module, then the week or test it covers, then the date and
        time — the four things a student scanning a schedule actually needs.
        """
        lines = []
        programme = self.resolved_programme
        if self.module_id:
            lines.append(f'{programme.label} | {self.module.code}' if programme else self.module.label)
        elif programme is not None:
            lines.append(programme.label)
        elif self.institution_id:
            lines.append(self.institution.display_name)
        if self.week_id:
            lines.append(self.week.display_title)
        elif self.calendar_event_id:
            lines.append(self.calendar_event.title)
        if self.scheduled_start:
            lines.append(f'{timezone.localtime(self.scheduled_start):%a %d %b %Y · %H:%M}')
        return lines


class MeetingParticipant(models.Model):
    """An invitee / attendee of a :class:`MeetingRoom` (used for RSVPs & roles)."""

    ROLE_CHOICES = [('host', 'Host'), ('cohost', 'Co-host'), ('attendee', 'Attendee')]
    RSVP_CHOICES = [('pending', 'Pending'), ('yes', 'Going'), ('no', 'Not going'), ('maybe', 'Maybe')]

    meeting = models.ForeignKey(MeetingRoom, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='meeting_invites')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='attendee')
    rsvp = models.CharField(max_length=10, choices=RSVP_CHOICES, default='pending')
    invited_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('meeting', 'user')

    def __str__(self):
        return f'{self.user} → {self.meeting}'


# ===========================================================================
# Notifications & announcements
# ===========================================================================
class Notification(models.Model):
    """A single notification delivered to one user (also shown in the bell menu)."""

    LEVEL_CHOICES = [('info', 'Info'), ('success', 'Success'), ('warning', 'Warning'), ('error', 'Error')]

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    verb = models.CharField(max_length=120, blank=True, help_text='e.g. "mentioned you", "sent an announcement"')
    title = models.CharField(max_length=200, blank=True)
    body = models.TextField(blank=True)
    # Plain text is escaped and line-broken; ``html`` is rendered as-is on the
    # detail page. Only ever set ``html`` for bodies the system itself composes
    # (welcome guides, digests) — never for anything a user typed.
    FORMAT_TEXT = 'text'
    FORMAT_HTML = 'html'
    FORMAT_CHOICES = [(FORMAT_TEXT, 'Plain text'), (FORMAT_HTML, 'Rich text (system-authored)')]
    body_format = models.CharField(max_length=4, choices=FORMAT_CHOICES, default=FORMAT_TEXT)
    # Optional one-line standfirst shown under the headline on the reading page.
    summary = models.CharField(max_length=300, blank=True)
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default='info')
    url = models.CharField(max_length=500, blank=True, help_text='Where clicking the notification goes.')

    # Optional links back to the thing this notification is about.
    message = models.ForeignKey(Message, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    meeting = models.ForeignKey(MeetingRoom, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    announcement = models.ForeignKey('Announcement', on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')

    is_read = models.BooleanField(default=False, db_index=True)
    # Starred by the recipient so they can find it again from the favourites
    # rail on the inbox, independent of whether it has been read.
    is_favourite = models.BooleanField(default=False, db_index=True)
    emailed = models.BooleanField(default=False)
    whatsapped = models.BooleanField(default=False,
                                     help_text='A copy reached the recipient on WhatsApp.')
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['recipient', 'is_read'])]

    def __str__(self):
        return f'{self.recipient}: {self.title or self.verb}'

    def mark_read(self):
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=['is_read'])

    @property
    def is_html(self):
        return self.body_format == self.FORMAT_HTML

    @property
    def reading_minutes(self):
        """Rough reading time for the detail page, at 200 words a minute."""
        import re
        text = re.sub(r'<[^>]+>', ' ', self.body or '')
        words = len([w for w in text.split() if w])
        return max(1, round(words / 200))


class Announcement(models.Model):
    """A broadcast composed by a staff member / admin.

    :attr:`audience` picks who receives it; :func:`apps.communication.services.send_announcement`
    resolves that to a set of users, creates one :class:`Notification` each and
    (if :attr:`send_email`) e-mails them via :mod:`apps.communication.emails`.
    """

    AUDIENCE_ALL = 'all'
    AUDIENCE_TARGETED = 'targeted'
    AUDIENCE_USER_TYPE = 'user_type'
    AUDIENCE_MODULES = 'modules'
    AUDIENCE_USERS = 'users'
    AUDIENCE_CHOICES = [
        (AUDIENCE_ALL, 'Everyone'),
        (AUDIENCE_TARGETED, 'Selected institutions, programmes, cohorts, modules or people'),
        # The three below predate the composer's "targeted" audience. They are
        # kept so old rows and the REST API still resolve, but the composer no
        # longer offers them: "Everyone" + a role filter is a user category, and
        # "targeted" covers modules and named people.
        (AUDIENCE_USER_TYPE, 'A user category'),
        (AUDIENCE_MODULES, 'Members of selected modules'),
        (AUDIENCE_USERS, 'Specific individuals'),
    ]
    LEVEL_CHOICES = Notification.LEVEL_CHOICES

    STATUS_DRAFT = 'draft'
    STATUS_SCHEDULED = 'scheduled'
    STATUS_SENDING = 'sending'
    STATUS_SENT = 'sent'
    STATUS_FAILED = 'failed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'), (STATUS_SCHEDULED, 'Scheduled'), (STATUS_SENDING, 'Sending'),
        (STATUS_SENT, 'Sent'), (STATUS_FAILED, 'Failed'), (STATUS_CANCELLED, 'Cancelled'),
    ]

    #: Roles a broadcast can be narrowed to — the values of ``Person.user_type``.
    ROLE_CHOICES = [('student', 'Students'), ('educator', 'Educators'), ('parent', 'Parents'),
                    ('staff', 'Staff'), ('admin', 'Admins')]

    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='announcements_sent')
    title = models.CharField(max_length=200)
    body = models.TextField()
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default='info')
    url = models.CharField(max_length=500, blank=True)
    url_label = models.CharField(max_length=60, blank=True,
                                 help_text='Button text for the link, e.g. "Open the blueprint".')
    media_url = models.URLField(max_length=500, blank=True,
                                help_text='A YouTube, Vimeo or other video link to play inside the notification.')

    audience = models.CharField(max_length=12, choices=AUDIENCE_CHOICES, default=AUDIENCE_ALL)
    # Used when audience == user_type — matches accounts.Person.user_type.
    user_type = models.CharField(max_length=20, blank=True)
    institutions = models.ManyToManyField('learning.Institution', blank=True, related_name='announcements')
    programmes = models.ManyToManyField('learning.Programme', blank=True, related_name='announcements')
    cohorts = models.ManyToManyField('learning.Cohort', blank=True, related_name='announcements')
    modules = models.ManyToManyField('learning.ProgrammeModule', blank=True, related_name='announcements')
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='+')
    #: Narrow the audience to these ``Person.user_type`` values; empty = every role.
    #: People picked by name are always included, whatever their role.
    roles = models.JSONField(default=list, blank=True)
    include_parents = models.BooleanField(
        default=False, help_text="Also send a copy to the parents/guardians of every student reached.")
    is_important = models.BooleanField(
        default=False, help_text='Deliver even to people who have switched announcements off.')

    send_email = models.BooleanField(default=True, help_text='Also deliver a copy by e-mail.')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_DRAFT, db_index=True)
    scheduled_for = models.DateTimeField(null=True, blank=True, db_index=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    recipient_count = models.PositiveIntegerField(default=0)
    failure = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def is_sent(self):
        return self.sent_at is not None

    @property
    def is_editable(self):
        return self.status in (self.STATUS_DRAFT, self.STATUS_SCHEDULED)

    @property
    def role_labels(self):
        names = dict(self.ROLE_CHOICES)
        return [names.get(r, r) for r in (self.roles or [])]

    @property
    def embed_url(self):
        """An iframe-able player URL for :attr:`media_url`, or '' if it isn't one."""
        from .broadcast import embed_url_for
        return embed_url_for(self.media_url)


class AnnouncementAttachment(models.Model):
    """A picture, video or document sent with an :class:`Announcement`.

    Every recipient's notification points at the same announcement, so the file
    is stored once and shown on each person's notification page.
    """

    KIND_IMAGE = 'image'
    KIND_VIDEO = 'video'
    KIND_FILE = 'file'
    KIND_CHOICES = [(KIND_IMAGE, 'Image'), (KIND_VIDEO, 'Video'), (KIND_FILE, 'File')]

    IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.avif'}
    VIDEO_EXTS = {'.mp4', '.webm', '.mov', '.m4v'}

    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='announcements/%Y/%m/', storage=files_storage,
                            validators=v.validate_broadcast)
    kind = models.CharField(max_length=10, choices=KIND_CHOICES, default=KIND_FILE)
    original_name = models.CharField(max_length=255, blank=True)
    size = models.PositiveBigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at', 'pk']

    def __str__(self):
        return self.original_name or self.file.name

    @classmethod
    def classify(cls, filename):
        import os
        ext = os.path.splitext(filename or '')[1].lower()
        if ext in cls.IMAGE_EXTS:
            return cls.KIND_IMAGE
        if ext in cls.VIDEO_EXTS:
            return cls.KIND_VIDEO
        return cls.KIND_FILE

    def save(self, *args, **kwargs):
        if self.file and not self.original_name:
            self.original_name = getattr(self.file, 'name', '')
        if self.file and not self.size:
            try:
                self.size = self.file.size
            except (OSError, ValueError):
                self.size = 0
        if self.original_name:
            self.kind = self.classify(self.original_name)
        super().save(*args, **kwargs)


class AutoNotice(models.Model):
    """One automatic notification waiting to go out (or already sent).

    Things that happen in the platform — a blueprint published, a test opening,
    a task assigned — queue a row here keyed by what happened (``key``), so the
    same event can never notify twice however often it is saved. A scheduler
    job (:func:`apps.communication.auto.run`) sends the rows whose ``due_at``
    has passed, checks each is still true at that moment (a material unpublished
    in the meantime is dropped) and folds several new items on one module into a
    single notification.
    """

    key = models.CharField(max_length=120, unique=True)
    kind = models.CharField(max_length=30, db_index=True)
    #: The object the event is about, as ``app_label.model:pk``.
    ref = models.CharField(max_length=80, blank=True)
    #: Groups items that can be folded into one notification (e.g. ``module:12``).
    group = models.CharField(max_length=60, blank=True, db_index=True)
    title = models.CharField(max_length=200)
    body = models.TextField(blank=True)
    url = models.CharField(max_length=500, blank=True)
    level = models.CharField(max_length=10, default='info')
    category = models.CharField(max_length=20, blank=True)
    #: Who it is for: the keyword arguments of ``broadcast.audience_users``.
    audience = models.JSONField(default=dict, blank=True)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                              blank=True, related_name='+')
    due_at = models.DateTimeField(default=timezone.now, db_index=True)
    sent_at = models.DateTimeField(null=True, blank=True, db_index=True)
    recipient_count = models.PositiveIntegerField(default=0)
    dropped = models.CharField(max_length=200, blank=True,
                               help_text='Why it was not sent, when it was not.')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['due_at', 'pk']

    def __str__(self):
        return self.key


# ===========================================================================
# Discussions (Q&A-style forum: posts, replies, media, tagging, likes)
# ===========================================================================
class Discussion(models.Model):
    """A discussion thread / post a user starts.

    Can be scoped to a :class:`learning.ProgrammeModule` so
    members of that course/module see it; tags and @mentions surface it to
    specific people. Supports media attachments and threaded replies (see
    :class:`DiscussionReply`).
    """

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        related_name='discussions',
    )
    title = models.CharField(max_length=255)
    body = models.TextField(blank=True)

    # Optional scope — a course or a module.
    module = models.ForeignKey(
        'learning.ProgrammeModule', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='discussions',
    )

    tags = models.CharField(max_length=255, blank=True, help_text='Comma separated')
    mentions = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name='mentioned_in_discussions',
    )
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name='liked_discussions',
    )

    is_pinned = models.BooleanField(default=False)
    is_closed = models.BooleanField(default=False)
    view_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_pinned', '-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('communication:discussion-detail', args=[self.pk])

    @property
    def tag_list(self):
        return [t.strip() for t in self.tags.split(',') if t.strip()]

    @property
    def reply_count(self):
        return self.replies.count()

    @property
    def like_count(self):
        return self.likes.count()


class DiscussionReply(models.Model):
    """A reply to a :class:`Discussion` (optionally nested via ``reply_to``)."""

    discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE, related_name='replies')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='discussion_replies',
    )
    body = models.TextField()
    reply_to = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True, related_name='child_replies',
    )
    mentions = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name='mentioned_in_replies',
    )
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name='liked_replies',
    )
    is_answer = models.BooleanField(default=False, help_text='Marked as the accepted answer.')
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Reply by {self.author} on {self.discussion}'

    @property
    def like_count(self):
        return self.likes.count()


class DiscussionAttachment(models.Model):
    """Media attached to a discussion or a reply (image / video / file)."""

    KIND_IMAGE = 'image'
    KIND_VIDEO = 'video'
    KIND_FILE = 'file'
    KIND_CHOICES = [(KIND_IMAGE, 'Image'), (KIND_VIDEO, 'Video'), (KIND_FILE, 'File')]

    IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg'}
    VIDEO_EXTS = {'.mp4', '.webm', '.mov', '.m4v', '.avi', '.mkv', '.ogg'}

    discussion = models.ForeignKey(
        Discussion, on_delete=models.CASCADE, null=True, blank=True, related_name='attachments',
    )
    reply = models.ForeignKey(
        DiscussionReply, on_delete=models.CASCADE, null=True, blank=True, related_name='attachments',
    )
    file = models.FileField(upload_to='discussions/%Y/%m/', storage=files_storage,
                            validators=v.validate_attachment)
    kind = models.CharField(max_length=10, choices=KIND_CHOICES, default=KIND_FILE)
    original_name = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.original_name or self.file.name

    @classmethod
    def classify(cls, filename):
        import os
        ext = os.path.splitext(filename or '')[1].lower()
        if ext in cls.IMAGE_EXTS:
            return cls.KIND_IMAGE
        if ext in cls.VIDEO_EXTS:
            return cls.KIND_VIDEO
        return cls.KIND_FILE

    def save(self, *args, **kwargs):
        if self.file and not self.original_name:
            self.original_name = getattr(self.file, 'name', '')
        if (not self.kind or self.kind == self.KIND_FILE) and self.original_name:
            self.kind = self.classify(self.original_name)
        super().save(*args, **kwargs)


# ===========================================================================
# Community Safety & Moderation (My Learning Hub plan, section 12)
# ===========================================================================
class Violation(models.Model):
    """A flagged piece of content with a risk score and category."""

    SOURCE_CHOICES = [
        ('chat', 'Chat'), ('dm', 'Direct message'), ('forum', 'Forum'),
        ('comment', 'Comment'), ('assignment', 'Assignment'), ('upload', 'Upload'),
        ('announcement', 'Announcement'), ('profile', 'Profile'),
    ]
    DETECTED_RULE = 'rule'
    DETECTED_AI = 'ai'
    DETECTED_REPORT = 'report'
    DETECTED_CHOICES = [(DETECTED_RULE, 'Rule'), (DETECTED_AI, 'AI'), (DETECTED_REPORT, 'User report')]

    # score: 0 Safe · 1 Warning · 2 Moderate · 3 High · 4 Severe.
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='violations')
    source = models.CharField(max_length=12, choices=SOURCE_CHOICES, default='chat')
    text = models.TextField(blank=True, help_text='Snapshot of the offending content (evidence).')
    category = models.CharField(max_length=40, blank=True)
    score = models.PositiveSmallIntegerField(default=0)
    message = models.ForeignKey(Message, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='violations')
    detected_by = models.CharField(max_length=8, choices=DETECTED_CHOICES, default=DETECTED_RULE)
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='reported_violations')
    evidence = models.JSONField(default=dict, blank=True)
    handled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['user', 'handled'], name='comm_violation_user_idx')]

    def __str__(self):
        return f'{self.user} · {self.category or "violation"} ({self.score})'


class Penalty(models.Model):
    """A penalty applied to a user (warning → mute → suspension → escalation)."""

    KIND_WARNING = 'warning'
    KIND_DELETE = 'delete'
    KIND_MUTE = 'mute'
    KIND_CHAT_SUSPEND = 'chat_suspend'
    KIND_CLASS_SUSPEND = 'class_suspend'
    KIND_PLATFORM_SUSPEND = 'platform_suspend'
    KIND_ESCALATE = 'escalate'
    KIND_CHOICES = [
        (KIND_WARNING, 'Warning'), (KIND_DELETE, 'Message deletion'), (KIND_MUTE, 'Temporary mute'),
        (KIND_CHAT_SUSPEND, 'Chat suspension'), (KIND_CLASS_SUSPEND, 'Class suspension'),
        (KIND_PLATFORM_SUSPEND, 'Platform suspension'), (KIND_ESCALATE, 'Escalated to staff'),
    ]
    # Penalty kinds that stop a user from sending messages while active.
    SILENCING = (KIND_MUTE, KIND_CHAT_SUSPEND, KIND_PLATFORM_SUSPEND)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='penalties')
    kind = models.CharField(max_length=18, choices=KIND_CHOICES, default=KIND_WARNING)
    reason = models.CharField(max_length=255, blank=True)
    violation = models.ForeignKey(Violation, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='penalties')
    issued_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='penalties_issued')
    starts_at = models.DateTimeField(default=timezone.now)
    ends_at = models.DateTimeField(null=True, blank=True, help_text='Blank = indefinite.')
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['user', 'active'], name='comm_penalty_user_idx')]

    def __str__(self):
        return f'{self.get_kind_display()} · {self.user}'

    def is_current(self):
        if not self.active:
            return False
        if self.ends_at and self.ends_at <= timezone.now():
            return False
        return True


class Appeal(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_ACCEPTED = 'accepted'
    STATUS_REJECTED = 'rejected'
    STATUS_CHOICES = [(STATUS_PENDING, 'Pending'), (STATUS_ACCEPTED, 'Accepted'), (STATUS_REJECTED, 'Rejected')]

    penalty = models.ForeignKey(Penalty, on_delete=models.CASCADE, related_name='appeals')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='appeals')
    message = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='appeals_reviewed')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Appeal by {self.user} ({self.get_status_display()})'


class ReputationScore(models.Model):
    """A community reputation score (100 = excellent). Violations lower it."""

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reputation')
    score = models.PositiveSmallIntegerField(default=100)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user}: {self.score}'


# ===========================================================================
# Attendance (automated class-session attendance — Learning Hub feature 2)
# ===========================================================================
class ClassSession(models.Model):
    """A single class session that attendance is recorded against.

    A session belongs to a :class:`accounts.ProgrammeModule` (the class) on a given
    date. It may optionally be backed by a live :class:`MeetingRoom` (a video
    class).

    **Attendance is automatic and time-based.** While a student has the session
    open their browser sends a heartbeat; each one accrues real seconds onto
    their :class:`Attendance` row (see
    :func:`apps.communication.services.record_presence_ping`). Once they have
    been present for :attr:`min_attendance_pct` of the session they are marked
    present automatically — merely opening the page is not enough. Educators,
    staff and admins can always override the result by hand, and a manual mark
    is never undone by a later heartbeat.
    """

    #: Attendance below this share of the session does not earn a "present".
    DEFAULT_MIN_ATTENDANCE_PCT = 50
    #: Used when a session has neither its own times nor a scheduled meeting.
    FALLBACK_DURATION_MINUTES = 60

    module = models.ForeignKey('learning.ProgrammeModule', on_delete=models.CASCADE,
                               null=True, blank=True, related_name='class_sessions')
    title = models.CharField(max_length=200, blank=True)
    session_date = models.DateField(default=timezone.localdate, db_index=True)
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    meeting = models.OneToOneField(
        MeetingRoom, on_delete=models.SET_NULL, null=True, blank=True, related_name='class_session',
    )
    late_after_minutes = models.PositiveIntegerField(
        default=10, help_text='A check-in this many minutes after the start counts as "late".')
    min_attendance_pct = models.PositiveIntegerField(
        default=DEFAULT_MIN_ATTENDANCE_PCT,
        help_text='Share of the session a student must actually attend to be auto-marked present.')
    is_open = models.BooleanField(
        default=True, help_text='While open, joining or checking-in records attendance.')
    #: Set by services.finalise_session_attendance once the roll is closed out —
    #: everyone below the threshold becomes absent and non-attendees get a row.
    finalised_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='class_sessions_created',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-session_date', '-starts_at']
        indexes = [models.Index(fields=['module', 'session_date'], name='comm_session_subj_idx')]

    def __str__(self):
        return f'{self.title or self.module} · {self.session_date}'

    # --- Timing -----------------------------------------------------------
    @property
    def scheduled_start(self):
        """The session's start — its own, else the backing meeting's."""
        return self.starts_at or getattr(self.meeting, 'scheduled_start', None)

    @property
    def scheduled_end(self):
        return self.ends_at or getattr(self.meeting, 'scheduled_end', None)

    @property
    def planned_seconds(self):
        """How long the session is meant to run, in seconds.

        Falls back to :attr:`FALLBACK_DURATION_MINUTES` when neither the session
        nor its meeting carries both times, so an ad-hoc class still produces a
        sane percentage rather than dividing by zero.
        """
        start, end = self.scheduled_start, self.scheduled_end
        if start and end and end > start:
            return int((end - start).total_seconds())
        return self.FALLBACK_DURATION_MINUTES * 60

    @property
    def has_ended(self):
        end = self.scheduled_end
        if end:
            return timezone.now() > end
        # No end time: treat it as over once the day has passed.
        return self.session_date < timezone.localdate()

    @property
    def is_live_now(self):
        start, end = self.scheduled_start, self.scheduled_end
        if not start:
            return self.is_open and self.session_date == timezone.localdate()
        now = timezone.now()
        return start <= now and (end is None or now <= end)

    @property
    def present_count(self):
        return self.attendance.filter(
            status__in=[Attendance.STATUS_PRESENT, Attendance.STATUS_LATE]).count()

    @property
    def absent_count(self):
        return self.attendance.filter(status=Attendance.STATUS_ABSENT).count()


class Attendance(models.Model):
    """One student's attendance for one :class:`ClassSession`.

    Presence is measured, not assumed: :attr:`seconds_attended` accumulates from
    heartbeats sent while the student actually has the session open, and the
    status is derived from that against the session's
    :attr:`ClassSession.min_attendance_pct`. An educator/staff/admin mark
    (``source='manual'``) overrides the measurement and is never undone by a
    later heartbeat.
    """

    STATUS_PRESENT = 'present'
    STATUS_LATE = 'late'
    STATUS_ABSENT = 'absent'
    STATUS_EXCUSED = 'excused'
    STATUS_CHOICES = [
        (STATUS_PRESENT, 'Present'), (STATUS_LATE, 'Late'),
        (STATUS_ABSENT, 'Absent'), (STATUS_EXCUSED, 'Excused'),
    ]

    SOURCE_AUTO = 'auto'      # measured by the in-page presence heartbeat
    SOURCE_TEAMS = 'teams'    # measured by the Microsoft Graph attendance report
    SOURCE_LOGIN = 'login'    # self check-in
    #: Studied the module's lesson content on the day of the session.
    SOURCE_LESSON = 'lesson'
    #: Signed in and used the platform that day, but did not touch this module.
    SOURCE_ACTIVE = 'active'
    SOURCE_MANUAL = 'manual'  # set by an educator / admin — wins over the rest
    SOURCE_CHOICES = [(SOURCE_AUTO, 'Auto (page time)'), (SOURCE_TEAMS, 'Teams report'),
                      (SOURCE_LOGIN, 'Check-in'), (SOURCE_LESSON, 'Lesson studied'),
                      (SOURCE_ACTIVE, 'On the platform'), (SOURCE_MANUAL, 'Manual')]

    session = models.ForeignKey(ClassSession, on_delete=models.CASCADE, related_name='attendance')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='attendance_records')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PRESENT, db_index=True)
    source = models.CharField(max_length=8, choices=SOURCE_CHOICES, default=SOURCE_MANUAL)
    check_in_at = models.DateTimeField(null=True, blank=True)

    # --- Measured presence (written by services.record_presence_ping) ---
    seconds_attended = models.PositiveIntegerField(
        default=0, help_text='Seconds the student was actually present, from heartbeats.')
    first_seen_at = models.DateTimeField(null=True, blank=True)
    last_seen_at = models.DateTimeField(null=True, blank=True)

    marked_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='attendance_marked')
    note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('session', 'student')
        ordering = ['session', 'student']

    def __str__(self):
        return f'{self.student} · {self.session} ({self.get_status_display()})'

    @property
    def minutes_attended(self):
        return round(self.seconds_attended / 60)

    @property
    def attended_pct(self):
        """Share of the session the student was actually present for (0–100)."""
        planned = self.session.planned_seconds
        if not planned:
            return 0
        return min(100, round(self.seconds_attended / planned * 100))

    @property
    def meets_threshold(self):
        return self.attended_pct >= (self.session.min_attendance_pct or 0)

    @property
    def is_manual(self):
        """True when an educator set this by hand — heartbeats must not touch it."""
        return self.source == self.SOURCE_MANUAL


# ===========================================================================
# Notification preferences (customizable notifications — Learning Hub feature 3)
# ===========================================================================
class NotificationPreference(models.Model):
    """Per-user delivery preferences for notifications & reminders.

    Channels (in-app is always on) and per-category switches are honoured by
    :func:`apps.communication.services.notify` and the reminder scan; a digest
    setting and quiet hours let users throttle e-mail.
    """

    DIGEST_OFF = 'off'
    DIGEST_DAILY = 'daily'
    DIGEST_WEEKLY = 'weekly'
    DIGEST_CHOICES = [(DIGEST_OFF, 'Send immediately'), (DIGEST_DAILY, 'Daily digest'),
                      (DIGEST_WEEKLY, 'Weekly digest')]

    # Categories — used as the ``category`` argument to ``notify(...)``.
    CATEGORIES = ['mentions', 'messages', 'announcements', 'deadlines', 'meetings', 'grades',
                  'content', 'assessments', 'tasks', 'weekly']

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notification_preference')

    # Channels. In-app is always on — the bell is the platform's own record.
    # The other two are copies of it, and a person can take both, either or
    # neither: e-mail for the paper trail, WhatsApp for the one they will
    # actually see today.
    email_enabled = models.BooleanField(default=True, help_text='Also deliver a copy by e-mail.')
    whatsapp_enabled = models.BooleanField(
        default=False,
        help_text='Also deliver a copy by WhatsApp, to the number on your contact details.')
    browser_enabled = models.BooleanField(default=True, help_text='Show desktop / browser notifications.')

    # Categories (which kinds of notification to receive at all)
    notify_mentions = models.BooleanField(default=True)
    notify_messages = models.BooleanField(default=True)
    notify_announcements = models.BooleanField(default=True)
    notify_deadlines = models.BooleanField(default=True, help_text='Upcoming task / assessment deadlines.')
    notify_meetings = models.BooleanField(default=True, help_text='Live sessions & meeting invites.')
    notify_grades = models.BooleanField(default=True, help_text='New grades & certificates.')
    notify_content = models.BooleanField(
        default=True, help_text='New material on your modules: blueprints, mock exams, solutions, lessons, videos.')
    notify_assessments = models.BooleanField(
        default=True, help_text='A test, quiz or mock exam opening, and solutions being released.')
    notify_tasks = models.BooleanField(default=True, help_text='A task being assigned to you.')
    notify_weekly = models.BooleanField(
        default=True, help_text='A Monday-morning summary of the week ahead.')

    # Delivery throttling
    digest = models.CharField(max_length=8, choices=DIGEST_CHOICES, default=DIGEST_OFF)
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)
    reminder_lead_minutes = models.PositiveIntegerField(
        default=60, help_text='How long before a deadline / session to remind you.')

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Notification preferences · {self.user}'

    @classmethod
    def for_user(cls, user):
        pref, _ = cls.objects.get_or_create(user=user)
        return pref

    def allows(self, category):
        """True if the user wants notifications of this ``category`` at all."""
        return bool(getattr(self, f'notify_{category}', True)) if category else True

    def allows_email(self, category=None):
        return self.email_enabled and self.allows(category)

    def allows_whatsapp(self, category=None):
        return self.whatsapp_enabled and self.allows(category)

    @property
    def channels(self):
        """The channels this person has switched on, for showing back to them."""
        picked = ['in-app']
        if self.email_enabled:
            picked.append('e-mail')
        if self.whatsapp_enabled:
            picked.append('WhatsApp')
        return picked

    def in_quiet_hours(self, now=None):
        """True if the current local time falls inside the user's quiet hours."""
        if not self.quiet_hours_start or not self.quiet_hours_end:
            return False
        now = now or timezone.localtime()
        t_now = now.time()
        start, end = self.quiet_hours_start, self.quiet_hours_end
        if start <= end:
            return start <= t_now <= end
        # Overnight window (e.g. 22:00 → 07:00).
        return t_now >= start or t_now <= end


# ===========================================================================
# Group collaboration workspaces (shared files + notes — Learning Hub feature 4)
# ===========================================================================
class Workspace(models.Model):
    """A shared collaboration space for a class/group or a module.

    Complements the existing chat + discussion forum with a place to keep
    shared **files** and collaborative **notes / project areas**. Access is open
    to admins/staff, the workspace's creator, explicit ``members`` and anyone
    enrolled in the linked course or module.
    """

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    module = models.ForeignKey('learning.ProgrammeModule', on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='workspaces')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='workspaces_created')
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='workspaces')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('communication:workspace-detail', args=[self.pk])

    def can_access(self, user):
        if not user or not user.is_authenticated:
            return False
        if user.is_staff or user.is_superuser:
            return True
        if self.created_by_id == user.id or self.members.filter(pk=user.pk).exists():
            return True
        person = getattr(user, 'profile', None)
        if person:
            if self.module_id and self.module.member_people.filter(pk=person.pk).exists():
                return True
        return False


class WorkspaceFile(models.Model):
    """A shared file in a :class:`Workspace` (simple re-upload versioning)."""

    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='workspaces/%Y/%m/', storage=files_storage,
                            validators=v.validate_attachment)
    title = models.CharField(max_length=200, blank=True)
    original_name = models.CharField(max_length=255, blank=True)
    size = models.PositiveBigIntegerField(default=0)
    version = models.PositiveIntegerField(default=1)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='workspace_files')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title or self.original_name or self.file.name

    def save(self, *args, **kwargs):
        if self.file and not self.original_name:
            self.original_name = getattr(self.file, 'name', '')[:255]
        if self.file and not self.size:
            try:
                self.size = self.file.size
            except (OSError, ValueError):
                self.size = 0
        super().save(*args, **kwargs)


class MailMessage(models.Model):
    """An in-system e-mail composed by an admin/staff/educator. On send it's
    stored here (an internal mailbox) *and* delivered as a real branded e-mail
    to each recipient's registered address, with the sender's address as
    reply-to (so replies go straight back to them)."""

    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_mail')
    sender_email = models.CharField(max_length=254, blank=True, help_text='Sender registered e-mail (used as reply-to).')
    subject = models.CharField(max_length=255, help_text='The e-mail subject line.')
    body = models.TextField(blank=True)
    external_to = models.CharField(max_length=500, blank=True, help_text='Comma-separated external addresses (no in-system inbox).')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.subject or f'Mail #{self.pk}'

    @property
    def recipient_names(self):
        names = [r.recipient.get_full_name() or r.recipient.get_username() for r in self.recipients.all()]
        if self.external_to:
            names.append(self.external_to)
        return ', '.join(names)


class MailRecipient(models.Model):
    """One recipient's copy of a :class:`MailMessage` (their inbox row)."""

    message = models.ForeignKey(MailMessage, on_delete=models.CASCADE, related_name='recipients')
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_mail')
    is_read = models.BooleanField(default=False, db_index=True)
    starred = models.BooleanField(default=False)
    trashed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('message', 'recipient')
        ordering = ['-message__created_at']

    def __str__(self):
        return f'{self.message} → {self.recipient}'


class WorkspaceNote(models.Model):
    """A collaborative note / project area within a :class:`Workspace`."""

    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='notes')
    title = models.CharField(max_length=200)
    body = models.TextField(blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='workspace_notes')
    pinned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-pinned', '-updated_at']

    def __str__(self):
        return self.title


class Feed(models.Model):
    """A user-authored post in the unified activity feed — a status update with
    optional image / video / file, or an event share. Aggregated together with
    announcements, notifications, messages, tasks, calendar events and reminders
    by :func:`apps.communication.feed.build_feed` for the dashboard / social page."""

    VIS_PUBLIC = 'public'
    VIS_GROUPS = 'groups'
    VIS_STAFF = 'staff'
    VISIBILITY_CHOICES = [
        (VIS_PUBLIC, 'Everyone'),
        (VIS_GROUPS, 'My courses & modules'),
        (VIS_STAFF, 'Staff & admins'),
    ]
    KIND_TEXT = 'text'
    KIND_IMAGE = 'image'
    KIND_VIDEO = 'video'
    KIND_FILE = 'file'
    KIND_EVENT = 'event'

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='feed_posts')
    body = models.TextField(blank=True)
    media = models.FileField(upload_to='feed/%Y/%m/', blank=True, null=True, storage=files_storage,
                             validators=v.validate_media)
    media_kind = models.CharField(max_length=10, blank=True)   # image / video / file
    kind = models.CharField(max_length=10, default=KIND_TEXT)
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default=VIS_PUBLIC)
    group = models.ForeignKey('ChatGroup', on_delete=models.SET_NULL, null=True, blank=True, related_name='feed_posts')
    # Which module this post belongs to, so the feed's module filter can pick
    # it up. Blank = a general post, only visible under "General".
    module = models.ForeignKey('learning.ProgrammeModule', on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='feed_posts')
    # ``likes`` is authoritative (one row per person, so a like can be undone and
    # can't be spammed); ``like_count`` is the denormalised total the feed reads.
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_feed_posts', blank=True)
    like_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.author} · {(self.body or self.kind)[:40]}'

    def toggle_like(self, user):
        """Add or remove ``user``'s like and resync the counter. Returns
        ``(liked, count)``."""
        if self.likes.filter(pk=user.pk).exists():
            self.likes.remove(user)
            liked = False
        else:
            self.likes.add(user)
            liked = True
        self.like_count = self.likes.count()
        self.save(update_fields=['like_count'])
        return liked, self.like_count

    @classmethod
    def visible_to(cls, user):
        """Posts the given user is allowed to see (their groups / class, plus
        public posts and — for staff/admins — staff-only posts)."""
        from django.db.models import Q
        qs = cls.objects.select_related('author', 'author__profile', 'group', 'module')
        if not user.is_authenticated:
            return qs.filter(visibility=cls.VIS_PUBLIC)
        if user.is_staff or user.is_superuser:
            return qs
        group_ids = list(ChatGroup.objects.filter(memberships__user=user).values_list('id', flat=True))
        return qs.filter(
            Q(author=user)
            | Q(visibility=cls.VIS_PUBLIC)
            | Q(visibility=cls.VIS_GROUPS, group__isnull=True)
            | Q(visibility=cls.VIS_GROUPS, group_id__in=group_ids)
        ).distinct()


class FeedAttachment(models.Model):
    """A file attached to a :class:`Feed` post — an image, a video or a generic
    file. A post can carry several; the feed tiles them into a gallery. Mirrors
    :class:`MessageAttachment` so uploads classify and label themselves the same
    way. The legacy single ``Feed.media`` field is kept for old posts; new posts
    store every file here instead.
    """

    KIND_IMAGE = 'image'
    KIND_VIDEO = 'video'
    KIND_FILE = 'file'
    KIND_CHOICES = [(KIND_IMAGE, 'Image'), (KIND_VIDEO, 'Video'), (KIND_FILE, 'File')]

    feed = models.ForeignKey('Feed', on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='feed/%Y/%m/', storage=files_storage,
                            validators=v.validate_media)
    kind = models.CharField(max_length=10, choices=KIND_CHOICES, default=KIND_FILE)
    original_name = models.CharField(max_length=255, blank=True)
    size = models.PositiveBigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg'}
    VIDEO_EXTS = {'.mp4', '.webm', '.mov', '.m4v', '.avi', '.mkv', '.ogg'}

    class Meta:
        ordering = ['created_at', 'pk']

    def __str__(self):
        return self.original_name or self.file.name

    @classmethod
    def classify(cls, filename):
        import os
        ext = os.path.splitext(filename or '')[1].lower()
        if ext in cls.IMAGE_EXTS:
            return cls.KIND_IMAGE
        if ext in cls.VIDEO_EXTS:
            return cls.KIND_VIDEO
        return cls.KIND_FILE

    def save(self, *args, **kwargs):
        if self.file and not self.original_name:
            self.original_name = getattr(self.file, 'name', '')
        if self.file and not self.size:
            try:
                self.size = self.file.size
            except (OSError, ValueError):
                self.size = 0
        if (not self.kind or self.kind == self.KIND_FILE) and self.original_name:
            self.kind = self.classify(self.original_name)
        super().save(*args, **kwargs)


class FeedComment(models.Model):
    """A comment on a :class:`Feed` post (the feed's own comment thread)."""

    post = models.ForeignKey(Feed, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='feed_comments')
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.author}: {self.body[:40]}'


# ===========================================================================
# WhatsApp — the two-way channel
# ===========================================================================
class WhatsAppMessage(models.Model):
    """One message in or out on WhatsApp — the bot's transcript.

    Everything is kept: what the student asked, what the bot answered, and the
    notification copies pushed out to them. Three reasons, all practical.
    ``wa_id`` makes inbound handling idempotent (Meta re-delivers a webhook until
    it gets a 200, so the same message arrives more than once). The transcript
    lets staff see what a student was told when they say "the bot said my test
    was Friday". And the *inbound* timestamps are what decide whether a free-form
    reply is allowed at all — Meta only permits one within 24 hours of the
    person's last message (see :func:`core.whatsapp.send_text`).
    """

    IN = 'in'
    OUT = 'out'
    DIRECTION_CHOICES = [(IN, 'Received'), (OUT, 'Sent')]

    KIND_TEXT = 'text'
    KIND_DOCUMENT = 'document'
    KIND_NOTIFICATION = 'notification'
    KIND_OTHER = 'other'
    KIND_CHOICES = [
        (KIND_TEXT, 'Text'),
        (KIND_DOCUMENT, 'Document'),
        (KIND_NOTIFICATION, 'Notification copy'),
        (KIND_OTHER, 'Other'),
    ]

    direction = models.CharField(max_length=3, choices=DIRECTION_CHOICES, db_index=True)
    number = models.CharField(max_length=20, db_index=True,
                              help_text='The person\'s number, digits only (2782…).')
    # Null when the number belongs to nobody on the platform — those are kept
    # too, because "somebody messaged us from an unknown number" is a thing
    # staff need to be able to see.
    person = models.ForeignKey('accounts.Person', on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='whatsapp_messages')
    kind = models.CharField(max_length=12, choices=KIND_CHOICES, default=KIND_TEXT)
    body = models.TextField(blank=True)
    # The command the bot matched, when it recognised one — makes it obvious
    # from the transcript why it answered the way it did.
    command = models.CharField(max_length=30, blank=True, db_index=True)
    wa_id = models.CharField(max_length=128, blank=True, db_index=True,
                             help_text="Meta's message id — inbound de-duplication.")
    payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['number', '-created_at'])]
        constraints = [
            models.UniqueConstraint(fields=['wa_id'], condition=models.Q(direction='in'),
                                    name='uniq_inbound_whatsapp_message'),
        ]
        verbose_name = 'WhatsApp message'

    def __str__(self):
        arrow = '←' if self.direction == self.IN else '→'
        return f'{arrow} {self.number}: {(self.body or self.kind)[:50]}'

    @classmethod
    def within_service_window(cls, number, hours=24):
        """True when this number messaged us recently enough for a free-form reply.

        Meta's rule, not ours: outside 24 hours from the person's last inbound
        message only an approved template may be sent.
        """
        from datetime import timedelta
        cutoff = timezone.now() - timedelta(hours=hours)
        return cls.objects.filter(direction=cls.IN, number=number,
                                  created_at__gte=cutoff).exists()
