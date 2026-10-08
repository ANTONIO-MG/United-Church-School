"""HTML pages for the communication app.

These are thin shells around the REST API (:mod:`apps.communication.api`):

* ``chat_home`` / ``chat_room`` — chat UI (vanilla-JS, polls the API)
* ``meetings_list`` / ``meeting_create`` — schedule meetings; ``meeting_room``
  embeds a Jitsi Meet call
* ``notifications_list`` — the notification inbox
* ``announcement_compose`` / ``announcement_list`` — staff/admin bulk
  notifications (also delivered by e-mail)
"""

import logging

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from core.branding import t
from core.errors import note, report
from core.roles import role_flags

from . import forms, models, services

logger = logging.getLogger('apps')
staff_required = user_passes_test(lambda u: u.is_active and u.is_staff)


def _can_manage_classes(request):
    """Educators, staff and admins may open sessions and mark attendance."""
    flags = role_flags(request)
    return flags['is_admin_staff'] or flags['is_educator']


def _attendance_subject(request):
    """Whose attendance this request is about, and whether it is someone else's.

    The register is read by educators, staff and parents — never by the student
    it is about, who has no Attendance link in the nav. A parent is looking at
    their child, so the rows have to be the child's; everyone else is looking at
    their own. Returns ``(user_or_None, is_proxy)``; ``is_proxy`` is what stops a
    parent checking in on their child's behalf.
    """
    if role_flags(request).get('is_parent'):
        from core.scoping import viewing_child
        try:
            return viewing_child(request), True
        except Exception:            # never 500 the register over a missing link
            return None, True
    return request.user, False


# ---------------------------------------------------------------------------
# Chat
# ---------------------------------------------------------------------------
# Lives in services now that the module feed embeds a thread too — a chat header
# has to be decorated the same way wherever it is drawn.
_decorate_group = services.decorate_group


def _chat_context(request, active_group=None):
    """Conversations the user belongs to (General ensured) + people to DM."""
    from core.scoping import is_parent

    parent = is_parent(request.user)
    groups = models.ChatGroup.objects.filter(memberships__user=request.user, is_active=True)
    if parent:
        # A parent is not part of the school's group conversations — the platform
        # -wide "General" room and any class group would put them in a chat with
        # other families' children. They get their own direct threads only.
        groups = groups.filter(kind=models.ChatGroup.KIND_DIRECT)
    else:
        services.ensure_general_group(request.user)
    groups = groups.prefetch_related('memberships__user__profile').distinct()
    groups = [_decorate_group(g, request.user) for g in groups]
    if active_group is not None:
        # Reuse the decorated instance from the list so the header and the row
        # agree, rather than decorating a second copy of the same group.
        active_group = next((g for g in groups if g.pk == active_group.pk),
                            _decorate_group(active_group, request.user))
    # Who this person may start a conversation with. Scoped to their own spine
    # by ``directory_users``: people who share their institution, programme or
    # intake, plus every admin, staff member and educator — who must stay
    # reachable by everybody. A **parent** gets the narrower
    # ``parent_contacts`` rule (handled inside ``directory_users``), so the
    # account never becomes a directory of other families.
    from core.scoping import directory_users
    people = directory_users(request.user).select_related('profile')
    people = people.order_by('first_name', 'last_name', 'email')[:100]
    # For a 1:1 direct chat, work out whether a student↔student connection is
    # needed (and its state) so the template can gate the compose box.
    dm_gate = None
    if active_group is not None and active_group.kind == models.ChatGroup.KIND_DIRECT:
        other = services.other_member(active_group, request.user)
        if other is not None:
            dm_gate = services.direct_gate_state(request.user, other)
    return {'groups': groups, 'active_group': active_group, 'people': people,
            'dm_gate': dm_gate}


@login_required
def chat_home(request):
    ctx = _chat_context(request)
    ctx['page_title'] = 'Messages'
    return render(request, 'communication/chat.html', ctx)


@login_required
def chat_room(request, group_id):
    from core.scoping import is_parent

    group = get_object_or_404(models.ChatGroup, pk=group_id)
    if not (request.user.is_staff or group.memberships.filter(user=request.user).exists()):
        note('CHAT-2001', request, group=group_id)
        messages.error(request, t('messages.form_errors', 'You are not a member of that chat.'))
        return redirect('communication:chat-home')
    # A parent may be a legacy member of a group room; direct threads only.
    if is_parent(request.user) and group.kind != models.ChatGroup.KIND_DIRECT:
        messages.info(request, 'Parent accounts use direct messages rather than group chats.')
        return redirect('communication:chat-home')
    ctx = _chat_context(request, active_group=group)
    ctx['page_title'] = f"Messages · {getattr(ctx['active_group'], 'chat_title', group.display_name)}"
    return render(request, 'communication/chat.html', ctx)


@login_required
def chat_direct(request, user_id):
    """Open (or start) a 1:1 direct chat with another user.

    The lookup runs against :func:`core.scoping.directory_users` — your
    institution, programme or intake, plus every admin, staff member and
    educator (and, for a parent, the narrower
    :func:`core.scoping.parent_contacts` rule).
    """
    from core.scoping import directory_users

    # The pool is the control, not the contact list a template renders: a
    # hand-typed id for somebody at another institution gets a 404, not a chat.
    other = get_object_or_404(directory_users(request.user), pk=user_id, is_active=True)
    group = services.get_or_create_direct_chat(request.user, other)
    return redirect('communication:chat-room', group_id=group.pk)


@login_required
@require_POST
def connection_request(request, user_id):
    """Send a request to open 1:1 messaging with another student.

    Only meaningful between two students (``students_need_connection``); for any
    other pair direct messaging is already open, so we just say so and move on.
    """
    User = get_user_model()
    other = get_object_or_404(User, pk=user_id, is_active=True)
    if other.pk == request.user.pk:
        messages.error(request, 'You cannot connect with yourself.')
    elif services.are_connected(request.user, other):
        messages.info(request, f'You are already connected with {other.get_full_name() or other.get_username()}.')
    elif not services.students_need_connection(request.user, other):
        messages.info(request, 'You can message this person directly — no request needed.')
    else:
        services.request_connection(request.user, other)
        messages.success(
            request,
            f'Connection request sent to {other.get_full_name() or other.get_username()}. '
            f'You can chat once they accept.')
    return redirect(request.POST.get('next') or reverse('communication:chat-direct', args=[other.pk]))


@login_required
@require_POST
def connection_respond(request, pk):
    """Accept or decline a pending connection request addressed to you."""
    conn = get_object_or_404(models.ConnectionRequest, pk=pk, to_user=request.user)
    accept = request.POST.get('action') == 'accept'
    if services.respond_connection(conn, accept=accept, by_user=request.user):
        who = conn.from_user.get_full_name() or conn.from_user.get_username()
        if accept:
            messages.success(request, f'You are now connected with {who}. Say hello!')
        else:
            messages.info(request, f"Declined {who}'s connection request.")
    else:
        messages.error(request, 'That request could not be updated.')
    if accept:
        return redirect('communication:chat-direct', user_id=conn.from_user_id)
    return redirect(request.POST.get('next') or reverse('communication:chat-home'))


