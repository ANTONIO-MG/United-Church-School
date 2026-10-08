"""Request-scoped middleware for the accounts app.

* :class:`CurrentUserMiddleware` — stashes the active request in thread-local
  storage so model signals (see :mod:`apps.accounts.signals`) can record *who*
  triggered a change; read it back with :func:`get_current_request`.

* :class:`LoginRequiredMiddleware` — makes the whole site private: anonymous
  visitors are redirected to the login page for **every** page except a small
  allow-list (login, sign-up, forgot-password, the e-mail-confirmation pages,
  and the ``/admin/`` · ``/api/`` · ``/static/`` · ``/media/`` endpoints, which
  do their own authentication). This is enforced centrally so individual views
  don't each need an ``@login_required`` decorator.
"""

import threading
from functools import lru_cache

from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.urls import NoReverseMatch, reverse

_thread_locals = threading.local()


# ---------------------------------------------------------------------------
# CurrentUserMiddleware
# ---------------------------------------------------------------------------
class CurrentUserMiddleware:
    """Store the active request on a thread-local for the duration of the view."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_locals.request = request
        try:
            return self.get_response(request)
        finally:
            # Avoid leaking the request onto a pooled worker thread.
            _thread_locals.request = None


def get_current_request():
    """Return the request currently being processed on this thread, or ``None``."""
    return getattr(_thread_locals, 'request', None)


# ---------------------------------------------------------------------------
# LoginRequiredMiddleware
# ---------------------------------------------------------------------------
# URL-path prefixes that never require a login:
#   /admin/    — Django admin has its own login screen
#   /api/      — DRF endpoints authenticate themselves (and must return JSON,
#                not an HTML redirect)
#   /accounts/ — django-allauth (e-mail confirmation, password reset, …)
#   /static/, /media/ — public assets
#   /reports/verify/ — public certificate verification (QR links)
#   /social/landing/ — the public landing page (the platform's front door)
#   /social/stories/ — the school's stories, linked from the landing page
#   /finance/pay/ — tokenised invoice pay-link (e-mailed; may not be logged in)
#   /finance/payfast/ — PayFast return/cancel + server-to-server ITN webhook
# ``/calendar/feed/`` is the subscribable .ics: Google, Outlook and Apple fetch
# it from their own servers with no session and no way to sign in, so the secret
# token in the URL is the credential. Only that one prefix is opened — the rest
# of /calendar/ stays behind the gate.
_EXEMPT_PREFIXES = ('/static/', '/media/', '/admin/', '/api/', '/accounts/',
                    '/calendar/feed/',
                    '/captcha/',  # sign-up math-CAPTCHA image/refresh — served to anonymous visitors
                    '/reports/verify/', '/social/landing/', '/social/privacy-and-terms/',
                    '/social/stories/',  # the school's public stories (core/stories.py)
                    '/finance/pay/', '/finance/payfast/', '/community/parents/',
                    '/communication/whatsapp/',  # Meta's webhook — signature-checked, no session
                    '/community/invite/')   # invite links open before the invitee has an account

# View names reachable without logging in (the site root — which redirects
# anonymous visitors to the public landing page — plus login, sign-up,
# forgot-password and logout). E-mail confirmation lives under /accounts/.
_EXEMPT_VIEW_NAMES = (
    'home',                       # '/' → public landing page for anonymous users
    'myhub:page-login',
    'myhub:page-register',
    'myhub:page-forgot-password',
    'myhub:logout',
    'accounts:cookie-consent',    # POPIA cookie banner — anonymous visitors respond too
)


@lru_cache(maxsize=1)
def _exempt_exact_paths():
    """Resolve the allow-listed view names to URL paths (computed once, lazily)."""
    paths = set()
    for name in _EXEMPT_VIEW_NAMES:
        try:
            paths.add(reverse(name))
        except NoReverseMatch:  # pragma: no cover - URL not wired
            pass
    return frozenset(paths)


class LoginRequiredMiddleware:
    """Redirect anonymous users to ``settings.LOGIN_URL`` for every non-exempt page.

    Place this **after** ``AuthenticationMiddleware`` in ``settings.MIDDLEWARE``
    so ``request.user`` is available.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, 'user', None)
        if (user is None or not user.is_authenticated) and self._requires_login(request):
            # Preserves ?next= so the user lands back where they were headed.
            return redirect_to_login(request.get_full_path(), settings.LOGIN_URL)
        return self.get_response(request)

    @staticmethod
    def _requires_login(request):
        path = request.path_info
        if path.startswith(_EXEMPT_PREFIXES):
            return False
        if path in _exempt_exact_paths():
            return False
        return True


