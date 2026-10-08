"""Bookkeeping for the built-in job scheduler.

One row per registered job, holding when it last ran and how it went. The row is
what makes a *single* cron entry sufficient: ``run_scheduled_jobs`` can fire
every minute and each job decides for itself whether its interval has elapsed,
so intervals live in the code (:mod:`apps.scheduler.jobs`) rather than being
smeared across crontab lines that drift out of sync with the app.
"""

from django.db import models
from django.utils import timezone


class JobRun(models.Model):
    """Last-run state and health for one registered job."""

    STATUS_OK = 'ok'
    STATUS_FAILED = 'failed'
    STATUS_RUNNING = 'running'
    STATUS_CHOICES = [(STATUS_OK, 'OK'), (STATUS_FAILED, 'Failed'), (STATUS_RUNNING, 'Running')]

    name = models.CharField(max_length=100, unique=True)
    last_started_at = models.DateTimeField(null=True, blank=True)
    last_finished_at = models.DateTimeField(null=True, blank=True)
    last_status = models.CharField(max_length=8, choices=STATUS_CHOICES, blank=True)
    last_output = models.TextField(blank=True)
    last_duration_ms = models.PositiveIntegerField(default=0)

    run_count = models.PositiveIntegerField(default=0)
    failure_count = models.PositiveIntegerField(default=0)
    consecutive_failures = models.PositiveIntegerField(default=0)

    # Set while a run is in flight so two overlapping schedulers don't both fire
    # the same job. Cleared on completion; treated as stale after
    # ``jobs.LOCK_STALE_AFTER`` in case a process was killed mid-run.
    locked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'scheduled job'

    def __str__(self):
        return f'{self.name} ({self.last_status or "never run"})'

    @property
    def is_due_basis(self):
        """The timestamp an interval is measured from — the last *start*.

        Measuring from the start (not the finish) keeps a slow job on a steady
        cadence instead of drifting later by its own runtime every cycle.
        """
        return self.last_started_at

    @property
    def is_healthy(self):
        return self.consecutive_failures == 0

    def seconds_since_run(self):
        if not self.last_started_at:
            return None
        return int((timezone.now() - self.last_started_at).total_seconds())
