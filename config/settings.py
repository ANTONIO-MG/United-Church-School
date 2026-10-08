"""Django settings for the United Church School learning platform.

Configuration is environment-driven: values are read from ``.env`` next to ``manage.py``
(committed with the code) with development-friendly defaults so the project runs
out of the box. Notable choices:

* PostgreSQL is the primary database (``default``); a MySQL ``backup``
  connection is defined for disaster-recovery / reporting (see
  :mod:`core.db_router`).
* REST API via DRF + SimpleJWT; auth flows via dj-rest-auth + django-allauth.
* Redis cache is used only when ``USE_REDIS=true``; otherwise local-memory.
* The admin is themed with django-admin-soft-dashboard.

Docs: https://docs.djangoproject.com/en/4.2/ref/settings/
"""

# ---------------------------------------------------------
# Core Python imports
# ---------------------------------------------------------
import os
import sys
import warnings
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv


# ---------------------------------------------------------
# Base directory
# ---------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env, but remember whether it actually existed. A missing .env (e.g.
# accidentally deleted) is the single most
# common cause of a cryptic "fe_sendauth: no password supplied" crash deep
# inside a management command — see the POSTGRES_PASSWORD guard below.
ENV_FILE = BASE_DIR / '.env'
ENV_FILE_FOUND = ENV_FILE.is_file()

# What the *platform* set, captured before .env is layered in. This file is
# committed (see the note in .gitignore), so it travels to the deployment host
# carrying development values — DEBUG=True, ALLOWED_HOSTS=*, a localhost
# database. ``load_dotenv`` never overwrites a variable that already exists, so
# anything set in the host's dashboard wins; this snapshot is what lets the
# settings below tell "the platform said so" apart from "the committed .env
# said so" *after* the merge, when os.environ no longer remembers which was
# which. Production defaults key off the platform, not off .env.
PROCESS_ENV = dict(os.environ)

load_dotenv(ENV_FILE)

# --- Hosting platform ---------------------------------------------------
# Render sets RENDER=true and RENDER_EXTERNAL_HOSTNAME=<service>.onrender.com in
# every service; Railway sets its own RAILWAY_* pair. Detecting the platform
# lets a deploy be correct with no configuration at all: the public hostname is
# already known, TLS is already terminated upstream, and DEBUG must be off.
ON_RENDER = bool(PROCESS_ENV.get('RENDER'))
ON_RAILWAY = bool(
    PROCESS_ENV.get('RAILWAY_ENVIRONMENT')
    or PROCESS_ENV.get('RAILWAY_ENVIRONMENT_NAME')
    or PROCESS_ENV.get('RAILWAY_PROJECT_ID')
    or PROCESS_ENV.get('RAILWAY_SERVICE_ID')
)
ON_PLATFORM = ON_RENDER or ON_RAILWAY
# Host only — Django strips the port before matching ALLOWED_HOSTS, so an entry
# carrying one can never match and every request would 400 with DisallowedHost.
RENDER_EXTERNAL_HOSTNAME = (
    (PROCESS_ENV.get('RENDER_EXTERNAL_HOSTNAME') or '').strip().split('://')[-1].split('/')[0]
)
_RENDER_HOST_PORT = ''
if ':' in RENDER_EXTERNAL_HOSTNAME:
    RENDER_EXTERNAL_HOSTNAME, _, _RENDER_HOST_PORT = RENDER_EXTERNAL_HOSTNAME.partition(':')
# CSRF origins and absolute links, by contrast, are compared/served with the
# port included, so they keep it.
RENDER_EXTERNAL_NETLOC = (
    f'{RENDER_EXTERNAL_HOSTNAME}:{_RENDER_HOST_PORT}' if _RENDER_HOST_PORT
    else RENDER_EXTERNAL_HOSTNAME
)

if not ENV_FILE_FOUND:
    warnings.warn(
        f"No .env file found at {ENV_FILE}; using process environment only. "
        f"Restore it from git: `git checkout -- .env`.",
        stacklevel=2,
    )


def env_bool(name, default=False):
    return os.getenv(name, str(default)).strip().lower() in ('1', 'true', 'yes', 'on')


def env_int(name, default=0):
    try:
        return int(os.getenv(name, '').strip() or default)
    except ValueError:
        return default


def env_list(name, default=()):
    """Comma-separated env var → list of non-empty stripped strings."""
    raw = os.getenv(name)
    if raw is None:
        return list(default)
    return [item.strip() for item in raw.split(',') if item.strip()]


def platform_decides(name):
    """True when *name*'s value must not be taken from the committed ``.env``.

    The .env in this repository is tracked (see the note in .gitignore), so it
    is deployed along with the code, carrying a developer's values for things
    that are dangerous to get wrong in production — an insecure cookie flag, a
    localhost site URL. ``load_dotenv`` does not overwrite variables the host
    already set, so anything configured in the platform's own dashboard still
    wins; what this catches is the *absence* of such a variable, where the .env
    value would otherwise become the production value by default.

    Only used for the handful of settings where the safe production value is
    knowable without being told (see PRODUCTION DEFAULTS below).
    """
    return ON_PLATFORM and name not in PROCESS_ENV


# Prefer the C extension ``mysqlclient`` for the MySQL "backup" connection;
# fall back to the pure-Python ``PyMySQL`` driver if it is not installed so
# the project still imports/runs in any environment.
try:  # pragma: no cover
    import MySQLdb  # noqa: F401
except Exception:  # pragma: no cover
    try:
        import pymysql
        pymysql.install_as_MySQLdb()
    except Exception:
        pass


SCHOOL_EMIS_NUMBER = os.getenv('SCHOOL_EMIS_NUMBER', '').strip()  # GDE EMIS number (SA-SAMS export header)
# ---------------------------------------------------------
# SECURITY SETTINGS
# ---------------------------------------------------------
# ``or``, not a getenv default: a blank ``SECRET_KEY=`` line in .env
# sets the variable to "" and would otherwise crash every manage.py command with
# "The SECRET_KEY setting must not be empty". .02_setup.py writes a real key.
SECRET_KEY = os.getenv('SECRET_KEY', '').strip() or (
    'django-insecure-bq5ce)%1j-iqh@snbr6=3ddq-p(s!_n@ue8hm$lu1-cy(88amz'
)

# On a hosting platform the default flips to False, and only a DEBUG set in the
# platform's own dashboard can turn it back on. The committed .env carries
# DEBUG=True for local work; without this, deploying it would serve tracebacks,
# settings and source to the public internet — the single most expensive thing
# that can go wrong here, and it would look like it was working fine.
if ON_PLATFORM and 'DEBUG' not in PROCESS_ENV:
    DEBUG = False
else:
    DEBUG = env_bool('DEBUG', True)

# True while the Django test runner is driving. The runner forces DEBUG=False,
# so deployment guards that key on ``not DEBUG`` (e.g. apps.finance.checks,
# which refuses to start a production build pointed at PayFast's sandbox) would
# otherwise fire on every test run and block the suite. Guards consult this to
# tell "this is production" apart from "this is a test".
TESTING = 'test' in sys.argv or bool(os.getenv('PYTEST_CURRENT_TEST'))

# '*' is a development convenience — it accepts any Host header, which defeats
# the Host-header check that stops cache-poisoning and password-reset links
# being minted for an attacker's domain. It is the default only while DEBUG is
# on; a production build must name its hosts, and apps.diagnostics.deploy_checks
# refuses to boot if it has not (``deploy.E001`` / ``deploy.E002``).
ALLOWED_HOSTS = env_list('ALLOWED_HOSTS', ['*'] if DEBUG else [])

# The platform already knows the public hostname it routes to this service, so
# add it rather than making the deploy depend on somebody copying it into an
# env var correctly. The wildcard is then dropped: it is meaningless once the
# real host is listed, it comes from the committed .env rather than from any
# deployment decision, and deploy.E002 refuses to start with it.
if RENDER_EXTERNAL_HOSTNAME and RENDER_EXTERNAL_HOSTNAME not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
if ON_PLATFORM and not DEBUG and len(ALLOWED_HOSTS) > 1:
    ALLOWED_HOSTS = [h for h in ALLOWED_HOSTS if h != '*']


