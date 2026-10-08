"""Views for the MyHub dashboard.

Domain sections (Professors, Students, Courses, Library, Staff,
Holidays, Fees, CMS) are backed by real models and support full
list / create / update / delete.  The remaining pages are UI showcase pages
from the MyHub theme and are rendered as plain templates.

NOTE: view function names are intentionally kept in sync with the keys in
``dz.py`` so the shared layout can resolve the correct per-page CSS/JS.
"""

import logging

from allauth.account.models import EmailAddress
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from allauth.core import ratelimit

from apps.accounts.forms import TERMS_VERSION, UCSSignupForm
from core.branding import t  # central string catalog (.strings.json) — see core.branding
from core.roles import role_flags

from . import forms, models

logger = logging.getLogger(__name__)


def _email_is_verified(user):
    """True if the user has at least one verified e-mail address (django-allauth)."""
    return EmailAddress.objects.filter(user=user, verified=True).exists()


def _send_verification_email(request, user, *, signup=False):
    """Register the user's (unverified) e-mail address if needed and e-mail a
    confirmation link via django-allauth. No-op if the user has no e-mail."""
    if not user.email:
        return
    email_address, _ = EmailAddress.objects.get_or_create(
        user=user, email=user.email,
        defaults={'primary': True, 'verified': False},
    )
    email_address.send_confirmation(request, signup=signup)


# ===========================================================================
# Helpers
# ===========================================================================
def _save_form(request, form_class, instance, template, *, list_url, page_title,
               extra_context=None):
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, t('messages.saved', '{name} saved successfully.', name=page_title))
            return redirect(list_url)
        messages.error(request, t('messages.form_errors', 'Please correct the errors highlighted below.'))
    else:
        form = form_class(instance=instance)
    context = {'form': form, 'object': instance, 'page_title': page_title}
    if extra_context:
        context.update(extra_context)
    return render(request, template, context)


def _delete(request, model, pk, list_url, label):
    obj = get_object_or_404(model, pk=pk)
    obj.delete()
    messages.success(request, t('messages.deleted', '{name} deleted.', name=label))
    return redirect(list_url)


# ===========================================================================
# Dashboards
# ===========================================================================
def _child_card(child_user):
    """What a parent's dashboard shows for one child."""
    from apps.admissions.models import Application
    from apps.learning import fees

    person = getattr(child_user, 'profile', None)
    if person is None:
        return None
    card = {'user': child_user, 'person': person,
            'name': f'{person.first_name} {person.last_name}'.strip() or child_user.get_username(),
            'fees': None, 'application': None, 'results': []}
    try:
        card['fees'] = fees.fee_status(person)
    except Exception:  # pragma: no cover - a dashboard card must never break the page
        logger.exception('parent home: fees status failed')
    card['application'] = Application.objects.filter(person=person).order_by('-year').first()
    try:
        from apps.reports.models import TermResult
        latest = (TermResult.objects.filter(student=child_user, status=TermResult.STATUS_PUBLISHED)
                  .order_by('-year', '-term').first())
        if latest is not None:
            card['term'] = (latest.year, latest.term)
            card['results'] = list(TermResult.objects.filter(
                student=child_user, status=TermResult.STATUS_PUBLISHED, year=latest.year,
                term=latest.term).select_related('module__module'))
    except Exception:  # pragma: no cover
        logger.exception('parent home: term results failed')
    return card


def parent_home(request):
    """A parent's dashboard: one card per linked child, and the child selector."""
    from core.scoping import children_of, viewing_child
    children = list(children_of(request.user).select_related('profile').order_by('first_name', 'pk'))
    selected = viewing_child(request)
    cards = [card for card in (_child_card(child) for child in children) if card]
    return render(request, 'myhub/parent-home.html', {
        'page_title': 'My children', 'cards': cards, 'selected': selected,
    })


