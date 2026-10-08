"""DRF serializers for the communication REST API (``/api/communication/``)."""

from django.contrib.auth import get_user_model
from rest_framework import serializers

from core.utils import DISCONTINUED_USER, avatar_url, display_name, initials

from . import models

User = get_user_model()


class UserMiniSerializer(serializers.ModelSerializer):
    """Compact user representation embedded in chat / meeting / notification payloads.

    Identify a user by ``id`` and label them with ``display_name`` — the e-mail-only
    platform has no usernames, so no ``username`` field is exposed. ``avatar`` is
    the profile picture (``null`` when unset) and ``initials`` the fallback the UI
    draws in its place, so a client never has to guess how to letter a face.
    """

    display_name = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    initials = serializers.SerializerMethodField()

    class Meta:
        model = User
        # No e-mail: everyone in a conversation would otherwise receive every
        # other member's address. People are identified by name and picture.
        fields = ['id', 'first_name', 'last_name', 'display_name', 'avatar', 'initials']

    def get_display_name(self, obj):
        return display_name(obj)

    def get_avatar(self, obj):
        url = avatar_url(obj)
        request = self.context.get('request')
        return request.build_absolute_uri(url) if (url and request) else url

    def get_initials(self, obj):
        return initials(obj)


class MessageAttachmentSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = models.MessageAttachment
        fields = ['id', 'kind', 'original_name', 'size', 'url', 'created_at']

    def get_url(self, obj):
        request = self.context.get('request')
        if not obj.file:
            return None
        return request.build_absolute_uri(obj.file.url) if request else obj.file.url


class MessageMentionSerializer(serializers.ModelSerializer):
    user = UserMiniSerializer(read_only=True)

    class Meta:
        model = models.MessageMention
        fields = ['id', 'user', 'seen', 'created_at']


class MessageSerializer(serializers.ModelSerializer):
    # SerializerMethodField rather than a nested serializer: ``Message.sender`` is
    # SET_NULL, so a message whose author closed their account has no user row
    # left. The thread still belongs to everyone else in it, so the bubble stays
    # and is attributed to the discontinued account instead of going blank.
    sender = serializers.SerializerMethodField()
    attachments = MessageAttachmentSerializer(many=True, read_only=True)
    mention_links = MessageMentionSerializer(many=True, read_only=True)
    # The quoted message a reply points at — just enough to draw the quote strip
    # above the bubble without a second round trip per message.
    reply_preview = serializers.SerializerMethodField()
    # How many other members have read this message (their ``last_read_at`` is at
    # or past it). Drives the sent / read ticks on your own bubbles.
    read_by_count = serializers.SerializerMethodField()
    other_member_count = serializers.SerializerMethodField()
    # Write-only: list of user ids to tag (in addition to any @handles in `body`).
    mention_ids = serializers.PrimaryKeyRelatedField(
        many=True, write_only=True, required=False, queryset=User.objects.all(), source='_mention_ids',
    )
    # Write-only: list of uploaded files for this message.
    files = serializers.ListField(
        child=serializers.FileField(), write_only=True, required=False, source='_files',
    )

    class Meta:
        model = models.Message
        fields = [
            'id', 'group', 'sender', 'body', 'reply_to', 'reply_preview', 'attachments',
            'mention_links', 'mention_ids', 'files',
            'read_by_count', 'other_member_count',
            'is_edited', 'edited_at', 'is_deleted', 'created_at',
        ]
        read_only_fields = ['sender', 'is_edited', 'edited_at', 'is_deleted', 'created_at']

    def get_sender(self, obj):
        if obj.sender_id is None:
            return {'id': None, 'email': '', 'first_name': '', 'last_name': '',
                    'display_name': DISCONTINUED_USER, 'avatar': None, 'initials': '–',
                    'discontinued': True}
        return UserMiniSerializer(obj.sender, context=self.context).data

    # --- Read receipts -----------------------------------------------------
    # One query per group per request, cached on the serializer context, rather
    # than one per message: a 200-message thread would otherwise issue 200.
    def _read_marks(self, group_id):
        cache = self.context.setdefault('_read_marks', {})
        if group_id not in cache:
            cache[group_id] = list(
                models.ChatMembership.objects.filter(group_id=group_id)
                .values_list('user_id', 'last_read_at'))
        return cache[group_id]

    def get_read_by_count(self, obj):
        if not obj.group_id:
            return 0
        return sum(
            1 for user_id, last_read in self._read_marks(obj.group_id)
            if user_id != obj.sender_id and last_read and last_read >= obj.created_at
        )

    def get_other_member_count(self, obj):
        if not obj.group_id:
            return 0
        return sum(1 for user_id, _ in self._read_marks(obj.group_id) if user_id != obj.sender_id)

    def get_reply_preview(self, obj):
        parent = obj.reply_to
        if parent is None:
            return None
        return {
            'id': parent.id,
            'sender': display_name(parent.sender) or 'Someone',
            'body': (parent.body or '')[:140],
            'has_attachment': parent.attachments.exists(),
        }

    # ``_files`` / ``_mention_ids`` are not model fields — strip them before the
    # ModelSerializer hands ``validated_data`` to ``Message(...)``. The view
    # still reads them off ``serializer.validated_data`` to create attachments
    # and mention rows.
    def create(self, validated_data):
        validated_data.pop('_files', None)
        validated_data.pop('_mention_ids', None)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.pop('_files', None)
        validated_data.pop('_mention_ids', None)
        return super().update(instance, validated_data)


