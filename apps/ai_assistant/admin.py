"""Admin for the AI assistant: cached page text and conversation history (read-only)."""

from django.contrib import admin

from . import models


@admin.register(models.PageDocument)
class PageDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', 'fetched_at')
    search_fields = ('url', 'title')
    readonly_fields = ('fetched_at',)


class AssistantTurnInline(admin.TabularInline):
    model = models.AssistantTurn
    extra = 0
    readonly_fields = ('question', 'answer', 'page_url', 'used_crewai', 'error', 'created_at')
    can_delete = False


@admin.register(models.AssistantSession)
class AssistantSessionAdmin(admin.ModelAdmin):
    list_display = ('public_id', 'user', 'page_url', 'created_at', 'updated_at')
    search_fields = ('public_id', 'page_url')
    readonly_fields = ('public_id', 'created_at', 'updated_at')
    inlines = [AssistantTurnInline]


class AssistantActionInline(admin.TabularInline):
    model = models.AssistantAction
    extra = 0
    fields = ('action_type', 'title', 'status', 'priority', 'due_at', 'result_note')
    readonly_fields = ('result_note',)


@admin.register(models.AssistantUpload)
class AssistantUploadAdmin(admin.ModelAdmin):
    list_display = ('original_name', 'kind', 'status', 'user', 'created_at')
    list_filter = ('kind', 'status')
    search_fields = ('original_name', 'summary')
    readonly_fields = ('public_id', 'transcript', 'summary', 'takeaways', 'result_json',
                       'created_at', 'updated_at')
    inlines = [AssistantActionInline]


@admin.register(models.AssistantAction)
class AssistantActionAdmin(admin.ModelAdmin):
    list_display = ('title', 'action_type', 'status', 'priority', 'due_at', 'created_by', 'created_at')
    list_filter = ('action_type', 'status', 'priority')
    search_fields = ('title', 'description', 'result_note')
    readonly_fields = ('public_id', 'applied_ref', 'result_note', 'created_at', 'updated_at')


@admin.register(models.AiReport)
class AiReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'kind', 'module', 'student', 'used_llm', 'status', 'created_by', 'created_at')
    list_filter = ('kind', 'status', 'used_llm')
    search_fields = ('title', 'content', 'prompt')
    date_hierarchy = 'created_at'
    readonly_fields = ('public_id', 'data', 'linked_ref', 'created_at', 'updated_at')
    autocomplete_fields = ('module', 'student', 'created_by')


@admin.register(models.AiInsight)
class AiInsightAdmin(admin.ModelAdmin):
    list_display = ('title', 'kind', 'severity', 'status', 'module', 'created_at')
    list_filter = ('severity', 'status', 'kind')
    search_fields = ('title', 'body', 'dedupe_key')
    date_hierarchy = 'created_at'
    readonly_fields = ('public_id', 'dedupe_key', 'data', 'created_at', 'updated_at')
    autocomplete_fields = ('module', 'student', 'owner', 'suggested_action')


class AdminAIMessageInline(admin.TabularInline):
    model = models.AdminAIMessage
    extra = 0
    fields = ('role', 'content', 'input_tokens', 'output_tokens', 'model', 'created_at')
    readonly_fields = fields
    can_delete = False


@admin.register(models.AdminAIThread)
class AdminAIThreadAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'total_input_tokens', 'total_output_tokens', 'updated_at')
    search_fields = ('title', 'user__username', 'user__email')
    readonly_fields = ('public_id', 'total_input_tokens', 'total_output_tokens', 'created_at', 'updated_at')
    inlines = [AdminAIMessageInline]
