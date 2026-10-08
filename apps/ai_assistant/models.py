"""Models for the AI assistant: cached page text (so the crew doesn't re-scrape
on every question) and a lightweight conversation history."""

import hashlib
import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

from core import validators as v


class PageDocument(models.Model):
    """Cached, cleaned text extracted from a webpage — the assistant's "knowledge"
    about that page (a real vector DB can replace this; see :mod:`apps.ai_assistant.services`).

    Pages are de-duplicated on :attr:`url_hash` (a SHA-256 of the URL) rather
    than on the URL column itself: a URL can be long, and MySQL can't put a
    unique index on a long ``VARCHAR`` (the 3072-byte key-length limit). The
    fixed 64-char hash is unique and index-safe on every supported database.
    """

    url = models.URLField(max_length=1000)
    # SHA-256 hex digest of ``url`` — the actual unique key. Set in save().
    url_hash = models.CharField(max_length=64, unique=True, editable=False)
    title = models.CharField(max_length=300, blank=True)
    text = models.TextField(blank=True)
    fetched_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-fetched_at']

    def __str__(self):
        return self.title or self.url

    @staticmethod
    def hash_url(url):
        """Return the lookup key for ``url`` (stable SHA-256 hex digest)."""
        return hashlib.sha256((url or '').encode('utf-8')).hexdigest()

    def save(self, *args, **kwargs):
        if not self.url_hash:
            self.url_hash = self.hash_url(self.url)
        super().save(*args, **kwargs)


class AssistantSession(models.Model):
    """One chat thread with the assistant widget."""

    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                             related_name='ai_sessions')
    page_url = models.URLField(max_length=1000, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f'AI session {self.public_id} ({self.user or "anon"})'


class AssistantTurn(models.Model):
    """A question/answer pair within an :class:`AssistantSession`."""

    session = models.ForeignKey(AssistantSession, on_delete=models.CASCADE, related_name='turns')
    question = models.TextField()
    answer = models.TextField(blank=True)
    page_url = models.URLField(max_length=1000, blank=True)
    used_crewai = models.BooleanField(default=False)
    error = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Q: {self.question[:50]}'


# ---------------------------------------------------------------------------
# Media ingestion → summary → action extraction (the CrewAI pipeline)
# ---------------------------------------------------------------------------
class AssistantUpload(models.Model):
    """A file the user dropped on the assistant (audio / video / PDF / text).

    The CrewAI media crew transcribes it (if needed), reads & summarises it, and
    extracts action items. The transcript / summary land here; each extracted
    action becomes an :class:`AssistantAction` awaiting human approval.
    """

    KIND_AUTO = 'auto'
    KIND_AUDIO = 'audio'
    KIND_VIDEO = 'video'
    KIND_PDF = 'pdf'
    KIND_TEXT = 'text'
    KIND_CHOICES = [
        (KIND_AUTO, 'Auto-detect'),
        (KIND_AUDIO, 'Audio'),
        (KIND_VIDEO, 'Video'),
        (KIND_PDF, 'PDF / document'),
        (KIND_TEXT, 'Text'),
    ]

    STATUS_PENDING = 'pending'
    STATUS_PROCESSING = 'processing'
    STATUS_DONE = 'done'
    STATUS_FAILED = 'failed'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Queued'),
        (STATUS_PROCESSING, 'Processing'),
        (STATUS_DONE, 'Done'),
        (STATUS_FAILED, 'Failed'),
    ]

    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                             related_name='ai_uploads')
    file = models.FileField(upload_to='ai_uploads/', blank=True, null=True,
                            validators=v.validate_attachment)
    kind = models.CharField(max_length=10, choices=KIND_CHOICES, default=KIND_AUTO)
    original_name = models.CharField(max_length=255, blank=True)
    note = models.TextField(blank=True, help_text='Optional instruction from the user for the crew.')

    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=STATUS_PENDING, db_index=True)
    transcript = models.TextField(blank=True)
    summary = models.TextField(blank=True)
    takeaways = models.TextField(blank=True)
    result_json = models.JSONField(default=dict, blank=True)
    error = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.original_name or f'Upload {self.public_id}'