class ChatMembershipSerializer(serializers.ModelSerializer):
    user = UserMiniSerializer(read_only=True)
    unread_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.ChatMembership
        fields = ['id', 'user', 'role', 'is_auto', 'muted', 'last_read_at', 'joined_at', 'unread_count']


class ChatGroupSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(read_only=True)
    is_auto_managed = serializers.BooleanField(read_only=True)
    member_count = serializers.IntegerField(source='memberships.count', read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = models.ChatGroup
        fields = [
            'id', 'kind', 'name', 'display_name', 'description',
            'programme_module', 'is_auto_managed', 'is_active', 'member_count',
            'last_message', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_last_message(self, obj):
        msg = obj.messages.filter(is_deleted=False).order_by('-created_at').first()
        if not msg:
            return None
        return {'id': msg.id, 'body': (msg.body or '')[:120],
                'sender': display_name(msg.sender),
                'created_at': msg.created_at}


class MeetingRoomSerializer(serializers.ModelSerializer):
    host = UserMiniSerializer(read_only=True)
    join_url = serializers.SerializerMethodField()
    external_url = serializers.CharField(read_only=True)
    room_name = serializers.CharField(read_only=True)
    is_live_now = serializers.BooleanField(read_only=True)
    is_upcoming = serializers.BooleanField(read_only=True)

    class Meta:
        model = models.MeetingRoom
        fields = [
            'id', 'title', 'slug', 'description', 'host', 'group',
            'scheduled_start', 'scheduled_end', 'is_recurring', 'recurrence',
            'requires_login', 'is_active', 'join_url', 'external_url', 'room_name',
            'is_live_now', 'is_upcoming', 'created_at',
        ]
        read_only_fields = ['slug', 'host', 'created_at']

    def get_join_url(self, obj):
        request = self.context.get('request')
        url = obj.get_join_url()
        return request.build_absolute_uri(url) if request else url


class NotificationSerializer(serializers.ModelSerializer):
    actor = UserMiniSerializer(read_only=True)

    class Meta:
        model = models.Notification
        fields = ['id', 'actor', 'verb', 'title', 'body', 'level', 'url',
                  'is_read', 'emailed', 'created_at', 'message', 'meeting', 'announcement']
        read_only_fields = fields


class AnnouncementSerializer(serializers.ModelSerializer):
    sender = UserMiniSerializer(read_only=True)

    class Meta:
        model = models.Announcement
        # 'courses' was removed from Announcement — keep only real fields, or the
        # serializer 500s the moment there is an announcement to render.
        fields = ['id', 'sender', 'title', 'body', 'level', 'url', 'audience',
                  'user_type', 'modules', 'users', 'send_email',
                  'sent_at', 'recipient_count', 'created_at']
        read_only_fields = ['sender', 'sent_at', 'recipient_count', 'created_at']
