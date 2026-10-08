"""Root URL configuration.

Routes:

* ``/``                      → redirect to the MyHub dashboard
* ``/myhub/``                → MyHub dashboard (HTML pages + CRUD)
* ``/communication/``        → chat, meetings (Jitsi), notifications, announcements (HTML)
* ``/calendar/``             → the school calendar, live sessions & the recording archive
* ``/accounts/``             → django-allauth (e-mail confirmation, password reset, …)
* ``/admin/``                → Django admin (themed by django-admin-soft-dashboard)
* ``/soft/``                 → django-admin-soft-dashboard demo pages
* ``/api/auth/``             → dj-rest-auth (login / logout / password / registration)
* ``/api/token/``            → SimpleJWT token obtain / refresh
* ``/api/myhub/``            → REST API for the MyHub domain models
* ``/api/accounts/``         → REST API for users / organisations / courses / subjects
* ``/api/communication/``    → REST API for chat, meetings, notifications, announcements
* ``/assistant/chat/``       → admin Claude chat (CrewAI assistant retired)

In ``DEBUG`` mode the media and static directories are also served directly.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from config import auth_urls


# Brand the django-admin-soft-dashboard admin site.
admin.site.site_header = 'United Church School — Administration'
admin.site.site_title = 'United Church School Admin'
admin.site.index_title = 'Administration'


def root_redirect(request):
    """Site root: signed-in users go to their dashboard; everyone else lands on
    the public landing page (the platform's front door)."""
    user = getattr(request, 'user', None)
    if user is not None and user.is_authenticated:
        return redirect('myhub:index')
    return redirect('pages:landing')


urlpatterns = [
    # Root → MyHub dashboard
    path('', root_redirect, name='home'),

    # MyHub dashboard (HTML pages + CRUD)
    path('myhub/', include('apps.myhub.urls')),

    # Communication: chat, meetings (Jitsi), notifications, announcements (HTML pages)
    path('communication/', include('apps.communication.urls')),
    path('calendar/', include('apps.livesessions.urls')),

    # Accounts community pages (profile / settings / groups) — HTML, under the
    # ``accounts`` namespace. Mounted at /community/ so it doesn't clash with
    # django-allauth's /accounts/ (e-mail confirmation, password reset, …).
    path('community/', include('apps.accounts.urls')),

    # Social theme demo pages (Feed, blog, events, help, …) under the ``pages``
    # namespace so the themed navbar/sidebar links resolve.
    path('social/', include('apps.myhub.social_urls')),

    # AI assistant — the admin Claude chat (HTML, ``assistant``). CrewAI retired.
    path('assistant/', include('apps.ai_assistant.urls')),

    # Shop (products & services), Finance (invoices) and Tasks (assignments)
    path('shop/', include('apps.shop.urls')),
    path('finance/', include('apps.finance.urls')),
    path('admissions/', include('apps.admissions.urls')),       # UCS application for admission
    path('attendance/', include('apps.attendance.urls')),       # daily school register
    path('sasams/', include('apps.sasams.urls')),               # SA-SAMS export for the Department
    path('tasks/', include('apps.tasks.urls')),

    # My Learning Hub — lessons/study, assessments, reports/certificates, analytics
    path('learning/', include('apps.learning.urls')),
    path('assessments/', include('apps.assessments.urls')),
    path('reports/', include('apps.reports.urls')),
    path('analytics/', include('apps.analytics.urls')),

    # Developer diagnostics: the error dictionary and the error log. Every view
    # 404s for anyone who is not admin/staff — see apps.diagnostics.views.
    path('diagnostics/', include('apps.diagnostics.urls')),
    path('staff/', include('apps.staffdesk.urls')),
    path('revision/', include('apps.revision.urls')),

    # Math CAPTCHA image / refresh endpoints (django-simple-captcha).
    path('captcha/', include('captcha.urls')),

    # Django admin (themed by django-admin-soft-dashboard).
    # The two overrides MUST precede admin.site.urls — URL resolution is
    # first-match — so the admin never shows its own login form (the hub session
    # is the admin session) and "leaving" it returns you to the dashboard rather
    # than signing you out onto a dead account page. See config.auth_urls.
    path('admin/login/', auth_urls.admin_login),
    path('admin/logout/', auth_urls.admin_logout),
    path('admin/', admin.site.urls),

    # REST auth
    path('api/auth/', include('dj_rest_auth.urls')),
    path('api/auth/registration/', include('dj_rest_auth.registration.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # The hub has exactly ONE login, ONE sign-up and ONE password-reset page —
    # the Soft-UI ones under /myhub/. allauth ships its own HTML versions of all
    # three; they are intercepted here (before the include, so they win) and
    # redirected to the Soft-UI pages. allauth itself stays mounted because it is
    # the engine behind e-mail confirmation, the emailed reset link and Google
    # sign-in — only its duplicate *entry pages* are taken out of service.
    path('accounts/login/', auth_urls.to_login),
    path('accounts/signup/', auth_urls.to_register),
    path('accounts/password/reset/', auth_urls.to_forgot_password),
    # A completed reset ends at the login page rather than allauth's dead-end
    # "password changed" page. Keeps allauth's URL name so its own view's
    # success_url still reverses.
    path('accounts/password/reset/key/done/', auth_urls.to_login_after_reset,
         name='account_reset_password_from_key_done'),

    # django-allauth — e-mail confirmation links, password reset, etc.
    # NOTE: included *after* dj_rest_auth.registration so allauth's real HTML
    # confirm-email view wins the shared ``account_confirm_email`` URL name —
    # verification links then open the HTML page (not dj-rest-auth's API shim).
    path('accounts/', include('allauth.urls')),

    # REST API (for web / mobile / desktop clients)
    path('api/myhub/', include('apps.myhub.api_urls')),
    path('api/accounts/', include('apps.accounts.api_urls')),
    path('api/communication/', include('apps.communication.api_urls')),

    # django-admin-soft-dashboard's demo pages (Tables / Billing / VR / RTL and a
    # second Sign-In / Sign-Up / Logout) are NOT part of this product — but the
    # admin's chrome reverses their URL names, so they are replaced by a shim that
    # keeps the names and points them at real hub pages. See config.auth_urls.
    # Included WITHOUT a namespace on purpose: the theme reverses these as bare
    # names ({% url "logout" %}), exactly as admin_soft registered them.
    path('soft/', include(auth_urls.soft_shim_urlpatterns)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
elif getattr(settings, 'SERVE_MEDIA_FROM_DJANGO', False):
    # Uploaded files, served by the app itself in production.
    #
    # ``static()`` is a no-op when DEBUG is off — deliberately, because serving
    # user uploads through Django is slower than any web server and bypasses
    # every access control. Here it is the lesser evil: on a container platform
    # with no object store and no front-end web server, the alternative is that
    # every avatar, course cover and chat attachment 404s. WhiteNoise cannot
    # stand in for it either — it indexes its files once at start-up, so
    # anything uploaded after boot would be invisible until the next deploy.
    #
    # core.media_headers.MediaSecurityHeadersMiddleware still stamps these
    # responses, so an uploaded .svg/.html cannot execute in this origin.
    # Point FILE_SERVER_BACKEND at s3/azure to take this path out of use.
    from django.views.static import serve as _serve
    from django.urls import re_path as _re_path

    urlpatterns += [
        _re_path(r'^media/(?P<path>.*)$', _serve,
                 {'document_root': settings.MEDIA_ROOT}),
    ]
