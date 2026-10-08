"""Django admin for the assessment engine (soft-dashboard themed)."""

from django.contrib import admin

from . import models


class SectionInline(admin.TabularInline):
    model = models.Section
    extra = 1
    show_change_link = True


class ChoiceInline(admin.TabularInline):
    model = models.Choice
    extra = 2


class QuestionInline(admin.TabularInline):
    model = models.Question
    extra = 1
    fields = ('type', 'text', 'marks', 'marking_mode', 'order')
    show_change_link = True


class ExamSectionInline(admin.TabularInline):
    model = models.ExamSection
    extra = 1
    autocomplete_fields = ('assessment',)


class AnswerInline(admin.TabularInline):
    model = models.Answer
    extra = 0
    readonly_fields = ('question', 'awarded_marks', 'is_correct', 'marked', 'marked_by')
    can_delete = False


@admin.register(models.Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'kind', 'grade_component', 'module', 'total_marks', 'pass_mark_pct',
                    'time_limit_minutes', 'attempts_allowed', 'status', 'available_from')
    list_filter = ('kind', 'component', 'status', 'module', 'available_from')
    search_fields = ('title', 'description')
    date_hierarchy = 'available_from'
    autocomplete_fields = ('module', 'lesson', 'created_by')
    inlines = [SectionInline]

    @admin.display(description='Component')
    def grade_component(self, obj):
        return obj.grade_component


@admin.register(models.Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'assessment', 'order')
    search_fields = ('title', 'assessment__title')
    autocomplete_fields = ('assessment',)
    inlines = [QuestionInline]


@admin.register(models.Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('short_text', 'type', 'marking_mode', 'section', 'marks', 'order')
    list_filter = ('type', 'marking_mode')
    search_fields = ('text',)
    autocomplete_fields = ('section',)
    inlines = [ChoiceInline]

    @admin.display(description='Question')
    def short_text(self, obj):
        return obj.text[:60]


@admin.register(models.Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'status', 'lock_after_submit', 'invigilator_mode', 'available_from')
    list_filter = ('status', 'module', 'available_from')
    search_fields = ('title', 'description')
    date_hierarchy = 'available_from'
    autocomplete_fields = ('module', 'created_by')
    inlines = [ExamSectionInline]


@admin.register(models.AssessmentAttempt)
class AssessmentAttemptAdmin(admin.ModelAdmin):
    list_display = ('student', 'assessment', 'attempt_no', 'status', 'score', 'passed', 'submitted_at')
    list_filter = ('status', 'passed', 'submitted_at')
    search_fields = ('student__username', 'student__email', 'assessment__title')
    date_hierarchy = 'created_at'
    autocomplete_fields = ('assessment', 'student')
    readonly_fields = ('public_id',)
    inlines = [AnswerInline]


@admin.register(models.AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'assessment', 'status', 'grade', 'submitted_at', 'marked_by')
    list_filter = ('status', 'submitted_at')
    search_fields = ('student__username', 'student__email', 'assessment__title')
    date_hierarchy = 'created_at'
    autocomplete_fields = ('assessment', 'student', 'marked_by')
