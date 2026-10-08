"""The error log: one row per distinct problem, with an occurrence count.

Errors are **deduplicated on a fingerprint** (code + where it was raised + the
exception type) rather than appended blindly. A loop that fails ten thousand
times should be one row saying ``10000`` — an append-only log of the same
traceback buries every other problem and is exactly how a real fault gets missed.

Only the newest occurrence's traceback is kept, for the same reason.
"""

import hashlib

from django.conf import settings
from django.db import models
from django.utils import timezone

from .catalog import ERRORS, SEVERITIES, cause_label, get, prefix_of


def fingerprint(code, module, function, exception_type):
    """A stable key for "the same problem happening again"."""
    raw = '|'.join(str(part or '') for part in (code, module, function, exception_type))
    return hashlib.sha1(raw.encode('utf-8')).hexdigest()[:40]


class ErrorEvent(models.Model):
    """A distinct error, with how often and where it has happened."""

    STATUS_OPEN = 'open'
    STATUS_ACKNOWLEDGED = 'ack'
    STATUS_RESOLVED = 'resolved'
    STATUS_IGNORED = 'ignored'
    STATUS_CHOICES = [
        (STATUS_OPEN, 'Open'),
        (STATUS_ACKNOWLEDGED, 'Acknowledged'),
        (STATUS_RESOLVED, 'Resolved'),
        (STATUS_IGNORED, 'Ignored'),
    ]

    # --- Identity ---
    code = models.CharField(max_length=16, db_index=True,
                            help_text='Catalog code, e.g. CERT-8001.')
    fingerprint = models.CharField(max_length=40, unique=True, db_index=True)
    severity = models.CharField(max_length=10, choices=[(s, s.title()) for s in SEVERITIES],
                                default='error', db_index=True)

    # --- What happened ---
    message = models.TextField(blank=True, help_text='The exception text or log message.')
    exception_type = models.CharField(max_length=120, blank=True)
    traceback = models.TextField(blank=True, help_text='Most recent occurrence only.')
    context = models.JSONField(default=dict, blank=True,
                               help_text='Structured extras the reporting site attached.')

    # --- Where ---
    module = models.CharField(max_length=200, blank=True, db_index=True)
    function = models.CharField(max_length=200, blank=True)
    line = models.PositiveIntegerField(null=True, blank=True)
    path = models.CharField(max_length=500, blank=True, help_text='Request path, when there was one.')
    method = models.CharField(max_length=10, blank=True)
    view_name = models.CharField(max_length=200, blank=True)

    # --- Who (best effort — an error may happen with no user) ---
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                             null=True, blank=True, related_name='+')
    user_label = models.CharField(max_length=200, blank=True,
                                  help_text='Kept as text so the row survives account deletion.')
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    # --- How often ---
    count = models.PositiveIntegerField(default=1, db_index=True)
    first_seen = models.DateTimeField(default=timezone.now, db_index=True)
    last_seen = models.DateTimeField(default=timezone.now, db_index=True)

    # --- Triage ---
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_OPEN,
                              db_index=True)
    note = models.TextField(blank=True, help_text='Developer notes on this error.')
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                    null=True, blank=True, related_name='+')

    # The short id quoted to a user on an error page, so support can find the row.
    reference = models.CharField(max_length=12, blank=True, db_index=True)

    class Meta:
        ordering = ['-last_seen']
        indexes = [
            models.Index(fields=['status', '-last_seen']),
            models.Index(fields=['code', '-last_seen']),
        ]
        verbose_name = 'error event'
        verbose_name_plural = 'error events'

    def __str__(self):
        return f'{self.code} ×{self.count} — {self.title}'

    # --- Catalog passthroughs, so a template never has to do the lookup ---
    @property
    def spec(self):
        return get(self.code)

    @property
    def title(self):
        return self.spec.title

    @property
    def why(self):
        return self.spec.why

    @property
    def fix(self):
        return self.spec.fix

    @property
    def action(self):
        return self.spec.action

    @property
    def is_documented(self):
        """False when the code is not in the catalog — itself worth fixing."""
        return self.code in ERRORS

    @property
    def domain(self):
        return prefix_of(self.code)

    @property
    def cause(self):
        return cause_label(self.code)

    @property
    def is_open(self):
        return self.status in (self.STATUS_OPEN, self.STATUS_ACKNOWLEDGED)

    def resolve(self, user=None, note=''):
        self.status = self.STATUS_RESOLVED
        self.resolved_at = timezone.now()
        self.resolved_by = user
        if note:
            self.note = note
        self.save(update_fields=['status', 'resolved_at', 'resolved_by', 'note'])