# ---------------------------------------------------------
# APPLICATION REGISTRATION
# ---------------------------------------------------------
INSTALLED_APPS = [

    # --------------------
    # ASGI / WebSockets (Django Channels). `daphne` must be listed FIRST so its
    # ASGI-aware ``runserver`` replaces Django's WSGI one; `channels` provides the
    # consumer/routing layer. See config/asgi.py, CHANNEL_LAYERS below and
    # docs/WEBSOCKETS.md.
    # --------------------
    'daphne',
    'channels',

    # --------------------
    # Admin theme (must be before django.contrib.admin)
    # --------------------
    'admin_soft.apps.AdminSoftDashboardConfig',

    # --------------------
    # Django Core Apps
    # --------------------
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
     'django.contrib.humanize',

    # --------------------
    # Local Project Apps
    # --------------------
    'apps.accounts',
    'apps.myhub',                 # MyHub dashboard: HTML pages, models, views
    'apps.communication',         # chat, meetings, notifications, announcements + e-mail
    'apps.msteams',               # Microsoft Teams live classroom via Microsoft Graph
    'apps.livesessions',          # school calendar, session audience, reminders, recording pipeline
    'apps.ai_assistant',          # Claude admin layer + AiReport/AiInsight (Teams recaps)
    'apps.shop',                  # products & services store: orders, payments, expiry
    'apps.finance',               # invoicing & payment tracking (due payments, receipts)
    'apps.tasks',                 # assignable tasks (per-user / group / subject / course)
    'apps.admissions',            # UCS application for admission: family, medical, documents, office checklist
    'apps.attendance',            # daily school register: everyone present, teacher marks absentees
    'apps.sasams',                # SA-SAMS / LURITS export for the Department (learners, marks, attendance)

    # --------------------
    # My Learning Hub (learning-lifecycle platform)
    # --------------------
    'apps.learning',              # modules, lessons (resources + versioning), study-session timers
    'apps.assessments',           # quizzes, tests, exams, questions, attempts, assignments
    'apps.reports',               # weighted grades, report cards, certificates
    'apps.analytics',             # admin/staff/educator academic intelligence + risk monitoring
    'apps.scheduler',             # unattended background jobs (see apps/scheduler/jobs.py)
    'apps.diagnostics',           # error dictionary + error log (admin/staff only)
    'apps.staffdesk',             # /staff/: jobs, moderation, audit, certificates, dashboards
    'apps.revision',              # spaced-repetition review cards from the student's own mistakes

    # --------------------
    # Third-Party Apps
    # --------------------
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt.token_blacklist',

    'dj_rest_auth',
    'dj_rest_auth.registration',

    'allauth',
    'allauth.account',
    # Multi-factor authentication (TOTP authenticator app + recovery codes).
    # Chosen over django-otp because it plugs straight into the allauth login,
    # signup, social-login and password-reset flows this project already runs —
    # django-otp would have meant a second, parallel login pipeline to keep in
    # step with them. See docs/PACKAGE_DECISIONS.md.
    'allauth.mfa',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.facebook',

    'corsheaders',
    'guardian',
    'django_filters',

    # Self-hosted math CAPTCHA on the sign-up form (django-simple-captcha).
    # Renders a small arithmetic image ("3 + 4 = ?") the user must answer — no
    # third-party keys, no external calls, works offline. Replaces Google
    # reCAPTCHA. See CAPTCHA_* settings below and captcha.urls in config/urls.py.
    'captcha',

    # Brute-force protection. allauth already rate-limits the login/signup/reset
    # *forms* (see apps.myhub.views), but that is per-request throttling with no
    # record: axes adds per-account and per-IP lockout with a persisted
    # AccessAttempt / AccessLog trail an admin can actually audit and reset.
    'axes',

    # Excel / CSV import & export in the Django admin — bulk student intake and
    # marks / report exports for admins, staff and educators.
    'import_export',
]


# ---------------------------------------------------------
# MIDDLEWARE
# ---------------------------------------------------------
MIDDLEWARE = [
    # First in, so its process_exception runs LAST on the way out and therefore
    # sees exceptions that inner middleware did not convert into a response.
    'apps.diagnostics.middleware.ErrorCaptureMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    # Serves everything in STATIC_ROOT straight from the app process, with
    # correct caching headers. With DEBUG=False Django's own static serving is
    # switched off, and platforms like Render's free tier put no web server in
    # front of the app — so without this the deployed site loads with no CSS,
    # no JS and no images, which reads as "the deploy is broken" rather than as
    # a missing static handler. Must sit directly after SecurityMiddleware.
    'whitenoise.middleware.WhiteNoiseMiddleware',
    # Early, so it stamps every /media/ response including ones short-circuited
    # by middleware further down. Stops an uploaded .svg / .html executing in
    # this site's origin (see core.media_headers).
    'core.media_headers.MediaSecurityHeadersMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'apps.accounts.middleware.CurrentUserMiddleware',    # logging / audit
    # Theme + language: the saved Preferences actually govern the session.
    # After auth (it reads the user's row) and before anything that renders.
    'apps.accounts.middleware.UserPreferenceMiddleware',
    'core.i18n_runtime.RuntimeTranslationMiddleware',    # translate un-marked HTML
    'apps.accounts.middleware.LoginRequiredMiddleware',  # site-wide login gate
    'apps.accounts.middleware.OnboardingMiddleware',     # force registration + profile completion
    'apps.accounts.middleware.ManagementAccessMiddleware',  # CRUD/management is admin/staff only
    'apps.accounts.middleware.ParentAccessMiddleware',   # parents see their child, and nothing else
    'apps.accounts.middleware.ModuleAccessMiddleware',   # content closes when the trial lapses unpaid
    'apps.accounts.middleware.MfaRequiredMiddleware',    # second factor for privileged roles (opt-in)
    # An unconfigured social provider raises deep inside allauth; this turns
    # that 500 on a public login URL into a redirect with an explanation.
    'apps.accounts.middleware.SocialAppGuardMiddleware',
    # Must be LAST — axes needs the fully-resolved request to attribute a failed
    # login to the right account and IP.
    'axes.middleware.AxesMiddleware',
]


# ---------------------------------------------------------
# URL & TEMPLATE CONFIGURATION
# ---------------------------------------------------------
ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # ALL project templates live here, organised per-app in templates/<app>/.
        'DIRS': [BASE_DIR / 'templates'],
        # Kept True so third-party apps (allauth, admin_soft, DRF, guardian) can
        # still ship their own bundled templates from inside their packages.
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.branding',          # brand / UI strings (.strings.json)
                'core.context_processors.ui_chrome',         # resolved theme + language
                'core.context_processors.parent_children',   # a parent's children + the one viewed
                'django.template.context_processors.i18n',   # LANGUAGES / LANGUAGE_CODE
                'core.roles.user_roles',                     # role flags (is_student/parent/educator/admin…)
                'apps.myhub.context_processors.get_dashboard_data',  # aggregated dashboard data
                'apps.accounts.context_processors.account_stats',  # profile card + group count
                'apps.communication.context_processors.comm_stats',  # unread messages / notifications
                'apps.ai_assistant.context_processors.ai_assistant',  # AI widget enabled flag
                'apps.shop.context_processors.shop_stats',    # shop counts / revenue
                'apps.finance.context_processors.finance_stats',  # invoice totals / due
                'apps.tasks.context_processors.task_stats',   # task counts / my pending
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ---------------------------------------------------------
# ASGI / WebSockets (Django Channels)
# ---------------------------------------------------------
# Real-time push over WebSockets: instant chat delivery, live notification /
# message sounds and badge counts, and a foundation for live-lesson presence.
# See config/asgi.py (protocol router), apps/communication/consumers.py &
# routing.py (the sockets), apps/communication/realtime.py (server-side push)
# and docs/WEBSOCKETS.md.
#
# The channel layer is how a Django view/DRF call reaches a connected socket. In
# production it MUST be Redis so every web worker shares one layer; a single-proc
# dev server can use the in-memory layer. Gated on the same USE_REDIS switch the
# cache uses, with a dedicated Redis URL/db so channel traffic never collides
# with cached values.
ASGI_APPLICATION = 'config.asgi.application'

# Clients only try to open a socket when this is on; with it off everything
# falls back to the existing REST polling, so the site works with no ASGI server.
WEBSOCKETS_ENABLED = env_bool('WEBSOCKETS_ENABLED', True)

if env_bool('USE_REDIS', False):
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                'hosts': [os.getenv('CHANNEL_REDIS_URL',
                                    os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/2'))],
            },
        },
    }
else:
    # In-memory layer: fine for a single-process dev server, useless across
    # workers — never run more than one process with this backend.
    CHANNEL_LAYERS = {
        'default': {'BACKEND': 'channels.layers.InMemoryChannelLayer'},
    }


# ---------------------------------------------------------
# CORS SETTINGS
# ---------------------------------------------------------
# Allowing every origin was hard-coded. That lets any website script the API in
# a signed-in user's browser, which matters more now that /api/ is exempt from
# the site-wide login gate and authenticates itself. Open in development (so the
# mobile/desktop clients can be pointed at a laptop), explicit in production.
CORS_ALLOW_ALL_ORIGINS = env_bool('CORS_ALLOW_ALL_ORIGINS', DEBUG)
CORS_ALLOWED_ORIGINS = env_list('CORS_ALLOWED_ORIGINS')
CORS_ALLOW_CREDENTIALS = env_bool('CORS_ALLOW_CREDENTIALS', False)


