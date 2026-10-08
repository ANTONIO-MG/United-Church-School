"""Context processor exposing communication counters to every template:
unread notifications (navbar bell badge), unread chat messages, the number of
announcements — and ``alerts``, the merged newest-first list of notifications
AND unread messages that the navbar bell drops down. Guarded so a missing table
/ DB error degrades to ``{}``.

Cached per request — these are navbar badges, they cannot change while a single
response is being rendered, and this processor runs for every template in it.
"""

from core.request_cache import cached_per_request

from . import models


def _build(user):
    """The counters, in a handful of queries flat."""
    unread_notifications = models.Notification.objects.filter(
        recipient=user, is_read=False).count()

    # One aggregate over every conversation, not one COUNT per membership.
    # The loop this replaced also called `unread_count` — a @property — as if it
    # were a method, so it raised TypeError into a bare `except: pass` and the
    # badge silently read zero for everyone.
    unread_messages = models.ChatMembership.unread_total_for(user)

    # The bell only carries messages actually aimed at this user (direct chats +
    # @-mentions), so its badge counts those, not every unread message — that is
    # what the separate Messages badge (`unread_messages`) is for.
    unread_bell_messages = _bell_message_qs(user).count()

    announcements = 0
    if hasattr(models, 'Announcement'):
        announcements = models.Announcement.objects.count()

    return {
        'unread_notifications': unread_notifications,
        'unread_messages': unread_messages,
        'announcements': announcements,
        'alerts': _inbox(user),
        'alerts_total': unread_notifications + unread_bell_messages,
    }


def _display_name(user, fallback='Someone'):
    """A person's name for the bell — profile name first, never their address."""
    if user is None:
        return fallback
    profile = getattr(user, 'profile', None)
    parts = [getattr(profile, 'first_name', '') or '', getattr(profile, 'last_name', '') or '']
    name = ' '.join(p for p in parts if p).strip()
    if not name:
        name = (user.get_full_name() or '').strip()
    return name if (name and '@' not in name) else fallback


def _bell_message_qs(user):
    """Unread messages that belong in the navbar bell.

    Only messages actually aimed at this user: **every** message in a 1:1
    ``direct`` chat, and in group chats **only** the ones that ``@``-mention them
    (via :class:`MessageMention`). A busy module group therefore no longer buries
    the notifications under traffic that was never addressed to the reader.

    "Unread" is judged against the conversation's ``last_read_at`` watermark, the
    reader's own messages are excluded, and ``distinct()`` collapses the row
    fan-out the mention join would otherwise cause.
    """
    from django.db.models import F, Q

    unseen = Q(group__memberships__last_read_at__isnull=True) | Q(
        created_at__gt=F('group__memberships__last_read_at'))
    aimed_at_me = Q(group__kind=models.ChatGroup.KIND_DIRECT) | Q(mention_links__user=user)
    return (models.Message.objects
            .filter(group__memberships__user=user, is_deleted=False)
            .exclude(sender=user)
            .filter(unseen)
            .filter(aimed_at_me)
            .distinct())


def _inbox(user, limit=8):
    """The navbar bell's list: notifications **and** messages aimed at you, merged.

    One bell, one list, newest first — but each row keeps its own identity, so a
    message shows a message icon and a notification shows a bell. Two icons in
    one menu beats two menus the reader has to check separately.

    Notifications link to their own detail page (the full message), and messages
    are limited to direct chats + ``@``-mentions — see :func:`_bell_message_qs`.
    """
    from django.urls import reverse

    rows = []

    # Only unread notifications: opening one (notification-detail marks it read)
    # drops it off the bell, so the bell shows only what still needs attention.
    for note in (models.Notification.objects
                 .filter(recipient=user, is_read=False)
                 .order_by('-created_at')[:limit]):
        rows.append({
            'kind': 'notification',
            'icon': 'bi-bell-fill',
            'title': note.title or note.verb or 'Notification',
            'body': (note.summary or note.body or '')[:120],
            # Always open the notification in full (marks it read) rather than a
            # deep-link that may resolve to the page you're already on.
            'url': reverse('communication:notification-detail', args=[note.pk]),
            'when': note.created_at,
            'unread': True,
        })

    for message in (_bell_message_qs(user)
                    .select_related('group', 'sender')
                    .order_by('-created_at')[:limit]):
        # Never fall back to get_username(): on this deployment that IS the
        # e-mail address, so the bell would list people by their address.
        who = _display_name(message.sender)
        rows.append({
            'kind': 'message',
            'icon': 'bi-chat-left-text-fill',
            'title': who,
            'body': (message.body or 'Sent an attachment')[:120],
            'url': reverse('communication:chat-room', args=[message.group_id]),
            'when': message.created_at,
            'unread': True,
        })

    rows.sort(key=lambda r: r['when'], reverse=True)
    return rows[:limit]


def comm_stats(request):
    user = getattr(request, 'user', None)
    if user is None or not user.is_authenticated:
        return {'comm_stats': {}}

    def build():
        try:
            return _build(user)
        except Exception:
            return {}

    return {'comm_stats': cached_per_request(request, 'comm_stats', build)}
