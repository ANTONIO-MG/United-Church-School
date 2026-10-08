"""Small project-wide helper functions shared across the apps."""

import logging

logger = logging.getLogger(__name__)

#: What ``SITE_URL`` falls back to when nothing is configured. Only ever right
#: on a developer's own machine.
LOCAL_SITE_URL = 'http://127.0.0.1:8000'


def site_base():
    """The public base URL of this installation, with no trailing slash.

    Every outbound link the platform sends — invoice pay-links, PayFast return
    and ITN callbacks, e-mail buttons, WhatsApp messages — is built on this. It
    used to be copied into four modules, which meant four chances to have a
    different idea of where the site lives; PayFast in particular signs the
    return URL, so a mismatch there is a payment that never confirms.

    Getting it wrong in production is quiet and expensive: mail goes out with
    ``127.0.0.1`` links that work fine for whoever tested them and for nobody
    else. So when the site is not in DEBUG and ``SITE_URL`` is still the local
    default, that is logged as an error rather than shrugged off.
    """
    from django.conf import settings

    raw = (getattr(settings, 'SITE_URL', '') or '').strip().rstrip('/')
    if not raw:
        raw = LOCAL_SITE_URL
    if not getattr(settings, 'DEBUG', False) and raw == LOCAL_SITE_URL:
        logger.error(
            'SITE_URL is still %s with DEBUG off — every e-mailed link and every '
            'PayFast callback will point at localhost. Set SITE_URL in .env.',
            LOCAL_SITE_URL)
    return raw


def absolute_url(path=''):
    """``site_base()`` joined to ``path`` — the safe way to build an outbound link.

    Callers were concatenating by hand, which double-slashes the moment a path
    already starts with one (``get_pay_url()`` does). Joins exactly once.
    """
    base = site_base()
    if not path:
        return base
    return f'{base}/{str(path).lstrip("/")}'


#: What a closed-and-purged account is called wherever it still appears.
#: A candidate who closes their account is erased, but the conversations they
#: took part in belong to everyone who was in them: deleting the other side of a
#: thread would rewrite other people's history. So the rows stay, the author link
#: is dropped (every author FK worth keeping is ``SET_NULL``), and the gap reads
#: as this rather than as a blank or a stray "User 41".
DISCONTINUED_USER = 'Discontinued user'


def display_name(user):
    """Return a human-friendly name for ``user``.

    The platform is e-mail-only — there are no usernames — so this prefers the
    person's full name and falls back to the local-part of their e-mail address
    (e.g. ``jane`` for ``jane@example.com``), never the internal username column.

    ``None`` means the account was closed and purged; see
    :data:`DISCONTINUED_USER`.
    """
    if user is None:
        return DISCONTINUED_USER
    # The profile is where people type their name (registration, settings); the
    # login's own first/last name is only sometimes copied across.
    person = getattr(user, 'profile', None)
    full = ' '.join(filter(None, [getattr(person, 'first_name', '').strip() if person else '',
                                  getattr(person, 'last_name', '').strip() if person else ''])).strip()
    if not full:
        full = (user.get_full_name() or '').strip()
    if full:
        return full
    email = getattr(user, 'email', '') or ''
    return email.split('@')[0] or f'User {user.pk}'


def avatar_url(user):
    """URL of ``user``'s profile picture, or the default avatar for them.

    Never empty: someone who has not uploaded a picture gets the default that
    matches their gender (or title), and an account with no profile at all
    gets the neutral one. Storage-safe — see ``Person.avatar_url``.
    """
    from apps.accounts.models import default_avatar_url
    profile = getattr(user, 'profile', None) if user is not None else None
    if profile is None:
        return default_avatar_url()
    return profile.avatar_url


def initials(user):
    """One- or two-letter initials for ``user`` — the avatar fallback."""
    name = (display_name(user) or '?').strip()
    parts = [p for p in name.replace('.', ' ').split() if p]
    if len(parts) >= 2:
        return (parts[0][:1] + parts[-1][:1]).upper()
    return (parts[0][:2] if parts else '?').upper()
