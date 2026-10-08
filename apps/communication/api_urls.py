"""URL routing for the communication REST API (mounted at ``/api/communication/``)."""

from rest_framework.routers import DefaultRouter

from . import api

app_name = 'communication-api'

router = DefaultRouter()
router.register('chat-groups', api.ChatGroupViewSet, basename='chatgroup')
router.register('messages', api.MessageViewSet, basename='message')
router.register('meetings', api.MeetingRoomViewSet, basename='meeting')
router.register('notifications', api.NotificationViewSet, basename='notification')
router.register('announcements', api.AnnouncementViewSet, basename='announcement')

urlpatterns = router.urls
