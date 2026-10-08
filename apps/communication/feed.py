"""Unified activity feed aggregator.

``build_feed(user)`` merges every relevant source — user-authored :class:`Feed`
posts, announcements, the user's notifications, recent messages from their direct
and group conversations, their task assignments, assessments/quizzes open to
them, and calendar events / reminders — into a single list of lightweight dicts
sorted by timestamp (newest first).

Each item is a dict with a common shape so a single template loop can render them
all, branching on ``item.type`` for the icon / colour / layout, and showing any
attached media (image / video / file) inline. Three keys drive that branching:

``type``        what the item is, e.g. ``quiz`` or ``message-direct``
``open_label``  what the top-right button should say ("Open quiz", "Open in chats")
``can_react``   whether Like / Comment apply — only social posts can be reacted
                to; a task, reminder, assessment or quiz is something you open,
                not something you like.

``module_id`` / ``module_name`` let the page's module filter narrow the feed
to one module; items with no module only appear under "General".
"""

import logging

from django.urls import reverse

from core.errors import report
from core.utils import avatar_url, initials

from . import models

logger = logging.getLogger('apps')


# Presentation per item type: (icon, colour, what the "open" button says,
# whether Like/Comment make sense).
TYPE_STYLE = {
    'post':          ('chat-square-text-fill', '#0d6efd', 'Open post',         True),
    'message-direct': ('chat-dots-fill',       '#6610f2', 'Open in chats',     False),
    'message-group': ('people-fill',           '#6610f2', 'Open in chats',     False),
    'announcement':  ('megaphone-fill',        '#198754', 'Open announcement', False),
    'notification':  ('bell-fill',             '#0dcaf0', 'Open notification', False),
    'task':          ('check2-square',         '#fd7e14', 'Open task',         False),
    'reminder':      ('alarm-fill',            '#6f42c1', 'Open reminder',     False),
    'event':         ('calendar-event-fill',   '#3a87ad', 'Open event',        False),
    'quiz':          ('patch-question-fill',   '#d63384', 'Open quiz',         False),
    'assessment':    ('ui-checks',             '#20c997', 'Open assessment',   False),
    'lesson':        ('journal-richtext',      '#0aa2c0', 'Open lesson',       False),
}
DEFAULT_STYLE = ('dot', '#6c757d', 'Open', False)


def _basename(field):
    """The stored file's own name, for a document card to label itself with."""
    import os
    return os.path.basename(getattr(field, 'name', '') or '') or 'Document'


def _safe_url(field):
    """A file's URL, or '' if the file is missing (``.url`` raises ValueError)."""
    try:
        return field.url
    except (ValueError, AttributeError):
        return ''


def _post_media(post):
    """Every attachment on a feed post as ``{url, kind, name}`` dicts, newest
    posts store several via :class:`FeedAttachment`; older posts fall back to the
    single legacy ``Feed.media`` field. Files whose storage has gone missing are
    dropped rather than crashing the whole feed.
    """
    out = []
    for att in post.attachments.all():
        url = _safe_url(att.file)
        if url:
            out.append({'url': url, 'kind': att.kind or 'file',
                        'name': att.original_name or _basename(att.file)})
    if not out and getattr(post, 'media', None):
        url = _safe_url(post.media)
        if url:
            out.append({'url': url, 'kind': post.media_kind or 'file', 'name': _basename(post.media)})
    return out


def _media_from_attachment(att):
    if att and getattr(att, 'file', None):
        try:
            return {'url': att.file.url, 'kind': att.kind, 'name': _basename(att.file)}
        except ValueError:
            return None
    return None


def user_modules(user):
    """Module offerings the user is part of — enrolled in, or teaching.

    These become the feed's filter buttons alongside "General", and the
    composer's "which module is this about?" picker.
    """
    from apps.learning.models import ProgrammeModule
    if not getattr(user, 'is_authenticated', False):
        return ProgrammeModule.objects.none()
    person = getattr(user, 'profile', None)
    if person is None:
        return ProgrammeModule.objects.none()
    from django.db.models import Q
    # ``students`` is a property, not a relation — the join is through the
    # enrolment row, which is where a candidate's link to a module actually is.
    return (ProgrammeModule.objects
            .filter(Q(enrolments__person=person) | Q(educators=person), is_active=True)
            .select_related('programme').distinct().order_by('order', 'name'))


