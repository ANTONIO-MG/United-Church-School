"""The school calendar, the session pages, and the scheduler.

The calendar is one page with one query behind it, filtered by
:func:`apps.livesessions.audience.visible_sessions`. Admin and staff get the
whole school's diary plus the free-slot strip; educators get their modules;
students get exactly the sessions they were invited to or enrolled into. Nobody
gets a second, differently-scoped view to keep in step.

Everything renders in the reader's own time zone: the middleware has already
activated it, so template dates are local without any per-view conversion.
"""

import calendar as calendar_module
from datetime import date, datetime, time, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.communication.models import MeetingRoom

from . import audience as aud
from . import forms, services, sources
from .models import LiveSessionSettings, SessionArtifact


# ---------------------------------------------------------------------------
# Calendar
# ---------------------------------------------------------------------------
@login_required
def calendar(request):
    """The school calendar — a month of sessions, plus the school's dates."""
    focus = _focus_month(request)
    first = focus.replace(day=1)
    last_day = calendar_module.monthrange(focus.year, focus.month)[1]
    window_start = _aware(first, time.min)
    window_end = _aware(first.replace(day=last_day), time.max)

    # One aggregation for every surface — see apps.livesessions.sources on why
    # the platform no longer has two calendars that disagree.
    selected = _selected_kinds(request)
    entries = sources.entries_for(request.user, window_start, window_end, kinds=selected)
    by_day = sources.group_by_day(entries)

    weeks = [[_cell(day, focus, by_day) for day in week]
             for week in calendar_module.Calendar(firstweekday=0).monthdatescalendar(focus.year, focus.month)]

    now = timezone.now()
    return render(request, 'livesessions/calendar.html', {
        'page_title': 'Calendar',
        'weeks': weeks,
        'focus': focus,
        'prev_month': (first - timedelta(days=1)).strftime('%Y-%m'),
        'next_month': (first.replace(day=last_day) + timedelta(days=1)).strftime('%Y-%m'),
        'today': timezone.localdate(),
        'upcoming': [e for e in entries if e.start and e.start >= now][:8],
        'legend': [{'kind': kind, 'label': label, 'colour': colour, 'icon': icon,
                    'on': kind in selected}
                   for kind, (label, colour, icon) in sources.KINDS.items()],
        'selected_kinds': ','.join(sorted(selected)),
        'can_schedule': aud.can_manage(request.user),
        'sees_everything': aud.sees_whole_calendar(request.user),
        'user_timezone': getattr(request, 'ui_timezone', ''),
        'subscribe_url': request.build_absolute_uri(_personal_feed_path(request.user)),
    })


@login_required
def day(request, on):
    """One day, with the free-slot strip for anyone who can schedule."""
    try:
        the_day = datetime.strptime(on, '%Y-%m-%d').date()
    except ValueError:
        raise Http404('Not a date')

    entries = sources.entries_for(request.user, _aware(the_day, time.min),
                                  _aware(the_day, time.max))
    can_schedule = aud.can_manage(request.user)
    return render(request, 'livesessions/day.html', {
        'page_title': f'{the_day:%A %d %B %Y}',
        'day': the_day,
        'entries': entries,
        'sessions': [e for e in entries if e.kind == 'session'],
        # The reader's own connected calendar is subtracted too, so a slot that
        # is free on the school calendar but taken in their Google diary is not offered.
        'free_slots': services.free_slots(the_day, for_user=request.user) if can_schedule else [],
        'can_schedule': can_schedule,
    })


@login_required
def feed(request):
    """The calendar as JSON, for the month grid's client-side navigation."""
    start = _parse_iso(request.GET.get('from')) or timezone.now() - timedelta(days=30)
    end = _parse_iso(request.GET.get('to')) or timezone.now() + timedelta(days=90)
    entries = sources.entries_for(request.user, start, end, kinds=_selected_kinds(request))
    return JsonResponse({'entries': [{
        'title': entry.title,
        'start': timezone.localtime(entry.start).isoformat() if entry.start else None,
        'end': timezone.localtime(entry.end).isoformat() if entry.end else None,
        'allDay': entry.all_day,
        'kind': entry.kind,
        'label': entry.label,
        'colour': entry.colour,
        'detail': entry.detail,
        'location': entry.location,
        'url': entry.url,
        'meta': entry.meta,
    } for entry in entries]})


