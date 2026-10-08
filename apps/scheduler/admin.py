"""Read-only health view of the background jobs.

Everything here is written by the runner, so the rows are evidence rather than
settings — the schedule itself lives in :mod:`apps.scheduler.jobs`.
"""

from django.contrib import admin
from django.utils.html import format_html

from . import models


@admin.register(models.JobRun)
class JobRunAdmin(admin.ModelAdmin):
    list_display = ('name', 'health', 'schedule', 'last_started_at', 'took',
                    'run_count', 'failure_count')
    list_filter = ('last_status',)
    search_fields = ('name', 'last_output')
    readonly_fields = [f.name for f in models.JobRun._meta.fields]

    def has_add_permission(self, request):
        return False   # rows are created by the runner

    @admin.display(description='Health', ordering='last_status')
    def health(self, obj):
        # NB: format_html requires at least one arg — pass the text as one.
        if obj.last_status == models.JobRun.STATUS_FAILED:
            return format_html('<b style="color:#c00">{}</b>',
                               f'failed ×{obj.consecutive_failures}')
        if obj.last_status == models.JobRun.STATUS_RUNNING:
            return format_html('<span style="color:#8a6a00">{}</span>', 'running…')
        if obj.last_status == models.JobRun.STATUS_OK:
            return format_html('<span style="color:#3c8000">{}</span>', 'ok')
        return '—'

    @admin.display(description='Every')
    def schedule(self, obj):
        from .jobs import JOBS_BY_NAME
        job = JOBS_BY_NAME.get(obj.name)
        if not job:
            return format_html('<span style="color:#8392ab">{}</span>', 'not registered')
        seconds = job.every
        return f'{seconds // 3600}h' if seconds % 3600 == 0 else f'{seconds // 60}m'

    @admin.display(description='Took')
    def took(self, obj):
        if not obj.last_duration_ms:
            return '—'
        return f'{obj.last_duration_ms / 1000:.1f}s'