# ---------------------------------------------------------------------------
# OnboardingMiddleware
# ---------------------------------------------------------------------------
# After signing up (and signing in) a user must complete a two-step onboarding
# before they can reach the dashboard / any other page:
#   1. Registration  — pick a role + what they're registering for.
#   2. Profile        — finish their personal profile.
# This middleware enforces that gate centrally. Place it AFTER
# ``LoginRequiredMiddleware`` (so only logged-in users reach it).
_ONBOARDING_EXEMPT_PREFIXES = ('/static/', '/media/', '/admin/', '/api/', '/accounts/',
                               '/reports/verify/', '/finance/pay/', '/finance/payfast/',
                               '/communication/whatsapp/')

_ONBOARDING_VIEW_NAMES = (
    'accounts:register',            # wizard step 1
    'accounts:register-course',     # wizard step 2 · grade & subjects
    'accounts:register-family',     # wizard step 3 · learner & family
    'accounts:register-medical',    # wizard step 4 · medical & documents
    'accounts:register-review',     # wizard step 5 · declarations & fees
    'accounts:register-complete',   # the "payment completed" hand-off screen
    'accounts:register-parent',     # invited parent/guardian/sponsor
    'accounts:register-educator',   # invited educator
    'accounts:register-staff',      # admin/staff/educator first-login profile
    'accounts:complete-profile',
    'accounts:enrol-checkout',
    'myhub:logout',
    'myhub:page-login',
)


@lru_cache(maxsize=1)
def _onboarding_paths():
    paths = {}
    for name in _ONBOARDING_VIEW_NAMES:
        try:
            paths[name] = reverse(name)
        except NoReverseMatch:  # pragma: no cover
            pass
    return paths