# ---------------------------------------------------------------------------
# Meetings (video / audio calls & class sessions)
# ---------------------------------------------------------------------------
@login_required
def meetings_list(request):
    return render(request, 'communication/meetings.html', {
        'page_title': 'Meetings',
        'meetings': models.MeetingRoom.objects.select_related('host', 'group').filter(is_active=True),
    })


@login_required
def meeting_create(request):
    if request.method == 'POST':
        form = forms.MeetingRoomForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            group = cd.get('group')
            # Auto-assign the session to the module behind the chosen group.
            module = getattr(group, 'module', None) if group else None

            # Create through the Teams service (falls back to the in-app room when
            # Teams isn't configured). The service saves the MeetingRoom.
            from apps.msteams import services as teams_services
            meeting = teams_services.create_class_meeting(
                host=request.user,
                title=cd['title'],
                start=cd.get('scheduled_start'),
                end=cd.get('scheduled_end'),
                module=module,
                group=group,
                description=cd.get('description', ''),
            )
            # Apply the remaining form fields the service doesn't take.
            meeting.is_recurring = cd.get('is_recurring', False)
            meeting.recurrence = cd.get('recurrence', '')
            meeting.save(update_fields=['is_recurring', 'recurrence'])

            try:
                from .emails import send_session_scheduled
                send_session_scheduled(
                    request.user, session_title=meeting.title,
                    session_when=meeting.scheduled_start or '',
                    join_url=request.build_absolute_uri(meeting.get_join_url()))
            except Exception:
                pass
            engine = 'Teams' if meeting.is_teams else 'meeting'
            messages.success(request, t('messages.created', '{name} created.', name=engine))
            return redirect('communication:meeting-room', slug=meeting.slug)
        messages.error(request, t('messages.form_errors', 'Please correct the errors highlighted below.'))
    else:
        form = forms.MeetingRoomForm()
    return render(request, 'communication/meeting-form.html', {'page_title': 'New Meeting', 'form': form})


@login_required
def chat_call(request, group_id):
    """Start a voice/video call for a chat conversation and jump into it.

    The engine follows the initiator: staff / educators / admins host on
    Microsoft Teams (their MS credentials); students — 1:1 and small student
    groups — use Jitsi. When the call ends the room returns to this chat.
    """
    group = get_object_or_404(models.ChatGroup, pk=group_id)
    if not (request.user.is_staff or group.memberships.filter(user=request.user).exists()):
        note('CHAT-2001', request, group=group_id, action='call')
        messages.error(request, 'You are not a member of that conversation.')
        return redirect('communication:chat-home')

    kind = 'audio' if request.GET.get('kind') == 'audio' else 'video'
    # Name the call after the people in it — "Ada Lovelace & Alan Turing" for a
    # 1:1, the group's own name otherwise — rather than the internal slug-ish
    # display name, because this title is what everyone sees in the call.
    from core.utils import display_name as _name
    peers = [m.user for m in group.memberships.select_related('user__profile') if m.user_id != request.user.pk and m.user]
    if group.kind == models.ChatGroup.KIND_DIRECT and peers:
        title = f'{_name(request.user)} & {_name(peers[0])}'
    else:
        title = group.display_name

    from apps.msteams import services as teams_services
    meeting = teams_services.create_class_meeting(
        host=request.user,
        title=title,
        module=getattr(group, 'module', None),
        group=group,
    )
    chat_url = reverse('communication:chat-room', args=[group.pk])
    return redirect(f'{meeting.get_join_url()}?return={chat_url}&kind={kind}')


@login_required
def meeting_room(request, slug):
    """Launch page for a live session (this URL *is* the shareable link).

    For the embedded Jitsi fallback, opening it auto-marks attendance. For Teams
    the authoritative attendance comes from the Graph attendance report after the
    class (students join anonymously), so we don't mark on page-open.
    """
    meeting = get_object_or_404(models.MeetingRoom, slug=slug)
    if not meeting.is_teams:
        services.record_meeting_join(meeting, request.user)

    # Where to go when the call ends (a chat conversation, if we came from one).
    from django.utils.http import url_has_allowed_host_and_scheme
    return_url = request.GET.get('return', '')
    if not (return_url and url_has_allowed_host_and_scheme(
            return_url, allowed_hosts={request.get_host()}, require_https=request.is_secure())):
        return_url = reverse('communication:chat-home')
    audio_only = request.GET.get('kind') == 'audio'

    # Surface the recap (if the after-class sync has filed one) on the page.
    recap = None
    try:
        from apps.ai_assistant.models import AiReport
        recap = (AiReport.objects.filter(linked_ref=f'meeting:{meeting.pk}')
                 .order_by('-created_at').first())
    except Exception:
        pass

    # The shareable link, plus a short human message to go with it when someone
    # hits "Share link" (copied together, so the paste explains itself).
    share_url = request.build_absolute_uri(meeting.get_join_url())
    when = meeting.scheduled_start.strftime('%a %d %b, %H:%M') if meeting.scheduled_start else 'now'
    share_message = (
        f'Join me on “{meeting.title}” ({when}) — {share_url}'
    )

    return render(request, 'communication/meeting-room.html', {
        'page_title': meeting.title, 'meeting': meeting, 'recap': recap,
        'return_url': return_url, 'audio_only': audio_only,
        'share_url': share_url, 'share_message': share_message,
        # "Open meeting in a new tab" — the call fills that tab so the original
        # one is free to carry on with other work.
        'fullscreen': request.GET.get('fullscreen') == '1',
    })


# ---------------------------------------------------------------------------
# Notifications
# ---------------------------------------------------------------------------
# Presentational themes derived from a notification's ``level`` — used only
# when the notification isn't tied to a richer related object below.
_LEVEL_THEME = {
    'info': ('Update', 'info-circle', 'info'),
    # "Success" said nothing about what the notification was — it named the
    # severity, not the thing. A plain bell reads as what it is: a notification.
    'success': ('Notification', 'bell-fill', 'success'),
    'warning': ('Reminder', 'exclamation-triangle', 'warning'),
    'error': ('Alert', 'exclamation-octagon', 'danger'),
}


