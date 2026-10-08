"""Django admin for reporting & certificates (soft-dashboard themed)."""

from django.contrib import admin
from import_export.admin import ExportActionModelAdmin

from . import models
from .resources import CertificateResource, GradeResource


@admin.register(models.ModuleWeighting)
class SubjectWeightingAdmin(admin.ModelAdmin):
    list_display = ('module', 'assignments_pct', 'quizzes_pct', 'tests_pct',
                    'exams_pct', 'tasks_pct', 'pass_mark_pct', 'extra_credit_pct', 'total')
    search_fields = ('module__name',)
    autocomplete_fields = ('module',)

    @admin.display(description='Total')
    def total(self, obj):
        return f'{obj.total()}%'


@admin.register(models.Grade)
class GradeAdmin(ExportActionModelAdmin):
    """Grades, exportable to Excel/CSV. Export-only by design — marks are
    computed by apps.reports.services, so importing them back would overwrite
    the calculation with whatever a spreadsheet happened to contain."""

    resource_classes = [GradeResource]
    list_display = ('student', 'module', 'final_pct', 'letter', 'extra_credit_pct',
                    'passed', 'standing', 'study_hours', 'computed_at')
    list_filter = ('passed', 'module', 'computed_at')
    search_fields = ('student__username', 'student__email', 'module__name')
    date_hierarchy = 'computed_at'
    autocomplete_fields = ('student', 'module')
    # Written module-wide by services.rank_module, never edited by hand.
    readonly_fields = ('class_position', 'cohort_size', 'cohort_average', 'ranked_at')

    @admin.display(description='Class position', ordering='class_position')
    def standing(self, obj):
        """"3rd of 24 (avg 61%)" — blank until the module has been ranked."""
        if not obj.class_position or not obj.cohort_size:
            return '—'
        return f'{obj.class_position} of {obj.cohort_size} (avg {obj.cohort_average}%)'


@admin.register(models.Certificate)
class CertificateAdmin(ExportActionModelAdmin):
    resource_classes = [CertificateResource]
    list_display = ('number', 'student', 'kind', 'title', 'final_mark', 'issued_at')
    list_filter = ('kind', 'issued_at')
    search_fields = ('number', 'student__username', 'student__email', 'title')
    date_hierarchy = 'issued_at'
    autocomplete_fields = ('student', 'module')
    readonly_fields = ('number', 'verification_uuid')
