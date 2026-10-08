"""How a person appears on the page: their picture and their name.

``{% person_chip someone %}`` is the one way to show a person — a round picture
(their upload, or the default for their gender) and "First Last", clickable to
open their card. ``someone`` may be a User or an accounts.Person. Use
``{{ someone|person_name }}`` where only the name fits.
"""

from django import template
from django.urls import reverse

from core.utils import avatar_url, display_name

register = template.Library()


def _user_and_person(who):
    if who is None:
        return None, None
    if hasattr(who, 'user_type') and hasattr(who, 'user_id'):     # a Person
        return who.user, who
    return who, getattr(who, 'profile', None)


@register.filter
def person_name(who):
    """First name and surname (never a username or an e-mail address).

    Tolerates being handed a name that was already resolved (``a|default:b|person_name``)
    and the anonymous user, so a chained filter can never take a page down.
    """
    if isinstance(who, str):
        return who
    if who is None or who == '':
        return ''      # let the template's own |default:"—" speak
    if who is not None and not hasattr(who, 'get_full_name') and not hasattr(who, 'user_type'):
        return ''
    user, person = _user_and_person(who)
    return display_name(user) if user is not None else (str(person) if person else display_name(None))


@register.filter
def person_avatar(who):
    if isinstance(who, str) or (who is not None and not getattr(who, 'pk', None)):
        return avatar_url(None)
    user, person = _user_and_person(who)
    return person.avatar_url if person is not None else avatar_url(user)


@register.inclusion_tag('accounts/_person_chip.html')
def person_chip(who, size='sm', subtitle='', link=True):
    user, person = _user_and_person(who)
    card = ''
    if link and person is not None:
        card = reverse('accounts:person-card', args=[person.pk])
    return {
        'name': person_name(who), 'avatar': person_avatar(who), 'card': card,
        'size': size, 'subtitle': subtitle,
    }


@register.simple_tag
def person_link(who, css=''):
    """Their name, clickable to open their person card (plain text if there is no profile)."""
    from django.utils.html import format_html
    user, person = _user_and_person(who)
    name = person_name(who)
    if person is None:
        return name
    card = reverse('accounts:person-card', args=[person.pk])
    return format_html('<a class="plink {}" href="{}" data-person-card="{}?fragment=1">{}</a>',
                       css, card, card, name)
