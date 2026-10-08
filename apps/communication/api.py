"""REST API for the communication app (mounted at ``/api/communication/``).

Endpoints (all require an authenticated user):

* ``chat-groups/``        — conversations the user belongs to (+ ``members`` /
  ``mark_read`` actions)
* ``messages/?group=<id>`` — messages in a group; create (with ``files`` and
  ``mention_ids``), edit your own (sets ``is_edited``), delete (soft delete)
* ``meetings/``           — video/audio rooms & class sessions (+ ``invite`` action)
* ``notifications/``      — your notifications (+ ``mark_read`` / ``mark_all_read`` /
  ``unread_count``)
* ``announcements/``      — staff/admin broadcasts (+ ``send`` action)
"""

from django.utils import timezone
from rest_framework import decorators, permissions, response, status, viewsets

from core.errors import note

from . import models, serializers, services


def _is_member(user, group):
    return group.memberships.filter(user=user).exists()


class ChatGroupViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ChatGroupSerializer
    permission_classes = [permissions.IsAuthenticated]
    # 'course' was removed from ChatGroup and 'module' is now 'programme_module' —
    # listing the old names made django-filter raise on every request (500).
    filterset_fields = ['kind', 'is_active', 'programme_module']
    search_fields = ['name', 'description']
    ordering_fields = ['updated_at', 'created_at']

    def get_queryset(self):
        qs = models.ChatGroup.objects.all().prefetch_related('memberships')
        user = self.request.user
        if user.is_staff:
            return qs
        return qs.filter(memberships__user=user).distinct()

    def perform_create(self, serializer):
        # Custom (manual) groups only — course/module groups are auto-managed.
        group = serializer.save(kind=models.ChatGroup.KIND_CUSTOM, created_by=self.request.user)
        group.add_member(self.request.user, role='owner')

    @decorators.action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        group = self.get_object()
        data = serializers.ChatMembershipSerializer(
            group.memberships.select_related('user'), many=True, context={'request': request}
        ).data
        return response.Response(data)

    @decorators.action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        group = self.get_object()
        membership = group.memberships.filter(user=request.user).first()
        if not membership:
            return response.Response(status=status.HTTP_403_FORBIDDEN)
        membership.last_read_at = timezone.now()
        membership.save(update_fields=['last_read_at'])
        return response.Response({'status': 'ok', 'last_read_at': membership.last_read_at})


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['group', 'sender']
    ordering_fields = ['created_at']

    def get_queryset(self):
        qs = (models.Message.objects.filter(is_deleted=False)
              .select_related('sender', 'sender__profile', 'group', 'reply_to', 'reply_to__sender')
              .prefetch_related('attachments', 'mention_links__user'))
        user = self.request.user
        if not user.is_staff:
            qs = qs.filter(group__memberships__user=user)
        return qs.distinct()

    def _save_extras(self, message, serializer):
        """Attach uploaded files and explicit mentions, then fan out notifications."""
        files = serializer.validated_data.get('_files') or []
        for f in files:
            att = models.MessageAttachment(message=message, file=f, original_name=getattr(f, 'name', ''))
            att.save()
        for user in serializer.validated_data.get('_mention_ids') or []:
            models.MessageMention.objects.get_or_create(message=message, user=user)
        services.create_mention_notifications(message)

    def perform_create(self, serializer):
        group = serializer.validated_data['group']
        if not (self.request.user.is_staff or _is_member(self.request.user, group)):
            from rest_framework.exceptions import PermissionDenied
            note('CHAT-2001', self.request, group=group.pk)
            raise PermissionDenied('You are not a member of this chat group. (CHAT-2001)')
        # Student ↔ student direct chats require an accepted connection first.
        if group.kind == models.ChatGroup.KIND_DIRECT:
            other = services.other_member(group, self.request.user)
            if other is not None and not services.can_direct_message(self.request.user, other):
                from rest_framework.exceptions import PermissionDenied
                note('CHAT-2002', self.request, group=group.pk, other=other.pk)
                raise PermissionDenied(
                    'You can only message this person once they accept your '
                    'connection request. (CHAT-2002)')
        # Block muted / chat-suspended users from sending (moderation penalties).
        penalty = services.active_silencing_penalty(self.request.user)
        if penalty is not None:
            from rest_framework.exceptions import PermissionDenied
            until = f' until {penalty.ends_at:%Y-%m-%d %H:%M}' if penalty.ends_at else ''
            note('CHAT-2003', self.request, penalty=penalty.pk, kind=penalty.kind)
            raise PermissionDenied(
                f'You are {penalty.get_kind_display().lower()}{until} and cannot '
                f'send messages. (CHAT-2003)')
        message = serializer.save(sender=self.request.user)
        self._save_extras(message, serializer)
        group.save(update_fields=['updated_at'])
        # Real-time fan-out: poke the open conversation + ping every other
        # member's bell (sound/badge). Best-effort; polling covers the rest.
        try:
            from .realtime import broadcast_new_message
            broadcast_new_message(message)
        except Exception:
            pass

    def perform_update(self, serializer):
        message = self.get_object()
        if message.sender_id != self.request.user.id and not self.request.user.is_staff:
            from rest_framework.exceptions import PermissionDenied
            note('CHAT-2004', self.request, message=message.pk, action='edit')
            raise PermissionDenied('You can only edit your own messages. (CHAT-2004)')
        message = serializer.save()
        message.mark_edited()
        message.save(update_fields=['is_edited', 'edited_at'])
        self._save_extras(message, serializer)

    def perform_destroy(self, instance):
        if instance.sender_id != self.request.user.id and not self.request.user.is_staff:
            from rest_framework.exceptions import PermissionDenied
            note('CHAT-2004', self.request, message=instance.pk, action='delete')
            raise PermissionDenied('You can only delete your own messages. (CHAT-2004)')
        instance.is_deleted = True
        instance.body = ''
        instance.save(update_fields=['is_deleted', 'body'])


class MeetingRoomViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.MeetingRoomSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['is_active', 'is_recurring', 'group', 'host']
    search_fields = ['title', 'description']
    ordering_fields = ['scheduled_start', 'created_at']

    def get_queryset(self):
        return models.MeetingRoom.objects.select_related('host', 'group').all()

    def perform_create(self, serializer):
        serializer.save(host=self.request.user)

    @decorators.action(detail=True, methods=['post'])
    def invite(self, request, pk=None):
        """Invite users by id: ``{"user_ids": [...], "role": "attendee"}``. Notifies them."""
        meeting = self.get_object()
        role = request.data.get('role', 'attendee')
        from django.contrib.auth import get_user_model
        users = get_user_model().objects.filter(pk__in=request.data.get('user_ids', []))
        for user in users:
            models.MeetingParticipant.objects.get_or_create(meeting=meeting, user=user, defaults={'role': role})
            services.notify(
                user, actor=request.user, verb='invited you to a meeting',
                title=f'Meeting: {meeting.title}',
                body=meeting.description, level='info',
                url=meeting.get_join_url(), meeting=meeting,
                email=meeting.scheduled_start is not None,
            )
        return response.Response({'invited': users.count()})


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['is_read', 'level']
    ordering_fields = ['created_at']

    def get_queryset(self):
        return models.Notification.objects.filter(recipient=self.request.user).select_related('actor')

    @decorators.action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        note = self.get_object()
        note.mark_read()
        return response.Response({'status': 'ok'})

    @decorators.action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        updated = self.get_queryset().filter(is_read=False).update(is_read=True)
        return response.Response({'updated': updated})

    @decorators.action(detail=False, methods=['get'])
    def unread_count(self, request):
        return response.Response({'unread': self.get_queryset().filter(is_read=False).count()})


class AnnouncementViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.AnnouncementSerializer
    permission_classes = [permissions.IsAdminUser]  # staff/admin only
    filterset_fields = ['audience', 'level', 'send_email']
    search_fields = ['title', 'body']
    ordering_fields = ['created_at']

    def get_queryset(self):
        return models.Announcement.objects.select_related('sender').all()

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

    @decorators.action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        """Deliver this announcement (notifications + optional e-mail). Idempotent-ish."""
        announcement = self.get_object()
        count = services.send_announcement(announcement)
        return response.Response({'sent_to': count, 'sent_at': announcement.sent_at})
