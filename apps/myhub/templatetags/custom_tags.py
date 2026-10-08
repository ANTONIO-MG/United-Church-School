"""Small template filters shared across the hub's pages.

Once this module also carried ``getdata``, which resolved a per-page CSS/JS
asset list out of ``apps.myhub.dz.dz_array``. Both went with the old MyHub
theme: the platform's pages declare their own assets in their own templates, so a
central asset map keyed by view name had nothing left to key.
"""

from django import template

register = template.Library()


@register.filter(name='get_item')
def get_item(dictionary, key):
    """Look a key up in a dict from a template, where ``dict[key]`` is not valid syntax.

    Usage: ``{{ status_badges|get_item:obj.status }}``. Returns ``None`` rather
    than raising when the key is absent or the left-hand side is not a dict, so
    a missing entry renders as empty instead of breaking the page.
    """
    if not isinstance(dictionary, dict):
        return None
    return dictionary.get(str(key), None)
