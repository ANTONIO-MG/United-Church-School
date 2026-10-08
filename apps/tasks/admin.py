"""Django admin registration for the tasks models."""

from django.contrib import admin

from . import models


class TaskAssignmentInline(admin.TabularInline):
    model = models.TaskAssignment
    extra = 0
    readonly_fields = ('submitted_at', 'completed_at')


@admin.register(models.Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'assign_to', 'priority', 'due_date', 'status', 'delivery',
                    'created_by', 'created_at')
    list_filter = ('assign_to', 'priority', 'status', 'due_date', 'created_at')
    search_fields = ('title', 'description')
    date_hierarchy = 'due_date'
    ordering = ('-created_at',)
    autocomplete_fields = ('lesson', 'assessment')
    inlines = [TaskAssignmentInline]

    @admin.display(description='Delivery')
    def delivery(self, obj):
        return obj.kind_label


@admin.register(models.TaskAssignment)
class TaskAssignmentAdmin(admin.ModelAdmin):
    list_display = ('task', 'user', 'status', 'progress', 'score')
    list_filter = ('status',)
    search_fields = ('task__title', 'user__email', 'user__username')