class AssistantAction(models.Model):
    """An action the AI proposed (a task, reminder, event, meeting, email or
    invoice). It sits in the To-Do / Reminders inbox until a human approves it,
    at which point :func:`apps.ai_assistant.actions.apply_action` creates the
    real record in the relevant app."""

    TYPE_TASK = 'task'
    TYPE_REMINDER = 'reminder'
    TYPE_EVENT = 'event'
    TYPE_MEETING = 'meeting'
    TYPE_EMAIL = 'email'
    TYPE_INVOICE = 'invoice'
    TYPE_CHOICES = [
        (TYPE_TASK, 'Task'),
        (TYPE_REMINDER, 'Reminder'),
        (TYPE_EVENT, 'Calendar event'),
        (TYPE_MEETING, 'Meeting'),
        (TYPE_EMAIL, 'Email'),
        (TYPE_INVOICE, 'Invoice'),
    ]

    PRIORITY_CHOICES = [('low', 'Low'), ('normal', 'Normal'), ('high', 'High')]

    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_APPLIED = 'applied'
    STATUS_FAILED = 'failed'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending approval'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
        (STATUS_APPLIED, 'Applied'),
        (STATUS_FAILED, 'Failed'),
    ]

    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    upload = models.ForeignKey(AssistantUpload, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='actions')
    session = models.ForeignKey(AssistantSession, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='actions')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='ai_actions')

    action_type = models.CharField(max_length=12, choices=TYPE_CHOICES, default=TYPE_TASK, db_index=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    # Structured, editable fields for the action (owner_email, amount, due_date,
    # location, recipients, …). The inbox form edits these before applying.
    payload = models.JSONField(default=dict, blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    due_at = models.DateTimeField(null=True, blank=True)

    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=STATUS_PENDING, db_index=True)
    # Free-text record of what happened when applied (e.g. "Created Task #42").
    result_note = models.CharField(max_length=255, blank=True)
    # Loose link back to the created object (app_label.Model, pk) — kept as text
    # so we don't need a GenericForeignKey.
    applied_ref = models.CharField(max_length=120, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['status', 'action_type'], name='ai_assist_status_type_idx')]

    def __str__(self):
        return f'[{self.get_action_type_display()}] {self.title[:50]}'


# ===========================================================================
# Admin AI layer — the advanced, Claude-powered institutional analyst.
# Only admins/staff can use it (role-checked in the view). Token usage is
# recorded per message because this layer uses a paid, token-billed model.
# ===========================================================================
class AdminAIThread(models.Model):
    """A Claude-style conversation thread for the admin AI assistant."""

    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='admin_ai_threads')
    title = models.CharField(max_length=200, blank=True, default='New chat')
    total_input_tokens = models.PositiveIntegerField(default=0)
    total_output_tokens = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f'{self.title} · {self.user}'

    @property
    def total_tokens(self):
        return self.total_input_tokens + self.total_output_tokens