class OnboardingMiddleware:
    """Force new users through registration → profile completion before the hub.

    Staff / superusers are exempt (they're provisioned directly). Anonymous
    users are handled by :class:`LoginRequiredMiddleware`, which runs first.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self._maybe_redirect(request)
        return response if response is not None else self.get_response(request)

    def _maybe_redirect(self, request):
        from django.shortcuts import redirect

        user = getattr(request, 'user', None)
        if user is None or not user.is_authenticated:
            return None
        if user.is_staff or user.is_superuser:
            return None

        path = request.path_info
        if path.startswith(_ONBOARDING_EXEMPT_PREFIXES):
            return None

        # Always allow the onboarding pages + logout themselves.
        if path in _onboarding_paths().values():
            return None

        person = getattr(user, 'profile', None)
        if person is None:
            return None  # signal will create one; nothing to gate yet.

        if not person.registered:
            return redirect('accounts:register')
        if not person.profile_status:
            return redirect('accounts:complete-profile')
        # Enrolment payment gate: the registration invoice must be settled
        # (paid, or a free 0-cost enrolment confirmed) before entering the hub.
        if person.pending_invoice_uid:
            invoice = person.get_pending_invoice()
            if invoice is not None and invoice.status != 'paid':
                return redirect('accounts:enrol-checkout')
            # Settled (or the invoice vanished) — clear it so we stop querying.
            person.pending_invoice_uid = None
            person.save(update_fields=['pending_invoice_uid'])
        return None


# ---------------------------------------------------------------------------
# ManagementAccessMiddleware — CRUD is admin/staff only
# ---------------------------------------------------------------------------
# Institution management (professors, students, courses, departments, staff,
# library, holidays, fees, CMS…) is full-CRUD for admin/staff ONLY. Educators are
# teach-only, students view their own data, parents view + pay — so none of them
# may reach these management pages. Enforced centrally by URL name (place this
# AFTER OnboardingMiddleware). Uses process_view so request.resolver_match is set.
_ADMIN_ONLY_URL_NAMES = frozenset({
    # myhub CRUD sections (list + create + edit + delete + detail)
    'myhub:all-professors', 'myhub:add-professor', 'myhub:edit-professor',
    'myhub:delete-professor', 'myhub:professor-profile',
    'myhub:all-students', 'myhub:add-student', 'myhub:edit-student',
    'myhub:delete-student', 'myhub:about-student',
    'myhub:all-courses', 'myhub:add-courses', 'myhub:edit-courses',
    'myhub:delete-courses', 'myhub:about-courses',
    'myhub:all-departments', 'myhub:add-departments', 'myhub:edit-departments',
    'myhub:delete-departments',
    'myhub:all-staff', 'myhub:add-staff', 'myhub:edit-staff', 'myhub:delete-staff',
    'myhub:staff-profile',
    'myhub:all-library', 'myhub:add-library', 'myhub:edit-library', 'myhub:delete-library',
    'myhub:all-holiday', 'myhub:add-holiday', 'myhub:edit-holiday',
    'myhub:delete-holiday', 'myhub:holiday-calendar',
    'myhub:fees-collection', 'myhub:add-fees', 'myhub:delete-fees', 'myhub:fees-receipt',
    'myhub:content', 'myhub:add-content', 'myhub:delete-content',
    'myhub:menu', 'myhub:delete-menu',
    'myhub:email-template', 'myhub:add-email', 'myhub:delete-email',
    'myhub:email-inbox', 'myhub:email-compose', 'myhub:email-read',
    'myhub:blog', 'myhub:add-blog', 'myhub:edit-blog', 'myhub:delete-blog',
    'myhub:blog-category', 'myhub:delete-blog-category',
    # The recovery desk: reactivating or restoring somebody else's account is
    # the most consequential thing an administrator does here.
    'accounts:closed-accounts', 'accounts:reactivate-account', 'accounts:restore-archive',
})


class ManagementAccessMiddleware:
    """Block non-admin/staff from institution-management (CRUD) pages."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        from django.contrib import messages
        from django.shortcuts import redirect

        from core.roles import role_flags
        match = getattr(request, 'resolver_match', None)
        if match is None or not match.url_name:
            return None
        name = f'{match.namespace}:{match.url_name}' if match.namespace else match.url_name
        if name in _ADMIN_ONLY_URL_NAMES and not role_flags(request).get('is_admin_staff'):
            messages.error(request, "You don't have permission to manage that — ask an administrator.")
            return redirect('myhub:index')
        return None


