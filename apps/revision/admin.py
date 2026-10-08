from django.contrib import admin

from . import models


@admin.register(models.ReviewCard)
class ReviewCardAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'box', 'due_at', 'streak', 'lapses', 'suspended', 'created_at')
    list_filter = ('box', 'suspended')
    search_fields = ('user__email', 'user__username', 'question__text')
    raw_id_fields = ('user', 'question', 'source_attempt')
    date_hierarchy = 'due_at'


@admin.register(models.ReviewLog)
class ReviewLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'card', 'grade', 'box_before', 'box_after', 'reviewed_at')
    list_filter = ('grade',)
    raw_id_fields = ('user', 'card')