def _decorate_notification(n):
    """Attach display-only ``category_label`` / ``icon`` / ``color`` and a
    ``related_url`` + ``related_label`` to a :class:`Notification`.

    The category is derived from which related object the notification points at
    (announcement / meeting / mention) falling back to its ``level``. Nothing is
    persisted — these are purely for theming the list & detail templates.
    """
    if n.announcement_id:
        n.category_label, n.icon, n.color = 'Announcement', 'megaphone', 'primary'
    elif n.meeting_id:
        n.category_label, n.icon, n.color = 'Meeting', 'camera-video', 'info'
    elif n.message_id:
        n.category_label, n.icon, n.color = 'Mention', 'at', 'success'
    else:
        n.category_label, n.icon, n.color = _LEVEL_THEME.get(n.level, _LEVEL_THEME['info'])

    # A safe display name / photo / initial for the actor (may be absent — "System").
    from core.utils import avatar_url, display_name as _name, initials as _initials
    actor = n.actor
    n.actor_name = _name(actor) if actor else 'System'
    n.actor_avatar = avatar_url(actor)
    n.actor_initial = _initials(actor) if actor else 'S'

    # Where a "view the related item" button should send the user.
    related_url, related_label = '', ''
    if n.url:
        related_url, related_label = n.url, 'Open'
    elif n.meeting_id and n.meeting:
        related_url = reverse('communication:meeting-room', args=[n.meeting.slug])
        related_label = 'Join meeting'
    elif n.message_id and n.message and n.message.group_id:
        related_url = reverse('communication:chat-room', args=[n.message.group_id])
        related_label = 'Open conversation'
    n.related_url, n.related_label = related_url, related_label
    return n


@login_required
def notifications_list(request):
    qs = (
        models.Notification.objects
        .filter(recipient=request.user)
        .select_related('actor', 'actor__profile', 'message', 'message__group', 'meeting', 'announcement')
    )

    unread_notifications = qs.filter(is_read=False)
    unread_count = unread_notifications.count()

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'mark_all_read':
            unread_notifications.update(is_read=True)
        elif action == 'toggle_favourite':
            note = qs.filter(pk=request.POST.get('pk')).first()
            if note:
                note.is_favourite = not note.is_favourite
                note.save(update_fields=['is_favourite'])
        return redirect('communication:notifications')

    notifications = [_decorate_notification(n) for n in qs[:200]]
    favourites = [_decorate_notification(n) for n in qs.filter(is_favourite=True)[:20]]

    return render(request, 'communication/notifications.html', {
        'page_title': 'Notifications',
        'notifications': notifications,
        'favourites': favourites,
        'unread': unread_count,
        'unread_notifications': unread_notifications[:10],
        'unread_notifications_count': unread_count,
        'recent_notifications': qs[:10],
    })


@login_required
def notification_detail(request, pk):
    """A single notification in full detail (blog-details-style page).

    Only the recipient may view it (404 otherwise). Opening it marks it read;
    the recipient can also toggle read/unread via a POST action.
    """
    notification = get_object_or_404(
        models.Notification.objects.select_related(
            'actor', 'message', 'message__group', 'message__sender',
            'meeting', 'announcement', 'announcement__sender',
        ),
        pk=pk, recipient=request.user,
    )

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'mark_unread':
            # Leave the page as well as flipping the flag — staying here would
            # immediately re-read it on the redirect and undo the click.
            notification.is_read = False
            notification.save(update_fields=['is_read'])
            return redirect('communication:notifications')
        if action == 'toggle_favourite':
            notification.is_favourite = not notification.is_favourite
            notification.save(update_fields=['is_favourite'])
        elif action == 'mark_read':
            notification.mark_read()
        return redirect('communication:notification-detail', pk=notification.pk)

    # Opening a notification marks it read.
    notification.mark_read()
    _decorate_notification(notification)

    return render(request, 'communication/notification-detail.html', {
        'page_title': notification.title or notification.verb or 'Notification',
        'notification': notification,
    })

# ---------------------------------------------------------------------------
# Announcements — the broadcast composer (admin / staff)
#
# Staff write a message, attach pictures / video / documents, choose who gets it
# (everyone, or any mix of institutions, programmes, cohorts, modules and
# people, narrowed by role) and send it now, schedule it or keep it as a draft.
# Educators use the same composer for *their* subjects and classes only: the
# form narrows their audience (AnnouncementForm._scope_for_educator), and they
# see, edit and send only the notifications they wrote (_own_or_404).
# ---------------------------------------------------------------------------
announce_required = user_passes_test(
    lambda u: u.is_active and (u.is_staff or getattr(
        getattr(u, 'profile', None), 'user_type', '') in ('staff', 'admin', 'educator')))


def _own_or_404(request, announcement):
    """A teacher may open only the notifications they sent themselves."""
    if role_flags(request).get('is_educator') and announcement.sender_id != request.user.pk:
        raise Http404

#: The most files one broadcast may carry.
MAX_BROADCAST_FILES = 10


def _broadcast_files(request):
    """Validated uploads from the composer, or ``(files, errors)``."""
    from django.core.exceptions import ValidationError
    from core import validators as v

    files, errors = request.FILES.getlist('attachments'), []
    for f in files:
        for validator in v.validate_broadcast:
            try:
                validator(f)
            except ValidationError as exc:
                errors.append(f'{f.name}: {" ".join(exc.messages)}')
                break
    return files, errors


@login_required
@announce_required
def announcement_list(request):
    from django.db.models import Count, Q as _Q
    from . import broadcast

    A = models.Announcement
    base = A.objects.select_related('sender').annotate(
        n_read=Count('notifications', filter=_Q(notifications__is_read=True), distinct=True),
        n_attachments=Count('attachments', distinct=True))
    if role_flags(request).get('is_educator'):
        base = base.filter(sender=request.user)          # a teacher sees what they sent
    tab = request.GET.get('tab', 'all')
    tabs = {
        'all': base,
        'sent': base.filter(status=A.STATUS_SENT),
        'scheduled': base.filter(status__in=(A.STATUS_SCHEDULED, A.STATUS_SENDING)),
        'drafts': base.filter(status__in=(A.STATUS_DRAFT, A.STATUS_FAILED, A.STATUS_CANCELLED)),
    }
    qs = tabs.get(tab, base)
    search = (request.GET.get('q') or '').strip()
    if search:
        qs = qs.filter(_Q(title__icontains=search) | _Q(body__icontains=search))

    month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    sent_month = A.objects.filter(status=A.STATUS_SENT, sent_at__gte=month_start)
    reached = sum(sent_month.values_list('recipient_count', flat=True))
    notes = models.Notification.objects.filter(announcement__in=sent_month)
    total_notes = notes.count()
    kpis = {
        'sent_month': sent_month.count(),
        'reached_month': reached,
        'read_rate': round(100 * notes.filter(is_read=True).count() / total_notes) if total_notes else None,
        'scheduled': A.objects.filter(status=A.STATUS_SCHEDULED).count(),
    }
    rows = list(qs[:200])
    for a in rows:
        a.read_pct = round(100 * a.n_read / a.recipient_count) if a.recipient_count else 0
    return render(request, 'communication/announcements.html', {
        'page_title': 'Notifications centre', 'announcements': rows, 'tab': tab, 'search': search,
        'counts': {k: v.count() for k, v in tabs.items()}, 'kpis': kpis,
        'scheduler_ok': broadcast.scheduler_is_running(),
    })


