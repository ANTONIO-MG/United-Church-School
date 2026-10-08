"""Which social logins are actually usable right now.

A provider listed in ``INSTALLED_APPS`` is only *available* once somebody has
registered a :class:`~allauth.socialaccount.models.SocialApp` for it in the
admin and attached it to the Site. Until then its login route raises — Facebook
raises ``SocialApp.DoesNotExist`` outright (a 500 on a login page), and Google
redirects back with an error. Either way the button was a dead end.

So the templates ask this instead of hard-coding buttons. Nothing configured →
nothing rendered → nobody can click into the failure.
"""

from django import template

register = template.Library()

#: Provider id → (label, brand icon file under static/images/icon/).
KNOWN_PROVIDERS = {
    'google': ('Google', 'images/icon/google-icon.svg'),
    'facebook': ('Facebook', 'images/icon/facebook-icon.svg'),
}

_CACHE_ATTR = '_ucs_social_providers'


@register.simple_tag(takes_context=True)
def social_providers(context):
    """``[{'id', 'label', 'icon'}, …]`` for every provider with a live SocialApp.

    Cached on the request, because both the login and the sign-up page ask and
    the sidebar shell renders on every response — one query per request, not
    one per call site. Returns ``[]`` if socialaccount is not installed at all.
    """
    request = context.get('request')
    cached = getattr(request, _CACHE_ATTR, None) if request is not None else None
    if cached is not None:
        return cached

    found = {}
    try:
        from django.conf import settings

        # 1. Credentials set in settings (SOCIALACCOUNT_PROVIDERS[x]['APP']).
        #    This is how Google is wired here — env vars, no database row — so
        #    checking only the SocialApp table would hide a working button.
        #    Blank client_id means the env var was never filled in.
        for provider_id, conf in (getattr(settings, 'SOCIALACCOUNT_PROVIDERS', {}) or {}).items():
            app = (conf or {}).get('APP') or {}
            if app.get('client_id'):
                found[provider_id] = True

        # 2. ...or a SocialApp registered in the admin and attached to this Site.
        #    One not attached to the Site cannot authenticate against it, so the
        #    row existing is not enough.
        from allauth.socialaccount.models import SocialApp
        site_id = getattr(settings, 'SITE_ID', None)
        rows = SocialApp.objects.all()
        if site_id:
            rows = rows.filter(sites__id=site_id)
        for provider_id in rows.values_list('provider', flat=True).distinct():
            found[provider_id] = True
    except Exception:  # pragma: no cover - socialaccount optional / un-migrated
        found = {}

    providers = []
    for provider_id in sorted(found):
        label, icon = KNOWN_PROVIDERS.get(provider_id, (provider_id.title(), ''))
        providers.append({'id': provider_id, 'label': label, 'icon': icon})

    if request is not None:
        setattr(request, _CACHE_ATTR, providers)
    return providers