@login_required
def ics(request):
    """Download the visible calendar as a one-off ``.ics`` file."""
    start, end = sources.window_around()
    entries = sources.entries_for(request.user, start, end, kinds=_exportable_kinds(request))
    return _ics_response(entries, filename='school-calendar.ics')


def personal_feed(request, token):
    """The subscribable calendar feed — the "export to Google / Outlook" route.

    Deliberately unauthenticated and addressed by a secret token, because that is
    the only thing Google Calendar, Outlook and Apple can actually subscribe to:
    they fetch the URL from their own servers, with no session and no way to sign
    in. The token is therefore the credential, which is why it can be rotated
    from Settings — rotating instantly revokes every device it was ever added to.

    Events the user *imported* are left out. Publishing them back would loop them
    into the calendar they came from, where they would arrive as duplicates of
    entries that calendar already owns.
    """
    from apps.accounts.models import UserSettings

    row = (UserSettings.objects
           .select_related('user')
           .filter(calendar_token=token, user__is_active=True)
           .first())
    if row is None:
        raise Http404('No such calendar')

    start, end = sources.window_around()
    entries = sources.entries_for(row.user, start, end,
                                  kinds=[k for k in sources.KINDS if k != 'external'])
    name = f'{row.user.get_full_name() or row.user.get_username()} · United Church School'
    return _ics_response(entries, filename='school-calendar.ics', name=name)