@login_required
@announce_required
def announcement_compose(request, pk=None):
    """Write a new broadcast, or edit a draft / scheduled one."""
    from . import broadcast

    A = models.Announcement
    instance = None
    if pk is not None:
        instance = get_object_or_404(A, pk=pk)
        if role_flags(request).get('is_educator') and instance.sender_id != request.user.pk:
            raise Http404                                 # a teacher edits only their own
        if not instance.is_editable:
            messages.info(request, 'That notification has already gone out — duplicate it to send again.')
            return redirect('communication:announcement-detail', pk=pk)
    elif request.GET.get('copy'):
        source = A.objects.filter(pk=request.GET.get('copy')).first()
        if source is not None and role_flags(request).get('is_educator') \
                and source.sender_id != request.user.pk:
            source = None
    else:
        source = None

    if request.method == 'POST':
        form = forms.AnnouncementForm(request.POST, instance=instance, user=request.user)
        files, file_errors = _broadcast_files(request)
        kept = instance.attachments.count() if instance else 0
        removed = [x for x in request.POST.getlist('remove_attachment') if x.isdigit()]
        if kept - len(removed) + len(files) > MAX_BROADCAST_FILES:
            file_errors.append(f'A notification can carry up to {MAX_BROADCAST_FILES} files.')
        if form.is_valid() and not file_errors:
            with transaction.atomic():
                announcement = form.save(commit=False)
                if announcement.sender_id is None:
                    announcement.sender = request.user
                when = form.cleaned_data['when']
                announcement.status = (A.STATUS_SCHEDULED if when == form.WHEN_LATER else A.STATUS_DRAFT)
                if when != form.WHEN_LATER:
                    announcement.scheduled_for = None
                announcement.save()
                form.save_m2m()
                if instance and removed:
                    for att in instance.attachments.filter(pk__in=removed):
                        att.file.delete(save=False)
                        att.delete()
                for f in files:
                    models.AnnouncementAttachment.objects.create(
                        announcement=announcement, file=f, original_name=f.name)
                for att in (source.attachments.all() if source and not instance else []):
                    if request.POST.get(f'keep_copy_{att.pk}'):
                        models.AnnouncementAttachment.objects.create(
                            announcement=announcement, file=att.file.name, original_name=att.original_name,
                            size=att.size)

            if when == form.WHEN_NOW:
                inline, count = broadcast.dispatch(announcement)
                if inline:
                    messages.success(request, f'Sent to {count} {"person" if count == 1 else "people"}.')
                else:
                    messages.success(request, f'Sending to about {count} people in the background — '
                                              'the numbers on this page fill in as it goes.')
            elif when == form.WHEN_LATER:
                messages.success(request, 'Scheduled for '
                                 + timezone.localtime(announcement.scheduled_for).strftime('%a %d %b, %H:%M') + '.')
            else:
                messages.success(request, 'Saved as a draft.')
            return redirect('communication:announcement-detail', pk=announcement.pk)
        for err in file_errors:
            messages.error(request, err)
        if file_errors:
            note('NOTF-1002', request, problems=file_errors[:5])
        if not form.is_valid():
            messages.error(request, t('messages.form_errors', 'Please correct the errors highlighted below.'))
    else:
        initial = {}
        if source is not None:
            initial = {f: getattr(source, f) for f in ('title', 'body', 'level', 'url', 'url_label', 'media_url',
                                                       'audience', 'roles', 'include_parents', 'is_important',
                                                       'send_email')}
            for f in ('institutions', 'programmes', 'cohorts', 'modules', 'users'):
                initial[f] = list(getattr(source, f).values_list('pk', flat=True))
            if request.GET.get('unread'):
                # "Remind unread": the same message, to the people who haven't opened it.
                initial.update(audience=A.AUDIENCE_TARGETED, roles=[], include_parents=False,
                               institutions=[], programmes=[], cohorts=[], modules=[],
                               title=f'Reminder: {source.title}'[:200],
                               users=list(source.notifications.filter(is_read=False)
                                          .values_list('recipient', flat=True)))
        else:
            # Deep links: ?module=12 or ?programme=3 pre-select the audience.
            for key, field in (('institution', 'institutions'), ('programme', 'programmes'),
                               ('cohort', 'cohorts'), ('module', 'modules'), ('user', 'users')):
                ids = [x for x in request.GET.getlist(key) if x.isdigit()]
                if ids:
                    initial[field] = ids
                    initial['audience'] = A.AUDIENCE_TARGETED
        form = forms.AnnouncementForm(instance=instance, initial=initial, user=request.user)
        if source is not None and initial.get('users'):
            from django.contrib.auth import get_user_model
            form.fields['users'].widget.choices = [
                (u.pk, broadcast.person_label(u))
                for u in get_user_model().objects.filter(pk__in=initial['users']).select_related('profile')]

    return render(request, 'communication/announcement-form.html', {
        'page_title': 'Edit notification' if instance else 'Send a notification',
        'form': form, 'announcement': instance,
        'existing_attachments': instance.attachments.all() if instance else [],
        'copied_attachments': source.attachments.all() if source and not instance else [],
        'max_files': MAX_BROADCAST_FILES,
        'scheduler_ok': broadcast.scheduler_is_running(),
    })


@login_required
@announce_required
def announcement_detail(request, pk):
    """The sender's view: what went out, to whom, and who has read it."""
    from . import broadcast

    announcement = get_object_or_404(
        models.Announcement.objects.select_related('sender').prefetch_related(
            'attachments', 'institutions', 'programmes', 'cohorts', 'modules', 'users'), pk=pk)
    _own_or_404(request, announcement)
    notes = (models.Notification.objects.filter(announcement=announcement)
             .select_related('recipient', 'recipient__profile').order_by('is_read', 'recipient__first_name'))
    show = request.GET.get('show', 'all')
    if show == 'unread':
        notes = notes.filter(is_read=False)
    elif show == 'read':
        notes = notes.filter(is_read=True)
    audience = None
    if announcement.status != models.Announcement.STATUS_SENT:
        audience = broadcast.audience_summary(broadcast.recipients_for_announcement(announcement))
    return render(request, 'communication/announcement-detail.html', {
        'page_title': announcement.title, 'a': announcement,
        'stats': broadcast.read_stats(announcement), 'notes': notes[:500], 'show': show,
        'audience': audience, 'scheduler_ok': broadcast.scheduler_is_running(),
    })


