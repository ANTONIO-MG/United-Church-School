"""REST API viewsets for the accounts app (mounted at ``/api/accounts/``).

Exposes the universal user/profile and organisation-structure models so the
web, mobile and desktop clients share one API surface.  All endpoints require
an authenticated user; the activity log is read-only.
"""

from django.contrib.auth import get_user_model
from rest_framework import permissions, viewsets

from core.roles import role_flags

from . import serializers as s
from apps.learning.models import ProgrammeModule
from .models import ActivityLog, Person

User = get_user_model()


class IsManager(permissions.BasePermission):
    """Admin/staff only — the API twin of ``ManagementAccessMiddleware``.

    Uses ``role_flags(...)['is_admin_staff']`` rather than DRF's ``IsAdminUser``
    so it recognises the same people the HTML management pages do: Django
    staff/superusers *and* accounts whose ``Person.user_type`` is admin or staff.
    """

    message = 'Only administrators and staff may perform this action.'

    def has_permission(self, request, view):
        user = getattr(request, 'user', None)
        if user is None or not user.is_authenticated:
            return False
        return role_flags(request)['is_admin_staff']


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = s.UserSerializer
    permission_classes = [permissions.IsAdminUser]
    search_fields = ['email', 'first_name', 'last_name']
    ordering_fields = ['id', 'email', 'date_joined']
    filterset_fields = ['is_active', 'is_staff']


class PersonViewSet(viewsets.ModelViewSet):
    """Profiles. Admin/staff see everyone; everybody else sees only themselves.

    The HTML side is gated by ``ManagementAccessMiddleware``, but ``/api/`` is on
    that middleware's exempt list — so the scoping has to be repeated here or the
    API is a way round it. Three things are enforced:

    * ``get_queryset`` narrows non-admins to their own row, so another person's
      profile cannot be read, rewritten or deleted;
    * ``get_serializer_class`` gives non-admins a serializer where
      :data:`~.serializers.PERSON_PRIVILEGED_FIELDS` (``user_type`` above all)
      are read-only, so nobody can promote themselves;
    * creating and deleting people is admin-only regardless of scope — a
      profile is created by the signup flow, not by a client.
    """

    queryset = Person.objects.select_related('user').order_by('first_name', 'last_name', 'id')
    serializer_class = s.PersonSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['first_name', 'last_name', 'user__email']
    ordering_fields = ['first_name', 'last_name']
    filterset_fields = ['user_type', 'gender', 'profile_status']
    # Only admin/staff may bring a Person into existence or remove one.
    admin_only_actions = ('create', 'destroy')

    def _is_manager(self):
        return role_flags(self.request)['is_admin_staff']

    def get_permissions(self):
        if getattr(self, 'action', None) in self.admin_only_actions:
            return [IsManager()]
        return super().get_permissions()

    def get_queryset(self):
        qs = super().get_queryset()
        if self._is_manager():
            return qs
        return qs.filter(user=self.request.user)

    def get_serializer_class(self):
        return s.PersonAdminSerializer if self._is_manager() else s.PersonSerializer


class ActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ActivityLog.objects.select_related('actor', 'target_user').all()
    serializer_class = s.ActivityLogSerializer
    permission_classes = [permissions.IsAdminUser]
    search_fields = ['description', 'request_path']
    ordering_fields = ['timestamp', 'action']
    filterset_fields = ['action', 'actor', 'target_user']
