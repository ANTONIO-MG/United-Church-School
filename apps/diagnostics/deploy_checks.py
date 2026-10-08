"""Deployment guards: refuse to boot in a configuration that is unsafe to serve.

The settings that matter for a public deployment — TLS redirect, secure
cookies, HSTS, the Host-header allow-list, CORS — now default to the secure
value whenever ``DEBUG`` is off, so the ordinary path is already correct. These
checks catch the case where somebody has explicitly overridden one back to its
development value in the environment, which is the only way left to end up
serving a production site with development security.

They stand down under ``DEBUG`` and under the test runner (which forces
``DEBUG=False``); see ``settings.TESTING``.

Registered in :meth:`apps.diagnostics.apps.DiagnosticsConfig.ready`. Lives here
rather than in ``config/`` because ``config`` is not an installed app and so has
no ``ready()`` to register from.
"""

from django.conf import settings
from django.core.checks import Error, Tags, Warning as CheckWarning, register


def _not_production():
    return bool(settings.DEBUG or getattr(settings, 'TESTING', False))


@register(Tags.security)
def allowed_hosts_is_not_a_wildcard(app_configs, **kwargs):
    """``ALLOWED_HOSTS=['*']`` accepts any Host header.

    Django uses the Host header to build absolute URLs — including the ones in
    password-reset and invoice pay-link e-mails. With a wildcard, a request
    carrying ``Host: attacker.example`` mints a reset link pointing at the
    attacker's domain, and any caching layer in front will happily store it.
    """
    if _not_production():
        return []
    hosts = list(getattr(settings, 'ALLOWED_HOSTS', []) or [])
    if not hosts:
        return [Error(
            'ALLOWED_HOSTS is empty with DEBUG=False — every request will 400.',
            hint='Set ALLOWED_HOSTS to a comma-separated list of the hostnames '
                 'this site is served on, e.g. '
                 'ALLOWED_HOSTS=ucs.org.za,www.ucs.org.za',
            id='deploy.E001',
        )]
    if '*' in hosts:
        return [Error(
            'ALLOWED_HOSTS contains "*" with DEBUG=False.',
            hint='A wildcard accepts any Host header, so password-reset and '
                 'pay-link e-mails can be made to point at another domain. '
                 'Name the hostnames explicitly.',
            id='deploy.E002',
        )]
    return []


@register(Tags.security)
def cookies_and_transport_are_secure(app_configs, **kwargs):
    """Session/CSRF cookies and the TLS redirect must be on in production."""
    if _not_production():
        return []
    problems = []
    for name, cid in (('SESSION_COOKIE_SECURE', 'deploy.E003'),
                      ('CSRF_COOKIE_SECURE', 'deploy.E004'),
                      ('SECURE_SSL_REDIRECT', 'deploy.E005')):
        if not getattr(settings, name, False):
            problems.append(Error(
                f'{name} is False with DEBUG=False.',
                hint=f'It defaults to True when DEBUG is off, so something has '
                     f'set {name} in the environment. Cookies and credentials '
                     f'would travel over plain HTTP. Remove the override.',
                id=cid,
            ))
    if not getattr(settings, 'SECURE_HSTS_SECONDS', 0):
        problems.append(CheckWarning(
            'SECURE_HSTS_SECONDS is 0 with DEBUG=False.',
            hint='Without HSTS a first visit over http:// can be intercepted '
                 'before the redirect to https:// happens. The default is one '
                 'year when DEBUG is off; something has overridden it.',
            id='deploy.W001',
        ))
    return problems


@register(Tags.security)
def cors_is_not_wide_open(app_configs, **kwargs):
    """``CORS_ALLOW_ALL_ORIGINS`` lets any site script the API."""
    if _not_production():
        return []
    if not getattr(settings, 'CORS_ALLOW_ALL_ORIGINS', False):
        return []
    return [Error(
        'CORS_ALLOW_ALL_ORIGINS is True with DEBUG=False.',
        hint='Any website could then call /api/ in a signed-in user\'s browser. '
             'List the origins that need it in CORS_ALLOWED_ORIGINS instead.',
        id='deploy.E006',
    )]


@register(Tags.security)
def secret_key_is_not_the_shipped_default(app_configs, **kwargs):
    """The fallback SECRET_KEY is in the source tree — and it signs the JWTs."""
    if _not_production():
        return []
    key = getattr(settings, 'SECRET_KEY', '') or ''
    if key.startswith('django-insecure-'):
        return [Error(
            'SECRET_KEY is still the development fallback from settings.py.',
            hint='It is committed to the repository, and it signs session '
                 'cookies, password-reset tokens and JWTs — anyone with the '
                 'source can forge all three. Set SECRET_KEY in the '
                 'environment to a fresh random value.',
            id='deploy.E007',
        )]
    return []