@login_required
@announce_required
@require_POST
def announcement_action(request, pk):
    """Send now, cancel a scheduled send, or delete a draft."""
    from . import broadcast

    A = models.Announcement
    announcement = get_object_or_404(A, pk=pk)
    _own_or_404(request, announcement)
    action = request.POST.get('action')
    if action == 'send' and announcement.status in (A.STATUS_DRAFT, A.STATUS_SCHEDULED, A.STATUS_FAILED,
                                                    A.STATUS_CANCELLED):
        if announcement.status == A.STATUS_CANCELLED:
            A.objects.filter(pk=pk).update(status=A.STATUS_DRAFT)
            announcement.refresh_from_db()
        inline, count = broadcast.dispatch(announcement)
        messages.success(request, f'Sent to {count} people.' if inline else
                         f'Sending to about {count} people in the background.')
    elif action == 'cancel' and announcement.status == A.STATUS_SCHEDULED:
        A.objects.filter(pk=pk, status=A.STATUS_SCHEDULED).update(status=A.STATUS_CANCELLED)
        messages.success(request, 'Scheduled send cancelled. It is kept as a draft you can send later.')
    elif action == 'delete' and announcement.status in (A.STATUS_DRAFT, A.STATUS_CANCELLED, A.STATUS_FAILED) \
            and not announcement.recipient_count:
        for att in announcement.attachments.all():
            att.file.delete(save=False)
        announcement.delete()
        messages.success(request, 'Draft deleted.')
        return redirect('communication:announcements')
    else:
        note('NOTF-4001', request, announcement=pk, action=action, status=announcement.status)
        messages.error(request, 'That action is not available for this notification.')
    return redirect('communication:announcement-detail', pk=pk)


@login_required
@announce_required
@require_POST
def announcement_audience_preview(request):
    """Live "who will get this" count for the composer (JSON)."""
    from . import broadcast

    A = models.Announcement

    def ids(name):
        return [x for x in request.POST.getlist(name) if x.isdigit()]

    roles = [r for r in request.POST.getlist('roles') if r in dict(A.ROLE_CHOICES)]
    if role_flags(request).get('is_educator'):
        # A teacher's preview counts only the audience they are allowed to pick.
        scoped = forms.AnnouncementForm(user=request.user)
        allowed = {name: {str(pk) for pk in scoped.fields[name].queryset.values_list('pk', flat=True)}
                   for name in ('institutions', 'programmes', 'cohorts', 'modules')}
        raw_ids = ids
        def ids(name):  # noqa: F811 — narrowed for teachers
            if name == 'users':
                reach = set(scoped.fields['users'].queryset.values_list('pk', flat=True))
                return [x for x in raw_ids(name) if int(x) in reach]
            return [x for x in raw_ids(name) if x in allowed[name]]
        if request.POST.get('audience') == A.AUDIENCE_ALL:
            return JsonResponse(broadcast.audience_summary(broadcast.audience_users(users=[])))
    if request.POST.get('audience') == A.AUDIENCE_ALL:
        users = broadcast.audience_users(everyone=True, roles=roles)
    else:
        users = broadcast.audience_users(
            institutions=ids('institutions'), programmes=ids('programmes'), cohorts=ids('cohorts'),
            modules=ids('modules'), users=ids('users'), roles=roles,
            include_parents=bool(request.POST.get('include_parents')))
    return JsonResponse(broadcast.audience_summary(users))


@login_required
@announce_required
def announcement_people_search(request):
    """Search active accounts by name, username or e-mail for the people picker."""
    from django.contrib.auth import get_user_model

    from core.utils import avatar_url
    from . import broadcast

    q = (request.GET.get('q') or '').strip()
    if len(q) < 2:
        return JsonResponse({'results': []})
    from core.scoping import directory_users
    users = directory_users(request.user)               # teachers: their own reach only
    for word in q.split()[:3]:
        users = users.filter(Q(first_name__icontains=word) | Q(last_name__icontains=word)
                             | Q(profile__first_name__icontains=word) | Q(profile__last_name__icontains=word)
                             | Q(email__icontains=word))
    results = [{
        'id': u.pk, 'name': broadcast.person_label(u), 'avatar': avatar_url(u),
        'role': getattr(getattr(u, 'profile', None), 'get_user_type_display', lambda: '')(),
    } for u in users.select_related('profile').distinct().order_by('first_name', 'last_name')[:20]]
    return JsonResponse({'results': results})


# ---------------------------------------------------------------------------
# Discussions (Q&A-style forum)
# ---------------------------------------------------------------------------
def _save_attachments(request, *, discussion=None, reply=None):
    """Persist any uploaded media against a discussion or reply."""
    for f in request.FILES.getlist('attachments'):
        models.DiscussionAttachment.objects.create(
            discussion=discussion, reply=reply, file=f,
            original_name=getattr(f, 'name', ''),
        )


@login_required
def discussions(request):
    qs = (models.Discussion.objects
          .select_related('author', 'module')
          .prefetch_related('replies', 'likes'))

    module_id = request.GET.get('module')
    search = request.GET.get('q')
    if module_id:
        qs = qs.filter(module_id=module_id)
    if search:
        qs = qs.filter(Q(title__icontains=search) | Q(body__icontains=search) | Q(tags__icontains=search))

    return render(request, 'communication/discussions.html', {
        'page_title': 'Discussions', 'discussions': qs[:200],
        'search': search or '',
    })


@login_required
def discussion_detail(request, pk):
    discussion = get_object_or_404(
        models.Discussion.objects.select_related('author', 'module')
        .prefetch_related('attachments', 'replies__author', 'replies__attachments'),
        pk=pk,
    )
    # Count a view (cheap, best-effort).
    models.Discussion.objects.filter(pk=pk).update(view_count=discussion.view_count + 1)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'reply':
            form = forms.DiscussionReplyForm(request.POST)
            if form.is_valid():
                reply = form.save(commit=False)
                reply.discussion = discussion
                reply.author = request.user
                reply.save()
                _save_attachments(request, reply=reply)
                messages.success(request, t('messages.saved', '{name} saved successfully.', name='Reply'))
            else:
                messages.error(request, t('messages.form_errors', 'Please correct the errors highlighted below.'))
            return redirect('communication:discussion-detail', pk=discussion.pk)
        if action == 'like':
            if discussion.likes.filter(pk=request.user.pk).exists():
                discussion.likes.remove(request.user)
            else:
                discussion.likes.add(request.user)
            return redirect('communication:discussion-detail', pk=discussion.pk)

    return render(request, 'communication/discussion-detail.html', {
        'page_title': discussion.title, 'discussion': discussion,
        'reply_form': forms.DiscussionReplyForm(),
        'liked': discussion.likes.filter(pk=request.user.pk).exists(),
    })


@login_required
def discussion_create(request):
    if request.method == 'POST':
        form = forms.DiscussionForm(request.POST)
        if form.is_valid():
            discussion = form.save(commit=False)
            discussion.author = request.user
            discussion.save()
            form.save_m2m()
            _save_attachments(request, discussion=discussion)
            messages.success(request, t('messages.created', '{name} created.', name='Discussion'))
            return redirect('communication:discussion-detail', pk=discussion.pk)
        messages.error(request, t('messages.form_errors', 'Please correct the errors highlighted below.'))
    else:
        initial = {}
        if request.GET.get('course'):
            initial['course'] = request.GET['course']
        if request.GET.get('module'):
            initial['module'] = request.GET['module']
        form = forms.DiscussionForm(initial=initial)
    return render(request, 'communication/discussion-form.html', {
        'page_title': 'Start a Discussion', 'form': form,
    })


