"""Django admin for the communication app: chat groups, meetings, notifications
and announcements (announcements can be (re)sent from the changelist)."""

from django.contrib import admin, messages

from . import models, services


class ChatMembershipInline(admin.TabularInline):
    model = models.ChatMembership
    extra = 0
    fields = ('user', 'role', 'is_auto', 'muted', 'last_read_at', 'joined_at')
    readonly_fields = ('joined_at',)
    autocomplete_fields = ('user',)


@admin.register(models.ChatGroup)
class ChatGroupAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'kind', 'is_active', 'updated_at')
    list_filter = ('kind', 'is_active')
    search_fields = ('name', 'description')
    inlines = [ChatMembershipInline]


class MessageAttachmentInline(admin.TabularInline):
    model = models.MessageAttachment
    extra = 0
    readonly_fields = ('kind', 'original_name', 'size', 'created_at')


@admin.register(models.Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'group', 'sender', 'short_body', 'is_edited', 'is_deleted', 'created_at')
    list_filter = ('is_edited', 'is_deleted', 'created_at')
    search_fields = ('body',)
    inlines = [MessageAttachmentInline]
    autocomplete_fields = ('group', 'sender', 'reply_to')

    @admin.display(description='Body')
    def short_body(self, obj):
        return (obj.body or '')[:60]


class MeetingParticipantInline(admin.TabularInline):
    model = models.MeetingParticipant
    extra = 0
    autocomplete_fields = ('user',)


@admin.register(models.MeetingRoom)
class MeetingRoomAdmin(admin.ModelAdmin):
    list_display = ('title', 'host', 'scheduled_start', 'scheduled_end', 'is_recurring', 'is_active', 'slug')
    list_filter = ('is_active', 'is_recurring', 'recurrence')
    search_fields = ('title', 'description', 'slug')
    readonly_fields = ('slug', 'external_url')
    inlines = [MeetingParticipantInline]
    autocomplete_fields = ('host', 'group')


@admin.register(models.Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'title', 'verb', 'level', 'is_read', 'emailed', 'created_at')
    list_filter = ('level', 'is_read', 'emailed', 'created_at')
    search_fields = ('title', 'body', 'verb')
    autocomplete_fields = ('recipient', 'actor')


class AnnouncementAttachmentInline(admin.TabularInline):
    model = models.AnnouncementAttachment
    extra = 0
    readonly_fields = ('kind', 'size', 'created_at')


@admin.register(models.Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'sender', 'audience', 'status', 'level', 'send_email', 'scheduled_for',
                    'recipient_count', 'created_at')
    list_filter = ('status', 'audience', 'level', 'send_email', 'is_important')
    search_fields = ('title', 'body')
    filter_horizontal = ('institutions', 'programmes', 'cohorts', 'modules', 'users')
    inlines = [AnnouncementAttachmentInline]
    actions = ['send_now']

    @admin.action(description='Send selected announcements now')
    def send_now(self, request, queryset):
        total = 0
        for announcement in queryset:
            count = services.send_announcement(announcement)
            total += count
        self.message_user(request, f'Sent {queryset.count()} announcement(s) to {total} recipient(s).',
                          level=messages.SUCCESS)


class DiscussionAttachmentInline(admin.TabularInline):
    model = models.DiscussionAttachment
    extra = 0
    fk_name = 'discussion'
    readonly_fields = ('kind', 'original_name', 'created_at')


class DiscussionReplyInline(admin.TabularInline):
    model = models.DiscussionReply
    extra = 0
    fields = ('author', 'body', 'is_answer', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(models.Discussion)
class DiscussionAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'module', 'is_pinned', 'is_closed', 'view_count', 'created_at')
    list_filter = ('is_pinned', 'is_closed', 'created_at')
    search_fields = ('title', 'body', 'tags')
    inlines = [DiscussionAttachmentInline, DiscussionReplyInline]


@admin.register(models.DiscussionReply)
class DiscussionReplyAdmin(admin.ModelAdmin):
    list_display = ('discussion', 'author', 'is_answer', 'created_at')
    list_filter = ('is_answer', 'created_at')
    search_fields = ('body',)


# ---------------------------------------------------------------------------
# Moderation
# ---------------------------------------------------------------------------
class PenaltyInline(admin.TabularInline):
    model = models.Penalty
    extra = 0
    fields = ('kind', 'reason', 'starts_at', 'ends_at', 'active')


@admin.register(models.Violation)
class ViolationAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'score', 'source', 'detected_by', 'handled', 'created_at')
    list_filter = ('score', 'category', 'source', 'detected_by', 'handled', 'created_at')
    search_fields = ('user__username', 'user__email', 'text', 'category')
    date_hierarchy = 'created_at'
    autocomplete_fields = ('user', 'message', 'reporter')
    inlines = [PenaltyInline]


