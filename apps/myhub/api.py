"""REST API viewsets for the MyHub domain.

The calendar is all that is left here after the clean sweep. ``/api/myhub/events/``
supports list / create / retrieve / update / partial-update / destroy, plus
search (``?search=``), ordering (``?ordering=``) and field filtering. Every
method requires an authenticated user.
"""

from rest_framework import permissions, viewsets

from . import models, serializers


class BaseModelViewSet(viewsets.ModelViewSet):
    """Signed-in users only — including for reads.

    ``/api/`` is on ``LoginRequiredMiddleware``'s exempt list (DRF authenticates
    itself, and has to answer in JSON rather than redirect to a login page), so
    the site-wide login gate does not cover these URLs. That made
    ``IsAuthenticatedOrReadOnly`` the one anonymous data path into an otherwise
    private site: an Event carries its title, location, description and times.
    Nothing in the product reads this logged out, so requiring authentication
    costs nothing.
    """

    permission_classes = [permissions.IsAuthenticated]


class EventViewSet(BaseModelViewSet):
    queryset = models.Event.objects.all()
    serializer_class = serializers.EventSerializer
    filterset_fields = ['all_day']
    search_fields = ['title', 'location', 'description']
    ordering_fields = ['start', 'end', 'title']