# ---------------------------------------------------------
# NETWORK / LAN ACCESS  (everyone on the same Wi-Fi can reach the server)
# ---------------------------------------------------------
# Start the server so it listens on every interface — either
#     python run_server.py                 (prints the LAN URLs to share)
# or  python manage.py runserver 0.0.0.0:8000
# ALLOWED_HOSTS defaults to '*' (see above) so any Host header is accepted in
# dev. For form POSTs (login, settings, posting to the feed, …) to succeed from
# ANOTHER device, that device's origin must be a trusted CSRF origin. Same-origin
# requests already pass; here we additionally trust this machine's own LAN
# address(es) on the common dev ports, plus anything in the CSRF_TRUSTED_ORIGINS
# env var (comma-separated, full "scheme://host:port" entries).
def _detect_lan_ips():
    import socket
    ips = set()
    try:
        ips.add(socket.gethostbyname(socket.gethostname()))
    except Exception:
        pass
    try:
        probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        probe.connect(('8.8.8.8', 80))   # UDP: sends nothing, just selects the outward interface
        ips.add(probe.getsockname()[0])
        probe.close()
    except Exception:
        pass
    return {ip for ip in ips if ip and not ip.startswith('127.')}

# The LAN probe is a development affordance and costs a DNS lookup plus a UDP
# socket at import time; a hosted deployment has no LAN to trust and serves one
# public origin over TLS, so it is skipped there.
LAN_IPS = [] if ON_PLATFORM else sorted(_detect_lan_ips())
_LAN_PORTS = [p.strip() for p in os.getenv('LAN_PORTS', '8000,80,8080').split(',') if p.strip()]
CSRF_TRUSTED_ORIGINS = env_list('CSRF_TRUSTED_ORIGINS')
for _ip in LAN_IPS:
    CSRF_TRUSTED_ORIGINS.append(f'http://{_ip}')            # bare host (implicit :80)
    CSRF_TRUSTED_ORIGINS += [f'http://{_ip}:{_port}' for _port in _LAN_PORTS]
# Django compares the Origin header against this list for every unsafe request
# behind a proxy, so the site's own public origin has to be in it or every POST
# (login included) fails CSRF with "Origin checking failed".
if RENDER_EXTERNAL_NETLOC:
    CSRF_TRUSTED_ORIGINS.append(f'https://{RENDER_EXTERNAL_NETLOC}')
CSRF_TRUSTED_ORIGINS = sorted(set(CSRF_TRUSTED_ORIGINS))


# ---------------------------------------------------------
# SESSION COOKIE
# ---------------------------------------------------------
# 'Lax' is right for this platform: every page is same-site, and Lax still lets
# the cookie ride a normal top-level navigation in from an e-mailed link.
# (SameSite=None was here for cross-site LTI launches inside an LMS iframe;
# LTI is gone, and None would only widen CSRF exposure for no benefit. If it is
# ever set again, it *requires* Secure — hence the pairing below.)
SESSION_COOKIE_SAMESITE = os.getenv('SESSION_COOKIE_SAMESITE', 'Lax') or None
# The committed .env sets this to false for plain-HTTP local work. On a hosted
# deployment that value would send the session cookie — the credential for the
# whole logged-in session — over any plain-HTTP hop, and deploy.E003 refuses to
# start because of it. The platform serves HTTPS, so it decides.
SESSION_COOKIE_SECURE = (
    not DEBUG if platform_decides('SESSION_COOKIE_SECURE')
    else env_bool('SESSION_COOKIE_SECURE', not DEBUG)
)

# A Secure cookie is only *stored* by the browser over HTTPS. The dev server is
# plain HTTP, so leaving this on in DEBUG throws the session away on every
# response: the login POST succeeds, the very next request is anonymous, and the
# login gate bounces the user straight back to the login page — with no error
# anywhere to explain it. Refuse to boot into that state.
if DEBUG and SESSION_COOKIE_SECURE and not env_bool('DEV_HTTPS', False):
    import warnings
    warnings.warn(
        'SESSION_COOKIE_SECURE=True with DEBUG=True: the dev server serves plain '
        'HTTP, so the browser would discard the session cookie and every login '
        'would loop back to the login page. Forcing it off. (Set DEV_HTTPS=true '
        'if you really are serving the dev site over TLS.)',
        RuntimeWarning,
    )
    SESSION_COOKIE_SECURE = False
    # SameSite=None is only legal on a Secure cookie — Chrome drops it otherwise.
    if SESSION_COOKIE_SAMESITE is None:
        SESSION_COOKIE_SAMESITE = 'Lax'


# ---------------------------------------------------------
# DATABASE CONFIGURATION
#   default -> PostgreSQL  (PRIMARY)
#   backup  -> MySQL       (BACKUP / DR SERVER)
#
# All reads & writes are routed to "default" (PostgreSQL) by
# core.db_router.PrimaryReplicaRouter.  The "backup" connection is
# defined so the same schema can be kept in sync on a MySQL server
# (e.g. `python manage.py migrate --database=backup`) and used for
# disaster-recovery / reporting / replication.
#
# Two ways to point at PostgreSQL, in this order of precedence:
#
#   1. A connection URL — ``DATABASE_URL``. Every managed host injects one:
#      Render, Railway, Heroku, Fly, Neon, Supabase. A deploy therefore needs no
#      database configuration of its own; attaching the database is enough.
#   2. The discrete ``POSTGRES_*`` variables — the local-development path, and
#      what the committed .env carries.
#
# A URL wins outright for NAME/USER/PASSWORD/HOST/PORT; the POSTGRES_* values
# are not merged into it. Half-overriding a URL with a stale POSTGRES_HOST is
# how a deploy ends up quietly writing to the wrong database, so it is one or
# the other. Note the committed .env supplies POSTGRES_* on every host — that is
# exactly why the URL has to win rather than merge.
# ---------------------------------------------------------
from urllib.parse import parse_qsl, unquote, urlsplit

_POSTGRES_SCHEMES = {
    'postgres', 'postgresql', 'pgsql',
    'postgres+psycopg2', 'postgresql+psycopg2',
    'postgres+psycopg', 'postgresql+psycopg',
}


def _parse_database_url(url, source='DATABASE_URL'):
    """Parse ``postgres://user:pass@host:port/dbname?sslmode=require``.

    Returns a Django ``DATABASES['default']``-shaped dict. Only PostgreSQL
    schemes are accepted: this project's primary database is PostgreSQL, and a
    silently-ignored ``mysql://`` would be far worse than a loud error.
    """
    from django.core.exceptions import ImproperlyConfigured

    parts = urlsplit(url)
    scheme = parts.scheme.lower()
    if scheme not in _POSTGRES_SCHEMES:
        raise ImproperlyConfigured(
            f"{source} has scheme '{parts.scheme or '(none)'}'; expected a "
            f"PostgreSQL URL such as "
            f"postgresql://user:password@host:5432/dbname"
        )
    if not parts.hostname:
        raise ImproperlyConfigured(
            f"{source} has no host: {url!r}. Expected "
            f"postgresql://user:password@host:5432/dbname"
        )

    # Credentials and the database name are percent-encoded in a URL. A password
    # containing '@', '/' or ':' arrives escaped and must be decoded, or
    # authentication fails on a password that looks correct in every log line.
    options = {}
    query = dict(parse_qsl(parts.query, keep_blank_values=False))
    for _key in ('sslmode', 'sslrootcert', 'sslcert', 'sslkey', 'options',
                 'connect_timeout', 'application_name', 'target_session_attrs'):
        if query.get(_key):
            options[_key] = query[_key]
    if 'connect_timeout' in options:
        options['connect_timeout'] = int(options['connect_timeout'])

    return {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': unquote(parts.path.lstrip('/')) or 'postgres',
        'USER': unquote(parts.username or ''),
        'PASSWORD': unquote(parts.password or ''),
        'HOST': parts.hostname,
        'PORT': str(parts.port or ''),
        'OPTIONS': options,
    }


# Railway publishes two URLs: DATABASE_URL on a *.railway.internal address that
# resolves only inside its network, and DATABASE_PUBLIC_URL for everywhere else.
# Render publishes one DATABASE_URL (its internal hostname) plus an external URL
# you paste in yourself. Preferring the public one off-platform means the same
# .env works from a laptop and inside the container.
_URL_VARS = (
    ('DATABASE_URL', 'DATABASE_PUBLIC_URL') if ON_PLATFORM
    else ('DATABASE_PUBLIC_URL', 'DATABASE_URL')
)
_URL_CANDIDATES = [
    (name, value) for name in _URL_VARS
    if (value := (os.getenv(name) or '').strip())
]


def _is_private_railway_url(value):
    try:
        return (urlsplit(value).hostname or '').endswith('.railway.internal')
    except ValueError:
        return False