def index(request):
    """Home dashboard: an academic-journey summary strip, module progress,
    study analytics, the events/live-session lists, a notice board and a right
    rail of messages + notifications.

    The student-facing numbers are assembled by :mod:`apps.myhub.dashboard`;
    heavy institution counts still come from the ``get_dashboard_data`` context
    processor (admin/staff/educators only)."""
    from django.utils import timezone as _tz

    from . import dashboard as dash

    user = request.user
    # The admin team and educators have dashboards of their own on the staff
    # desk; this page is the student's. ``?view=classic`` still opens it.
    if request.GET.get('view') != 'classic' and user.is_authenticated:
        from core.roles import role_of_user
        role = role_of_user(user)
        if role in ('admin', 'staff'):
            return redirect('staffdesk:home')
        if role == 'educator':
            return redirect('staffdesk:teaching')
        if role == 'parent':
            return parent_home(request)
    now = _tz.now()
    announcements, my_tasks, recent_activity = [], [], []

    try:
        from apps.communication.models import Announcement
        announcements = list(Announcement.objects.filter(sent_at__isnull=False)
                             .select_related('sender').order_by('-sent_at')[:5])
    except Exception:
        pass
    if user.is_authenticated:
        try:
            from apps.tasks.models import TaskAssignment
            my_tasks = list(TaskAssignment.objects.filter(user=user)
                            .exclude(status=TaskAssignment.STATUS_COMPLETED)
                            .select_related('task').order_by('task__due_date')[:6])
        except Exception:
            pass
    flags = role_flags(request)
    if flags.get('is_admin_staff'):
        try:
            from apps.accounts.models import ActivityLog
            recent_activity = list(ActivityLog.objects.select_related('actor').order_by('-timestamp')[:8])
        except Exception:
            pass

    # (The AI Secretary insights preview was retired with the CrewAI assistant.)

    upcoming = [i for i in _calendar_items(request) if i['when'] >= now][:8]

    context = {
        'page_title': 'Dashboard',
        'announcements': announcements, 'my_tasks': my_tasks,
        'recent_activity': recent_activity, 'upcoming_events': upcoming,
    }
    # Recent messages: the newest message received in each of the user's chats,
    # newest chat first. Set here (not only inside student_dashboard) so the card
    # still fills if that heavier builder trips over another panel below.
    if user.is_authenticated:
        try:
            context['recent_messages'] = dash.recent_messages(user)
        except Exception:
            logger.exception('index: recent_messages failed')
            context['recent_messages'] = []
    try:
        context.update(dash.student_dashboard(user, my_tasks=my_tasks))
    except Exception:  # pragma: no cover — the dashboard must never 500
        logger.exception('index: student dashboard failed')
    # The notice board falls back to the generic announcement list.
    context.setdefault('notices', announcements)
    return render(request, 'myhub/index.html', context)


def event_management(request):
    if request.method == 'POST':
        form = forms.EventForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, t('messages.created', '{name} created.', name='Event'))
            return redirect('myhub:event-management')
        messages.error(request, t('messages.form_errors', 'Please correct the errors highlighted below.'))
    else:
        form = forms.EventForm()
    return render(request, 'myhub/event-management.html', {
        'page_title': 'Event Management',
        'events': models.Event.objects.all(),
        'form': form,
    })


def events_feed(request):
    """Aggregated JSON feed consumed by FullCalendar.

    Delegates to :mod:`apps.livesessions.sources`, which is now the single place
    every calendar entry is gathered. This used to hold its own copy of that
    aggregation, and the two drifted: this one showed only the meetings a user
    hosted or was individually invited to, so a module class never reached the
    calendar of the students it was actually for. One aggregation, one answer.
    """
    from apps.livesessions import sources

    start, end = sources.window_around()
    entries = sources.entries_for(request.user, start, end)
    return JsonResponse(sources.as_fullcalendar(entries), safe=False)


def _calendar_items(request):
    """The user's calendar entries as dicts, for the events page list."""
    from apps.livesessions import sources

    start, end = sources.window_around()
    return sources.as_items(sources.entries_for(request.user, start, end))


def events(request):
    """Events page (social events-2 look): everything on the user's calendar."""
    from django.utils import timezone as _tz
    now = _tz.now()
    items = _calendar_items(request)
    upcoming = [i for i in items if i['when'] >= now]
    past = [i for i in reversed(items) if i['when'] < now][:12]
    return render(request, 'myhub/events.html', {
        'page_title': 'Events', 'upcoming': upcoming, 'past': past,
    })


