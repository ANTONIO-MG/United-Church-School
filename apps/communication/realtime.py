"""Server-side WebSocket push helpers.

Called from ordinary synchronous code (DRF views, the ``notify`` service) to
reach connected sockets through the channel layer. Every function is best-effort
and swallows its own errors: real-time delivery is an enhancement, never a
reason for a message-send or notification to fail. When Channels/the channel
layer is not configured, these are silent no-ops and the app falls back to the
existing REST polling.

See apps/communication/consumers.py for the receiving end.
"""

import logging

logger = logging.getLogger('apps.communication')


def _layer():
    try:
        from channels.layers import get_channel_layer
        return get_channel_layer()
    except Exception:
        return None


def _send(group, message):
    layer = _layer()
    if layer is None:
        return
    try:
        from asgiref.sync import async_to_sync
        async_to_sync(layer.group_send)(group, message)
    except Exception:
        logger.debug('realtime push to %s failed', group, exc_info=True)


def push_alert(user_id, *, kind, title='', body='', url=''):
    """Send one alert event to a user's :class:`AlertConsumer` socket(s).

    ``kind`` is ``'notification'`` or ``'message'`` — the client plays the
    matching sound and bumps the bell badge.
    """
    if not user_id:
        return
    _send(f'alerts_{user_id}', {
        'type': 'alert',
        'payload': {'kind': kind, 'title': title, 'body': body, 'url': url},
    })


def push_chat(group_id, payload):
    """Poke a conversation's :class:`ChatConsumer` so open messengers refresh."""
    if not group_id:
        return
    _send(f'chat_{group_id}', {'type': 'chat_message', 'payload': payload})


def broadcast_new_message(message):
    """Fan a freshly-created chat message out to the conversation and to each
    other member's personal alert socket. Call right after the message is saved.
    """
    try:
        group_id = message.group_id
        sender_id = message.sender_id
        sender_name = ''
        sender = getattr(message, 'sender', None)
        if sender is not None:
            sender_name = (sender.get_full_name() or '').strip() or sender.get_username()
        # Poke the open conversation.
        push_chat(group_id, {
            'event': 'message',
            'group_id': group_id,
            'message_id': message.id,
            'sender_id': sender_id,
        })
        # Ping every other member's bell (sound + badge) wherever they are.
        from .models import ChatMembership
        member_ids = (ChatMembership.objects
                      .filter(group_id=group_id)
                      .exclude(user_id=sender_id)
                      .values_list('user_id', flat=True))
        preview = (message.body or 'Sent an attachment')[:80]
        for uid in member_ids:
            push_alert(uid, kind='message', title=sender_name or 'New message',
                       body=preview, url=f'/communication/chat/{group_id}/')
    except Exception:
        logger.debug('broadcast_new_message failed', exc_info=True)