# A *.railway.internal URL cannot resolve off-platform no matter which variable
# it was pasted into, so rank by reachability rather than by variable name.
_usable = [c for c in _URL_CANDIDATES
           if ON_PLATFORM or not _is_private_railway_url(c[1])]
DATABASE_URL_SOURCE = (_usable or _URL_CANDIDATES or [(None, None)])[0][0]

if DATABASE_URL_SOURCE:
    _default_db = _parse_database_url(
        os.getenv(DATABASE_URL_SOURCE).strip(), DATABASE_URL_SOURCE
    )
else:
    _default_db = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB', 'united_church_school_db'),
        'USER': os.getenv('POSTGRES_USER', 'postgres'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', ''),
        'HOST': os.getenv('POSTGRES_HOST', '127.0.0.1'),
        'PORT': os.getenv('POSTGRES_PORT', '5432'),
        'OPTIONS': {},
    }

_db_host = _default_db['HOST'] or ''
_db_is_local = _db_host in ('', 'localhost', '127.0.0.1', '::1') or _db_host.startswith('/')

# A database reached over a network must be encrypted. Render, Railway, Neon and
# Supabase all speak TLS; a unix socket and a loopback connection do not need
# it. POSTGRES_SSLMODE (or an sslmode= in the URL) overrides either way,
# 'disable' included.
_sslmode = (os.getenv('POSTGRES_SSLMODE') or '').strip()
if _sslmode:
    _default_db['OPTIONS']['sslmode'] = _sslmode
elif not _db_is_local and not _db_host.endswith('.railway.internal'):
    _default_db['OPTIONS'].setdefault('sslmode', 'require')

# Without a timeout an unreachable host hangs the request — and `migrate`, and
# the release command — until the OS gives up, minutes later.
_default_db['OPTIONS'].setdefault('connect_timeout', env_int('POSTGRES_CONNECT_TIMEOUT', 10))

# Persistent connections: a managed database pays 50-150 ms per TCP+TLS
# handshake, so reuse matters far more there than on a local socket. The health
# check then reconnects a pooled connection the server has since closed instead
# of handing a dead socket to a view.
_default_db['CONN_MAX_AGE'] = env_int('POSTGRES_CONN_MAX_AGE', 60)
_default_db['CONN_HEALTH_CHECKS'] = env_bool('POSTGRES_CONN_HEALTH_CHECKS', True)

DATABASES = {
    # PRIMARY DATABASE — PostgreSQL
    'default': _default_db,

    # BACKUP DATABASE — MySQL
    # 'backup': {
    #     'ENGINE': 'django.db.backends.mysql',
    #     'NAME': os.getenv('MYSQL_DB', os.getenv('DB_NAME', 'united_church_school_db')),
    #     'USER': os.getenv('MYSQL_USER', os.getenv('DB_USER', 'root')),
    #     'PASSWORD': os.getenv('MYSQL_PASSWORD', os.getenv('DB_PASSWORD', '')),
    #     'HOST': os.getenv('MYSQL_HOST', os.getenv('DB_HOST', '127.0.0.1')),
    #     'PORT': os.getenv('MYSQL_PORT', os.getenv('DB_PORT', '3306')),
    #     'OPTIONS': {'charset': 'utf8mb4'},
    # },
}

# *.railway.internal resolves only inside Railway's private network; reaching it
# from anywhere else fails as a DNS error that reads like a typo.
if _db_host.endswith('.railway.internal') and not ON_RAILWAY:
    warnings.warn(
        f"Database host '{_db_host}' is a Railway *private* address and only "
        f"resolves from inside Railway. Connecting from here fails with "
        f"\"could not translate host name\". Use the public URL instead: "
        f"Railway dashboard → Postgres service → Variables → "
        f"DATABASE_PUBLIC_URL (a *.proxy.rlwy.net host on its own port).",
        RuntimeWarning,
        stacklevel=2,
    )

# The committed .env points at 127.0.0.1, so a hosted deploy that reaches this
# line has no database attached — and would fail later, mid-migration, with a
# connection-refused traceback that says nothing about the cause.
if ON_PLATFORM and not DATABASE_URL_SOURCE and _db_is_local:
    from django.core.exceptions import ImproperlyConfigured

    raise ImproperlyConfigured(
        f"Running on a hosting platform with the database host set to "
        f"'{_db_host or 'localhost'}' — that is this container's own loopback "
        f"address, where nothing is listening. Attach a managed PostgreSQL "
        f"instance and expose its connection string as DATABASE_URL (on Render: "
        f"the database's Internal Database URL, added to the web service's "
        f"environment)."
    )

# Fail fast with an actionable message instead of letting psycopg2 raise a
# cryptic "fe_sendauth: no password supplied" from deep inside a migration or
# a destructive management command. The usual root cause is a missing .env.
if not DATABASES['default'].get('PASSWORD'):
    from django.core.exceptions import ImproperlyConfigured

    if DATABASE_URL_SOURCE:
        _hint = (
            f"{DATABASE_URL_SOURCE} carries no password — copy the full "
            f"connection string, including the ':password@' part."
        )
    elif not ENV_FILE_FOUND:
        _hint = (
            f"No .env file exists at {ENV_FILE}. Restore it "
            "from git (`git checkout -- .env`) and set DATABASE_URL or "
            "POSTGRES_PASSWORD."
        )
    else:
        _hint = (
            "POSTGRES_PASSWORD is blank in your .env — set it to the database "
            "password, or set DATABASE_URL instead."
        )
    raise ImproperlyConfigured(
        f"PostgreSQL 'default' database has no password. {_hint}"
    )

DATABASE_ROUTERS = ['core.db_router.PrimaryReplicaRouter']


# ---------------------------------------------------------
# DJANGO REST FRAMEWORK & JWT
# ---------------------------------------------------------
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'dj_rest_auth.jwt_auth.JWTCookieAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'core.pagination.StandardResultsSetPagination',
    'PAGE_SIZE': 25,
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

REST_USE_JWT = True
JWT_AUTH_COOKIE = 'access'
JWT_AUTH_REFRESH_COOKIE = 'refresh'

REST_AUTH_REGISTER_SERIALIZERS = {
    'REGISTER_SERIALIZER': 'apps.accounts.serializers.CustomRegisterSerializer',
}


# ---------------------------------------------------------
# SECURITY SETTINGS FOR HTTPS
# ---------------------------------------------------------
# These used to be commented out with "enable in production" next to them, which
# meant production ran with the development settings: no TLS redirect, cookies
# sent over plain HTTP, no HSTS. Nobody remembers to uncomment a block. They are
# derived from DEBUG instead, so the secure values are what you get by default
# and dev is unchanged — each can still be overridden from the environment.
#
# SESSION_COOKIE_SECURE is deliberately NOT set here: it is defined in the
# session block above, which also refuses to keep it on under DEBUG (a Secure
# cookie over the plain-HTTP dev server silently loops every login).
SECURE_SSL_REDIRECT = env_bool('SECURE_SSL_REDIRECT', not DEBUG)
CSRF_COOKIE_SECURE = env_bool('CSRF_COOKIE_SECURE', not DEBUG)
SECURE_HSTS_SECONDS = env_int('SECURE_HSTS_SECONDS', 0 if DEBUG else 31536000)
SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool('SECURE_HSTS_INCLUDE_SUBDOMAINS', not DEBUG)
SECURE_HSTS_PRELOAD = env_bool('SECURE_HSTS_PRELOAD', not DEBUG)

# Behind a TLS-terminating proxy (nginx, Render, Railway, a load balancer)
# Django sees plain HTTP and would redirect forever unless it is told how the
# proxy reports the original scheme. Trusting this header when nothing upstream
# sets it lets a client claim its own request was HTTPS, so it stays off by
# default — but on Render and Railway the router always terminates TLS and
# always overwrites X-Forwarded-Proto, and there SECURE_SSL_REDIRECT without it
# is an infinite redirect loop on the very first request.
if env_bool('USE_X_FORWARDED_PROTO', ON_PLATFORM):
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# The session cookie must never be readable from JavaScript.
SESSION_COOKIE_HTTPONLY = True
# The CSRF cookie deliberately stays readable: theme.js, the presence ping and
# the assessment marking page all read ``document.cookie`` for csrftoken to set
# the X-CSRFToken header on fetch(). Turning this on breaks those three
# silently. It is also not much of a defence — a script that can read cookies
# can just read the token out of the rendered form. Left as an env override so
# it can be turned on once those call sites read the token from a <meta> tag.
CSRF_COOKIE_HTTPONLY = env_bool('CSRF_COOKIE_HTTPONLY', False)
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = os.getenv('SECURE_REFERRER_POLICY', 'same-origin')

# (CSRF_TRUSTED_ORIGINS is built in the NETWORK / LAN ACCESS block above, from
# the env var plus the LAN addresses plus the platform's public origin. It used
# to be reassigned here from the env var alone, which silently discarded both of
# the other two — so LAN POSTs and, on a hosted deploy, every login POST failed
# the Origin check. Do not reintroduce an assignment here.)