def event_detail(request, pk):
    """Detail page for a stored calendar Event."""
    event = get_object_or_404(models.Event, pk=pk)
    # A personal reminder belongs to its owner (and the office) only.
    if event.owner_id and event.owner_id != request.user.pk and not role_flags(request).get('is_admin_staff'):
        raise Http404
    return render(request, 'myhub/event-detail.html', {'page_title': event.title, 'event': event})


@require_POST
def add_reminder(request):
    """Create a personal calendar reminder for the signed-in user."""
    from django.http import HttpResponseBadRequest
    from django.utils import timezone as _tz
    from django.utils.dateparse import parse_date, parse_datetime

    if not request.user.is_authenticated:
        return HttpResponseBadRequest('auth required')
    title = (request.POST.get('title') or '').strip()
    raw_start = (request.POST.get('start') or '').strip()
    # A <input type="datetime-local"> submits a tz-naive value (e.g. 2026-07-05T08:13);
    # fall back to a date-only value at midnight, then make it aware for USE_TZ.
    start = parse_datetime(raw_start)
    if start is None:
        date = parse_date(raw_start)
        if date is not None:
            start = _tz.datetime(date.year, date.month, date.day)
    if start is not None and _tz.is_naive(start):
        start = _tz.make_aware(start, _tz.get_current_timezone())
    if not title or not start:
        messages.error(request, 'A reminder needs a title and a date/time.')
        return redirect('myhub:events')
    models.Event.objects.create(
        title=title, start=start, owner=request.user,
        category=models.Event.CATEGORY_REMINDER, color='#6f42c1',
        description=request.POST.get('description', ''),
    )
    messages.success(request, 'Reminder added to your calendar.')
    return redirect('myhub:events')


# ===========================================================================
# Auth pages
# ===========================================================================
def page_login(request):
    """Sign-in page (open to anonymous users — see ``LoginRequiredMiddleware``).

    Accounts sign in with their **e-mail address** — there is no username. New
    accounts store the e-mail as their username too, so authentication is a
    direct match; older accounts are looked up by e-mail as a fallback.

    An account whose e-mail has not been verified cannot sign in: a fresh
    confirmation link is e-mailed instead. Staff / superusers are exempt from
    that check so an administrator can never lock themselves out.

    Throttled with allauth's own rate limiter (ACCOUNT_RATE_LIMITS), because
    this page authenticates directly rather than going through allauth's
    LoginView — without it the limits configured for the project would simply
    not apply here, leaving the page open to credential stuffing.
    """
    error = None
    if request.method == 'POST':
        email = (request.POST.get('email') or '').strip()
        password = request.POST.get('password') or ''

        # 'login' caps attempts per IP — a coarse flood guard.
        limited = ratelimit.consume_or_429(request, action='login')
        if limited:
            return limited

        User = get_user_model()
        # Resolve the typed address to a real username BEFORE authenticating, so
        # one sign-in attempt is exactly one authentication attempt. This used to
        # call authenticate() twice — once with the e-mail, once with a legacy
        # username — which spends two of the account's lockout budget per try and
        # halves how many honest fumbles a user gets before django-axes locks them.
        username = email
        match = User.objects.filter(email__iexact=email).first()
        if match and match.get_username() != email:
            username = match.get_username()

        # django-axes blocks a locked-out account inside authenticate(), which
        # just returns None — indistinguishable from a wrong password. Ask it
        # directly, and BEFORE allauth's own throttle, so a locked-out person
        # gets the page that explains what happened instead of a bare 429 (the
        # two budgets are matched deliberately — see AXES_FAILURE_LIMIT).
        try:
            from axes.handlers.proxy import AxesProxyHandler
            if not AxesProxyHandler.is_allowed(request, {'username': username}):
                from django.shortcuts import render as _render
                return _render(request, 'account/lockout.html', status=429)
        except ImportError:
            pass

        # 'login_failed' additionally caps *failures* per account, so one address
        # can't be brute-forced from a spread of IPs. Checked with dry_run here
        # (a successful sign-in must not spend the failure budget) and only
        # consumed below if the credentials actually turn out to be wrong.
        key = email.lower()
        if key and not ratelimit.consume(request, action='login_failed', key=key, dry_run=True):
            return ratelimit.respond_429(request)

        user = authenticate(request, username=username, password=password)
        if user is None:
            if key:
                ratelimit.consume(request, action='login_failed', key=key)
            error = t('messages.invalid_credentials', 'Invalid e-mail or password.')
        elif not user.is_staff and not _email_is_verified(user):
            # Account exists but isn't verified — re-send the link, don't log in.
            _send_verification_email(request, user)
            error = t('messages.verify_email_required',
                      "Please verify your e-mail before signing in. We've sent a fresh link to {email}.",
                      email=user.email)
        else:
            # Signed in successfully — forget this account's failure count so a
            # user who fumbled their password a few times isn't still throttled.
            if key:
                ratelimit.clear(request, action='login_failed', key=key)
            auth_login(request, user)
            from core.utils import display_name
            messages.success(request, t('messages.welcome_back', 'Welcome back, {name}.', name=display_name(user)))
            return redirect(request.GET.get('next') or 'myhub:index')
    return render(request, 'myhub/pages/page-login.html', {'page_title': 'Login', 'error': error})


