"""Django admin for analytics (soft-dashboard themed)."""

from django.contrib import admin

from . import models


@admin.register(models.RiskFlag)
class RiskFlagAdmin(admin.ModelAdmin):
    list_display = ('student', 'module', 'score', 'resolved', 'created_at')
    list_filter = ('resolved', 'created_at')
    search_fields = ('student__username', 'student__email')
    date_hierarchy = 'created_at'
    autocomplete_fields = ('student', 'module')


@admin.register(models.ReportSnapshot)
class ReportSnapshotAdmin(admin.ModelAdmin):
    list_display = ('scope', 'period', 'generated_at')
    list_filter = ('period', 'generated_at')
    search_fields = ('scope',)
    date_hierarchy = 'generated_at'
    readonly_fields = ('generated_at',)