# ---------------------------------------------------------------------------
# ParentAccessMiddleware — a parent sees their child, and nothing else
# ---------------------------------------------------------------------------
# Every other role is scoped by *narrowing* what its pages return. A parent is
# different: almost nothing on the platform is theirs to see, so the sensible
# shape is the other way round — an **allow-list** of what they may reach, and a
# refusal for everything else.
#
# Written as prefixes rather than URL names on purpose. A deny-list, or a list of
# named views, silently opens up every route added afterwards; a prefix
# allow-list fails closed, so a new page is private until someone deliberately
# lists it here.
#
# What a parent may do:
#   • pay for things            — the shop, their invoices, checkout
#   • be told things            — notifications, announcements they received
#   • ask questions             — messaging (contacts restricted separately, see
#                                 core.scoping.parent_contacts)
#   • follow their own child    — reports/progress, tasks, assessments, calendar
#   • look after their account  — profile, settings, password, sign-out
_PARENT_ALLOWED_PREFIXES = (
    # Infrastructure that must never be gated (assets, auth, webhooks, health).
    '/static/', '/media/', '/accounts/', '/api/', '/__debug__/',

    # Money: the shop and their own invoices.
    '/shop/', '/finance/',

    # Being told things, and asking.
    #
    # Not /communication/announcements/ or /mail/ — both are *senders'* pages
    # (compose + what-I-sent), and both already require staff/educator. An
    # announcement reaches a parent as a notification, which is where they read
    # it; listing the compose page here would only dead-end them.
    '/communication/notifications/',
    '/communication/chat/',

    # Their child's work: results, progress, tasks, assessments.
    '/reports/', '/tasks/', '/assessments/',

    # Their child's application for admission, and the documents uploaded with
    # it (the office pages under /admissions/office/ stay closed).
    '/admissions/my-application/', '/admissions/documents/',

    # Their child's daily school register record.
    '/attendance/my/',

    # When things happen.
    '/myhub/events/', '/myhub/event-management/', '/myhub/events-feed/',

    # Their own account, and invitations to be another child's parent.
    '/community/profile/', '/community/settings/', '/community/invite/',

    # The school's public stories, and the school calendar's day pages (the
    # calendar shows a parent their children's grades — apps.livesessions.academic).
    '/social/stories/', '/calendar/day/',
)

# Individual pages inside otherwise-closed sections. Exact paths, not prefixes,
# because the section around them is not open.
#
# ``/social/`` in particular is the programme feed (not a parent's), while the
# informational pages under it are things every account needs. So they are listed
# one by one rather than by prefix.
_PARENT_ALLOWED_EXACT = frozenset({
    '/',                            # the front door redirects onward
    '/myhub/',                      # the dashboard, with its parent panel — and
                                    # what ``myhub:index`` now resolves to. A
                                    # duplicate ``index/`` route used to claim
                                    # that name, so the redirect target and the
                                    # allow-listed path were different URLs and
                                    # parents looped. The route is gone; the
                                    # self-redirect guard in process_view stays,
                                    # so a future divergence degrades to one
                                    # refused page rather than a dead account.
    '/social/privacy-and-terms/',   # terms and the cookie/privacy notice are
    '/social/landing/',             # everybody's, whatever their role
    # The school calendar (whole-school dates + their children's grades), its
    # JSON feed and the .ics download. Session pages under /calendar/ stay closed.
    '/calendar/', '/calendar/feed.json', '/calendar/school-calendar.ics',
})