def _apply_invite_to_signup(request, user):
    """If sign-up followed an invite link, stamp the new account's role + invite
    from the pending invite in the session (parent/educator). No-op otherwise —
    a normal sign-up stays a student."""
    token = request.session.pop('invite_token', None)
    if not token or user is None:
        return
    try:
        from apps.accounts.models import Invitation
        invite = Invitation.objects.filter(token=token, status=Invitation.STATUS_PENDING).first()
        if invite is None:
            return
        person = getattr(user, 'profile', None)
        if person is not None:
            person.user_type = invite.role
            person.invite = invite
            person.save(update_fields=['user_type', 'invite'])
    except Exception:
        logger.warning('Could not apply invite to sign-up', exc_info=True)


def page_register(request):
    """Sign-up page (open to anonymous users).

    Sign-up is **e-mail only** — there is no username field. The account is
    created, a verification link is e-mailed (django-allauth) and the visitor
    is sent to the "check your inbox" page; the account is unusable until that
    link is confirmed, so the user is deliberately *not* logged in here.

    The work is delegated to :class:`~apps.accounts.forms.UCSSignupForm`
    (allauth's ``SignupForm`` + a recorded Terms & Conditions consent) rather
    than being hand-rolled, so password validators, the password-confirm check,
    e-mail-format validation and allauth's rate limits all apply. allauth keeps
    the default ``User`` model's required ``username`` column in sync with the
    e-mail for us — see ``ACCOUNT_USER_MODEL_USERNAME_FIELD`` in settings.
    """
    if request.user.is_authenticated:
        return redirect('myhub:index')

    if request.method == 'POST':
        # Same limiter allauth's own SignupView uses — this view would otherwise
        # be an unthrottled account-creation endpoint.
        limited = ratelimit.consume_or_429(request, action='signup')
        if limited:
            return limited
        form = UCSSignupForm(request.POST)
        if form.is_valid():
            # try_save() — not save(). With ACCOUNT_PREVENT_ENUMERATION a
            # sign-up for an address that already exists is deliberately
            # *valid*: try_save then e-mails "you already have an account"
            # and hands back a response identical to a real sign-up, so the
            # page can't be used to discover who is registered. Calling save()
            # directly raises ValueError in that case.
            user, resp = form.try_save(request)
            email = form.cleaned_data.get('email')
            # Show ONE "check your e-mail" page whether the account is new or
            # already existed (the `resp` branch). Returning different responses
            # would let this form reveal which addresses are registered, which
            # is exactly what ACCOUNT_PREVENT_ENUMERATION guards against. The
            # user is deliberately NOT logged in — the account is activated by
            # clicking the e-mailed link.
            if resp is None:
                # If they arrived via an invite link, set their role from it now
                # (parent/educator) so onboarding routes them correctly and they
                # never have to pick a user type. Default (no invite) = student.
                _apply_invite_to_signup(request, user)
                # save() created the user + EmailAddress but does not send the
                # activation e-mail (complete_signup used to, but it also logged
                # the user in and redirected to a URL *name*, which raised
                # DisallowedRedirect). Send it explicitly, tolerating a mail
                # hiccup so a transient SMTP error can't 500 the sign-up.
                try:
                    addr = EmailAddress.objects.filter(
                        user=user, email__iexact=email).first()
                    if addr and not addr.verified:
                        addr.send_confirmation(request, signup=True)
                except Exception:
                    logger.warning(
                        'Activation e-mail failed to send for %s', email, exc_info=True)
            # else: try_save already sent the "account already exists"/honeypot
            # e-mail — we just render the identical page below.

            # …and it must be *identical*. allauth queues a Django message
            # ("Confirmation e-mail sent to jane@example.com.") on one of these
            # two paths and not the other, which renders into the page and tells
            # an attacker whether the address was already registered — undoing
            # ACCOUNT_PREVENT_ENUMERATION.
            #
            # Iterating the storage is not enough: it marks the messages used but
            # leaves them in ``_loaded_messages``, so the template still renders
            # them. Swapping in a fresh storage discards them for good — the
            # page says "check your e-mail" on its own and needs no alert.
            from django.contrib.messages import get_messages
            from django.contrib.messages.storage import default_storage
            list(get_messages(request))          # mark the old queue consumed
            request._messages = default_storage(request)

            return render(request, 'myhub/pages/page-register-done.html', {
                'page_title': 'Check your e-mail',
                'email': email,
                'login_url': reverse('myhub:page-login'),
                'redirect_seconds': 10,
            })
    else:
        form = UCSSignupForm()

    return render(request, 'myhub/pages/page-register.html',
                  {'page_title': 'Register', 'form': form,
                   'terms_version': TERMS_VERSION,
                   # Prefill from an invite link (?email=...), safely from the view.
                   'prefill_email': request.GET.get('email', '')})