def _actor_name(actor):
    """A person's display name for the feed — their profile's full name first
    (that is where names live on this platform; the User row is usually blank),
    then the User's name, then the e-mail local-part, but never the raw address.
    """
    if actor is None:
        return 'System'
    profile = getattr(actor, 'profile', None)
    if profile is not None:
        name = f"{getattr(profile, 'first_name', '') or ''} {getattr(profile, 'last_name', '') or ''}".strip()
        if name:
            return name
    full = (actor.get_full_name() or '').strip()
    if full:
        return full
    email = getattr(actor, 'email', '') or ''
    return email.split('@')[0] or f'Member {getattr(actor, "pk", "")}'.strip()


def _actor_url(actor):
    """Link to the poster's profile page, or '' for a system/actor-less item."""
    profile = getattr(actor, 'profile', None) if actor is not None else None
    if profile is not None and getattr(profile, 'pk', None):
        from django.urls import reverse
        return reverse('accounts:profile', args=[profile.pk])
    return ''


def build_feed(user, limit=40, module_id=None):
    """Build the feed. ``module_id`` narrows it to a single module."""
    items = []

    def add(*, type, when, actor=None, title='', body='', media=None, media_list=None,
            url='', location='', label='', extra=None, module=None):
        if not when:
            return
        icon, color, open_label, can_react = TYPE_STYLE.get(type, DEFAULT_STYLE)
        items.append({
            'type': type, 'when': when, 'actor': actor, 'title': title, 'body': body,
            'media': media, 'media_list': media_list or [],
            'icon': icon, 'color': color, 'url': url, 'location': location,
            'label': label, 'extra': extra or {},
            'open_label': open_label, 'can_react': can_react,
            'module_id': getattr(module, 'pk', None),
            'module_name': getattr(module, 'name', ''),
            # The author's photo, so the card never has to fall back on a
            # coloured initial unless they genuinely have no picture.
            'avatar': avatar_url(actor),
            'initials': initials(actor) if actor else '',
            # Full name (never the e-mail) + a link to their profile.
            'actor_name': _actor_name(actor),
            'actor_url': _actor_url(actor),
        })

    authed = getattr(user, 'is_authenticated', False)

    # --- User-authored feed posts ---
    posts = (models.Feed.visible_to(user)
             .select_related('author__profile')
             .prefetch_related('likes', 'comments__author__profile', 'attachments'))
    if module_id:
        posts = posts.filter(module_id=module_id)
    for f in posts[:limit]:
        media_list = _post_media(f)
        # A plain post carries no "Open" button — it is already fully shown in
        # the card; only richer items (notification, document, session, event…)
        # link out. So url stays empty for posts.
        add(type='post', when=f.created_at, actor=f.author, body=f.body,
            media=(media_list[0] if media_list else None), media_list=media_list,
            url='', label='shared a post', module=f.module,
            extra={'pk': f.pk, 'visibility': f.get_visibility_display(), 'likes': f.like_count,
                   'liked': authed and f.likes.filter(pk=user.pk).exists(),
                   'comments': list(f.comments.all())})

    # --- Announcements (broadcasts) ---
    try:
        announcements = (models.Announcement.objects.filter(sent_at__isnull=False)
                         .select_related('sender__profile').order_by('-sent_at'))
        if module_id:
            announcements = announcements.filter(modules__id=module_id)
        for a in announcements[:limit]:
            add(type='announcement', when=a.sent_at, actor=a.sender, title=a.title, body=a.body,
                url='/communication/announcements/', label='posted an announcement')
    except Exception as exc:
        report('FEED-9001', exc, context={'source': 'announcements'})

    if not authed:
        items.sort(key=lambda i: i['when'], reverse=True)
        return items[:limit]

    # --- Notifications (the user's own) ---
    # Not module-scoped, so they only belong in the unfiltered "General" view.
    if not module_id:
        try:
            for n in (models.Notification.objects.filter(recipient=user)
                      .select_related('actor__profile').order_by('-created_at')[:limit]):
                add(type='notification', when=n.created_at, actor=n.actor,
                    title=n.title or n.verb, body=n.body,
                    url=reverse('communication:notification-detail', args=[n.pk]), label='Notification',
                    extra={'is_read': n.is_read})
        except Exception as exc:
            report('FEED-9001', exc, context={'source': 'notifications'})

    # --- Messages from the user's conversations (direct + group) ---
    try:
        groups = models.ChatGroup.objects.filter(memberships__user=user)
        if module_id:
            groups = groups.filter(module_id=module_id)
        gids = list(groups.values_list('id', flat=True))
        if gids:
            msgs = (models.Message.objects.filter(group_id__in=gids, is_deleted=False)
                    .exclude(sender=user).select_related('sender__profile', 'group', 'group__module')
                    .prefetch_related('attachments').order_by('-created_at')[:limit])
            for m in msgs:
                is_direct = m.group.kind == models.ChatGroup.KIND_DIRECT
                add(type='message-direct' if is_direct else 'message-group',
                    when=m.created_at, actor=m.sender, title=m.group.display_name, body=m.body,
                    media=_media_from_attachment(m.attachments.first()),
                    url=f'/communication/chat/{m.group_id}/',
                    module=m.group.module,
                    label='sent a message' if is_direct else 'messaged a group')
    except Exception as exc:
        report('FEED-9001', exc, context={'source': 'messages'})

    # --- Task assignments ---
    try:
        from apps.tasks.models import TaskAssignment
        assignments = (TaskAssignment.objects.filter(user=user)
                       .select_related('task', 'task__module').order_by('-created_at'))
        if module_id:
            assignments = assignments.filter(task__module_id=module_id)
        for ta in assignments[:limit]:
            when = ta.task.due_date or getattr(ta, 'created_at', None)
            add(type='task', when=when, title=ta.task.title,
                body=(ta.task.description or '') if hasattr(ta.task, 'description') else '',
                label='Task', module=getattr(ta.task, 'module', None),
                url=ta.task.get_absolute_url(), extra={'status': ta.get_status_display()})
    except Exception as exc:
        report('FEED-9001', exc, context={'source': 'tasks'})

    # --- Assessments & quizzes open to this learner ---
    # A quiz reads differently from a test/exam/assignment, so they get their own
    # type (and icon) even though they are the same model.
    try:
        from apps.assessments.models import Assessment
        person = getattr(user, 'profile', None)
        module_ids = ([module_id] if module_id
                       else list(person.selected_modules.values_list('id', flat=True)) if person else [])
        if module_ids:
            for a in (Assessment.objects.filter(status='open', module_id__in=module_ids)
                      .select_related('module').order_by('-created_at')[:limit]):
                add(type='quiz' if a.kind == Assessment.KIND_QUIZ else 'assessment',
                    when=a.created_at, title=a.title, body=a.description or '',
                    label=a.get_kind_display(), module=a.module,
                    url=reverse('assessments:take', args=[a.pk]),
                    extra={'status': f'{a.total_marks} marks · pass {a.pass_mark_pct}%'})
    except Exception as exc:
        report('FEED-9001', exc, context={'source': 'assessments'})

    # --- Calendar events + reminders ---
    # Events carry no module, so they belong to the "General" view only.
    if not module_id:
        try:
            from django.db.models import Q
            from apps.myhub.models import Event
            for e in Event.objects.filter(Q(owner__isnull=True) | Q(owner=user))[:limit]:
                is_rem = e.category == Event.CATEGORY_REMINDER
                add(type='reminder' if is_rem else 'event', when=e.start, title=e.title,
                    body=e.description or '', location=e.location or '',
                    url='/myhub/events/', label='Reminder' if is_rem else 'Event')
        except Exception:
            pass

    items.sort(key=lambda i: i['when'], reverse=True)
    return items[:limit]
