"""One login, one sign-up, one password reset — and one way into the admin.

The project used to ship **three** competing account UIs:

1. ``/myhub/page-login/``, ``page-register/``, ``page-forgot-password/``
   — the Soft-UI pages the hub actually uses.
2. ``/accounts/…`` — django-allauth's own HTML pages.
3. ``/soft/accounts/…`` — the demo pages that ship inside
   ``django-admin-soft-dashboard`` (its "Sign In" / "Sign Up" / "Logout" links
   are what the Django admin's sidebar points at).

Only the first set is wanted. But allauth cannot simply be unmounted: it is the
*engine* behind e-mail confirmation, the emailed password-reset link and Google
sign-in. So instead of deleting it, the duplicate **entry pages** are intercepted
here and redirected to the Soft-UI ones, while allauth's machinery routes
(confirm-email, reset-from-key, social callbacks) stay exactly where they are.

The same module owns the Django-admin doorway:

* ``/admin/login/``  — never show a second login form. A signed-in admin goes
  straight through; a signed-in non-admin is sent back to the hub; an anonymous
  visitor is sent to the hub's login page with ``?next=``.
* ``/admin/logout/`` — "leaving the admin" returns you to the dashboard **still
  signed in**; it is not a sign-out. The real sign-out lives in the hub navbar
  (``myhub:logout``), which ends the session properly.
"""

from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import path, reverse
from django.utils.http import url_has_allowed_host_and_scheme


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def _safe_next(request, fallback):
    """The ``?next=`` target, but only if it points back at this site."""
    nxt = request.GET.get('next') or request.POST.get('next')
    if nxt and url_has_allowed_host_and_scheme(
            nxt, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        return nxt
    return fallback


def _is_admin(user):
    return user.is_authenticated and user.is_active and (user.is_staff or user.is_superuser)


# ---------------------------------------------------------------------------
# the duplicate account pages → the Soft-UI ones
# ---------------------------------------------------------------------------
def to_login(request):
    """``/accounts/login/`` (allauth) → the hub's Soft-UI login, keeping ``?next=``."""
    target = reverse('myhub:page-login')
    nxt = _safe_next(request, '')
    return redirect(f'{target}?next={nxt}' if nxt else target)


def to_register(request):
    """``/accounts/signup/`` (allauth) → the hub's Soft-UI registration page."""
    return redirect('myhub:page-register')


def to_forgot_password(request):
    """``/accounts/password/reset/`` (allauth) → the hub's Soft-UI reset page.

    The Soft-UI page posts through allauth's own ``ResetPasswordForm``, so the
    emailed link still lands on allauth's ``…/password/reset/key/<key>/`` view.
    """
    return redirect('myhub:page-forgot-password')


def to_login_after_reset(request):
    """``/accounts/password/reset/key/done/`` → the hub's login page.

    A finished password reset should hand the user straight back to the sign-in
    form, rather than parking them on allauth's stock "your password is changed"
    page (which is a dead end offering only a link onwards). The confirmation
    e-mail is sent separately by the ``password_reset`` signal — see
    apps.accounts.signals.
    """
    messages.success(request, 'Your password has been changed. Please sign in with it.')
    return redirect('myhub:page-login')


# ---------------------------------------------------------------------------
# the Django admin doorway
# ---------------------------------------------------------------------------
def admin_login(request):
    """Stand in front of ``/admin/login/`` so nobody is asked to sign in twice.

    The admin session *is* the hub session — an admin who is already signed in to
    the hub is simply let through.
    """
    nxt = _safe_next(request, reverse('admin:index'))
    if _is_admin(request.user):
        return redirect(nxt)
    if request.user.is_authenticated:
        messages.warning(request, 'You need an administrator account to open the Django admin.')
        return redirect('myhub:index')
    return redirect(f"{settings.LOGIN_URL}?next={nxt}")


def admin_logout(request):
    """Leaving the admin returns you to the hub — it does **not** end your session.

    (The hub navbar's *Sign out* is the real one.) Kept at ``/admin/logout/`` so
    the admin's own "Log out" control, and the theme's sidebar link, both land
    here instead of dumping the user on a dead account page.
    """
    messages.info(request, 'You left the Django admin. You are still signed in.')
    return redirect('myhub:index')


# ---------------------------------------------------------------------------
# ``admin_soft``'s demo pages — replaced, but the URL *names* are kept.
#
# The admin's chrome (layouts/base.html → includes/sidebar.html + navigation.html)
# reverses ``index``/``tables``/``billing``/``vr``/``rtl``/``profile``/``login``/
# ``logout``/``register``. Dropping the include outright would raise
# NoReverseMatch on every admin page, so each name is kept and pointed at a real
# destination in the hub instead of at a demo page.
# ---------------------------------------------------------------------------
def _to(route):
    def _view(request, *args, **kwargs):
        return redirect(route)
    return _view


soft_shim_urlpatterns = [
    path('', _to('myhub:index'), name='index'),
    path('tables/', _to('myhub:index'), name='tables'),
    path('billing/', _to('finance:invoices'), name='billing'),
    path('vr/', _to('myhub:index'), name='vr'),
    path('rtl/', _to('myhub:index'), name='rtl'),
    path('profile/', _to('accounts:my-profile'), name='profile'),

    # The three that caused the bug: the theme's sidebar/navbar pointed "Logout"
    # at admin_soft's own view, which signed the user out and dumped them on
    # /accounts/login/ — a page this project does not use.
    path('accounts/login/', to_login, name='login'),
    path('accounts/register/', to_register, name='register'),
    path('accounts/logout/', admin_logout, name='logout'),

    # admin_soft also registered these; keep the names resolvable.
    path('accounts/password-change/', _to('accounts:settings'), name='password_change'),
    path('accounts/password-change-done/', _to('accounts:settings'), name='password_change_done'),
    path('accounts/password-reset/', to_forgot_password, name='password_reset'),
    path('accounts/password-reset-confirm/<uidb64>/<token>/', to_forgot_password,
         name='password_reset_confirm'),
    path('accounts/password-reset-done/', to_forgot_password, name='password_reset_done'),
    path('accounts/password-reset-complete/', to_login, name='password_reset_complete'),
]
