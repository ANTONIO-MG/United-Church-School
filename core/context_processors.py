"""Template context processors.

``branding`` makes the single control document (see :mod:`core.branding` /
``.strings.json``) available in every template, so layouts and pages render the
organisation's identity, standard wording and dynamic-element toggles without
hard-coding anything:

    {{ brand.name }}   {{ brand.logo }}   {{ brand.contact.phone }}
    {{ org.social.facebook }}             {{ brand.welcome.title }}
    {% if dynamic.badges.unread_messages %}…{% endif %}
    {{ site.header_tagline }}

``brand`` and ``org`` are the same dict (two readable names for the
organisation section). Registered in
``TEMPLATES[...]['OPTIONS']['context_processors']`` in settings.
"""

from core.branding import strings


def branding(request):
    catalog = strings()
    organisation = catalog.get('brand', {})
    return {
        'strings': catalog,          # the whole catalog (dotted access in templates)
        'brand': organisation,       # the organisation's identity (logo, name, contact, …)
        'org': organisation,         # readable alias for the same section
        'dynamic': catalog.get('dynamic', {}),  # badge / widget / banner toggles
        'site': catalog.get('site', {}),        # arbitrary site-wide injected values
    }


def ui_chrome(request):
    """Theme + language for the layouts, resolved once per request.

    ``apps.accounts.middleware.UserPreferenceMiddleware`` has already worked out
    which of ``light`` / ``dark`` / ``auto`` applies; this hands it to the
    templates so ``<html data-bs-theme="…">`` is correct in the FIRST byte of the
    response. Doing it in JS after load is what produces the white flash before a
    dark page paints.

    ``ui_theme_attr`` is empty for ``auto`` — Bootstrap's own
    ``prefers-color-scheme`` handling should decide, and a hard-coded attribute
    would override the very system setting the user asked us to follow.
    """
    theme = getattr(request, 'ui_theme', 'auto')
    return {
        'ui_theme': theme,
        'ui_theme_attr': '' if theme == 'auto' else theme,
        'ui_language': getattr(request, 'LANGUAGE_CODE', 'en'),
    }


def parent_children(request):
    """For a parent: their linked children and the one they are viewing, so
    every page can show the child selector (``?student=<id>`` switches, and the
    choice is remembered — see core.scoping.viewing_child)."""
    user = getattr(request, 'user', None)
    if not (user and user.is_authenticated):
        return {}
    from core.scoping import children_of, is_parent, viewing_child
    if not is_parent(user):
        return {}
    children = list(children_of(user).select_related('profile').order_by('first_name', 'pk'))
    if not children:
        return {'parent_children': []}
    child = viewing_child(request)
    profile = getattr(child, 'profile', None)
    return {
        'parent_children': [{
            'id': c.pk,
            'name': (f'{c.profile.first_name} {c.profile.last_name}'.strip()
                     if getattr(c, 'profile', None) else c.get_username()),
            'grade': getattr(getattr(c, 'profile', None), 'enrolled_class', ''),
        } for c in children],
        'child': child,
        'child_name': (f'{profile.first_name} {profile.last_name}'.strip() if profile else ''),
    }