# ---------------------------------------------------------------------------
# Attendance (automated class-session attendance)
# ---------------------------------------------------------------------------
@login_required
def attendance_sessions(request):
    """List class sessions. Educators/admins manage them; students see their own
    attendance per session."""
    can_manage = _can_manage_classes(request)
    sessions = models.ClassSession.objects.select_related('module', 'meeting', 'created_by')
    if not can_manage:
        # Scoped to the modules the subject is enrolled in — their own for a
        # student, their child's for a parent.
        subject, _is_proxy = _attendance_subject(request)
        person = getattr(subject, 'profile', None) if subject else None
        if person:
            sessions = sessions.filter(module__in=person.selected_modules.all())
        else:
            sessions = sessions.none()
    form = forms.ClassSessionForm() if can_manage else None
    if can_manage and request.method == 'POST':
        form = forms.ClassSessionForm(request.POST)
        if form.is_valid():
            class_session = form.save(commit=False)
            class_session.created_by = request.user
            class_session.save()
            messages.success(request, t('messages.created', '{name} created.', name='Class session'))
            return redirect('communication:attendance-session', pk=class_session.pk)
        messages.error(request, t('messages.form_errors', 'Please correct the errors highlighted below.'))
    return render(request, 'communication/attendance-sessions.html', {
        'page_title': 'Attendance', 'sessions': sessions[:200],
        'form': form, 'can_manage': can_manage,
    })


@login_required
@require_POST
def attendance_ping(request, pk):
    """Heartbeat from a student who has the class session open.

    Called every ~60s by the meeting-room / session page while the tab is
    visible. Each ping credits the elapsed time (capped, see
    :data:`apps.communication.services.PRESENCE_MAX_GAP_SECONDS`) and re-derives
    the status, so attendance reflects time actually spent rather than a single
    click on the join link.
    """
    session = get_object_or_404(models.ClassSession, pk=pk)
    if not session.is_open:
        note('MEET-4001', request, session=pk)
        return JsonResponse({'ok': False, 'reason': 'closed'}, status=409)

    record = services.record_presence_ping(session, request.user)
    if record is None:
        return JsonResponse({'ok': False}, status=400)
    return JsonResponse({
        'ok': True,
        'seconds': record.seconds_attended,
        'minutes': record.minutes_attended,
        'pct': record.attended_pct,
        'required_pct': session.min_attendance_pct,
        'status': record.status,
        'status_display': record.get_status_display(),
        'manual': record.is_manual,
    })


@login_required
def attendance_session(request, pk):
    """A single session: educators mark the roll; students can self check-in."""
    session = get_object_or_404(models.ClassSession.objects.select_related('module'), pk=pk)
    can_manage = _can_manage_classes(request)

    if request.method == 'POST':
        action = request.POST.get('action')
        subject, is_proxy = _attendance_subject(request)
        if action == 'checkin' and not can_manage and is_proxy:
            # A parent cannot mark their child present — presence is measured.
            messages.error(request, 'Attendance is recorded automatically; it cannot be checked in for someone else.')
        elif action == 'checkin' and not can_manage:
            # Self check-in starts the clock; presence is still earned by time.
            services.open_attendance(session, request.user)
            services.record_presence_ping(session, request.user)
            messages.success(request, 'Checked in — your time in this session is now being tracked.')
        elif action == 'finalise' and can_manage:
            present, late, absent, excused = services.finalise_session_attendance(session)
            messages.success(
                request,
                f'Register closed — {present} present, {late} late, {absent} absent, {excused} excused.')
        elif action == 'mark' and can_manage:
            # Bulk-mark: status_<user_id> inputs.
            for person in session.module.member_people.select_related('user'):
                user = person.user
                if not user:
                    continue
                status = request.POST.get(f'status_{user.id}')
                if status:
                    services.record_attendance(session, user, source=models.Attendance.SOURCE_MANUAL,
                                               status=status, marked_by=request.user)
            messages.success(request, 'Attendance saved.')
        elif action == 'toggle_open' and can_manage:
            session.is_open = not session.is_open
            session.save(update_fields=['is_open'])
        return redirect('communication:attendance-session', pk=session.pk)

    records = {a.student_id: a for a in session.attendance.select_related('student')}
    roster = []
    for person in session.module.member_people.select_related('user'):
        if person.user:
            roster.append({'user': person.user, 'record': records.get(person.user_id)})
    subject, is_proxy = _attendance_subject(request)
    my_record = records.get(subject.id) if subject else None
    return render(request, 'communication/attendance-session.html', {
        'page_title': f'Attendance · {session}', 'session': session,
        'roster': roster, 'can_manage': can_manage, 'my_record': my_record,
        'subject': subject, 'is_proxy': is_proxy,
        'STATUS': models.Attendance,
    })


# ---------------------------------------------------------------------------
# Notification preferences (customizable notifications)
# ---------------------------------------------------------------------------
@login_required
def notification_preferences(request):
    pref = models.NotificationPreference.for_user(request.user)
    if request.method == 'POST':
        form = forms.NotificationPreferenceForm(request.POST, instance=pref)
        if form.is_valid():
            form.save()
            messages.success(request, t('messages.saved', '{name} saved successfully.', name='Preferences'))
            return redirect('communication:notification-preferences')
        messages.error(request, t('messages.form_errors', 'Please correct the errors highlighted below.'))
    else:
        form = forms.NotificationPreferenceForm(instance=pref)
    return render(request, 'communication/notification-preferences.html', {
        'page_title': 'Notification preferences', 'form': form,
    })


# ---------------------------------------------------------------------------
# Collaboration workspaces (shared files + notes)
# ---------------------------------------------------------------------------
def _visible_workspaces(request):
    qs = models.Workspace.objects.filter(is_active=True).select_related('module')
    flags = role_flags(request)
    if flags['is_admin_staff']:
        return qs
    person = getattr(request.user, 'profile', None)
    cond = Q(created_by=request.user) | Q(members=request.user)
    if person:
        cond |= Q(module__enrolments__person=person) | Q(module__educators=person)
    return qs.filter(cond).distinct()


@login_required
def workspaces(request):
    if request.method == 'POST':
        form = forms.WorkspaceForm(request.POST)
        if form.is_valid():
            workspace = form.save(commit=False)
            workspace.created_by = request.user
            workspace.save()
            form.save_m2m()
            messages.success(request, t('messages.created', '{name} created.', name='Workspace'))
            return redirect('communication:workspace-detail', pk=workspace.pk)
        messages.error(request, t('messages.form_errors', 'Please correct the errors highlighted below.'))
    else:
        form = forms.WorkspaceForm()
    return render(request, 'communication/workspaces.html', {
        'page_title': 'Workspaces', 'workspaces': _visible_workspaces(request)[:100], 'form': form,
    })