def _ics_response(entries, *, filename, name='United Church School'):
    from . import ics as ics_mod

    body = ics_mod.serialise([{
        'uid': entry.uid or f'entry-{index}@ucs-lms',
        'title': entry.title,
        'start': entry.start,
        'end': entry.end,
        'all_day': entry.all_day,
        'description': entry.detail,
        'location': entry.location,
    } for index, entry in enumerate(entries)], name=name)

    response = HttpResponse(body, content_type='text/calendar; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    # Subscribers re-poll on their own schedule; nothing here is worth caching.
    response['Cache-Control'] = 'no-store, max-age=0'
    return response


# ---------------------------------------------------------------------------
# Sessions
# ---------------------------------------------------------------------------
@login_required
def session_detail(request, pk):
    """One session: details, join button, and afterwards the recording and pack."""
    meeting = get_object_or_404(
        MeetingRoom.objects.select_related('module', 'host', 'programme', 'institution',
                                           'cohort', 'week', 'calendar_event'),
        pk=pk)
    if not aud.can_view(request.user, meeting):
        raise Http404('No such session')

    artifact = getattr(meeting, 'artifact', None)
    recap, pack = _reports_for(meeting)

    from . import identity as ident
    return render(request, 'livesessions/session-detail.html', {
        'page_title': meeting.title,
        'meeting': meeting,
        'artifact': artifact,
        'recap': recap,
        'pack': pack,
        'can_manage': aud.can_manage(request.user, meeting),
        'is_invited': meeting.participants.filter(user=request.user).exists(),
        'attendance': _my_attendance(meeting, request.user),
        # The exact name we ask them to type into Teams — see session_join.
        'join_name': ident.display_name_for(request.user),
    })


@login_required
def session_create(request):
    if not aud.can_manage(request.user):
        messages.error(request, 'Only admins, staff and educators can schedule sessions.')
        return redirect('livesessions:calendar')

    if request.method == 'POST':
        form = forms.SessionForm(request.POST, user=request.user)
        if form.is_valid():
            cleaned = form.cleaned_data
            meeting = services.create_session(
                host=request.user,
                title=cleaned['title'],
                start=cleaned['scheduled_start'],
                end=cleaned['scheduled_end'],
                audience=cleaned['audience'],
                description=cleaned.get('description', ''),
                session_kind=cleaned['session_kind'],
                institution=cleaned.get('institution'),
                programme=cleaned.get('programme'),
                cohort=cleaned.get('cohort'),
                module=cleaned.get('module'),
                week=cleaned.get('week'),
                calendar_event=cleaned.get('calendar_event'),
                invitees=cleaned.get('invitees') or (),
                record=cleaned.get('record_automatically'),
                publish_recording=cleaned.get('publish_recording'),
            )
            if cleaned.get('is_recurring'):
                meeting.is_recurring = True
                meeting.recurrence = cleaned.get('recurrence', '')
                meeting.save(update_fields=['is_recurring', 'recurrence', 'updated_at'])

            engine = 'Teams session' if meeting.is_teams else 'Session'
            messages.success(request, f'{engine} scheduled — the audience has been notified.')
            return redirect('livesessions:session-detail', pk=meeting.pk)
        messages.error(request, 'Please correct the errors highlighted below.')
    else:
        initial = {}
        start = _parse_iso(request.GET.get('start'))
        if start:
            initial['scheduled_start'] = timezone.localtime(start)
            initial['scheduled_end'] = timezone.localtime(start + timedelta(hours=1))
        form = forms.SessionForm(user=request.user, initial=initial)

    return render(request, 'livesessions/session-form.html', {
        'page_title': 'Schedule a live session',
        'form': form,
        'teams_ready': _teams_ready(),
    })


@login_required
def session_edit(request, pk):
    meeting = get_object_or_404(MeetingRoom, pk=pk)
    if not aud.can_manage(request.user, meeting):
        raise Http404('No such session')

    if request.method == 'POST':
        form = forms.SessionForm(request.POST, instance=meeting, user=request.user)
        if form.is_valid():
            moved = ('scheduled_start' in form.changed_data
                     or 'scheduled_end' in form.changed_data)
            meeting = form.save()
            meeting.participants.exclude(role='host').exclude(
                user__in=form.cleaned_data.get('invitees') or []).delete()
            for user in form.cleaned_data.get('invitees') or []:
                meeting.participants.get_or_create(user=user)
            services.update_session(meeting, reschedule=moved)
            if moved:
                # People planned around the old time; the ledger is cleared so
                # the reminder job tells them again against the new one.
                meeting.reminders_sent.all().delete()
            messages.success(request, 'Session updated.')
            return redirect('livesessions:session-detail', pk=meeting.pk)
        messages.error(request, 'Please correct the errors highlighted below.')
    else:
        form = forms.SessionForm(instance=meeting, user=request.user, initial={
            'invitees': [p.user_id for p in meeting.participants.exclude(role='host')]})

    return render(request, 'livesessions/session-form.html', {
        'page_title': f'Edit — {meeting.title}',
        'form': form,
        'meeting': meeting,
        'teams_ready': _teams_ready(),
    })


@login_required
@require_POST
def session_cancel(request, pk):
    meeting = get_object_or_404(MeetingRoom, pk=pk)
    if not aud.can_manage(request.user, meeting):
        raise Http404('No such session')
    services.cancel_session(meeting, by=request.user,
                            reason=(request.POST.get('reason') or '').strip())
    messages.success(request, 'Session cancelled — everyone invited has been told.')
    return redirect('livesessions:calendar')


@login_required
def session_join(request, pk):
    """Record who is going in, then hand them over to Teams.

    This is the only route into a live session, and it sits behind the login
    gate, so at this moment we know exactly who the person is — their name,
    surname and e-mail, from their own profile. That is written down as a
    :class:`~apps.livesessions.models.SessionJoin` *before* the redirect.

    It matters because Microsoft gives no supported way to pre-fill an anonymous
    attendee's display name: Teams will ask them to type one, and whatever they
    type is all the attendance report carries. Recording the hand-off here means
    the register no longer depends on what they typed — the Graph report is
    matched back against this roster instead (see
    :mod:`apps.livesessions.identity`).

    Clicking is not attending. The row starts no clock and marks nobody present;
    presence is still measured by the Graph report and the page heartbeat.
    """
    meeting = get_object_or_404(MeetingRoom, pk=pk)
    if not aud.can_view(request.user, meeting):
        raise Http404('No such session')

    from . import identity as ident
    from .models import SessionJoin

    join, created = SessionJoin.objects.get_or_create(
        meeting=meeting, user=request.user,
        defaults={'display_name': ident.display_name_for(request.user),
                  'email': request.user.email or ''},
    )
    if not created:
        # Re-joining after a dropped connection is normal; keep the snapshot
        # fresh but count the visits so an educator can see it happened.
        join.display_name = ident.display_name_for(request.user)
        join.email = request.user.email or ''
        join.click_count += 1
        join.save(update_fields=['display_name', 'email', 'click_count', 'last_clicked_at'])

    # Open the attendance row so the student appears on the register straight
    # away — at zero seconds, absent until presence is actually measured.
    session = getattr(meeting, 'class_session', None)
    if session is not None and session.is_open:
        from apps.communication import services as comm
        comm.open_attendance(session, request.user)

    target = meeting.external_url
    if not target:
        messages.error(request, 'This session has no live room yet — please try again shortly.')
        return redirect('livesessions:session-detail', pk=meeting.pk)
    return redirect(target)


@login_required
def session_register(request, pk):
    """The register for one session, plus the attendees Teams could not name.

    Anonymous joining means a handful of people every week come back from Graph
    as "Tebza 📱" or an unrecognised address. Rather than leaving an educator to
    reconcile that by hand each time, they are listed here with the roster of
    people who clicked through but were not matched — one click attaches them,
    and the answer is remembered for every future session.
    """
    meeting = get_object_or_404(MeetingRoom.objects.select_related('module'), pk=pk)
    if not aud.can_manage(request.user, meeting):
        raise Http404('No such session')

    from . import identity as ident
    from .models import SessionJoin

    artifact = getattr(meeting, 'artifact', None)
    session = getattr(meeting, 'class_session', None)
    records = list(session.attendance.select_related('student__profile')
                   .order_by('student__first_name')) if session else []

    matched_ids = {r.student_id for r in records}
    joins = (SessionJoin.objects.filter(meeting=meeting)
             .select_related('user__profile').order_by('display_name'))

    return render(request, 'livesessions/session-register.html', {
        'page_title': f'Register — {meeting.title}',
        'meeting': meeting,
        'session': session,
        'records': records,
        'joins': joins,
        'unresolved': (artifact.unresolved_attendees if artifact else []) or [],
        # Who to offer when attaching an unnamed attendee: the session's own
        # roster, minus anyone already on the register.
        'candidates': [u for u in ident.roster_for(meeting) if u.pk not in matched_ids],
    })


@login_required
@require_POST
def resolve_attendee(request, pk):
    """Attach an unmatched Teams attendee to a candidate, and remember it."""
    meeting = get_object_or_404(MeetingRoom, pk=pk)
    if not aud.can_manage(request.user, meeting):
        raise Http404('No such session')

    from django.contrib.auth import get_user_model

    from apps.communication import services as comm
    from apps.communication.models import Attendance
    from . import identity as ident
    from .models import SessionArtifact

    label = (request.POST.get('label') or '').strip()
    user_id = (request.POST.get('user') or '').strip()
    seconds = int(request.POST.get('seconds') or 0)

    user = get_user_model().objects.filter(pk=user_id).first() if user_id.isdigit() else None
    if user is None or not label:
        messages.error(request, 'Choose which learner that attendee is.')
        return redirect('livesessions:session-register', pk=meeting.pk)

    # 1) Put the measured time on the register.
    session = getattr(meeting, 'class_session', None)
    if session is not None and seconds > 0:
        comm.apply_measured_attendance(session, user, seconds=seconds,
                                       source=Attendance.SOURCE_TEAMS, authoritative=True)

    # 2) Remember it, so the same person matches automatically next week.
    person = getattr(user, 'profile', None)
    for key in (request.POST.getlist('keys') or [label]):
        ident.remember(person, key, by=request.user)

    # 3) Take them off the unresolved list.
    artifact = SessionArtifact.objects.filter(meeting=meeting).first()
    if artifact is not None:
        artifact.unresolved_attendees = [row for row in (artifact.unresolved_attendees or [])
                                         if row.get('label') != label]
        artifact.save(update_fields=['unresolved_attendees', 'updated_at'])

    messages.success(request, f'“{label}” is now recorded as {ident.display_name_for(user)} — '
                              f'and will be matched automatically from now on.')
    return redirect('livesessions:session-register', pk=meeting.pk)


@login_required
def past_sessions(request):
    """The re-watch library: every finished session the viewer may see."""
    sessions = (aud.visible_sessions(request.user)
                .filter(scheduled_end__lt=timezone.now())
                .select_related('module', 'host', 'artifact')
                .order_by('-scheduled_start'))

    module_id = request.GET.get('module')
    if module_id and module_id.isdigit():
        sessions = sessions.filter(module_id=int(module_id))
    if request.GET.get('watchable') == '1':
        sessions = sessions.filter(artifact__state=SessionArtifact.STATE_PUBLISHED)

    # Imported YouTube recordings for the modules this person is enrolled on.
    recordings = []
    try:
        from . import imported
        person = getattr(request.user, 'profile', None)
        recordings = list(imported.videos_for_person(person, surface='past_sessions')[:60])
    except Exception:
        pass

    return render(request, 'livesessions/past-sessions.html', {
        'page_title': 'Past sessions',
        'sessions': sessions[:120],
        'selected_module': module_id or '',
        'recordings': recordings,
    })


# ---------------------------------------------------------------------------
# Settings (admin / staff)
# ---------------------------------------------------------------------------
@login_required
@require_POST
def connect_calendar(request):
    """Subscribe to the reader's own Google / Outlook / Apple calendar feed."""
    from .forms import CalendarSubscriptionForm
    from . import subscriptions as subs

    form = CalendarSubscriptionForm(request.POST, user=request.user)
    if not form.is_valid():
        for errors in form.errors.values():
            for error in errors:
                messages.error(request, error)
        return redirect(_settings_return(request))

    subscription = form.save(commit=False)
    subscription.user = request.user
    subscription.save()

    # Sync immediately: "did it work?" is the only question anyone has at this
    # point, and waiting half an hour for the job to answer it is no answer.
    ok, detail = subs.refresh(subscription)
    if ok:
        messages.success(request, f'“{subscription.name}” connected — {detail} imported.')
    else:
        messages.error(request, f'Connected, but nothing could be read yet: {detail}')
    return redirect(_settings_return(request))


@login_required
@require_POST
def disconnect_calendar(request, pk):
    """Remove a connected calendar and everything imported from it."""
    from .models import CalendarSubscription

    subscription = get_object_or_404(CalendarSubscription, pk=pk, user=request.user)
    name = subscription.name
    subscription.delete()        # cascades to its ExternalEvent rows
    messages.success(request, f'“{name}” disconnected and its events removed.')
    return redirect(_settings_return(request))


@login_required
@require_POST
def refresh_calendar(request, pk):
    """Re-import one connected calendar now, rather than waiting for the job."""
    from .models import CalendarSubscription
    from . import subscriptions as subs

    subscription = get_object_or_404(CalendarSubscription, pk=pk, user=request.user)
    subscription.is_active = True
    subscription.consecutive_failures = 0
    subscription.save(update_fields=['is_active', 'consecutive_failures', 'updated_at'])

    ok, detail = subs.refresh(subscription)
    if ok:
        messages.success(request, f'“{subscription.name}” refreshed — {detail}.')
    else:
        messages.error(request, f'Could not read “{subscription.name}”: {detail}')
    return redirect(_settings_return(request))


@login_required
@require_POST
def rotate_calendar_token(request):
    """Mint a new secret for the personal feed, revoking the old link.

    The token is the only thing protecting that feed, so this is the "I shared it
    with the wrong person" button. Every calendar app subscribed to the old URL
    stops updating immediately and has to be pointed at the new one.
    """
    import uuid

    from apps.accounts.models import UserSettings

    row = UserSettings.for_user(request.user)
    row.calendar_token = uuid.uuid4()
    row.save(update_fields=['calendar_token', 'updated_at'])
    messages.success(request, 'Your calendar link has been reset. Any app still using the old '
                              'address will stop updating — add the new one instead.')
    return redirect(_settings_return(request))


def _settings_return(request):
    """Back to whichever page the calendar form was submitted from."""
    from django.utils.http import url_has_allowed_host_and_scheme

    target = request.POST.get('next') or ''
    if target and url_has_allowed_host_and_scheme(
            target, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        return target
    return reverse('accounts:settings') + '?tab=connected'


@login_required
def settings_page(request):
    from core.roles import role_of_user
    if role_of_user(request.user) not in ('admin', 'staff'):
        raise Http404('Not available')

    conf = LiveSessionSettings.load()
    if request.method == 'POST':
        form = forms.LiveSessionSettingsForm(request.POST, request.FILES, instance=conf)
        if form.is_valid():
            saved = form.save(commit=False)
            saved.updated_by = request.user
            saved.save()
            messages.success(request, 'Live session settings saved.')
            return redirect('livesessions:settings')
        messages.error(request, 'Please correct the errors highlighted below.')
    else:
        form = forms.LiveSessionSettingsForm(instance=conf)

    from . import youtube
    return render(request, 'livesessions/settings.html', {
        'page_title': 'Live session settings',
        'form': form,
        'conf': conf,
        'teams_ready': _teams_ready(),
        'youtube_configured': youtube.is_configured(),
        'youtube_remaining': youtube.uploads_remaining_today() if youtube.is_configured() else 0,
        'pipeline_counts': _pipeline_counts(),
    })


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def _focus_month(request):
    raw = (request.GET.get('m') or '').strip()
    try:
        return datetime.strptime(raw, '%Y-%m').date().replace(day=1)
    except ValueError:
        today = timezone.localdate()
        return today.replace(day=1)


def _aware(day, at):
    return timezone.make_aware(datetime.combine(day, at), timezone.get_current_timezone())


def _cell(day, focus, by_day):
    entries = by_day.get(day, [])
    return {
        'date': day,
        'in_month': day.month == focus.month,
        'is_today': day == timezone.localdate(),
        'entries': entries[:4],
        'overflow': max(0, len(entries) - 4),
    }


def _selected_kinds(request):
    """Which sources the reader has switched on, via ``?show=session,task``."""
    raw = (request.GET.get('show') or '').strip()
    if not raw:
        return set(sources.KINDS)
    wanted = {chunk.strip() for chunk in raw.split(',') if chunk.strip()}
    return (wanted & set(sources.KINDS)) or set(sources.KINDS)


def _exportable_kinds(request):
    """Everything except what we imported — see :func:`personal_feed`."""
    return [kind for kind in _selected_kinds(request) if kind != 'external']


def _personal_feed_path(user):
    """The subscribable feed URL for ``user``, minting their token on first use."""
    from apps.accounts.models import UserSettings
    try:
        row = UserSettings.for_user(user)
    except Exception:       # pragma: no cover - a missing row must not 500 the page
        return ''
    return reverse('livesessions:personal-feed', args=[row.calendar_token])


def _reports_for(meeting):
    """``(recap, pack)`` — the automatic recap and the Claude follow-up pack."""
    try:
        from apps.ai_assistant.models import AiReport
        recap = AiReport.objects.filter(linked_ref=f'meeting:{meeting.pk}').first()
        pack = AiReport.objects.filter(linked_ref=f'session-followup:{meeting.pk}').first()
        return recap, pack
    except Exception:
        return None, None


def _my_attendance(meeting, user):
    session = getattr(meeting, 'class_session', None)
    if session is None:
        return None
    return session.attendance.filter(student=user).first()


def _teams_ready():
    from apps.msteams import graph
    return graph.is_configured()


def _pipeline_counts():
    from django.db.models import Count
    rows = (SessionArtifact.objects.values('state')
            .annotate(n=Count('pk')).order_by('state'))
    return {row['state']: row['n'] for row in rows}


def _parse_iso(raw):
    if not raw:
        return None
    try:
        parsed = datetime.fromisoformat(str(raw).replace('Z', '+00:00'))
    except ValueError:
        return None
    if timezone.is_naive(parsed):
        parsed = timezone.make_aware(parsed, timezone.get_current_timezone())
    return parsed


def _ics_stamp(moment):
    from datetime import timezone as dt_timezone
    if moment is None:
        moment = timezone.now()
    return moment.astimezone(dt_timezone.utc).strftime('%Y%m%dT%H%M%SZ')


def _ics_escape(text):
    return (str(text or '')
            .replace('\\', '\\\\').replace(';', r'\;')
            .replace(',', r'\,').replace('\n', r'\n'))


# ---------------------------------------------------------------------------
# YouTube recordings — staff mapping screen (scan the channel, place playlists)

@login_required
def youtube_admin(request):
    """Admin/staff screen: scan the channel and map each playlist to a module +
    cohort and the places its videos should appear. Admin/staff only — mapping
    spans every institution's modules, which is not an educator's remit."""
    from core.roles import role_flags
    if not role_flags(request)['is_admin_staff']:
        raise Http404
    from apps.learning.models import Cohort, ProgrammeModule

    from . import models as ls_models
    from . import youtube as yt

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'scan':
            if not yt.can_scan():
                messages.error(request, 'YouTube reading is not configured — set the '
                                        'credentials in .env (see the note on this page).')
            else:
                import io

                from django.core.management import call_command
                buf = io.StringIO()
                try:
                    call_command('scan_youtube', stdout=buf)
                    messages.success(request, buf.getvalue().strip() or 'Scan complete.')
                except Exception as exc:  # pragma: no cover
                    messages.error(request, f'Scan failed: {exc}')
            return redirect('livesessions:youtube-admin')

        if action == 'map':
            pl = get_object_or_404(ls_models.YouTubePlaylist, pk=request.POST.get('playlist'))
            mod_id = (request.POST.get('programme_module') or '').strip()
            coh_id = (request.POST.get('cohort') or '').strip()
            pl.programme_module_id = int(mod_id) if mod_id.isdigit() else None
            pl.cohort_id = int(coh_id) if coh_id.isdigit() else None
            if pl.programme_module_id:
                m = ProgrammeModule.objects.select_related('programme__institution').get(pk=pl.programme_module_id)
                pl.programme_id = m.programme_id
                pl.institution_id = m.programme.institution_id
            else:
                pl.programme_id = pl.institution_id = None
            pl.show_past_sessions = bool(request.POST.get('show_past_sessions'))
            pl.show_my_programme = bool(request.POST.get('show_my_programme'))
            pl.show_schedule = bool(request.POST.get('show_schedule'))
            pl.is_active = bool(request.POST.get('is_active'))
            pl.save()
            messages.success(request, f'Saved “{pl.title or pl.youtube_id}”.')
            return redirect('livesessions:youtube-admin')

    playlists = ls_models.YouTubePlaylist.objects.prefetch_related('videos').all()
    modules = (ProgrammeModule.objects
               .select_related('programme', 'programme__institution', 'module')
               .order_by('programme__institution__name', 'programme__name', 'order'))
    cohorts = (Cohort.objects.select_related('programme', 'programme__institution')
               .order_by('programme__institution__name', 'code'))
    return render(request, 'livesessions/youtube_admin.html', {
        'page_title': 'YouTube recordings',
        'playlists': playlists, 'modules': modules, 'cohorts': cohorts,
        'can_scan': yt.can_scan(), 'unmapped': sum(1 for p in playlists if not p.is_mapped),
    })