class ParentAccessMiddleware:
    """Confine a parent account to the small set of pages that concern them.

    Runs after :class:`ManagementAccessMiddleware` so admin-only pages are
    already refused for everyone; this narrows the remainder down to a parent's
    own corner of the platform.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        from django.contrib import messages
        from django.shortcuts import redirect

        from core.roles import role_of

        user = getattr(request, 'user', None)
        if user is None or not user.is_authenticated:
            return None
        # Django staff/superusers are never parents in the permission sense, even
        # if their profile says so — role_of already promotes them.
        if role_of(request) != 'parent':
            return None

        path = request.path
        if path in _PARENT_ALLOWED_EXACT or path.startswith(_PARENT_ALLOWED_PREFIXES):
            return None

        # An invited parent has to finish registering before there is anything
        # to confine them to, and everyone has to be able to log out. Those
        # pages are matched by view name rather than by path: the accounts app
        # moved from /accounts/ to /community/ once already, and a path list
        # that silently stops matching locks parents out of their own
        # registration. ``_ONBOARDING_VIEW_NAMES`` is the same list
        # OnboardingMiddleware exempts, so the two cannot drift apart.
        match = getattr(request, 'resolver_match', None)
        if match is not None and match.url_name:
            view_name = (f'{match.namespace}:{match.url_name}' if match.namespace
                         else match.url_name)
            if view_name in _ONBOARDING_VIEW_NAMES:
                return None

        # Never redirect a page to itself — that is an infinite loop, not a
        # refusal, and it takes the account down completely rather than just
        # denying the one page.
        landing = reverse('myhub:index')
        if path == landing:
            return None

        messages.info(
            request,
            'That part of the hub is not available to parent accounts. '
            'You can follow your child’s progress, results and tasks from here.')
        return redirect(landing)


# ---------------------------------------------------------------------------
# MfaRequiredMiddleware — compulsory second factor for privileged accounts
# ---------------------------------------------------------------------------
# Off by default. With MFA_REQUIRED_FOR_STAFF=true, any account that can change
# other people's data (staff, superusers, and educators/admins by profile type)
# must set up a second factor before it can reach anything else. Everyone else
# is unaffected — MFA stays opt-in for learners and parents.
#
# Placed AFTER the onboarding gate so a brand-new staff member still completes
# registration first, and exempt from the allauth pages themselves (otherwise
# the redirect to "add a factor" would loop).
_MFA_EXEMPT_PREFIXES = ('/static/', '/media/', '/accounts/', '/api/', '/lti/', '/xapi/',
                        '/lrs/cmi5/', '/finance/payfast/', '/reports/verify/')


class MfaRequiredMiddleware:
    """Send privileged users to MFA setup until they have a second factor."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self._maybe_redirect(request)
        return response if response is not None else self.get_response(request)

    def _maybe_redirect(self, request):
        from django.conf import settings
        from django.contrib import messages
        from django.shortcuts import redirect
        from django.urls import NoReverseMatch, reverse

        if not getattr(settings, 'MFA_REQUIRED_FOR_STAFF', False):
            return None
        user = getattr(request, 'user', None)
        if user is None or not user.is_authenticated:
            return None
        if request.path_info.startswith(_MFA_EXEMPT_PREFIXES):
            return None

        person = getattr(user, 'profile', None)
        privileged = (user.is_staff or user.is_superuser
                      or (person and person.user_type in ('admin', 'staff', 'educator')))
        if not privileged:
            return None

        try:
            from allauth.mfa.models import Authenticator
        except ImportError:      # allauth.mfa not installed — nothing to enforce
            return None
        if Authenticator.objects.filter(user=user).exists():
            return None

        try:
            target = reverse('mfa_activate_totp')
        except NoReverseMatch:
            return None
        messages.warning(
            request,
            'Your role can change other people’s data, so this account needs '
            'two-factor authentication before you can carry on.')
        return redirect(target)


# ---------------------------------------------------------------------------
# ModuleAccessMiddleware — when the week is up, the content closes
# ---------------------------------------------------------------------------
# A student who registers on the trial gets the whole platform for seven days.
# When those seven days are up and nothing has been paid, the account does NOT
# stop working: they sign in, they see their dashboard, their profile, their
# invoices and the pay page, and they can settle up. What closes is the material
# — lessons, assessments, the library, chats and documents — until either the
# invoice is paid or a staff member grants access against a recorded payment
# (see apps.finance.access.grant_access).
#
# Scoped by path prefix. Everything not listed stays open, because locking a
# student out of paying us is a special kind of self-defeating.
_CONTENT_PREFIXES = (
    '/learning/',                   # lessons, modules, the player
    '/assessments/',                # quizzes, tests, assignments
    '/communication/chat/',         # class + direct chat
    '/communication/announcements/',
    '/social/',                     # the feed and discussions
    '/reports/',                    # marks and progress
    '/library/',
    '/scorm/', '/h5p/', '/lti/', '/xapi/',
)

