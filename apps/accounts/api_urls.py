"""URL routing for the accounts REST API (mounted at ``/api/accounts/``)."""

from rest_framework.routers import DefaultRouter

from . import api

app_name = 'accounts-api'

router = DefaultRouter()
router.register('users', api.UserViewSet, basename='user')
router.register('people', api.PersonViewSet, basename='person')
router.register('activity-log', api.ActivityLogViewSet, basename='activitylog')

urlpatterns = router.urls