@admin.register(models.Penalty)
class PenaltyAdmin(admin.ModelAdmin):
    list_display = ('user', 'kind', 'active', 'starts_at', 'ends_at', 'issued_by', 'created_at')
    list_filter = ('kind', 'active', 'created_at')
    search_fields = ('user__username', 'user__email', 'reason')
    date_hierarchy = 'created_at'
    autocomplete_fields = ('user', 'issued_by', 'violation')
    actions = ['lift_penalties']

    @admin.action(description='Lift selected penalties (allow user to resume)')
    def lift_penalties(self, request, queryset):
        n = queryset.update(active=False)
        self.message_user(request, f'{n} penalty(ies) lifted.')


@admin.register(models.Appeal)
class AppealAdmin(admin.ModelAdmin):
    list_display = ('user', 'penalty', 'status', 'reviewed_by', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'user__email', 'message')
    date_hierarchy = 'created_at'
    autocomplete_fields = ('user', 'penalty', 'reviewed_by')


@admin.register(models.ReputationScore)
class ReputationScoreAdmin(admin.ModelAdmin):
    list_display = ('user', 'score', 'updated_at')
    search_fields = ('user__username', 'user__email')
    ordering = ('score',)


# ---------------------------------------------------------------------------
# Attendance, preferences & workspaces
# ---------------------------------------------------------------------------
class AttendanceInline(admin.TabularInline):
    model = models.Attendance
    extra = 0
    fields = ('student', 'status', 'source', 'check_in_at', 'marked_by')
    autocomplete_fields = ('student', 'marked_by')


@admin.register(models.ClassSession)
class ClassSessionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'module', 'session_date', 'is_open', 'present_count', 'absent_count')
    list_filter = ('is_open', 'session_date')
    search_fields = ('title', 'module__name')
    date_hierarchy = 'session_date'
    inlines = [AttendanceInline]


@admin.register(models.Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'session', 'status', 'source', 'check_in_at')
    list_filter = ('status', 'source')
    search_fields = ('student__username', 'student__email')
    autocomplete_fields = ('student', 'session', 'marked_by')


@admin.register(models.NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'email_enabled', 'digest', 'reminder_lead_minutes', 'updated_at')
    list_filter = ('email_enabled', 'browser_enabled', 'digest')
    search_fields = ('user__username', 'user__email')


class WorkspaceFileInline(admin.TabularInline):
    model = models.WorkspaceFile
    extra = 0
    fields = ('title', 'file', 'version', 'uploaded_by', 'created_at')
    readonly_fields = ('created_at',)


class WorkspaceNoteInline(admin.TabularInline):
    model = models.WorkspaceNote
    extra = 0
    fields = ('title', 'author', 'pinned', 'updated_at')
    readonly_fields = ('updated_at',)


@admin.register(models.Workspace)
class WorkspaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'module', 'created_by', 'is_active', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    inlines = [WorkspaceFileInline, WorkspaceNoteInline]


class MailRecipientInline(admin.TabularInline):
    model = models.MailRecipient
    extra = 0
    fields = ('recipient', 'is_read', 'starred', 'trashed')
    autocomplete_fields = ('recipient',)


@admin.register(models.MailMessage)
class MailMessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'sender', 'created_at')
    search_fields = ('subject', 'body', 'sender__username', 'sender__email')
    date_hierarchy = 'created_at'
    inlines = [MailRecipientInline]


@admin.register(models.ConnectionRequest)
class ConnectionRequestAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'status', 'created_at', 'responded_at')
    list_filter = ('status',)
    search_fields = ('from_user__username', 'from_user__email', 'to_user__username', 'to_user__email')
    autocomplete_fields = ('from_user', 'to_user')
    date_hierarchy = 'created_at'


@admin.register(models.WhatsAppMessage)
class WhatsAppMessageAdmin(admin.ModelAdmin):
    """The bot's transcript — what students asked and what they were told."""
    list_display = ('created_at', 'direction', 'number', 'person', 'command', 'short_body')
    list_filter = ('direction', 'kind', 'command', 'created_at')
    search_fields = ('number', 'body', 'wa_id', 'person__first_name', 'person__last_name',
                     'person__user__email')
    readonly_fields = ('direction', 'number', 'person', 'kind', 'body', 'command',
                       'wa_id', 'payload', 'created_at')
    date_hierarchy = 'created_at'

    @admin.display(description='Message')
    def short_body(self, obj):
        return (obj.body or '')[:80]

    def has_add_permission(self, request):
        # A transcript is a record of what happened, not somewhere to type.
        return False
