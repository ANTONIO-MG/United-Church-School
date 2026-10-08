"""Django admin for the error log (read-mostly: events are written by code)."""

from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html

from .catalog import get as spec_for
from .models import ErrorEvent


@admin.register(ErrorEvent)
class ErrorEventAdmin(admin.ModelAdmin):
    list_display = ('code', 'severity', 'short_title', 'count', 'status',
                    'module', 'last_seen')
    list_filter = ('severity', 'status', 'code', 'last_seen')
    search_fields = ('code', 'message', 'module', 'function', 'path',
                     'reference', 'exception_type')
    date_hierarchy = 'last_seen'
    readonly_fields = ('code', 'fingerprint', 'severity', 'message', 'exception_type',
                       'traceback', 'context', 'module', 'function', 'line', 'path',
                       'method', 'view_name', 'user', 'user_label', 'ip_address',
                       'count', 'first_seen', 'last_seen', 'reference', 'remedy')
    fields = ('code', 'remedy', 'severity', 'status', 'note', 'count',
              'first_seen', 'last_seen', 'reference',
              'message', 'exception_type', 'module', 'function', 'line',
              'path', 'method', 'view_name', 'user_label', 'ip_address',
              'context', 'traceback', 'fingerprint')
    actions = ['mark_resolved', 'mark_ignored', 'reopen']

    @admin.display(description='Title')
    def short_title(self, obj):
        return spec_for(obj.code).title

    @admin.display(description='What the dictionary says')
    def remedy(self, obj):
        spec = spec_for(obj.code)
        return format_html(
            '<strong>{}</strong><br><br>'
            '<em>Why:</em> {}<br><br>'
            '<em>Developer fix:</em> {}<br><br>'
            '<em>User action:</em> {}',
            spec.title, spec.why, spec.fix, spec.action)

    def has_add_permission(self, request):
        return False        # events are recorded by the platform, never typed in

    @admin.action(description='Mark selected as resolved')
    def mark_resolved(self, request, queryset):
        updated = queryset.update(status=ErrorEvent.STATUS_RESOLVED,
                                  resolved_at=timezone.now(), resolved_by=request.user)
        self.message_user(request, f'{updated} error(s) marked resolved.')

    @admin.action(description='Mark selected as ignored')
    def mark_ignored(self, request, queryset):
        updated = queryset.update(status=ErrorEvent.STATUS_IGNORED)
        self.message_user(request, f'{updated} error(s) ignored.')

    @admin.action(description='Reopen selected')
    def reopen(self, request, queryset):
        updated = queryset.update(status=ErrorEvent.STATUS_OPEN, resolved_at=None)
        self.message_user(request, f'{updated} error(s) reopened.')
