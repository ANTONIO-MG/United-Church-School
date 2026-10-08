"""Staff desk persistence."""

from django.conf import settings
from django.db import models


# ---------------------------------------------------------------------------
# dash — the educator dashboard's "Nudge inactive students" button
# ---------------------------------------------------------------------------
class Nudge(models.Model):
    """One "you've gone quiet" reminder sent to a module's inactive students.

    Kept so the button can be rate-limited (once per module per
    :data:`apps.staffdesk.dashboards.NUDGE_COOLDOWN`) and so the dashboard can
    say when the last one went out and to how many people.
    """

    module = models.ForeignKey('learning.ProgrammeModule', on_delete=models.CASCADE,
                               related_name='staffdesk_nudges')
    sent_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                null=True, blank=True, related_name='+')
    sent_at = models.DateTimeField(auto_now_add=True, db_index=True)
    recipients = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-sent_at']
        indexes = [models.Index(fields=['module', '-sent_at'], name='staffdesk_nudge_mod_sent')]

    def __str__(self):
        return f'Nudge · {self.module_id} · {self.sent_at:%Y-%m-%d %H:%M}'


# ---------------------------------------------------------------------------
# academic — content-import runs and at-risk triage
# ---------------------------------------------------------------------------
class ImportRun(models.Model):
    """One run of a content management command started from /staff/imports/.

    The command runs in a background thread (see
    :mod:`apps.staffdesk.views_academic`); this row is how the page knows it is
    still going, and what it printed when it finished.
    """

    STATUS_QUEUED = 'queued'
    STATUS_RUNNING = 'running'
    STATUS_OK = 'ok'
    STATUS_FAILED = 'failed'
    STATUS_CHOICES = [
        (STATUS_QUEUED, 'Queued'), (STATUS_RUNNING, 'Running'),
        (STATUS_OK, 'Finished'), (STATUS_FAILED, 'Failed'),
    ]

    command = models.CharField(max_length=60, db_index=True)
    # The exact argv handed to call_command, so a run can be read (or repeated
    # from a shell) without guessing what the form meant.
    args = models.JSONField(default=list, blank=True)
    started_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                   null=True, blank=True, related_name='+')
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default=STATUS_QUEUED, db_index=True)
    output = models.TextField(blank=True)
    started_at = models.DateTimeField(auto_now_add=True, db_index=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f'{self.command} · {self.get_status_display()} · {self.started_at:%Y-%m-%d %H:%M}'

    @property
    def is_active(self):
        return self.status in (self.STATUS_QUEUED, self.STATUS_RUNNING)

    @property
    def duration(self):
        if not self.finished_at:
            return None
        return self.finished_at - self.started_at


class RiskTriage(models.Model):
    """One step in handling an analytics :class:`~apps.analytics.models.RiskFlag`.

    RiskFlag itself only knows ``resolved``; acknowledging, notes and who was
    told what live here as an append-only log, so the at-risk page can show
    the history of a case and not just its latest state.
    """

    ACTION_ACK = 'ack'
    ACTION_RESOLVE = 'resolve'
    ACTION_REOPEN = 'reopen'
    ACTION_NOTE = 'note'
    ACTION_NOTIFY_STUDENT = 'notify_student'
    ACTION_NOTIFY_EDUCATOR = 'notify_educator'
    ACTION_CHOICES = [
        (ACTION_ACK, 'Acknowledged'), (ACTION_RESOLVE, 'Resolved'), (ACTION_REOPEN, 'Reopened'),
        (ACTION_NOTE, 'Note'), (ACTION_NOTIFY_STUDENT, 'Notified student'),
        (ACTION_NOTIFY_EDUCATOR, 'Notified educator'),
    ]

    flag = models.ForeignKey('analytics.RiskFlag', on_delete=models.CASCADE, related_name='triage')
    action = models.CharField(max_length=16, choices=ACTION_CHOICES)
    note = models.TextField(blank=True)
    by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                           null=True, blank=True, related_name='+')
    at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-at']

    def __str__(self):
        return f'{self.get_action_display()} · flag {self.flag_id}'
