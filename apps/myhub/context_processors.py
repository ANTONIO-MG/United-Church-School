"""Context processor exposing shared nav/dashboard data to every template.

This used to compute institution-wide aggregates for the old MyHub theme —
student / professor / course / library / holiday counts, recent-item lists, fee
collection totals. Those pages and their models are gone, and nothing rendered
the numbers, so all that is left is what templates actually read:

- ``badges`` — status → CSS-class map, so templates skip if/elif chains
- ``upcoming_events`` — the calendar strip on the dashboard
- ``my_programmes_count`` / ``my_modules_count`` — the "My Programme" nav link

Programmes and modules, never courses: a course is not a thing on this platform.
"""

from datetime import timedelta

from django.utils import timezone

from core.request_cache import cached_per_request

from . import models


def get_status_badge_config():
    """Map status values to badge CSS classes."""
    return {
        'status_badges': {
            'active': {'class': 'success', 'text': 'Active'},
            'inactive': {'class': 'secondary', 'text': 'Inactive'},
        },
        'fee_badges': {
            'paid': {'class': 'success', 'text': 'Paid'},
            'partial': {'class': 'warning', 'text': 'Partial'},
            'pending': {'class': 'danger', 'text': 'Pending'},
        },
        'publish_badges': {
            'draft': {'class': 'warning', 'text': 'Draft'},
            'published': {'class': 'success', 'text': 'Published'},
            'archived': {'class': 'secondary', 'text': 'Archived'},
        },
    }


def get_upcoming_events(days_ahead=30):
    """Events starting within the next N days."""
    now = timezone.now()
    return (models.Event.objects
            .filter(start__gte=now, start__lte=now + timedelta(days=days_ahead))
            .order_by('start'))


def _build_get_dashboard_data(request):
    data = {
        'badges': get_status_badge_config(),
        'upcoming_events': get_upcoming_events(),
        'my_programmes_count': 0,
        'my_modules_count': 0,
    }

    # What the candidate is registered for, off the academic spine — drives the
    # "My Programme(s)" nav link (its label, and whether it shows at all) and the
    # module count beside it.
    person = getattr(request.user, 'profile', None) if request.user.is_authenticated else None
    if person is not None:
        from apps.learning.models import ModuleEnrolment, ProgrammeEnrolment
        data['my_programmes_count'] = ProgrammeEnrolment.objects.filter(person=person).count()
        data['my_modules_count'] = ModuleEnrolment.objects.filter(person=person).count()
    return data


def get_dashboard_data(request):
    """Cached for the life of the request — these are nav badges, and this
    processor runs once per template rendered in a response, not once per
    response."""
    return cached_per_request(request, 'dashboard_data', lambda: _build_get_dashboard_data(request))
