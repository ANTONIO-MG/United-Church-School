"""Django admin registration for the MyHub domain.

The calendar is all that is left here after the clean sweep. This module used to
carry admin classes for Student, Professor, Staff, Course, CourseAddon, FeeType,
FeePayment, LibraryItem, Holiday, Content, Menu, EmailTemplate, BlogCategory and
BlogPost — every one of those models was deleted in
``myhub/migrations/0006_remove_blogpost_category_delete_content_and_more.py``.
The classes outlived their models because none of them was ever registered, so
nothing raised. They are removed rather than left as furniture: an
``EmailTemplateAdmin`` sitting in the tree reads as a feature that exists.

``Event`` is also exposed over the REST API (:mod:`apps.myhub.api`).
"""

from django.contrib import admin

from . import models


@admin.register(models.Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'start', 'end', 'all_day', 'location')
    list_filter = ('all_day', 'start')
    search_fields = ('title', 'location')
    date_hierarchy = 'start'
    ordering = ('-start',)
