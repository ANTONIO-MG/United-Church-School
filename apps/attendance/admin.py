from django.contrib import admin

from .models import AttendanceMark, DailyRegister


class AttendanceMarkInline(admin.TabularInline):
    model = AttendanceMark
    extra = 0
    fields = ('learner', 'status', 'reason', 'marked_by', 'parents_notified_at', 'updated_at')
    readonly_fields = ('updated_at', 'parents_notified_at')
    raw_id_fields = ('learner', 'marked_by')


@admin.register(DailyRegister)
class DailyRegisterAdmin(admin.ModelAdmin):
    list_display = ('date', 'cohort', 'status', 'auto_submitted', 'submitted_by', 'submitted_at')
    list_filter = ('status', 'auto_submitted', 'cohort__programme')
    date_hierarchy = 'date'
    raw_id_fields = ('submitted_by', 'task')
    inlines = [AttendanceMarkInline]


@admin.register(AttendanceMark)
class AttendanceMarkAdmin(admin.ModelAdmin):
    list_display = ('learner', 'register', 'status', 'reason', 'marked_by', 'updated_at')
    list_filter = ('status', 'register__date')
    search_fields = ('learner__first_name', 'learner__last_name', 'learner__user__email')
    raw_id_fields = ('register', 'learner', 'marked_by')
