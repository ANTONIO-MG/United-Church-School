"""URL routing for the MyHub REST API (mounted at ``/api/myhub/``)."""

from rest_framework.routers import DefaultRouter

from . import api

app_name = 'myhub-api'

router = DefaultRouter()
router.register('events', api.EventViewSet, basename='event')

urlpatterns = router.urls
