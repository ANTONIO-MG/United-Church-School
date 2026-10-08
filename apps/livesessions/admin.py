"""Admin for the live-session settings and the after-class pipeline.

The pipeline admin is a *diagnostic* surface, not a data-entry one: when a
recording has not appeared, this is where you look to see which step it is stuck
on and what Graph said. Hence the read-only fields and the two actions — retry
and requeue — which are the only two useful interventions.
"""

from django.contrib import admin, messages
from django.utils.html import format_html

from . import models


@admin.register(models.LiveSessionSettings)
class LiveSessionSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Recording', {'fields': ('auto_record', 'publish_recordings')}),
        ('OneDrive filing', {
            'fields': ('onedrive_root', 'onedrive_owner_upn', 'keep_teams_copy'),
            'description': 'Sessions are filed under '
                           '&lt;root&gt;/&lt;institution&gt;/&lt;programme&gt;/&lt;module&gt;/'
                           '&lt;date + title&gt;/, with the recording, transcript, summary and '
                           'thumbnail together in one folder.',
        }),
        ('YouTube', {
            'fields': ('youtube_enabled', 'youtube_privacy', 'youtube_daily_quota'),
            'description': 'Credentials live in the environment (YOUTUBE_CLIENT_ID, '
                           'YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN). An upload costs '
                           '1,600 quota units against a default daily allowance of 10,000, so '
                           'about six sessions a day upload before the rest queue for tomorrow.',
        }),
        ('Thumbnails', {'fields': ('thumbnail_background', 'thumbnail_text_colour',
                                   'thumbnail_accent_colour')}),
        ('Reminders', {'fields': ('reminder_leads', 'reminder_email')}),
        ('Microsoft calendar', {'fields': ('create_calendar_events',)}),
        ('AI follow-up', {'fields': ('ai_followup_enabled',)}),
    )
    readonly_fields = ()

    def has_add_permission(self, request):
        # One row only — "Add" would just edit the same settings under a
        # different button, which reads as though there could be two.
        return not models.LiveSessionSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(models.SessionArtifact)
class SessionArtifactAdmin(admin.ModelAdmin):
    list_display = ('meeting', 'state', 'watch_link', 'youtube_video_id',
                    'ai_followup_done', 'attempts', 'last_attempt_at')
    list_filter = ('state', 'ai_followup_done')
    search_fields = ('meeting__title', 'folder_path', 'youtube_video_id')
    readonly_fields = ('meeting', 'folder_id', 'folder_path', 'folder_web_url', 'drive_owner_upn',
                       'recording_item_id', 'recording_web_url', 'recording_share_url',
                       'recording_bytes', 'recording_filed_at', 'transcript_item_id',
                       'transcript_web_url', 'summary_item_id', 'summary_web_url',
                       'thumbnail_item_id', 'youtube_video_id', 'youtube_uploaded_at',
                       'youtube_error', 'ai_report_id', 'announced_at', 'attempts',
                       'last_error', 'last_attempt_at', 'published_at', 'created_at', 'updated_at')
    actions = ['retry_now', 'requeue_from_polling']

    @admin.display(description='Watch')
    def watch_link(self, obj):
        url = obj.watch_url
        return format_html('<a href="{}" target="_blank" rel="noopener">Open</a>', url) if url else '—'

    @admin.action(description='Retry the current step now')
    def retry_now(self, request, queryset):
        from . import pipeline
        done = 0
        for artifact in queryset:
            artifact.attempts = 0
            artifact.last_error = ''
            if artifact.state == models.SessionArtifact.STATE_FAILED:
                artifact.state = models.SessionArtifact.STATE_POLLING
            artifact.save(update_fields=['attempts', 'last_error', 'state', 'updated_at'])
            try:
                pipeline.step(artifact)
                done += 1
            except Exception as exc:
                artifact.record_failure(exc)
        self.message_user(request, f'{done} session(s) advanced.', messages.SUCCESS)

    @admin.action(description='Start again from “waiting for Teams artifacts”')
    def requeue_from_polling(self, request, queryset):
        updated = queryset.update(state=models.SessionArtifact.STATE_POLLING,
                                  attempts=0, last_error='')
        self.message_user(request, f'{updated} session(s) requeued.', messages.SUCCESS)