# ---------------------------------------------------------
# AUTHENTICATION BACKENDS
# ---------------------------------------------------------
AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',
    # AxesStandaloneBackend must come FIRST: it is what short-circuits an
    # authentication attempt for a locked-out account/IP before any real backend
    # gets to check the password.
    'django.contrib.auth.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# ---------------------------------------------------------
# BRUTE-FORCE PROTECTION (django-axes)
# ---------------------------------------------------------
# Lock on the *combination* of username and IP, so one attacker hammering an
# account cannot lock a legitimate user out from their own address, and a shared
# NAT address does not lock a whole office out because of one bad actor.
# Deliberately matched to allauth's own per-account budget
# (ACCOUNT_LOGIN_ATTEMPTS_LIMIT, default 5). Set higher and axes never fires at
# all, because allauth's throttle answers first — you keep the audit trail but
# lose the lockout and the page that explains it.
AXES_FAILURE_LIMIT = int(os.getenv('AXES_FAILURE_LIMIT') or 5)
AXES_COOLOFF_TIME = timedelta(minutes=int(os.getenv('AXES_COOLOFF_MINUTES') or 30))
AXES_LOCKOUT_PARAMETERS = [['username', 'ip_address']]
AXES_RESET_ON_SUCCESS = True
# Never write the attempted password (or the POST body) to the attempt log.
AXES_SENSITIVE_PARAMETERS = ['password', 'password1', 'password2', 'token']
AXES_ENABLE_ADMIN = True
# Behind a proxy/load balancer, trust the forwarded chain for the client IP.
AXES_IPWARE_PROXY_COUNT = int(os.getenv('AXES_PROXY_COUNT') or 0) or None
AXES_LOCKOUT_TEMPLATE = 'account/lockout.html'


# ---------------------------------------------------------
# PASSWORD VALIDATION
# ---------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ---------------------------------------------------------
# INTERNATIONALIZATION & TIME
# ---------------------------------------------------------
# Three languages, and only three: every one of them has a real catalog behind
# it (locale/<code>/LC_MESSAGES/django.po). A candidate's choice on the settings
# page is applied per request by apps.accounts.middleware.UserPreferenceMiddleware.
LANGUAGE_CODE = 'en'
LANGUAGES = [
    ('en', 'English'),
    ('fr', 'Français'),
    ('pt', 'Português'),
]
LOCALE_PATHS = [BASE_DIR / 'locale']
TIME_ZONE = 'Africa/Johannesburg'   # SAST (UTC+2), no daylight saving
USE_I18N = True
USE_TZ = True

#: Phrases the runtime translator rewrites in rendered HTML, for the screens
#: whose templates have not been marked up with ``{% translate %}`` yet. See
#: core.i18n_runtime.
RUNTIME_TRANSLATION = True


# ---------------------------------------------------------
# STATIC & MEDIA FILES
# ---------------------------------------------------------
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
# apps/myhub/static/ is picked up by AppDirectoriesFinder automatically.
STATICFILES_DIRS = [d for d in [BASE_DIR / 'static'] if d.exists()]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# User uploads (profile pictures, course covers, chat attachments) live on the
# app's own disk. Django refuses to serve MEDIA_URL once DEBUG is off, and
# WhiteNoise deliberately will not serve it either — it indexes its files once
# at start-up, so anything uploaded after boot would 404 until the next deploy.
# config/urls.py therefore serves /media/ through Django when this is on.
# It is on by default on a platform with no object store configured, because the
# alternative is a site where every avatar and course image is a broken image.
#
# NOTE this is a stop-gap, not a storage strategy: on an ephemeral container
# filesystem (Render's free tier included) every uploaded file is destroyed on
# the next deploy or restart. Set FILE_SERVER_BACKEND=s3 (or azure) with the
# credentials below to keep uploads.
SERVE_MEDIA_FROM_DJANGO = env_bool(
    'SERVE_MEDIA_FROM_DJANGO', ON_PLATFORM and os.getenv('FILE_SERVER_BACKEND', 'local') == 'local'
)

# Hard ceilings on what a request may carry, independent of the per-field
# validators in core.validators. Django buffers a request body in memory up to
# DATA_UPLOAD_MAX_MEMORY_SIZE and streams beyond it; without a cap, an upload is
# limited only by disk. The largest legitimate upload is a lecture recording or
# a SCORM package, so 250 MB is the outer bound and individual fields are much
# stricter.
DATA_UPLOAD_MAX_MEMORY_SIZE = env_int('DATA_UPLOAD_MAX_MEMORY_SIZE', 250 * 1024 * 1024)
FILE_UPLOAD_MAX_MEMORY_SIZE = env_int('FILE_UPLOAD_MAX_MEMORY_SIZE', 5 * 1024 * 1024)
# Caps the number of POST fields / GET params in one request, which is what
# stops a hash-collision DoS on form parsing. Django's default is 1000; the
# largest real form here is bulk marking, well under that.
DATA_UPLOAD_MAX_NUMBER_FIELDS = env_int('DATA_UPLOAD_MAX_NUMBER_FIELDS', 2000)


# ---------------------------------------------------------
# FILE SERVER — two storage tiers (see core.storage).
#   • default  → local disk (profile pictures, course images).
#   • files    → the "file server" for exchanged + generated files (chat/
#                discussion/feed attachments, workspace files, lesson material,
#                reports, summaries, certificates).
# For now the file server writes to the local media folder (well-organised,
# category-namespaced). Point FILE_SERVER_BACKEND at s3/azure and fill the creds
# to move it onto a real object store — no code change, no migration.
# ---------------------------------------------------------
def env_or(name, default):
    """Environment value, falling back to ``default`` when unset **or blank**.

    ``os.getenv(name, default)`` only falls back when the variable is *absent*.
    A declared-but-empty ``FILES_URL=`` in .env therefore resolved to ``''``,
    which silently stripped the ``/media/`` prefix off every file-server URL and
    rooted uploads at the project directory instead of ``media/``. Blank is
    never a meaningful value for these, so it is treated as "not set".
    """
    value = os.getenv(name)
    return value if (value or '').strip() else default


FILE_SERVER_BACKEND = env_or('FILE_SERVER_BACKEND', 'local')      # local | s3 | azure
FILES_ROOT = env_or('FILES_ROOT', str(MEDIA_ROOT))                # local backend root
FILES_URL = env_or('FILES_URL', MEDIA_URL)                        # local backend public URL


def _files_storage_backend():
    if FILE_SERVER_BACKEND == 's3':
        return {
            'BACKEND': 'storages.backends.s3.S3Storage',
            'OPTIONS': {
                'bucket_name': os.getenv('AWS_STORAGE_BUCKET_NAME', ''),
                'region_name': os.getenv('AWS_S3_REGION_NAME', ''),
                'endpoint_url': os.getenv('AWS_S3_ENDPOINT_URL', '') or None,
                'access_key': os.getenv('AWS_ACCESS_KEY_ID', ''),
                'secret_key': os.getenv('AWS_SECRET_ACCESS_KEY', ''),
                'location': os.getenv('FILES_PREFIX', 'files'),
                'default_acl': os.getenv('AWS_DEFAULT_ACL', 'private'),
                'querystring_auth': True,
            },
        }
    if FILE_SERVER_BACKEND == 'azure':
        return {
            'BACKEND': 'storages.backends.azure_storage.AzureStorage',
            'OPTIONS': {
                'account_name': os.getenv('AZURE_ACCOUNT_NAME', ''),
                'account_key': os.getenv('AZURE_ACCOUNT_KEY', ''),
                'azure_container': os.getenv('AZURE_CONTAINER', 'files'),
                'expiration_secs': int(os.getenv('AZURE_URL_EXPIRATION_SECS', '3600')),
            },
        }
    # Default: local disk (structured under FILES_ROOT).
    return {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
        'OPTIONS': {'location': FILES_ROOT, 'base_url': FILES_URL},
    }


# WhiteNoise's compressed backend gzips/brotlis every static file at
# collectstatic time and serves the pre-compressed copy. The *Manifest* variant
# would also hash filenames for far-future caching, but it hard-fails
# collectstatic on any {% static %} reference that does not resolve — a broken
# deploy in exchange for cache headers — so the plain compressed backend is the
# default and the manifest one is opt-in once the static tree is known clean.
_STATICFILES_BACKEND = (
    'whitenoise.storage.CompressedManifestStaticFilesStorage'
    if env_bool('STATIC_MANIFEST', False)
    else 'whitenoise.storage.CompressedStaticFilesStorage'
)

STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': _STATICFILES_BACKEND},
    'files': _files_storage_backend(),
}

