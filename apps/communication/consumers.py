"""WebSocket consumers for real-time communication.

Two consumers, both authenticated via the session (AuthMiddlewareStack in
config/asgi.py puts the logged-in user on ``self.scope['user']``):

* :class:`AlertConsumer` — a per-user channel. The server pushes small events
  ("a notification arrived", "a message arrived") that the client turns into a
  sound + a badge bump, with no polling.
* :class:`ChatConsumer` — a per-conversation channel. When someone posts to a
  chat the server pushes a "new message" poke so open messengers refresh at once.

Server-side senders live in :mod:`apps.communication.realtime`.
"""

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer


def _alerts_group(user_id):
    return f'alerts_{user_id}'


def _chat_group(group_id):
    return f'chat_{group_id}'


def _lesson_group(lesson_id):
    return f'lesson_{lesson_id}'


class AlertConsumer(AsyncJsonWebsocketConsumer):
    """Per-user socket carrying notification / message events for the navbar."""

    async def connect(self):
        user = self.scope.get('user')
        if user is None or not user.is_authenticated:
            await self.close()
            return
        self.group_name = _alerts_group(user.id)
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        if getattr(self, 'group_name', None):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    # channel_layer.group_send(..., {'type': 'alert', 'payload': {...}})
    async def alert(self, event):
        await self.send_json(event.get('payload', {}))


class ChatConsumer(AsyncJsonWebsocketConsumer):
    """Per-conversation socket. Membership is checked once, on connect."""

    async def connect(self):
        user = self.scope.get('user')
        self.group_id = self.scope['url_route']['kwargs']['group_id']
        if user is None or not user.is_authenticated or not await self._is_member(user.id, self.group_id):
            await self.close()
            return
        self.group_name = _chat_group(self.group_id)
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        if getattr(self, 'group_name', None):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    # channel_layer.group_send(..., {'type': 'chat_message', 'payload': {...}})
    async def chat_message(self, event):
        await self.send_json(event.get('payload', {}))

    @database_sync_to_async
    def _is_member(self, user_id, group_id):
        from .models import ChatMembership
        return ChatMembership.objects.filter(user_id=user_id, group_id=group_id).exists()


class LessonPresenceConsumer(AsyncJsonWebsocketConsumer):
    """"Who is in this lesson right now."

    Presence is peer-announced over the channel layer, so it is correct with the
    Redis layer across workers and needs no shared server-side roster: on connect
    a client broadcasts a ``join`` with its identity; every already-present client
    answers with a ``sync`` of its own identity (so the newcomer learns who is
    here); on disconnect a ``leave`` is broadcast. The browser keeps the roster.
    Access is gated by the same ``_can_view_lesson`` rule the lesson page uses.
    """

    async def connect(self):
        user = self.scope.get('user')
        self.lesson_id = self.scope['url_route']['kwargs']['lesson_id']
        self.me = None
        if user is not None and user.is_authenticated:
            self.me = await self._who(user.id, self.lesson_id)
        if not self.me:
            await self.close()
            return
        self.me['hand'] = False   # hand-raise state, carried in join/sync payloads
        self.group_name = _lesson_group(self.lesson_id)
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        # Tell this client its own identity so it can toggle its own hand.
        await self.send_json({'action': 'self', 'user': self.me})
        await self.channel_layer.group_send(
            self.group_name, {'type': 'presence_join', 'user': self.me, 'origin': self.channel_name})

    async def disconnect(self, code):
        if getattr(self, 'group_name', None):
            await self.channel_layer.group_send(
                self.group_name, {'type': 'presence_leave', 'user': self.me})
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        if not getattr(self, 'group_name', None):
            return
        if content.get('action') == 'hand':
            # Raise / lower this user's hand and fan the state out to everyone.
            self.me['hand'] = bool(content.get('up'))
            await self.channel_layer.group_send(self.group_name, {
                'type': 'presence_hand', 'user_id': self.me['id'], 'up': self.me['hand']})

    async def presence_join(self, event):
        await self.send_json({'action': 'join', 'user': event['user']})
        # Answer someone else's arrival with my own identity so they see me.
        # (A 'sync' never triggers another 'sync', so this can't loop.)
        if event.get('origin') != self.channel_name:
            await self.channel_layer.group_send(
                self.group_name, {'type': 'presence_sync', 'user': self.me})

    async def presence_sync(self, event):
        await self.send_json({'action': 'sync', 'user': event['user']})

    async def presence_leave(self, event):
        await self.send_json({'action': 'leave', 'user': event['user']})

    async def presence_hand(self, event):
        await self.send_json({'action': 'hand', 'user_id': event['user_id'], 'up': event['up']})

    @database_sync_to_async
    def _who(self, user_id, lesson_id):
        """Return {id,name,avatar} if the user may view the lesson, else None."""
        from django.contrib.auth import get_user_model

        from core.utils import avatar_url, display_name
        from apps.learning.models import Lesson
        from apps.learning.views import _can_view_lesson
        User = get_user_model()
        try:
            user = User.objects.select_related('profile').get(pk=user_id)
            lesson = Lesson.objects.select_related('module').get(pk=lesson_id)
        except (User.DoesNotExist, Lesson.DoesNotExist):
            return None
        try:
            if not _can_view_lesson(user, lesson):
                return None
        except Exception:
            return None
        return {'id': user_id, 'name': display_name(user) or 'Someone', 'avatar': avatar_url(user) or ''}