# Reachable with everything locked: their own account, the money, and the
# help/legal pages everybody needs.
_ALWAYS_OPEN_PREFIXES = (
    '/static/', '/media/', '/accounts/', '/api/', '/admin/',
    '/finance/',                    # invoices, the pay page, PayFast returns
    '/shop/',
    # The module pages ARE the lock screen: My Modules, the unlock/pay flow, and
    # the module feed, where a student sees the whole schedule with the material
    # they have not paid for marked locked. Bouncing them to the invoice list
    # would hide the very thing they are being asked to buy. Safe to leave open
    # because the feed gates every row itself — see apps.learning.access.Gate.
    '/learning/modules/',
    '/community/profile/', '/community/settings/', '/community/register/',
    '/myhub/', '/social/privacy-and-terms/',
)


class ModuleAccessMiddleware:
    """Close the content when a student's trial has run out and nothing is paid.

    Runs after OnboardingMiddleware (so the student has finished registering)
    and only ever looks at students: staff, educators and parents are not on
    per-module billing and are never gated here.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        from django.contrib import messages
        from django.shortcuts import redirect

        from core.roles import role_of

        user = getattr(request, 'user', None)
        if user is None or not user.is_authenticated:
            return None
        if role_of(request) != 'student':
            return None

        path = request.path
        if path.startswith(_ALWAYS_OPEN_PREFIXES) or not path.startswith(_CONTENT_PREFIXES):
            return None

        person = getattr(user, 'profile', None)
        if person is None:
            return None

        from apps.learning.models import ModuleEnrolment

        enrolments = list(ModuleEnrolment.objects.filter(person=person))
        # No enrolments at all = nothing has been bought yet, and nothing to
        # enforce; the guide course and the General material stay reachable.
        if not enrolments or any(e.is_unlocked for e in enrolments):
            return None

        messages.warning(
            request,
            'Your free week has ended, so lessons, assessments and chats are closed for now. '
            'Settle your invoice to reopen them straight away — or speak to us and a staff '
            'member can unlock your modules once your payment is recorded.')
        return redirect('finance:invoices')


# ---------------------------------------------------------------------------
# SocialAppGuardMiddleware — an unconfigured provider is a 404, not a 500
# ---------------------------------------------------------------------------
class SocialAppGuardMiddleware:
    """Turn "this social provider was never set up" into an honest refusal.

    ``allauth.socialaccount`` registers a full set of login routes for every
    provider in ``INSTALLED_APPS``, whether or not anybody has created the
    matching ``SocialApp``. Hitting one of those routes unconfigured raises
    ``SocialApp.DoesNotExist`` — a **500 on a public login URL**, which is both
    the worst place to have one and something a crawler will find on its own.

    The buttons are already hidden (see ``accounts/templatetags/social_tags.py``),
    so reaching one of these means a deep link, an old bookmark or a bot. Any of
    those deserves the login page and a sentence, not a stack trace.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        from django.conf import settings
        from django.contrib import messages
        from django.shortcuts import redirect

        try:
            from allauth.socialaccount.models import SocialApp
        except Exception:  # pragma: no cover - socialaccount optional
            return None
        if not isinstance(exception, SocialApp.DoesNotExist):
            return None

        from core.errors import note
        note('USER-2003', request, kind='social-provider-unconfigured',
             path=request.path)
        messages.info(
            request,
            'That sign-in option is not available on this site. '
            'Please sign in with your e-mail address and password.')
        return redirect(settings.LOGIN_URL)