def page_logout(request):
    auth_logout(request)
    messages.info(request, t('messages.signed_out', 'You have been signed out.'))
    return redirect('myhub:page-login')


def page_forgot_password(request):
    """The hub's only "forgot password" page.

    It posts through **allauth's** ``ResetPasswordForm``, which is what actually
    sends the mail and mints the key — the emailed link then opens allauth's
    ``/accounts/password/reset/key/<key>/`` page. (This view used to just flash
    "a reset link has been sent" and send nothing at all.)

    The outcome message is deliberately identical whether or not the address
    exists, so the page cannot be used to enumerate accounts.
    """
    from allauth.account.forms import ResetPasswordForm

    sent = False
    if request.method == 'POST':
        # Throttled: this endpoint sends mail to an attacker-chosen address, so
        # it is an e-mail-bombing vector otherwise. `reset_password` is
        # configured per IP *and* per key (20/m/ip,5/m/key), so the key must be
        # passed — one call covers both rates, and omitting it raises
        # ImproperlyConfigured rather than silently skipping the limit.
        email_in = (request.POST.get('email') or '').strip()
        limited = ratelimit.consume_or_429(request, action='reset_password',
                                           key=email_in.lower() or 'anonymous')
        if limited:
            return limited

        form = ResetPasswordForm({'email': email_in})
        if form.is_valid():
            form.save(request)          # sends the reset e-mail
        sent = True
        messages.info(request, t('messages.reset_link_sent',
                                 'If that e-mail exists, a reset link has been sent.'))
    return render(request, 'myhub/pages/page-forgot-password.html',
                  {'page_title': 'Forgot Password', 'sent': sent})


# ---------------------------------------------------------------------------
# Social theme — component reference + demo pages
# ---------------------------------------------------------------------------

def social_dashboard(request):
    """The programme feed, rendered inside the shared app chrome (same navbar +
    sidebar + footer as the rest of the hub).

    ``?module=<id>`` narrows it to one of the candidate's own modules; anything
    else falls back to General (everything, newest first). The same list drives
    the composer's "which module is this about?" picker, so a post can be filed
    where it belongs. The right-hand rail carries what a candidate needs beside
    it: the dates that are coming, the week they are in, their programme
    notifications, and the people who teach and run the programme.
    """
    feed_items, feed_modules, active_module_id = [], [], None
    try:
        from apps.communication.feed import build_feed, user_modules
        feed_modules = list(user_modules(request.user))
        raw = (request.GET.get('module') or '').strip()
        if raw.isdigit() and int(raw) in {m.pk for m in feed_modules}:
            active_module_id = int(raw)
        feed_items = build_feed(request.user, limit=40, module_id=active_module_id)
    except Exception as exc:
        # Never blank the page over one bad source, but never swallow the reason
        # either — a silent `pass` here turns a broken feed into "you have no
        # activity", which reads as normal and so goes unreported for weeks.
        from core.errors import report
        report('FEED-9001', exc, request, context={'source': 'build_feed'})

    return render(request, 'pages/feed.html', dict(
        {'page_title': 'Programme Feed', 'feed_items': feed_items,
         'feed_modules': feed_modules, 'active_module_id': active_module_id},
        **_feed_rail(request)))