# ===========================================================================
# AI Teaching Assistant (local CrewAI + Ollama) — generated documents + proactive
# insights for the My Learning Hub. Everything here works offline: the DB is
# always read locally; the LLM narrative is added when Ollama is configured and
# falls back to a deterministic template otherwise.
# ===========================================================================
class AiReport(models.Model):
    """A document the AI produced for review — a report card, a generated
    assignment/rubric, a parent letter, meeting minutes, an attendance analysis,
    an 'ask-the-data' answer or a secretary briefing. Kept as Markdown in
    ``content`` (+ structured ``data``) so it renders in the theme and can be
    finalised, downloaded or turned into real records."""

    KIND_MINUTES = 'meeting_minutes'
    KIND_ASSIGNMENT = 'assignment'
    KIND_REPORT_CARD = 'report_card'
    KIND_ATTENDANCE = 'attendance_analysis'
    KIND_PARENT = 'parent_letter'
    KIND_NL = 'nl_answer'
    KIND_BRIEFING = 'secretary_briefing'
    KIND_MEETING_RECAP = 'meeting_recap'   # Teams class recap (from the transcript)
    KIND_CHOICES = [
        (KIND_MINUTES, 'Meeting minutes'),
        (KIND_ASSIGNMENT, 'Generated assignment'),
        (KIND_REPORT_CARD, 'Report card'),
        (KIND_ATTENDANCE, 'Attendance analysis'),
        (KIND_PARENT, 'Parent message'),
        (KIND_NL, 'Ask-the-data answer'),
        (KIND_BRIEFING, 'Secretary briefing'),
        (KIND_MEETING_RECAP, 'Class recap'),
    ]

    STATUS_DRAFT = 'draft'
    STATUS_FINAL = 'final'
    STATUS_CHOICES = [(STATUS_DRAFT, 'Draft'), (STATUS_FINAL, 'Final')]

    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    kind = models.CharField(max_length=24, choices=KIND_CHOICES, db_index=True)
    title = models.CharField(max_length=255)
    module = models.ForeignKey('learning.ProgrammeModule', on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='ai_reports')
    # For per-student docs (report cards, parent letters): the module student.
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='ai_reports_about')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='ai_reports_created')

    prompt = models.TextField(blank=True, help_text='The instruction / inputs used to generate this.')
    content = models.TextField(blank=True, help_text='The generated document (Markdown).')
    data = models.JSONField(default=dict, blank=True)
    used_llm = models.BooleanField(default=False)
    # Loose link to a record this report produced (e.g. assessments.Assessment:42).
    linked_ref = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default=STATUS_DRAFT, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['kind', 'status'], name='ai_report_kind_status_idx')]

    def __str__(self):
        return f'[{self.get_kind_display()}] {self.title[:50]}'


class AiInsight(models.Model):
    """A proactive observation the *AI Secretary* surfaced from scanning the
    database — nobody asked, the AI noticed. Shown on dashboards; can be
    acknowledged, dismissed, or turned into an action."""

    SEVERITY_INFO = 'info'
    SEVERITY_WARNING = 'warning'
    SEVERITY_CRITICAL = 'critical'
    SEVERITY_CHOICES = [(SEVERITY_INFO, 'Info'), (SEVERITY_WARNING, 'Warning'), (SEVERITY_CRITICAL, 'Critical')]

    STATUS_NEW = 'new'
    STATUS_ACK = 'acknowledged'
    STATUS_DISMISSED = 'dismissed'
    STATUS_ACTIONED = 'actioned'
    STATUS_CHOICES = [
        (STATUS_NEW, 'New'), (STATUS_ACK, 'Acknowledged'),
        (STATUS_DISMISSED, 'Dismissed'), (STATUS_ACTIONED, 'Actioned'),
    ]

    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    kind = models.CharField(max_length=40, db_index=True)          # e.g. overdue_assessment, missing_attendance
    severity = models.CharField(max_length=8, choices=SEVERITY_CHOICES, default=SEVERITY_WARNING, db_index=True)
    title = models.CharField(max_length=255)
    body = models.TextField(blank=True)

    # Who it's for (an educator/admin) — null = institution-wide (any admin/staff).
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True,
                              related_name='ai_insights')
    module = models.ForeignKey('learning.ProgrammeModule', on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='ai_insights')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='ai_insights_about')
    data = models.JSONField(default=dict, blank=True)
    # Stable key so re-running the scan updates rather than duplicates an insight.
    dedupe_key = models.CharField(max_length=200, db_index=True, blank=True)
    suggested_action = models.ForeignKey(AssistantAction, on_delete=models.SET_NULL, null=True, blank=True,
                                         related_name='insights')
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=STATUS_NEW, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['status', 'severity'], name='ai_insight_status_sev_idx')]

    def __str__(self):
        return f'[{self.severity}] {self.title[:60]}'


class AdminAIMessage(models.Model):
    """One message in an :class:`AdminAIThread` (role = user or assistant)."""

    ROLE_USER = 'user'
    ROLE_ASSISTANT = 'assistant'
    ROLE_CHOICES = [(ROLE_USER, 'User'), (ROLE_ASSISTANT, 'Assistant')]

    thread = models.ForeignKey(AdminAIThread, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    # Token accounting for the paid model (assistant messages carry usage).
    input_tokens = models.PositiveIntegerField(default=0)
    output_tokens = models.PositiveIntegerField(default=0)
    model = models.CharField(max_length=60, blank=True)
    error = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.role}: {self.content[:50]}'