@login_required
def workspace_detail(request, pk):
    workspace = get_object_or_404(models.Workspace, pk=pk)
    if not workspace.can_access(request.user):
        note('USER-2001', request, workspace=pk)
        messages.error(request, 'You do not have access to that workspace.')
        return redirect('communication:workspaces')

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'file':
            form = forms.WorkspaceFileForm(request.POST, request.FILES)
            if form.is_valid():
                workspace_file = form.save(commit=False)
                workspace_file.workspace = workspace
                workspace_file.uploaded_by = request.user
                # Simple versioning: a re-upload with the same title bumps the version.
                if workspace_file.title:
                    previous = workspace.files.filter(title=workspace_file.title).order_by('-version').first()
                    if previous:
                        workspace_file.version = previous.version + 1
                workspace_file.save()
                workspace.save(update_fields=['updated_at'])
                messages.success(request, 'File uploaded.')
            else:
                note('FILE-1001', request, workspace=pk, errors=list(form.errors))
                messages.error(request, 'Could not upload that file.')
        elif action == 'note':
            form = forms.WorkspaceNoteForm(request.POST)
            if form.is_valid():
                note = form.save(commit=False)
                note.workspace = workspace
                note.author = request.user
                note.save()
                workspace.save(update_fields=['updated_at'])
                messages.success(request, 'Note added.')
            else:
                messages.error(request, 'Could not save that note.')
        return redirect('communication:workspace-detail', pk=workspace.pk)

    return render(request, 'communication/workspace-detail.html', {
        'page_title': workspace.name, 'workspace': workspace,
        'files': workspace.files.select_related('uploaded_by'),
        'notes': workspace.notes.select_related('author'),
        'file_form': forms.WorkspaceFileForm(), 'note_form': forms.WorkspaceNoteForm(),
    })


# ---------------------------------------------------------------------------
# In-system e-mail (admin / staff / educator) — Edumin-style inbox / compose
# ---------------------------------------------------------------------------
def _can_use_mail(request):
    flags = role_flags(request)
    return flags['is_admin_staff'] or flags['is_educator']


def _mail_counts(user):
    inbox = models.MailRecipient.objects.filter(recipient=user, trashed=False)
    return {
        'inbox': inbox.count(),
        'unread': inbox.filter(is_read=False).count(),
        'starred': inbox.filter(starred=True).count(),
        'sent': models.MailMessage.objects.filter(sender=user).count(),
        'trash': models.MailRecipient.objects.filter(recipient=user, trashed=True).count(),
    }


@login_required
def mail_inbox(request):
    if not _can_use_mail(request):
        note('MAIL-2001', request)
        messages.error(request, 'The mailbox is available to staff and educators.')
        return redirect('communication:chat-home')

    folder = request.GET.get('folder', 'inbox')
    search = request.GET.get('q', '').strip()
    sent_items = None
    rows = None
    if folder == 'sent':
        sent_items = models.MailMessage.objects.filter(sender=request.user).prefetch_related('recipients')
        if search:
            sent_items = sent_items.filter(Q(module__icontains=search) | Q(body__icontains=search))
        sent_items = sent_items[:200]
    else:
        rows = models.MailRecipient.objects.filter(recipient=request.user).select_related('message', 'message__sender')
        if folder == 'starred':
            rows = rows.filter(starred=True, trashed=False)
        elif folder == 'trash':
            rows = rows.filter(trashed=True)
        else:
            folder = 'inbox'
            rows = rows.filter(trashed=False)
        if search:
            rows = rows.filter(Q(message__module__icontains=search) | Q(message__body__icontains=search))
        rows = rows[:200]

    return render(request, 'communication/mail-inbox.html', {
        'page_title': 'Email', 'folder': folder, 'rows': rows, 'sent_items': sent_items,
        'counts': _mail_counts(request.user), 'search': search,
    })


@login_required
def mail_compose(request):
    if not _can_use_mail(request):
        return redirect('communication:chat-home')
    User = get_user_model()

    if request.method == 'POST':
        module = (request.POST.get('module') or '').strip()
        body = (request.POST.get('body') or '').strip()
        recipient_ids = request.POST.getlist('recipients')
        external_to = (request.POST.get('external_to') or '').strip()
        if not module or (not recipient_ids and not external_to):
            note('MAIL-1001', request)
            messages.error(request, 'A subject and at least one recipient are required.')
        else:
            mail = models.MailMessage.objects.create(
                sender=request.user, sender_email=getattr(request.user, 'email', ''),
                module=module, body=body, external_to=external_to,
            )
            recipients = list(User.objects.filter(pk__in=recipient_ids, is_active=True))
            for user in recipients:
                models.MailRecipient.objects.get_or_create(message=mail, recipient=user)

            # Deliver the real branded e-mail to each recipient privately
            # (one message each — no shared To: list), reply-to the sender.
            addresses = [u.email for u in recipients if u.email]
            addresses += [a.strip() for a in external_to.split(',') if a.strip()]
            reply_to = [request.user.email] if request.user.email else None
            for address in addresses:
                try:
                    from . import emails
                    emails.send_branded_email(
                        module, address, 'general',
                        {'heading': module, 'body': body}, reply_to=reply_to)
                except Exception as exc:
                    report('MAIL-5001', exc, request, context={'recipient': address})
                    logger.exception('mail: delivery failed to %s', address)
            messages.success(request, 'Message sent.')
            return redirect('communication:mail-inbox')

    return render(request, 'communication/mail-compose.html', {
        'page_title': 'Compose', 'counts': _mail_counts(request.user),
        'users': User.objects.filter(is_active=True).exclude(pk=request.user.pk).order_by('username'),
    })


@login_required
def mail_read(request, pk):
    if not _can_use_mail(request):
        return redirect('communication:chat-home')
    mail = get_object_or_404(models.MailMessage.objects.select_related('sender')
                             .prefetch_related('recipients__recipient'), pk=pk)
    row = models.MailRecipient.objects.filter(message=mail, recipient=request.user).first()
    is_recipient = row is not None
    if not (is_recipient or mail.sender_id == request.user.id):
        messages.error(request, 'You cannot view that message.')
        return redirect('communication:mail-inbox')
    if row and not row.is_read:
        row.is_read = True
        row.save(update_fields=['is_read'])
    return render(request, 'communication/mail-read.html', {
        'page_title': mail.subject, 'mail': mail, 'row': row,
        'counts': _mail_counts(request.user),
    })


@login_required
@require_POST
def mail_action(request, pk):
    if not _can_use_mail(request):
        return redirect('communication:chat-home')
    row = get_object_or_404(models.MailRecipient, message_id=pk, recipient=request.user)
    action = request.POST.get('action')
    if action == 'star':
        row.starred = not row.starred
    elif action == 'trash':
        row.trashed = True
    elif action == 'restore':
        row.trashed = False
    elif action == 'unread':
        row.is_read = False
    row.save()
    return redirect(request.POST.get('next') or 'communication:mail-inbox')


