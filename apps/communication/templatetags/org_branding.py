"""Template tags for reaching the central string catalog from *any* template —
including ones rendered without a request (e-mails, allauth's auth e-mails),
where the ``core.context_processors.branding`` processor doesn't run.

Usage::

    {% load org_branding %}
    {% org_brand as brand %}{{ brand.name }}
    {% org_string "messages.welcome_back" "Welcome!" as msg %}
"""

from django import template
from django.conf import settings
from django.templatetags.static import static

from core.branding import get as _get
from core.branding import strings as _strings

register = template.Library()


@register.simple_tag
def email_asset(path):
    """Absolute URL for a static asset used in an e-mail.

    E-mail clients can't load relative or ``127.0.0.1`` URLs, so image ``src``
    must be absolute against the public site. Combines ``SITE_URL`` with the
    static URL — and works without a request (allauth renders e-mails that way).

        {% load org_branding %}
        <img src="{% email_asset 'email/animated_header.gif' %}">
    """
    base = (getattr(settings, 'SITE_URL', '') or '').rstrip('/')
    return f'{base}{static(path)}'


@register.filter
def greeting_name(user, fallback='there'):
    """A friendly first name for an e-mail greeting — never an e-mail address.

    ``User.get_username`` is the address on this deployment (login is by
    e-mail), so the usual ``get_full_name|default:get_username`` chain greets
    people as "Hi someone@gmail.com". The real name lives on the profile
    (:class:`apps.accounts.models.Person`), which is filled in during
    registration; ``auth.User.first_name`` is often blank. Order of preference:
    profile first name → ``User.first_name`` → first word of the full name →
    ``fallback``.

        {% load org_branding %}
        Hi {{ invoice.customer|greeting_name }},
    """
    if not user:
        return fallback
    profile = getattr(user, 'profile', None)
    candidates = [
        getattr(profile, 'first_name', '') or '',
        getattr(user, 'first_name', '') or '',
    ]
    full = getattr(user, 'get_full_name', None)
    if callable(full):
        try:
            candidates.append(full() or '')
        except Exception:  # pragma: no cover — defensive, e-mails must never fail
            pass
    for name in candidates:
        name = str(name).strip()
        # Guard against profiles seeded with the address as the "name".
        if name and '@' not in name:
            return name.split()[0]
    return fallback


@register.simple_tag
def org_brand():
    """Return the ``brand`` section of ``.strings.json`` (a dict)."""
    return _strings().get('brand', {})


@register.simple_tag
def org_strings():
    """Return the whole string catalog (a dict)."""
    return _strings()


@register.simple_tag
def org_string(path, default=''):
    """Return the catalog value at dotted ``path`` (or ``default``)."""
    return _get(path, default)


@register.simple_tag
def static_or(*paths):
    """URL of the first static file that actually exists, of the ones given.

        {% static_or 'images/auth/login.jpg' 'soft-ui/img/curved-images/curved6.jpg' %}

    Used for artwork a deployment is expected to replace with its own: the page
    shows the house image until the real one is dropped in, rather than a broken
    background and a blank panel. Falls back to the last path given so the tag
    always returns something usable.
    """
    from django.contrib.staticfiles import finders

    for path in paths:
        if not path:
            continue
        try:
            if finders.find(path):
                return static(path)
        except Exception:
            continue
    return static(paths[-1]) if paths else ''
