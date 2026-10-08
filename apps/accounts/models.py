"""Core identity & user structure models.

This app provides the *universal* pieces every United Church School deployment
needs for user management:

* :class:`Person` — a profile attached one-to-one to Django's ``auth.User``.
* :class:`Group` — a sub-unit for organizing people (team, group, etc.)
  with a leader and members.
* :class:`Program` — an activity offered to users (course, study group,
  project, …) with a facilitator and participants.
* :class:`ActivityLog` — an audit trail of create/update/delete/login/logout
  events, populated by the signal handlers in :mod:`apps.accounts.signals`.
"""

import uuid
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone

from core import validators as v


# ---------------------------------------------------------------------------
# Choice constants (shared across the models below)
# ---------------------------------------------------------------------------
GENDER_CHOICES = [
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other'),
]

TITLE_CHOICES = [
    ('mr', 'Mr'), ('mrs', 'Mrs'), ('ms', 'Ms'), ('miss', 'Miss'),
    ('dr', 'Dr'), ('prof', 'Prof'),
]

# Who pays for the studies. Asked once, on the "About you" step of registration,
# right under the parent/guardian question it follows on from.
FUNDING_SOURCE_CHOICES = [
    ('self', 'Self'), ('parent', 'Parent / Guardian'), ('employer', 'Employer'),
    ('nsfas', 'NSFAS'), ('government', 'Government'), ('scholarship', 'Scholarship'),
    ('company', 'Company'), ('other', 'Other'),
]

# The device the learner mostly studies on — used to tune the experience.
DEVICE_CHOICES = [
    ('laptop', 'Laptop'), ('desktop', 'Desktop'), ('tablet', 'Tablet'), ('phone', 'Phone'),
]

# Role a person plays inside their organisation.
USER_TYPE_CHOICES = [
    ('student', 'Student'),
    ('admin', 'Admin'),
    ('staff', 'Staff'),
    ('parent', 'Parent'),
    ('educator', 'Educator'),
]


# ---------------------------------------------------------------------------
# Person (user profile)
# ---------------------------------------------------------------------------
def profile_picture_path(instance, filename):
    """A fresh name for every upload.

    Replacing a picture deletes the old file first (core.file_cleanup), so a
    second "photo.jpg" used to land on the very same path. Same URL, so browsers
    kept showing the cached old picture. A new name per upload means a new URL.
    """
    import os
    ext = os.path.splitext(filename or '')[1].lower()[:8] or '.jpg'
    return f'profile_pics/{uuid.uuid4().hex[:16]}{ext}'


#: Shown when someone has not uploaded a picture, chosen by gender (or, failing
#: that, by title). Static files, so every page can render them for free.
DEFAULT_AVATARS = {
    'male': 'images/avatar/default-male.svg',
    'female': 'images/avatar/default-female.svg',
    'neutral': 'images/avatar/default-neutral.svg',
}
_TITLE_GENDER = {'mr': 'male', 'mrs': 'female', 'ms': 'female', 'miss': 'female'}


def default_avatar_url(gender='', title=''):
    """The static URL of the default avatar for this gender / title."""
    from django.templatetags.static import static
    key = gender if gender in ('male', 'female') else _TITLE_GENDER.get(title or '', 'neutral')
    return static(DEFAULT_AVATARS[key])