# ===========================================================================
# Unified activity feed (dashboard + social page)
# ===========================================================================
def _infer_media_kind(uploaded):
    ct = (getattr(uploaded, 'content_type', '') or '').lower()
    name = (getattr(uploaded, 'name', '') or '').lower()
    if ct.startswith('image') or name.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg')):
        return 'image'
    if ct.startswith('video') or name.endswith(('.mp4', '.webm', '.mov', '.ogg')):
        return 'video'
    return 'file'


@login_required
@require_POST
def feed_create(request):
    """Create a feed post from the 'share your thoughts' composer (text +
    optional photo/video/file), visible by default to everyone the poster
    shares a space with (groups / class / staff & admin)."""
    body = (request.POST.get('body') or '').strip()
    # A post may carry several attachments (photos/videos/documents), all posted
    # under the same ``media`` field name — see the composer.
    files = request.FILES.getlist('media')
    visibility = request.POST.get('visibility') or models.Feed.VIS_PUBLIC
    if visibility not in dict(models.Feed.VISIBILITY_CHOICES):
        visibility = models.Feed.VIS_PUBLIC
    if not body and not files:
        note('FEED-1001', request)
        messages.error(request, 'Write something or attach a file to post.')
        return redirect(request.META.get('HTTP_REFERER') or 'pages:dashboard')
    # The post's headline kind reflects its first attachment (text if none).
    first_kind = _infer_media_kind(files[0]) if files else ''
    kind = first_kind if first_kind else models.Feed.KIND_TEXT
    # File the post under a module the poster actually belongs to, so the
    # feed's module filter can find it (blank = a general post).
    module_id = (request.POST.get('module') or '').strip()
    if module_id.isdigit():
        from .feed import user_modules
        if not user_modules(request.user).filter(pk=int(module_id)).exists():
            module_id = ''
    else:
        module_id = ''
    post = models.Feed.objects.create(
        author=request.user, body=body, media_kind=first_kind,
        kind=kind, visibility=visibility, module_id=int(module_id) if module_id else None,
    )
    # Every file becomes its own attachment row (self-classifying image/video/file).
    for upload in files:
        models.FeedAttachment(feed=post, file=upload).save()
    messages.success(request, 'Shared to your feed.')
    return redirect(request.META.get('HTTP_REFERER') or 'pages:dashboard')


@login_required
def alert_counts(request):
    """Tiny JSON of the viewer's unread counts, polled by the client so a sound
    can play the moment a new message or notification arrives while they are on
    the site (see the poller in chrome.js). Kept deliberately cheap — two counts,
    two queries — because it runs on a short interval.
    """
    user = request.user
    try:
        notifications = models.Notification.objects.filter(recipient=user, is_read=False).count()
        messages_unread = models.ChatMembership.unread_total_for(user)
    except Exception:
        notifications, messages_unread = 0, 0
    return JsonResponse({'notifications': notifications, 'messages': messages_unread})


@login_required
@require_POST
def feed_like(request, pk):
    """Toggle a like on a feed post.

    Answers XHR with the new state so the card can update its counter in place —
    liking a post must never navigate away from the feed. A plain form post (no
    JavaScript) still falls back to a redirect.
    """
    post = get_object_or_404(models.Feed, pk=pk)
    liked, count = post.toggle_like(request.user)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'ok': True, 'liked': liked, 'likes': count})
    return redirect(request.META.get('HTTP_REFERER') or 'pages:dashboard')


@login_required
@require_POST
def feed_comment(request, pk):
    """Add a comment to a feed post (the card's inline comment thread)."""
    post = get_object_or_404(models.Feed, pk=pk)
    body = (request.POST.get('body') or '').strip()
    if not body:
        note('FEED-1002', request, post=pk)
        return JsonResponse({'ok': False, 'error': 'empty'}, status=400)
    comment = models.FeedComment.objects.create(post=post, author=request.user, body=body)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        from core.utils import avatar_url, display_name as _name
        return JsonResponse({
            'ok': True,
            'comment': {
                'id': comment.pk,
                'author': _name(request.user),
                'avatar': avatar_url(request.user),
                'body': comment.body,
                'when': 'just now',
            },
            'count': post.comments.count(),
        })
    return redirect(request.META.get('HTTP_REFERER') or 'pages:dashboard')


# ---------------------------------------------------------------------------
# The wall — the social feed rendered on every profile (person / course /
# module). It is backed by :class:`Discussion` + :class:`DiscussionReply`,
# which already carry likes, threaded replies and attachments, and which can be
# scoped to a course or a module. Each action returns to the page it was fired
# from, so the wall works inline on whichever profile you are looking at.
# ---------------------------------------------------------------------------
def _back(request):
    return redirect(request.META.get('HTTP_REFERER') or 'myhub:index')


def _wall_title(body):
    """Discussions need a title; a wall post is just a body. Take the first line."""
    first = (body or '').strip().splitlines()[0] if (body or '').strip() else ''
    return (first[:97] + '…') if len(first) > 100 else (first or 'Post')


@login_required
@require_POST
def wall_post(request):
    """Publish a post to a wall (the composer on a profile / course / module)."""
    body = (request.POST.get('body') or '').strip()
    files = request.FILES.getlist('attachments')
    if not body and not files:
        messages.error(request, 'Write something or attach a file to post.')
        return _back(request)

    discussion = models.Discussion.objects.create(
        author=request.user,
        title=_wall_title(body),
        body=body,
        module_id=request.POST.get('module') or None,
    )
    _save_attachments(request, discussion=discussion)
    messages.success(request, 'Posted.')
    return _back(request)


@login_required
@require_POST
def wall_like(request, pk):
    """Toggle a like on a wall post.

    Answers XHR with the new state so the wall can tick the counter in place.
    Reloading the page to register a like threw the reader back to the top of a
    long wall and lost every open comment thread. The redirect is kept for a
    no-JavaScript post.
    """
    post = get_object_or_404(models.Discussion, pk=pk)
    if post.likes.filter(pk=request.user.pk).exists():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'ok': True, 'liked': liked, 'likes': post.likes.count()})
    return _back(request)


@login_required
@require_POST
def wall_comment(request, pk):
    """Comment on a wall post — or reply to a comment when ``reply_to`` is given."""
    post = get_object_or_404(models.Discussion, pk=pk)
    body = (request.POST.get('body') or '').strip()
    if not body:
        return _back(request)

    parent = None
    reply_to = request.POST.get('reply_to')
    if reply_to:
        parent = models.DiscussionReply.objects.filter(pk=reply_to, discussion=post).first()

    reply = models.DiscussionReply.objects.create(
        discussion=post, author=request.user, body=body, reply_to=parent,
    )
    _save_attachments(request, reply=reply)
    return _back(request)


@login_required
@require_POST
def wall_comment_like(request, pk):
    """Toggle a like on a comment."""
    reply = get_object_or_404(models.DiscussionReply, pk=pk)
    if reply.likes.filter(pk=request.user.pk).exists():
        reply.likes.remove(request.user)
    else:
        reply.likes.add(request.user)
    return _back(request)
