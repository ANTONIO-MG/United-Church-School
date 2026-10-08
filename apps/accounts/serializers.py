"""DRF serializers for the accounts app.

These power the ``/api/accounts/`` endpoints (see :mod:`apps.accounts.api`)
plus the custom registration serializer wired into dj-rest-auth via
``REST_AUTH_REGISTER_SERIALIZERS`` in settings.
"""

from django.contrib.auth import get_user_model
from rest_framework import serializers

from core.utils import display_name

from apps.learning.models import ProgrammeModule
from .models import ActivityLog, Person

try:  # dj-rest-auth may not be importable in some tooling contexts
    from dj_rest_auth.registration.serializers import RegisterSerializer
except Exception:  # pragma: no cover
    RegisterSerializer = serializers.Serializer

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    # The platform is e-mail-only — the internal `username` column is not exposed.
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'display_name', 'is_active', 'date_joined']
        read_only_fields = ['date_joined']

    def get_display_name(self, obj):
        return display_name(obj)


# Fields on Person that decide what an account is *allowed to do*, or that the
# enrolment/consent machinery owns. A user editing their own profile must never
# be able to set these — ``user_type`` in particular is what ``core.roles``
# reads to grant ``can_manage``, so a writable ``user_type`` is a self-service
# route to administrator. Admins still edit them through the management UI
# (and through :class:`PersonAdminSerializer` below).
PERSON_PRIVILEGED_FIELDS = (
    'user_type',            # the role itself — grants can_manage / can_teach
    'profile_status',       # onboarding gates
    'registered',
    'pending_invoice_uid',  # the enrolment payment gate
    'invite',
    'terms_accepted_at',    # consent is captured server-side at signup
    'terms_version',
    'guardian_emails',      # drives who gets a parent invite
)


class PersonSerializer(serializers.ModelSerializer):
    """A person as they may edit *themselves*.

    Everything in :data:`PERSON_PRIVILEGED_FIELDS` is exposed but read-only, so
    a client can display its own role/enrolment state without being able to
    change it.
    """

    user = UserSerializer(read_only=True)

    class Meta:
        model = Person
        fields = '__all__'
        read_only_fields = PERSON_PRIVILEGED_FIELDS


class PersonAdminSerializer(serializers.ModelSerializer):
    """The full record, writable. Only ever handed to admin/staff."""

    user = UserSerializer(read_only=True)

    class Meta:
        model = Person
        fields = '__all__'


class SubjectSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True, default=None)
    educator_count = serializers.IntegerField(source='educators.count', read_only=True)
    student_count = serializers.IntegerField(source='students.count', read_only=True)

    class Meta:
        model = ProgrammeModule
        fields = '__all__'


class ActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLog
        fields = '__all__'


class CustomRegisterSerializer(RegisterSerializer):
    """Registration serializer that also captures the new user's name and
    creates the matching :class:`~apps.accounts.models.Person` profile."""

    first_name = serializers.CharField(required=False, allow_blank=True, max_length=50)
    last_name = serializers.CharField(required=False, allow_blank=True, max_length=50)

    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        data['first_name'] = self.validated_data.get('first_name', '')
        data['last_name'] = self.validated_data.get('last_name', '')
        return data

    def save(self, request):
        user = super().save(request)
        Person.objects.get_or_create(
            user=user,
            defaults={
                'first_name': self.cleaned_data.get('first_name', ''),
                'last_name': self.cleaned_data.get('last_name', ''),
            },
        )
        return user