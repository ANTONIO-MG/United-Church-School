"""Analytics persistence: predictive risk flags and cached report snapshots.

Most analytics are computed on demand (see :mod:`apps.analytics.services`); these
two models persist the bits worth keeping — a student's latest risk assessment
and periodic big-data report snapshots / exports.
"""

from django.conf import settings
from django.db import models


class RiskFlag(models.Model):
    """Predictive risk monitoring — a student flagged as at-risk, with reasons."""

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='risk_flags')
    module = models.ForeignKey('learning.ProgrammeModule', on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='risk_flags')
    score = models.PositiveIntegerField(default=0, help_text='0–100 risk score.')
    reasons = models.JSONField(default=list, blank=True)
    resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-score', '-created_at']

    def __str__(self):
        return f'{self.student} — risk {self.score}%'


class ReportSnapshot(models.Model):
    """A cached big-data report (daily/weekly/…) for fast dashboards & exports."""

    PERIOD_CHOICES = [
        ('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'), ('yearly', 'Yearly'),
    ]

    scope = models.CharField(max_length=80, help_text='e.g. "institution", "module:12".')
    period = models.CharField(max_length=10, choices=PERIOD_CHOICES, default='monthly')
    data = models.JSONField(default=dict, blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-generated_at']

    def __str__(self):
        return f'{self.scope} · {self.period} @ {self.generated_at:%Y-%m-%d}'