class UserPreferenceMiddleware:
    """Make the saved *Preferences* actually govern the session.

    ``UserSettings.theme`` and ``UserSettings.language`` were stored but never
    applied: the theme buttons flipped a class that nothing persisted, and the
    language picker wrote a row no request ever read. So signing in always
    landed you on light-mode English no matter what you had saved.

    This closes both loops, once per request, before the view runs:

    * **Language** — activate the saved language so ``{% translate %}``, form
      labels and :func:`django.utils.formats` all speak it. An explicit
      ``?lang=`` (the switcher) wins for this request and is written back to the
      user's row, so switching language on one device follows them to the next.
    * **Theme** — resolve to ``light`` / ``dark`` / ``auto`` and hang it on
      ``request.ui_theme``; the context processor puts it on ``<html>`` so the
      first paint is already the right colour, with no flash of white.
    * **Time zone** — activate the saved zone so every ``{{ when }}`` in a
      template, every reminder rendered inside a request, and the calendar itself
      render in the reader's own clock. Stored data stays UTC; only the display
      moves. This is what makes a live session at 14:00 SAST read as 13:00 to a
      candidate in Lagos without anyone converting anything by hand.

    Anonymous visitors fall back to the ``django_language`` cookie and the
    ``ui_theme`` cookie, which is what the navbar toggle writes before sign-in.
    """

    THEME_COOKIE = 'ui_theme'
    TZ_COOKIE = 'ui_tz'
    VALID_THEMES = {'light', 'dark', 'auto'}

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        from django.utils import timezone as tz
        from django.utils import translation

        language, theme, zone = self._resolve(request)

        translation.activate(language)
        request.LANGUAGE_CODE = language
        request.ui_theme = theme
        request.ui_timezone = zone or settings.TIME_ZONE
        # activate() is thread-local and the thread is reused, so the "no zone"
        # branch has to *clear* it — otherwise an anonymous request served by the
        # same worker would silently inherit the last signed-in user's clock.
        if zone:
            tz.activate(zone)
        else:
            tz.deactivate()

        response = self.get_response(request)
        response.setdefault('Content-Language', language)
        # Keep the cookies in step so the *next* first paint (including the
        # login page, before we know who they are) is already right.
        if request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME) != language:
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, language,
                                max_age=365 * 24 * 3600, samesite='Lax')
        if request.COOKIES.get(self.THEME_COOKIE) != theme:
            response.set_cookie(self.THEME_COOKIE, theme,
                                max_age=365 * 24 * 3600, samesite='Lax')
        if zone and request.COOKIES.get(self.TZ_COOKIE) != zone:
            response.set_cookie(self.TZ_COOKIE, zone,
                                max_age=365 * 24 * 3600, samesite='Lax')
        return response

    # -- resolution ---------------------------------------------------------
    def _resolve(self, request):
        supported = {code for code, _label in settings.LANGUAGES}
        language = request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME) or settings.LANGUAGE_CODE
        theme = request.COOKIES.get(self.THEME_COOKIE) or 'auto'
        zone = request.COOKIES.get(self.TZ_COOKIE) or ''

        user = getattr(request, 'user', None)
        row = None
        if user is not None and user.is_authenticated:
            row = self._settings_for(user)
            if row is not None:
                language, theme = row.language, row.theme
                zone = row.timezone or ''

        # An explicit switch on this request beats everything, and is remembered.
        wanted = (request.GET.get('lang') or '').strip()
        if wanted in supported and wanted != language:
            language = wanted
            if row is not None:
                row.language = wanted
                row.save(update_fields=['language', 'updated_at'])

        if language not in supported:
            language = settings.LANGUAGE_CODE.split('-')[0]
        if theme not in self.VALID_THEMES:
            theme = 'auto'
        return language, theme, self._valid_zone(zone)

    @staticmethod
    def _valid_zone(name):
        """``name`` if it is a real IANA zone, else '' (meaning: platform default).

        A stale or hand-edited cookie must not be able to raise out of
        middleware, which runs before any error page could be rendered.
        """
        if not name:
            return ''
        try:
            from zoneinfo import ZoneInfo
            ZoneInfo(str(name))
        except Exception:
            return ''
        return str(name)

    @staticmethod
    def _settings_for(user):
        """The user's settings row, or ``None`` if the table is not there yet
        (a fresh checkout before ``migrate`` still has to serve pages)."""
        from apps.accounts.models import UserSettings
        try:
            return UserSettings.for_user(user)
        except Exception:                                # pragma: no cover
            return None