# Serve /static/ from memory-mapped files with long cache headers; also let
# WhiteNoise answer requests for files that only exist in STATICFILES_DIRS
# during development so `runserver --nostatic` and gunicorn behave alike.
WHITENOISE_AUTOREFRESH = DEBUG
WHITENOISE_USE_FINDERS = DEBUG


# ---------------------------------------------------------
# DEFAULT MODEL PRIMARY KEY TYPE
# ---------------------------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ---------------------------------------------------------
# CUSTOM USER MODEL
# ---------------------------------------------------------
# Uses the default Django User + apps.accounts.Person profile.
# AUTH_USER_MODEL = 'accounts.User'


# ---------------------------------------------------------
# DJANGO ALLAUTH CONFIGURATION
# ---------------------------------------------------------
# The platform is e-mail-only: users sign up and sign in with their e-mail
# address — there is no username field on any form. Django's default User
# model still has a (required, unique) ``username`` column, so allauth
# auto-generates a value for it from the e-mail; the custom HTML pages
# (apps/myhub/views.py) set ``username = email`` directly. Either way it is an
# internal detail the user never sees.
SITE_ID = 1

ACCOUNT_USER_MODEL_USERNAME_FIELD = 'username'  # column exists; allauth fills it for us
ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*']  # no 'username' → not asked
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_LOGIN_METHODS = {'email'}

# Keep `username` mirroring the e-mail (allauth would otherwise derive it from
# the local part) and apply the same rule to Google sign-ups.
ACCOUNT_ADAPTER = 'apps.accounts.adapters.HubAccountAdapter'
SOCIALACCOUNT_ADAPTER = 'apps.accounts.adapters.HubSocialAccountAdapter'

# Choosing a new password from a reset link must not re-set the current one —
# allauth allows that by default (see the form's docstring).
ACCOUNT_FORMS = {
    'reset_password_from_key': 'apps.accounts.forms.UCSResetPasswordKeyForm',
}

# E-mail verification is MANDATORY: a new account can't be used until the user
# clicks the confirmation link e-mailed to them (see apps/myhub/views.py
# page_register / page_login, which enforce this on the custom auth pages).
ACCOUNT_EMAIL_VERIFICATION = os.getenv('ACCOUNT_EMAIL_VERIFICATION', 'mandatory')
# Confirm the e-mail as soon as the link is opened (no extra "confirm" click).
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
# After confirming, send the user to the login page (not auto-logged-in).
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = False
# Subject-line prefix for allauth's auth e-mails (the branded HTML bodies live
# in templates/account/email/).
ACCOUNT_EMAIL_SUBJECT_PREFIX = os.getenv('ACCOUNT_EMAIL_SUBJECT_PREFIX', '')

LOGIN_URL = '/myhub/page-login/'
LOGIN_REDIRECT_URL = '/myhub/'
LOGOUT_REDIRECT_URL = '/myhub/page-login/'

# Where the e-mail-confirmation link lands the visitor afterwards — the login
# page, in both cases (anonymous click from the e-mail, or already logged in).
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = LOGIN_URL
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = LOGIN_URL


# ---------------------------------------------------------
# SOCIAL LOGIN — Google (django-allauth)
# ---------------------------------------------------------
# "Continue with Google" buttons live on the login/register pages. To enable a
# real OAuth round-trip:
#   1. Create OAuth 2.0 credentials at https://console.cloud.google.com/apis/credentials
#      Authorised redirect URI: <your-domain>/accounts/google/login/callback/
#   2. Set GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_SECRET in the environment
#      (or add a SocialApp in the Django admin bound to SITE_ID = 1).
# Starting an OAuth login straight from the button (no interstitial page).
SOCIALACCOUNT_LOGIN_ON_GET = True
# A Google sign-in proves the e-mail, so skip allauth's verification for it.
SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'
SOCIALACCOUNT_EMAIL_REQUIRED = True


# ---------------------------------------------------------
# MULTI-FACTOR AUTHENTICATION (allauth.mfa)
# ---------------------------------------------------------
# TOTP (any authenticator app) plus one-time recovery codes. Opt-in for
# everyone by default; set MFA_REQUIRED_FOR_STAFF=true to make it compulsory for
# the accounts that can change other people's data.
MFA_SUPPORTED_TYPES = ['totp', 'recovery_codes']
MFA_TOTP_ISSUER = os.getenv('MFA_TOTP_ISSUER', '') or 'United Church School'
MFA_RECOVERY_CODE_COUNT = 10
# Re-enter the password before adding or removing a factor, so a hijacked
# session cannot quietly swap the second factor for the attacker's own.
MFA_PASSKEY_LOGIN_ENABLED = False
ACCOUNT_REAUTHENTICATION_REQUIRED = env_bool('ACCOUNT_REAUTHENTICATION_REQUIRED', True)
MFA_REQUIRED_FOR_STAFF = env_bool('MFA_REQUIRED_FOR_STAFF', False)

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'OAUTH_PKCE_ENABLED': True,
        'APP': {
            'client_id': os.getenv('GOOGLE_OAUTH_CLIENT_ID', ''),
            'secret': os.getenv('GOOGLE_OAUTH_SECRET', ''),
            'key': '',
        },
    },
}


# ---------------------------------------------------------
# Math CAPTCHA on the sign-up form (django-simple-captcha)
# ---------------------------------------------------------
# A self-hosted arithmetic challenge ("3 + 4 = ?") rendered as a small image —
# no keys, no external service, no Google. The image and refresh endpoints are
# wired at /captcha/ (captcha.urls in config/urls.py); the field lives on
# apps.accounts.forms.UCSSignupForm. Run `migrate captcha` once to create the
# CaptchaStore table.
# Simple single-digit addition ("3 + 4 = ?"). We use our own challenge rather
# than captcha.helpers.math_challenge because that one picks the operator at
# random and only uses CAPTCHA_MATH_CHALLENGE_OPERATOR as multiplication's
# *display* symbol — which made multiplication problems render with a '+' sign
# but keep the multiplied answer, so correct answers were rejected.
CAPTCHA_CHALLENGE_FUNCT = 'apps.accounts.captcha_challenges.add_challenge'
CAPTCHA_LETTER_ROTATION = None             # keep the digits upright and legible
CAPTCHA_TIMEOUT = 10                        # minutes a challenge stays valid
# CAPTCHA_TEST_MODE is left at its default (False); the test suite overrides it
# to True and answers with the literal 'PASSED'.


# ---------------------------------------------------------
# CACHE
# Uses Redis when USE_REDIS=true; otherwise local-memory so the
# project still runs in environments without a Redis server.
# ---------------------------------------------------------
if env_bool('USE_REDIS', False):
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/1'),
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                # Treat a Redis outage as a cache miss rather than an exception.
                # allauth reads the cache on the sign-up / login path (rate
                # limiting), so without this a dead Redis turns every auth
                # request into a 500 — the cache is an optimisation, it must
                # never be able to take authentication down with it.
                'IGNORE_EXCEPTIONS': True,
            },
        }
    }
    # Log the connection errors that IGNORE_EXCEPTIONS swallows, so a Redis
    # outage is visible rather than silently degrading performance.
    DJANGO_REDIS_LOG_IGNORED_EXCEPTIONS = True
else:
    CACHES = {
        'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'},
    }


# ---------------------------------------------------------
# EMAIL
# Console backend by default (prints e-mails to the runserver console).
# Set EMAIL_BACKEND to SMTP + the EMAIL_HOST_* vars in .env for real delivery.
# All branded e-mails (notifications, announcements, allauth auth e-mails) are
# rendered via apps.communication.emails / templates/communication/email/.
# ---------------------------------------------------------
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST', 'localhost')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '25'))
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
# App passwords are shown grouped as "xxxx xxxx xxxx xxxx" but authenticate without
# the spaces — strip them so either form in .env works.
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '').replace(' ', '')
EMAIL_USE_TLS = env_bool('EMAIL_USE_TLS', False)
EMAIL_USE_SSL = env_bool('EMAIL_USE_SSL', False)
# Don't let a slow/unreachable SMTP server hang a request (auth e-mails send inline).
EMAIL_TIMEOUT = int(os.getenv('EMAIL_TIMEOUT', '20'))
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'United Church School <uchs@unitedcs.co.za>')
SERVER_EMAIL = os.getenv('SERVER_EMAIL', DEFAULT_FROM_EMAIL)

# Absolute base URL of this site (used to build links inside e-mails).
#
# The platform's own hostname is authoritative when it is hosting us: the
# committed .env carries a placeholder (https://example.com), and every
# verification link, password-reset link and invoice pay-link is built from
# this. Getting it wrong does not fail loudly — it sends users a link to
# somebody else's domain. An explicit SITE_URL in the dashboard still wins, for
# the custom-domain case.
if platform_decides('SITE_URL') and RENDER_EXTERNAL_NETLOC:
    SITE_URL = f'https://{RENDER_EXTERNAL_NETLOC}'