def _feed_rail(request):
    """The programme feed's right rail: key dates, the current week, programme
    notifications and the educators/staff a candidate can contact.

    Each panel is built inside its own ``try`` so one empty or broken source
    costs its own card rather than the whole rail.
    """
    person = getattr(request.user, 'profile', None)
    rail = {'rail_dates': [], 'rail_week': None, 'rail_notifications': [],
            'rail_people': [], 'rail_readiness': None}

    try:
        from apps.learning import progress
        rail['rail_dates'] = progress.upcoming_dates(request.user, person, limit=5)
        rail['rail_week'] = progress.current_week(request.user, person)
        rail['rail_readiness'] = progress.readiness(request.user, person)
    except Exception:                                    # pragma: no cover
        logger.exception('feed rail: study dates failed')

    try:
        from apps.communication.models import Notification
        rail['rail_notifications'] = list(
            Notification.objects.filter(recipient=request.user)
            .order_by('-created_at')[:6])
    except Exception:                                    # pragma: no cover
        logger.exception('feed rail: notifications failed')

    try:
        from apps.accounts.models import Person
        rail['rail_people'] = list(
            Person.objects.filter(user_type__in=['educator', 'staff', 'admin'],
                                  user__is_active=True)
            .select_related('user').order_by('user_type', 'first_name')[:8])
    except Exception:                                    # pragma: no cover
        logger.exception('feed rail: people failed')

    return rail


def _rand(amount):
    """``Decimal('16300')`` → ``'R 16 300'`` (non-breaking spaces, SA style)."""
    return 'R ' + f'{int(amount):,}'.replace(',', ' ')


def _landing_school_facts():
    """Fees and subjects for the landing page, straight from core.school.

    Deliberately not read from the database: the landing page is the first thing
    a fresh install shows, before any grade, subject or fee row has been seeded,
    and core.school is the same source the seeders and the registration wizard
    use — so the published figures cannot drift from what parents are billed.
    """
    from core import school

    fee_bands = [{
        'label': band['label'],
        'registration': _rand(band['registration']) if band['registration'] else '',
        'levy': _rand(band['levy']),
        'monthly': _rand(band['monthly']),
        'annual': _rand(band['annual']),
        'annual_new': _rand(band['annual_new']),
    } for band in school.FEE_BANDS]

    names = {s['code']: s['name'] for s in school.SUBJECTS}

    def subject_names(rows):
        seen = []
        for code, _group, _note in rows:
            if names[code] not in seen:
                seen.append(names[code])
        return seen

    fet = school.subjects_for(12)
    fet_groups = [{
        'label': label,
        'subjects': [names[code] for code, group, _ in fet if group == key],
    } for key, (label, _count) in school.SUBJECT_GROUPS.items()]

    return {
        'year': school.YEAR,
        'fee_bands': fee_bands,
        'subjects_foundation': subject_names(school.subjects_for(1)),
        'subjects_intermediate': subject_names(school.subjects_for(4)),
        'subjects_senior': subject_names(school.subjects_for(7)),
        'subjects_fet_core': [names[code] for code, group, _ in fet if not group],
        'subjects_fet_groups': fet_groups,
        'sibling_discount': f'{school.SIBLING_DISCOUNT_PCT:g}%',
        'prepay_discount': f'{school.ANNUAL_PREPAY_DISCOUNT_PCT:g}%',
    }


def page_landing(request):
    """The public front door — where an unauthenticated visitor lands."""
    return render(request, 'pages/landing.html', {
        'page_title': 'Welcome',
        'school_facts': _landing_school_facts(),
        'stories': _landing_stories(),
    })


def _landing_stories(count=4):
    """The most recent school stories for the landing page (core.stories)."""
    from core import stories
    return stories.recent(count)


def page_privacy_terms(request):
    """Privacy policy & terms. Open to everyone, signed in or not."""
    return render(request, 'pages/privacy-and-terms.html',
                  {'page_title': 'Privacy & terms'})
