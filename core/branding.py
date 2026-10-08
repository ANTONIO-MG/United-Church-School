"""Single-file string catalog: branding + UI text for the whole platform.

All user-facing static text — the brand name and tagline, SEO/social meta,
navigation labels, page titles, flash messages, error pages, the footer — lives
in :data:`STRINGS_FILE` (``.strings.json`` in the project root). Re-brand the
platform by editing the ``brand`` section; translate it by replacing the text
values (keep ``{placeholders}`` — they are filled with :meth:`str.format`).

Usage
-----
Python::

    from core.branding import t, BRAND, strings
    t("messages.saved", "Saved.", name="Department")   # -> "Department saved."
    BRAND["name"]                                      # -> "United Church School"

Templates (via the ``core.context_processors.branding`` context processor)::

    {{ brand.name }}
    {{ strings.auth.sign_in }}
    {{ strings.messages.form_errors }}

The file is read once and cached. Call :func:`reload_strings` after editing it
in a long-running process (or just restart the server).
"""

import json
from functools import lru_cache
from pathlib import Path

from django.conf import settings

#: Location of the catalog (a hidden JSON file next to ``manage.py``).
STRINGS_FILE = Path(settings.BASE_DIR) / '.strings.json'


@lru_cache(maxsize=1)
def strings():
    """Return the full catalog as a dict (cached). Empty dict if the file is missing/invalid."""
    try:
        with open(STRINGS_FILE, encoding='utf-8') as fh:
            data = json.load(fh)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def reload_strings():
    """Drop the cached catalog so the next access re-reads :data:`STRINGS_FILE`."""
    strings.cache_clear()


def get(path, default=None):
    """Look up a dotted ``path`` (e.g. ``"messages.saved"``) in the catalog.

    Returns ``default`` if any segment is missing.
    """
    node = strings()
    for key in path.split('.'):
        if not isinstance(node, dict) or key not in node:
            return default
        node = node[key]
    return node


def t(path, default='', **fmt):
    """Translate/brand a string by dotted ``path``.

    ``default`` is used when the key is absent. If ``fmt`` is given, the result
    is run through :meth:`str.format` (missing placeholders are tolerated, so a
    half-translated string never raises).
    """
    value = get(path, default)
    if fmt and isinstance(value, str):
        try:
            return value.format(**fmt)
        except (KeyError, IndexError):
            return value
    return value


#: Convenience handle on the ``brand`` section (your organisation's identity).
BRAND = strings().get('brand', {})
#: Alias — ``ORG`` reads more naturally as "the organisation's details".
ORG = BRAND
#: The dynamic-elements config (badges / widgets / announcement toggles).
DYNAMIC = strings().get('dynamic', {})
#: Arbitrary site-wide values injected into every template.
SITE = strings().get('site', {})
