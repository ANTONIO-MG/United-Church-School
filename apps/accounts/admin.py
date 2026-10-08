"""Django admin for the accounts app.

Registers every model — Person, ProgrammeModule and the read-only ActivityLog — with
name/date filtering, search and inline membership editing. Themed by
django-admin-soft-dashboard (see ``admin_soft`` in INSTALLED_APPS).
"""

from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from .models import (
    ActivityLog, Invitation, ParentLink, Person, PersonConsent, PersonContact,
    PersonStudyProfile,
)
from .resources import PersonResource


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ('email', 'role', 'student', 'status', 'created_at', 'accepted_at')
    list_filter = ('role', 'status', 'created_at')
    search_fields = ('email', 'student__user__email')
    autocomplete_fields = ('student', 'invited_by', 'accepted_by')


@admin.register(ParentLink)
class ParentLinkAdmin(admin.ModelAdmin):
    list_display = ('parent', 'student', 'created_at')
    search_fields = ('parent__username', 'parent__email', 'student__username', 'student__email')


class PersonContactInline(admin.StackedInline):
    model = PersonContact
    extra = 0
    can_delete = False


class PersonStudyProfileInline(admin.StackedInline):
    """The academic calendar (exam / assignment / practical / vacation dates)."""
    model = PersonStudyProfile
    extra = 0
    can_delete = False


class PersonConsentInline(admin.StackedInline):
    model = PersonConsent
    extra = 0
    can_delete = False


@admin.register(Person)
class PersonAdmin(ImportExportModelAdmin):
    """People, with Excel/CSV import & export (see :mod:`apps.accounts.resources`)."""

    resource_classes = [PersonResource]
    list_display = ('__str__', 'user_email', 'user_type', 'registered', 'profile_status')
    list_filter = ('user_type', 'registered', 'profile_status', 'gender')
    search_fields = ('first_name', 'last_name', 'user__email', 'user__username', 'phone', 'ms_upn')
    autocomplete_fields = ('user',)
    list_select_related = ('user',)
    inlines = [PersonContactInline, PersonStudyProfileInline, PersonConsentInline]

    @admin.display(description='Email', ordering='user__email')
    def user_email(self, obj):
        return obj.user.email if obj.user_id else ''


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'actor', 'target_user', 'ip_address', 'timestamp')
    list_filter = ('action', 'timestamp')
    search_fields = ('description',)
    date_hierarchy = 'timestamp'
    readonly_fields = ('timestamp',)