@admin.register(models.SessionJoin)
class SessionJoinAdmin(admin.ModelAdmin):
    """Who the platform handed into each session — the authoritative identity record."""

    list_display = ('meeting', 'display_name', 'email', 'click_count',
                    'matched_identity', 'first_clicked_at')
    list_filter = ('meeting__session_kind',)
    search_fields = ('meeting__title', 'display_name', 'email', 'user__username')
    readonly_fields = ('meeting', 'user', 'display_name', 'email', 'click_count',
                       'first_clicked_at', 'last_clicked_at', 'matched_identity',
                       'matched_seconds')

    def has_add_permission(self, request):
        return False


@admin.register(models.TeamsIdentityAlias)
class TeamsIdentityAliasAdmin(admin.ModelAdmin):
    """Teams names and addresses that are known to belong to a person.

    Every row here is a correction that will never have to be made again — the
    matcher consults them before falling back to name comparison.
    """

    list_display = ('raw', 'identity', 'person', 'source', 'created_by', 'created_at')
    list_filter = ('source',)
    search_fields = ('identity', 'raw', 'person__first_name', 'person__last_name')
    readonly_fields = ('created_at',)

    def save_model(self, request, obj, form, change):
        from . import identity as ident
        # Store the normalised form, whatever was typed in — the matcher only
        # ever looks up normalised keys.
        obj.raw = obj.raw or obj.identity
        key = ident.normalise_address(obj.identity)
        obj.identity = key if '@' in key else ident.normalise(obj.identity)
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(models.CalendarSubscription)
class CalendarSubscriptionAdmin(admin.ModelAdmin):
    """Outside calendars users have connected. Diagnostic, not data entry.

    ``url`` is deliberately absent from the list and the search: a Google
    "secret address" is a bearer credential for that person's whole diary, and it
    has no business being shoulder-surfable from an admin list.
    """

    list_display = ('name', 'user', 'provider', 'last_status', 'event_count',
                    'blocks_time', 'is_active', 'last_synced_at')
    list_filter = ('provider', 'last_status', 'is_active', 'blocks_time')
    search_fields = ('name', 'user__username', 'user__email')
    readonly_fields = ('last_synced_at', 'last_status', 'last_error', 'event_count',
                       'consecutive_failures', 'created_at', 'updated_at')
    actions = ['resync_now']

    @admin.action(description='Re-import these calendars now')
    def resync_now(self, request, queryset):
        from . import subscriptions
        ok = sum(1 for sub in queryset if subscriptions.refresh(sub)[0])
        self.message_user(request, f'{ok} of {queryset.count()} calendar(s) synced.',
                          messages.SUCCESS)


@admin.register(models.ExternalEvent)
class ExternalEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'subscription', 'start', 'end', 'all_day', 'busy')
    list_filter = ('all_day', 'busy', 'subscription__provider')
    search_fields = ('title', 'location', 'subscription__name')
    readonly_fields = ('subscription', 'uid', 'title', 'start', 'end', 'all_day',
                       'location', 'busy')

    def has_add_permission(self, request):
        # Imported wholesale on every sync — a hand-added row would vanish at the
        # next refresh, which reads as the admin silently losing edits.
        return False


@admin.register(models.SessionReminder)
class SessionReminderAdmin(admin.ModelAdmin):
    list_display = ('meeting', 'recipient', 'lead_minutes', 'emailed', 'sent_at')
    list_filter = ('lead_minutes', 'emailed')
    search_fields = ('meeting__title', 'recipient__username', 'recipient__email')
    readonly_fields = ('meeting', 'recipient', 'lead_minutes', 'emailed', 'sent_at')

    def has_add_permission(self, request):
        return False