class Person(models.Model):
    """Profile data for a Django ``auth.User``.

    Created automatically whenever a ``User`` is created (see
    :func:`apps.accounts.signals.create_person_profile`) and reachable from the
    user instance as ``user.profile``.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile',
    )

    # --- Personal information ---
    # ``title`` sits with the name it belongs to (it used to live on
    # PersonContact, a step away from the first/last name it prefixes).
    title = models.CharField(max_length=10, choices=TITLE_CHOICES, blank=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to=profile_picture_path, blank=True, null=True,
                                        validators=v.validate_avatar)

    # --- Study context ---
    # Both were one-field side-tables of their own (PersonFunding, PersonTech).
    # They are asked together in the "About you" step, so they live here now and
    # those two tables are gone.
    funding_source = models.CharField(
        'Who pays the fees', max_length=20, choices=FUNDING_SOURCE_CHOICES, blank=True)
    primary_device = models.CharField(
        'Primary learning device', max_length=12, choices=DEVICE_CHOICES, blank=True)

    # --- Role / status ---
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='student')
    # True once the profile has been completed by the user.
    profile_status = models.BooleanField(default=False)

    # --- Onboarding / registration ---
    # Set True once the user has completed the post-signup registration step
    # (chosen their role + what they are registering for). Together with
    # ``profile_status`` this gates access to the dashboard (see
    # apps.accounts.middleware.OnboardingMiddleware).
    registered = models.BooleanField(default=False)
    phone = models.CharField(max_length=30, blank=True)
    # Token used to build the "invite a parent" registration link for a student.
    parent_invite_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    # The student's PRIMARY / current course. Kept as a single FK for backward
    # compatibility (many views/e-mails/search compare ``person.course_id``);
    # it points at the most recently enrolled course. The full set of courses a
    # student is enrolled in lives in ``courses`` (M2M) below.
    # All courses the student is enrolled in (multi-course enrolment). ``course``
    # above is whichever of these is current/primary. Enrolment is managed by
    # apps.accounts.services.enrol_person, which keeps the two in sync.
    enrolled_class = models.CharField('Class', max_length=80, blank=True)
    # Learner identifiers the Department of Education uses (SA-SAMS / LURITS).
    admission_number = models.CharField(
        'Admission number', max_length=20, blank=True, db_index=True,
        help_text="The school's own learner number (SA-SAMS admission / accession number).")
    lurits_number = models.CharField(
        'LURITS number', max_length=20, blank=True, db_index=True,
        help_text='Learner Unit Record Information and Tracking System number issued by the DBE.')
    # Microsoft 365 / Teams user principal name (e.g. teacher@school.onmicrosoft.com).
    # When set for an educator, live classes are hosted under their licensed Teams
    # account; otherwise the account e-mail or MS_GRAPH_DEFAULT_ORGANIZER is used.
    # Read by apps.msteams.services.organizer_upn_for.
    ms_upn = models.CharField('Microsoft Teams UPN', max_length=255, blank=True)
    # For parents/guardians: the student they are registering on behalf of.
    child_name = models.CharField('Child / dependant name', max_length=160, blank=True)

    # --- Legal / consent ---
    # When the user accepted the Terms & Conditions, captured server-side at
    # signup (see apps.accounts.forms.UCSSignupForm). Null for accounts
    # provisioned by an administrator, or created before consent was recorded.
    terms_accepted_at = models.DateTimeField(null=True, blank=True)
    # Which revision of the terms was accepted, so a re-consent prompt can tell
    # who has only agreed to a superseded version.
    terms_version = models.CharField(max_length=20, blank=True)

    # Enrolment checkout gate: the ``public_id`` of the invoice the user must
    # settle — pay it, or confirm a free (0-cost) enrolment — before the
    # onboarding gate lifts. Stored as a UUID rather than a FK to avoid an
    # accounts↔finance migration cycle. Cleared once the invoice is paid.
    pending_invoice_uid = models.UUIDField(null=True, blank=True)
    # The invite this account signed up through (parent/educator flows). Drives
    # user_type + which single-page registration they get; None = a normal
    # student self-registration. See apps.accounts.models.Invitation.
    invite = models.ForeignKey(
        'accounts.Invitation', on_delete=models.SET_NULL, null=True, blank=True, related_name='+',
    )
    # E-mail addresses of parents/guardians/sponsors the STUDENT entered during
    # registration; each is sent an invite when the student's enrolment settles.
    guardian_emails = models.JSONField(default=list, blank=True)

    @property
    def has_own_picture(self):
        return bool(self.profile_picture)

    @property
    def avatar_url(self):
        """The uploaded picture, or the default that matches their gender / title."""
        if self.profile_picture:
            try:
                return self.profile_picture.url
            except ValueError:      # the row names a file storage no longer has
                pass
        return default_avatar_url(self.gender or '', self.title or '')

    # The course the student is registering for, awaiting payment. When the
    # enrolment invoice settles, the payment hook enrols them into it (auto mode)
    # and clears this. Separate from ``course`` (which means "already enrolled").
    def __str__(self):
        full_name = f'{self.first_name} {self.last_name}'.strip()
        if full_name:
            return full_name
        from core.utils import display_name
        return display_name(self.user)

    def get_pending_invoice(self):
        """The unsettled enrolment invoice for this person, or ``None``."""
        if not self.pending_invoice_uid:
            return None
        from apps.finance.models import Invoice
        return Invoice.objects.filter(public_id=self.pending_invoice_uid).first()

    @property
    def enrolment_settled(self):
        """True when no unpaid enrolment invoice is blocking access."""
        if not self.pending_invoice_uid:
            return True
        inv = self.get_pending_invoice()
        return inv is None or inv.status == 'paid'

    @property
    def onboarding_complete(self):
        """True once registration, profile AND the enrolment payment are done."""
        return bool(self.registered and self.profile_status and self.enrolment_settled)

    # --- New academic-spine enrolment (Institution → Programme → ProgrammeModule) ---
    # These replace the legacy ``course`` / ``courses`` enrolment. Backed by
    # apps.learning.models.ProgrammeEnrolment / ModuleEnrolment (kept in the
    # learning app to avoid an accounts↔learning dependency cycle).
    @property
    def enrolled_programmes(self):
        """Programmes this student is registered for."""
        from apps.learning.models import Programme
        return Programme.objects.filter(
            enrolments__person=self, enrolments__is_active=True,
        ).distinct()

    @property
    def enrolled_modules(self):
        """ProgrammeModules the student currently has access to (paid or on trial).

        Trial expiry is enforced precisely at access time by
        :meth:`apps.learning.models.ModuleEnrolment.is_unlocked`; this queryset is
        the fast "modules that aren't locked" list for dashboards/menus.
        """
        from apps.learning.models import ModuleEnrolment, ProgrammeModule
        return ProgrammeModule.objects.filter(
            enrolments__person=self,
            enrolments__status__in=[ModuleEnrolment.STATUS_TRIAL, ModuleEnrolment.STATUS_ACTIVE],
        ).distinct()

    @property
    def selected_modules(self):
        """Every module the student has an enrolment row for — locked ones included."""
        from apps.learning.models import ProgrammeModule
        return ProgrammeModule.objects.filter(enrolments__person=self).distinct()

    @property
    def programme(self):
        """The programme this candidate is registered for, or ``None``.

        Enrolment is by grade, so this is almost always a single
        row; where someone holds more than one, the most recent active
        registration is the one that answers "what are they studying?".
        """
        enrolment = (self.programme_enrolments
                     .filter(is_active=True)
                     .select_related('programme__institution')
                     .order_by('-created_at')
                     .first())
        return enrolment.programme if enrolment else None


# ---------------------------------------------------------------------------
# Extended profile — grouped side-tables normalised out of Person
# ---------------------------------------------------------------------------
# Registration asks for three things: who you are, how to reach you, and what
# you consent to. That is one side-table (PersonContact) plus the consent
# record; the rest of Person's detail lives on Person itself.
#
# PersonEducation, PersonFunding and PersonTech used to sit here too — a table
# each for a couple of optional fields nobody was answering. Funding and device
# moved onto Person (they are asked in "About you"); education was dropped.

# Bump when the POPIA consent wording changes materially, so a re-consent prompt
# can tell who has only agreed to a superseded version.
CONSENT_VERSION = '2026-07'


class PersonContact(models.Model):
    """How to reach a person, and roughly where they are.

    One phone number, stored with the country it belongs to. ``phone_country``
    is the ISO-3166 alpha-2 code the picker was left on (e.g. ``ZA``);
    ``primary_phone`` holds the number as typed, dialling code included. Keeping
    the code lets the picker come back to the right country when the form is
    re-opened, without having to parse the number back apart.
    """
    person = models.OneToOneField('accounts.Person', on_delete=models.CASCADE, related_name='contact')
    # contact — one number, which is also the WhatsApp number
    phone_country = models.CharField('Phone country', max_length=2, blank=True, default='ZA')
    primary_phone = models.CharField('Phone number (WhatsApp)', max_length=30, blank=True)
    # location — area (suburb), city and province only
    suburb = models.CharField('Area / suburb', max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    province = models.CharField(max_length=100, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Contact · {self.person}'


class PersonStudyProfile(models.Model):
    """The student's own academic-calendar dates, kept as JSON lists.

    Edited on the settings page (Calendar tab), not at registration — the
    registration-time "study goals" question is gone.
    """
    person = models.OneToOneField('accounts.Person', on_delete=models.CASCADE, related_name='study_profile')
    # academic calendar — lists of {'label': str, 'date': 'YYYY-MM-DD'}
    exam_dates = models.JSONField(default=list, blank=True)
    assignment_dates = models.JSONField(default=list, blank=True)
    practical_dates = models.JSONField(default=list, blank=True)
    vacation_dates = models.JSONField(default=list, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Study profile · {self.person}'


class PersonConsent(models.Model):
    """POPIA consent record. ``privacy_policy_accepted`` and
    ``data_processing_accepted`` are the mandatory basis for operating the LMS;
    the rest are optional opt-ins. The audit fields (date/version/IP/device) and
    the data-subject-rights timestamps satisfy POPIA accountability."""
    person = models.OneToOneField('accounts.Person', on_delete=models.CASCADE, related_name='consent')
    # mandatory — required to operate the LMS
    privacy_policy_accepted = models.BooleanField(default=False)
    data_processing_accepted = models.BooleanField(default=False)
    # optional opt-ins
    marketing_consent = models.BooleanField(default=False)
    research_consent = models.BooleanField(default=False)
    ai_personalisation_consent = models.BooleanField(default=False)
    analytics_consent = models.BooleanField(default=False)
    cookie_consent = models.BooleanField(default=False)
    data_sharing_consent = models.BooleanField(default=False)
    # audit
    consent_date = models.DateTimeField(null=True, blank=True)
    consent_version = models.CharField(max_length=20, blank=True)
    consent_ip = models.GenericIPAddressField(null=True, blank=True)
    consent_device = models.CharField(max_length=300, blank=True)   # user-agent
    # POPIA data-subject rights
    account_deletion_requested = models.DateTimeField(null=True, blank=True)
    data_export_requested = models.DateTimeField(null=True, blank=True)
    data_retention_expiry = models.DateField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Consent · {self.person}'


# ---------------------------------------------------------------------------
# ProgrammeModule (a module within a Course)
# ---------------------------------------------------------------------------
class ActivityLog(models.Model):
    """One row per audited event. Written by :mod:`apps.accounts.signals`;
    exposed read-only via the admin and the REST API."""

    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('login', 'Login'),
        ('logout', 'Logout'),
    ]

    # Who triggered the event (the logged-in user), if known.
    actor = models.ForeignKey(
        Person, null=True, blank=True, on_delete=models.SET_NULL, related_name='actions_performed',
    )
    # Who/what the event was about (e.g. the user that was edited).
    target_user = models.ForeignKey(
        Person, null=True, blank=True, on_delete=models.SET_NULL, related_name='actions_received',
    )

    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.TextField(blank=True)

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    request_path = models.CharField(max_length=255, null=True, blank=True)

    timestamp = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['action']),
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        return f'{self.action} - {self.timestamp}'


# ---------------------------------------------------------------------------
# Parent ↔ student links (a regular user may have up to two parents/guardians)
# ---------------------------------------------------------------------------
class ParentLink(models.Model):
    """Links a parent/guardian account to the student (regular user) they look
    after. A student may have at most :attr:`MAX_PER_STUDENT` parents."""

    MAX_PER_STUDENT = 2

    parent = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='guardian_of',
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='guardians',
    )
    relationship = models.CharField(max_length=60, blank=True, help_text='e.g. Mother, Sponsor')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('parent', 'student')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.parent} → {self.student}'

    @classmethod
    def count_for_student(cls, student):
        return cls.objects.filter(student=student).count()

    @classmethod
    def can_add_parent(cls, student):
        return cls.count_for_student(student) < cls.MAX_PER_STUDENT


# ---------------------------------------------------------------------------
# Invitation — invite a parent/guardian/sponsor or an educator to register
# ---------------------------------------------------------------------------
class Invitation(models.Model):
    """A single-use invite to register with a pre-decided role.

    A parent/guardian/sponsor invite is tied to a ``student`` (the Person they
    look after); an educator invite is tied to a ``programme`` they will teach.
    Clicking the link routes the invitee through the normal sign-up (create +
    verify account), then a single registration page for their role. The invite
    is **consumed** (``accepted``) once they finish — the link then stops
    working. The role means the invitee never has to pick student/parent/educator.
    """
    ROLE_PARENT = 'parent'
    ROLE_EDUCATOR = 'educator'
    ROLE_CHOICES = [(ROLE_PARENT, 'Parent / Guardian / Sponsor'), (ROLE_EDUCATOR, 'Educator')]

    STATUS_PENDING = 'pending'
    STATUS_ACCEPTED = 'accepted'
    STATUS_REVOKED = 'revoked'
    STATUS_CHOICES = [(STATUS_PENDING, 'Pending'), (STATUS_ACCEPTED, 'Accepted'), (STATUS_REVOKED, 'Revoked')]

    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    email = models.EmailField()
    # parent invites → the student; educator invites → the programme.
    student = models.ForeignKey(
        'accounts.Person', on_delete=models.CASCADE, null=True, blank=True, related_name='parent_invites')
    programme = models.ForeignKey(
        'learning.Programme', on_delete=models.CASCADE, null=True, blank=True, related_name='educator_invites')
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_invites')
    accepted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='accepted_invites')
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        target = self.student or self.programme or '—'
        return f'{self.get_role_display()} invite for {self.email} ({target})'

    @property
    def is_open(self):
        return self.status == self.STATUS_PENDING

    def accept(self, user):
        from django.utils import timezone as _tz
        self.status = self.STATUS_ACCEPTED
        self.accepted_by = user
        self.accepted_at = _tz.now()
        self.save(update_fields=['status', 'accepted_by', 'accepted_at'])


# ---------------------------------------------------------------------------
# UserSettings (per-user preferences, privacy & account-closure state)
# ---------------------------------------------------------------------------
class UserSettings(models.Model):
    """Functional per-user settings backing the community "Settings" hub.

    Holds the preference / privacy toggles the user controls from
    ``accounts:settings`` and the bookkeeping for the *close account* flow
    (soft-close now → 30-day grace → purge + archive by the
    ``purge_closed_accounts`` management command).
    """

    # Number of days a soft-closed account is kept before it is purged.
    GRACE_DAYS = 30

    VISIBILITY_PUBLIC = 'public'
    VISIBILITY_MEMBERS = 'members'
    VISIBILITY_PRIVATE = 'private'
    VISIBILITY_CHOICES = [
        (VISIBILITY_PUBLIC, 'Public — anyone signed in'),
        (VISIBILITY_MEMBERS, 'Members — people in my groups'),
        (VISIBILITY_PRIVATE, 'Private — only me'),
    ]

    THEME_LIGHT = 'light'
    THEME_DARK = 'dark'
    THEME_AUTO = 'auto'
    THEME_CHOICES = [
        (THEME_LIGHT, 'Light'),
        (THEME_DARK, 'Dark'),
        (THEME_AUTO, 'Match system'),
    ]

    DIGEST_OFF = 'off'
    DIGEST_DAILY = 'daily'
    DIGEST_WEEKLY = 'weekly'
    DIGEST_CHOICES = [
        (DIGEST_OFF, 'Never'),
        (DIGEST_DAILY, 'Daily'),
        (DIGEST_WEEKLY, 'Weekly'),
    ]

    # The three languages the interface is actually translated into. Offering a
    # language with no catalog behind it is worse than not offering it: the user
    # picks it, nothing changes, and they conclude the setting is broken.
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('fr', 'Français (French)'),
        ('pt', 'Português (Portuguese)'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='account_settings',
    )

    # --- Privacy ---
    profile_visibility = models.CharField(
        max_length=10, choices=VISIBILITY_CHOICES, default=VISIBILITY_MEMBERS,
        help_text='Who may see your member profile page.')
    show_email = models.BooleanField(
        default=False, help_text='Show your e-mail address on your profile.')
    show_activity = models.BooleanField(
        default=True, help_text='Show your recent activity on your profile.')
    allow_messages = models.BooleanField(
        default=True, help_text='Let other members start a direct chat with you.')

    # --- Preferences ---
    theme = models.CharField(max_length=6, choices=THEME_CHOICES, default=THEME_AUTO)
    language = models.CharField(max_length=8, choices=LANGUAGE_CHOICES, default='en')
    # Every stored datetime is UTC (``USE_TZ``); this is only how it is *shown*.
    # It exists because a live session is the one thing on the platform where
    # getting the hour wrong means missing it entirely — a candidate in Lagos and
    # one in Johannesburg must each read the start time in their own clock.
    # Blank = fall back to ``settings.TIME_ZONE``.
    timezone = models.CharField(
        max_length=64, blank=True,
        help_text='Your time zone. Session times, reminders and the calendar are '
                  'shown in it. Blank = the platform default.')
    # The secret in the personal calendar-feed URL. Google, Outlook and Apple all
    # subscribe to a plain URL with no sign-in, so the token *is* the
    # authentication — which is why it is regenerable: rotating it instantly
    # revokes every device and every person the old link was ever shared with.
    calendar_token = models.UUIDField(default=uuid.uuid4, editable=False, db_index=True)
    email_digest = models.CharField(
        max_length=8, choices=DIGEST_CHOICES, default=DIGEST_WEEKLY,
        help_text='How often to bundle non-urgent e-mail.')

    # --- Account closure bookkeeping (soft close → grace → purge) ---
    is_closing = models.BooleanField(default=False)
    closed_at = models.DateTimeField(null=True, blank=True)
    purge_at = models.DateTimeField(null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'user settings'
        verbose_name_plural = 'user settings'

    def __str__(self):
        return f'Settings · {self.user}'

    @classmethod
    def for_user(cls, user):
        """Get-or-create the settings row for ``user``."""
        obj, _ = cls.objects.get_or_create(user=user)
        return obj

    def mark_closing(self, now=None):
        """Flag the account as closing and stamp the 30-day purge deadline."""
        now = now or timezone.now()
        self.is_closing = True
        self.closed_at = now
        self.purge_at = now + timedelta(days=self.GRACE_DAYS)
        self.save(update_fields=['is_closing', 'closed_at', 'purge_at', 'updated_at'])
        return self

    def cancel_closing(self):
        """Undo a pending closure (an admin can reactivate the account)."""
        self.is_closing = False
        self.closed_at = None
        self.purge_at = None
        self.save(update_fields=['is_closing', 'closed_at', 'purge_at', 'updated_at'])
        return self


# ---------------------------------------------------------------------------
# AccountArchive (a JSON snapshot kept when a closed account is finally purged)
# ---------------------------------------------------------------------------
class AccountArchive(models.Model):
    """A frozen JSON copy of a user + their profile & key related data.

    Written by the ``purge_closed_accounts`` command just before the live user
    row is deleted, so a closed account can still be restored / audited. A twin
    copy is also written to ``BASE_DIR/backups/archived_accounts/`` (the
    stand-in "backup server").
    """

    original_user_id = models.IntegerField(null=True, blank=True)
    username = models.CharField(max_length=254, blank=True)
    email = models.EmailField(blank=True)
    data = models.JSONField(default=dict)
    file_path = models.CharField(max_length=500, blank=True)
    #: The account's own directory in the archive park — summary, serialised
    #: content rows and copies of its uploaded files. This is what a restore
    #: reads back; ``file_path`` above only points at the summary inside it.
    archive_dir = models.CharField(max_length=500, blank=True)
    content_rows = models.PositiveIntegerField(
        default=0, help_text='How many database rows were parked with this account.')
    archived_at = models.DateTimeField(default=timezone.now, db_index=True)
    restored_at = models.DateTimeField(
        null=True, blank=True,
        help_text='Set when an administrator restored this account back onto the live system.')

    class Meta:
        ordering = ['-archived_at']

    def __str__(self):
        return f'Archive · {self.username or self.email} ({self.archived_at:%Y-%m-%d})'

    @property
    def display_name(self):
        profile = (self.data or {}).get('profile') or {}
        name = f"{profile.get('first_name') or ''} {profile.get('last_name') or ''}".strip()
        return name or self.username or self.email or f'Account {self.original_user_id}'

    @property
    def is_restorable(self):
        """True while the park directory this row points at is still on disk."""
        from pathlib import Path
        return bool(self.archive_dir) and (Path(self.archive_dir) / 'content.json').exists()