else:
    SITE_URL = os.getenv('SITE_URL', 'http://127.0.0.1:8000')


# ---------------------------------------------------------
# PAYFAST — South African payment gateway (cart checkout + invoices)
# Sandbox-by-default. With NO merchant credentials, sandbox mode SIMULATES a
# successful payment locally (PayFast's shared public sandbox merchant now
# rejects unauthenticated signatures and its ITN can't reach localhost), so the
# checkout flow stays testable end to end. To exercise the real PayFast redirect,
# create a free sandbox account at https://sandbox.payfast.co.za and set the three
# vars below (PAYFAST_PASSPHRASE must match the one set in that dashboard). Set
# PAYFAST_SANDBOX=False with live keys to go live (notify_url must be publicly
# reachable in production).
# ---------------------------------------------------------
PAYFAST_SANDBOX = env_bool('PAYFAST_SANDBOX', True)
PAYFAST_MERCHANT_ID = os.getenv('PAYFAST_MERCHANT_ID', '')
PAYFAST_MERCHANT_KEY = os.getenv('PAYFAST_MERCHANT_KEY', '')
PAYFAST_PASSPHRASE = os.getenv('PAYFAST_PASSPHRASE', '')

# Whether this deployment takes online payments at all.
#
# apps.finance.checks refuses to start a production build that is either wired
# to PayFast's sandbox or live with no merchant credentials — correctly, because
# both states take money that never arrives. But that leaves no way to deploy
# the platform for the things it does besides selling: teaching, marking,
# reporting. This flag is that third state, stated explicitly rather than faked
# with placeholder credentials: the money path is switched off, the pay page
# says so instead of building a checkout, and the guards stand down because
# there is no longer a money path to guard.
#
# It defaults to off in production precisely because the alternative default —
# on, with whatever half-configuration the environment happens to carry — is the
# one that silently loses payments. Set PAYMENTS_ENABLED=true once PayFast is
# configured for real; the guards then apply in full.
PAYMENTS_ENABLED = env_bool('PAYMENTS_ENABLED', DEBUG or not ON_PLATFORM)

# VAT. The business is VAT-registered and its shop prices INCLUDE VAT, so an
# invoice extracts the VAT from its total rather than adding it on top — what the
# buyer saw in the shop is what they pay. New invoices capture the rate when they
# are created (a tax invoice must not change later); invoices raised before this
# was switched on keep a rate of 0 and the totals they were issued with.
# The VAT number is printed on every tax invoice: set VAT_NUMBER in .env.
VAT_REGISTERED = env_bool('VAT_REGISTERED', False)
VAT_RATE = os.getenv('VAT_RATE', '15')
VAT_NUMBER = os.getenv('VAT_NUMBER', '').strip()

# Delivery (study-materials store). The Courier Guy runs on Ship Logic; with no
# API key the shop quotes the flat rates below and staff enter tracking numbers
# by hand. Add COURIER_GUY_API_KEY (from the TCG portal) to switch to live
# quotes, locker search, one-click booking, waybills and tracking.
COURIER_GUY_API_KEY = os.getenv('COURIER_GUY_API_KEY', '').strip()
COURIER_GUY_BASE_URL = os.getenv('COURIER_GUY_BASE_URL',
                                 'https://api.portal.thecourierguy.co.za/v2/').strip()
SHOP_DELIVERY_DOOR_FEE = os.getenv('SHOP_DELIVERY_DOOR_FEE', '120')
SHOP_DELIVERY_LOCKER_FEE = os.getenv('SHOP_DELIVERY_LOCKER_FEE', '70')
SHOP_FREE_DELIVERY_OVER = os.getenv('SHOP_FREE_DELIVERY_OVER', '1500')   # 0 = never free
# Where the buyer's "Track parcel" link goes; {ref} is the tracking reference.
COURIER_TRACKING_URL = os.getenv('COURIER_TRACKING_URL',
                                 'https://www.thecourierguy.co.za/tracking?ref={ref}')
# Where parcels are collected from. The courier needs a street address, not the
# postal lines on the invoice — set these to the packing location.
SHOP_COLLECTION = {
    'company': os.getenv('SHOP_COLLECTION_COMPANY', 'United Church School'),
    'contact': os.getenv('SHOP_COLLECTION_CONTACT', 'UCS School Office'),
    'phone': os.getenv('SHOP_COLLECTION_PHONE', '+27116484727'),
    'email': os.getenv('SHOP_COLLECTION_EMAIL', 'uchs@unitedcs.co.za'),
    'street_address': os.getenv('SHOP_COLLECTION_STREET', '44 Frances Street'),
    'suburb': os.getenv('SHOP_COLLECTION_SUBURB', 'Yeoville'),
    'city': os.getenv('SHOP_COLLECTION_CITY', 'Johannesburg'),
    'zone': os.getenv('SHOP_COLLECTION_PROVINCE', 'GP'),
    'code': os.getenv('SHOP_COLLECTION_POSTAL_CODE', '2198'),
}


# ---------------------------------------------------------
# ENROLLMENT
# ---------------------------------------------------------
# How a student is placed into a course after their enrolment invoice is paid:
#   auto   = the moment payment settles, they are enrolled into the course + all
#            its subjects (and, via signals, the course/subject chat groups),
#            granted access to existing material and a "new member" note is
#            posted to the group.
#   manual = payment is recorded, but an admin reviews and enrols them.
ENROLLMENT_MODE = os.getenv('ENROLLMENT_MODE', 'manual').strip().lower()
if ENROLLMENT_MODE not in ('auto', 'manual'):
    ENROLLMENT_MODE = 'manual'

# School fees are paid per grade, per calendar month, in advance. A grade's
# subjects lock this many days into a month that has not been paid.
FEES_GRACE_DAYS = env_int('FEES_GRACE_DAYS', 7)


# ---------------------------------------------------------
# LIVE CLASSROOM — Microsoft Teams (primary) / Jitsi (fallback)
# ---------------------------------------------------------
# The live classroom is Microsoft Teams, driven from the LMS via the Microsoft
# Graph API (app-only / client credentials) — see docs/TEAMS_INTEGRATION.md.
# `MEETING_PROVIDER` selects the engine; everything stays DORMANT (and falls back
# to the in-app page) until the Graph credentials below are set.
MEETING_PROVIDER = os.getenv('MEETING_PROVIDER', 'teams')   # 'teams' | 'jitsi'

MS_TEAMS_ENABLED = env_bool('MS_TEAMS_ENABLED', False)
MS_GRAPH_TENANT_ID = os.getenv('MS_GRAPH_TENANT_ID', '')
MS_GRAPH_CLIENT_ID = os.getenv('MS_GRAPH_CLIENT_ID', '')
MS_GRAPH_CLIENT_SECRET = os.getenv('MS_GRAPH_CLIENT_SECRET', '')
# Fallback organizer UPN when an educator has no Microsoft UPN on file.
MS_GRAPH_DEFAULT_ORGANIZER = os.getenv('MS_GRAPH_DEFAULT_ORGANIZER', '')
MS_GRAPH_AUTHORITY = os.getenv(
    'MS_GRAPH_AUTHORITY', 'https://login.microsoftonline.com')
MS_GRAPH_BASE = os.getenv('MS_GRAPH_BASE', 'https://graph.microsoft.com/v1.0')

# ---------------------------------------------------------
# LIVE SESSIONS — the calendar, the recording pipeline, YouTube
# ---------------------------------------------------------
# Behaviour (auto-record, folder root, reminder leads, YouTube on/off, …) is NOT
# here: it lives in the admin-editable `livesessions.LiveSessionSettings` row, so
# switching recording off or renaming the OneDrive root never needs a deploy.
# Only credentials and machine-level defaults belong in the environment.
#
# YouTube is how a *recording* reaches a student: they join Teams anonymously and
# have no Microsoft account, so an unlisted YouTube video is the one player that
# reliably works for them. It stays DORMANT until all three values below are set
# AND YouTube is switched on in the settings row — until then the platform serves
# the OneDrive share link instead.
#
# Get these by creating an OAuth "Desktop app" client in a Google Cloud project
# with the YouTube Data API v3 enabled, then exchanging a one-time consent code
# for a refresh token against the youtube.upload scope. Mind the quota: an upload
# costs 1,600 units of a default 10,000/day allowance.
YOUTUBE_CLIENT_ID = os.getenv('YOUTUBE_CLIENT_ID', '')
YOUTUBE_CLIENT_SECRET = os.getenv('YOUTUBE_CLIENT_SECRET', '')
YOUTUBE_REFRESH_TOKEN = os.getenv('YOUTUBE_REFRESH_TOKEN', '')

# --- Reading the channel (importing existing playlists / past-session videos) ---
# To *scan* your channel and link existing videos to modules/cohorts, the app also
# reads playlists and videos. Two ways, tried in this order:
#   1. The OAuth token above — if you mint YOUTUBE_REFRESH_TOKEN with BOTH the
#      youtube.upload AND youtube.readonly scopes, the owner client can read even
#      UNLISTED videos/playlists (what session recordings usually are).
#   2. YOUTUBE_API_KEY — a public Data-API key; reads PUBLIC content only (unlisted
#      videos won't come back). Handy if you don't want to widen the OAuth scopes.
# YOUTUBE_CHANNEL_ID is your channel's UC… id; the scanner lists that channel's
# uploads and playlists.
YOUTUBE_CHANNEL_ID = os.getenv('YOUTUBE_CHANNEL_ID', '')
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY', '')

# Optional: a TrueType font for the generated session thumbnails. Left blank, the
# renderer looks for the usual system faces and falls back to Pillow's built-in.
SESSION_THUMBNAIL_FONT = os.getenv('SESSION_THUMBNAIL_FONT', '')

# ---------------------------------------------------------
# WhatsApp — invoice delivery
# ---------------------------------------------------------
# The platform's second channel out, shared by notification copies (opt-in per
# user under Settings > Notifications) and the registration invoice PDF. The
# client is core/whatsapp.py. Like Teams above, this stays
# DORMANT until credentials are set: with WHATSAPP_ENABLED off nothing is sent
# and nothing fails — the invoice still goes by e-mail and sits in the student's
# account. Credentials come from Meta's WhatsApp Business Cloud API.
WHATSAPP_ENABLED = env_bool('WHATSAPP_ENABLED', False)
WHATSAPP_PHONE_NUMBER_ID = os.getenv('WHATSAPP_PHONE_NUMBER_ID', '')
WHATSAPP_ACCESS_TOKEN = os.getenv('WHATSAPP_ACCESS_TOKEN', '')
WHATSAPP_API_VERSION = os.getenv('WHATSAPP_API_VERSION', 'v21.0')
# Meta requires an approved template for business-initiated messages outside the
# 24-hour customer-service window. Name one here and core.whatsapp uses it for
# notification copies; leave it blank and they go as free-form text.
WHATSAPP_TEMPLATE_NAME = os.getenv('WHATSAPP_TEMPLATE_NAME', '')
WHATSAPP_TEMPLATE_LANG = os.getenv('WHATSAPP_TEMPLATE_LANG', 'en')
# Inbound: the bot's webhook at /communication/whatsapp/webhook/.
# VERIFY_TOKEN is any string you also type into Meta's webhook setup; APP_SECRET
# is the Meta app secret and is what proves a POST really came from Meta. With no
# APP_SECRET the webhook refuses every request — an unsigned webhook would be a
# stranger's remote control over student data.
WHATSAPP_VERIFY_TOKEN = os.getenv('WHATSAPP_VERIFY_TOKEN', '')
WHATSAPP_APP_SECRET = os.getenv('WHATSAPP_APP_SECRET', '')
# Dialling code assumed when a stored number has no country code (082… → +2782…).
DEFAULT_DIAL_CODE = os.getenv('DEFAULT_DIAL_CODE', '27')

# Jitsi kept only as the fallback engine (MEETING_PROVIDER=jitsi or Teams off).
JITSI_BASE_URL = os.getenv('JITSI_BASE_URL', 'https://meet.jit.si')


# ---------------------------------------------------------
# AI ASSISTANT (CrewAI) — the floating "ask about this page" widget
# Optional & off until configured. CrewAI core is MIT licensed; the LLM is
# pluggable (a local Ollama model keeps it free + self-hosted). If `crewai`
# isn't installed or no model is set, the widget degrades to a helpful message.
#   AI_LLM_MODEL examples: "ollama/llama3", "groq/llama-3.1-8b-instant", "gpt-4o-mini"
# ---------------------------------------------------------
AI_ASSISTANT_ENABLED = env_bool('AI_ASSISTANT_ENABLED', False)
AI_LLM_MODEL = os.getenv('AI_LLM_MODEL', '')
AI_LLM_API_BASE = os.getenv('AI_LLM_API_BASE', '')   # e.g. http://localhost:11434 for Ollama
AI_LLM_API_KEY = os.getenv('AI_LLM_API_KEY', '')     # for hosted providers

# Local speech-to-text (faster-whisper) for the media pipeline (audio/video → text).
WHISPER_MODEL = os.getenv('WHISPER_MODEL', 'base')
WHISPER_DEVICE = os.getenv('WHISPER_DEVICE', 'cpu')
WHISPER_COMPUTE_TYPE = os.getenv('WHISPER_COMPUTE_TYPE', 'int8')

# ---------------------------------------------------------
# ADMIN AI (layer two) — the advanced, paid Claude model for admins/staff only.
# Powers the full-screen "Claude-style" chat (/assistant/chat/) for deep
# institutional analytics. Optional & off until configured; requires the
# `anthropic` SDK + an API key. ADMIN_AI_MODEL maps to the advanced model
# (e.g. claude-opus-4-8). Token usage is recorded per message.
# ---------------------------------------------------------
ADMIN_AI_ENABLED = env_bool('ADMIN_AI_ENABLED', False)
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
ADMIN_AI_MODEL = os.getenv('ADMIN_AI_MODEL', 'claude-opus-4-8')

# Keep CrewAI fully local: opt out of its telemetry (also honoured via .env).
os.environ.setdefault('CREWAI_TELEMETRY_OPT_OUT',
                      os.getenv('CREWAI_TELEMETRY_OPT_OUT', 'true'))
os.environ.setdefault('OTEL_SDK_DISABLED', os.getenv('OTEL_SDK_DISABLED', 'true'))


# (CELERY / Redis broker removed — it only ran the retired CrewAI media
#  pipeline. Chat is HTTP-polled and files are plain Django storage, so no task
#  queue is needed. Redis remains an OPTIONAL cache only, via USE_REDIS above.)


# ---------------------------------------------------------
# DJANGO GUARDIAN SETTINGS
# ---------------------------------------------------------
ANONYMOUS_USER_NAME = None


# ---------------------------------------------------------
# MESSAGES  (map Django's "error" level to Bootstrap's "danger")
# ---------------------------------------------------------
from django.contrib.messages import constants as message_constants  # noqa: E402

MESSAGE_TAGS = {message_constants.ERROR: 'danger'}


# ---------------------------------------------------------
# LOGGING
# ---------------------------------------------------------
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'user_activity.log',
        },
        # Turns every WARNING-and-above log record into a catalogued, deduplicated
        # row in the error log — which is how the log covers the *whole* codebase
        # rather than only the places that have been tagged with a code by hand.
        # See apps/diagnostics/handlers.py and docs/ERROR_CODES.md.
        'errorlog': {
            'class': 'apps.diagnostics.handlers.ErrorLogHandler',
            'level': 'WARNING',
        },
    },
    'loggers': {
        'accounts': {
            'handlers': ['console', 'file', 'errorlog'],
            'level': 'INFO',
            'propagate': False,
        },
        # Every apps.* logger: console for the developer, errorlog for triage.
        'apps': {
            'handlers': ['console', 'errorlog'],
            'level': 'INFO',
            'propagate': False,
        },
        # Django's own request/security warnings are worth catalogued too.
        'django.request': {
            'handlers': ['console', 'errorlog'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['console', 'errorlog'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}


# ---------------------------------------------------------
# ERROR REPORTING (Sentry) — OPTIONAL, dormant until SENTRY_DSN is set
# ---------------------------------------------------------
# LOGGING above records what happened on *this* server; Sentry aggregates
# unhandled exceptions across every server with a stack trace, the request that
# caused it and how often it recurs. It stays completely off without a DSN, so
# development is unaffected.
SENTRY_DSN = os.getenv('SENTRY_DSN', '').strip()
if SENTRY_DSN:  # pragma: no cover - only runs where a DSN is configured
    try:
        import sentry_sdk
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            environment=os.getenv('SENTRY_ENVIRONMENT') or ('development' if DEBUG else 'production'),
            release=os.getenv('SENTRY_RELEASE') or None,
            # Sampled, not exhaustive — full tracing on a busy LMS is expensive
            # and rarely more informative than a representative sample.
            traces_sample_rate=float(os.getenv('SENTRY_TRACES_SAMPLE_RATE') or 0.05),
            # Never ship personal data to a third party: no request bodies, no
            # cookies, no logged-in user identity, unless explicitly opted in.
            send_default_pii=env_bool('SENTRY_SEND_PII', False),
        )
    except Exception:
        warnings.warn('SENTRY_DSN is set but sentry-sdk could not be initialised.', stacklevel=2)


# ---------------------------------------------------------
# WARNING FILTERS
# ---------------------------------------------------------
warnings.filterwarnings('ignore', message='.*NotOpenSSLWarning.*', category=Warning)
warnings.filterwarnings('ignore', category=UserWarning)
