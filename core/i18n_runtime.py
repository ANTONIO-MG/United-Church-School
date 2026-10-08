"""Front-end translation for English / French / Portuguese.

The platform has 300-odd templates written in plain English. Marking every one
of them up with ``{% translate %}`` is the textbook route, but it is also the
route on which "the interface is in French" stays 90% true forever, because the
one screen nobody remembered to mark is the one the user opens.

So translation happens in two layers, and they share a single catalog:

1. **Catalog** — ``locale/runtime/<lang>.json``: a flat ``{english: translated}``
   map. ``manage.py compile_locales`` also renders it into real ``.mo`` files
   under ``locale/<lang>/LC_MESSAGES/`` so ``{% translate %}``, ``gettext()``
   and Django's own admin/auth strings resolve from the same source. (The
   catalogs are written by hand as JSON rather than ``.po`` because this
   deployment has no ``gettext`` binaries; the command writes the binary format
   itself.)

2. **Runtime pass** — :class:`RuntimeTranslationMiddleware` rewrites the text of
   an already-rendered HTML response against the same catalog whenever the
   active language is not English. Anything a template already translated is
   simply already in the target language and does not match an English key, so
   the two layers compose rather than fight.

The rewrite is deliberately conservative:

* ``<script>``, ``<style>``, ``<pre>``, ``<code>`` and ``<textarea>`` bodies are
  cut out first and put back untouched — translating a JS string literal or a
  code sample would break the page.
* Only whole text nodes are matched, normalised on whitespace, against exact
  catalog keys. There is no fuzzy or word-by-word substitution: a phrase is
  either in the catalog and translated as a unit, or left in English.
* Among attributes, only the human-readable ones are touched (``placeholder``,
  ``title``, ``alt``, ``aria-label``, and ``value`` on buttons).

Nothing here runs at all for English, which is the overwhelming majority of
requests: the middleware returns the response untouched.
"""

import json
import logging
import re
from functools import lru_cache
from pathlib import Path

from django.conf import settings
from django.utils import translation

logger = logging.getLogger('apps')

#: Where the flat JSON catalogs live.
CATALOG_DIR = Path(settings.BASE_DIR) / 'locale' / 'runtime'

#: Element bodies that must never be rewritten.
_PROTECTED = re.compile(
    r'(?is)<(script|style|pre|code|textarea|svg)\b[^>]*>.*?</\1\s*>')

#: A text node: everything between a ``>`` and the next ``<``.
_TEXT_NODE = re.compile(r'>([^<>]+)<')

#: Human-readable attributes worth translating.
_ATTR = re.compile(
    r'(?i)\b(placeholder|title|alt|aria-label)\s*=\s*"([^"<>]+)"')

#: Only translate a node that actually contains letters — skip "·", "3", "&nbsp;".
_HAS_LETTERS = re.compile(r'[A-Za-z]{2}')


# ---------------------------------------------------------------------------
# Catalog
# ---------------------------------------------------------------------------
@lru_cache(maxsize=8)
def catalog(language):
    """The ``{english: translated}`` map for ``language`` (empty for English or
    an unknown/missing catalog). Cached; call :func:`reload_catalogs` after
    editing a file in a long-running process."""
    language = (language or 'en').split('-')[0]
    if language == 'en':
        return {}
    path = CATALOG_DIR / f'{language}.json'
    try:
        with open(path, encoding='utf-8') as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return {}
    if not isinstance(data, dict):
        return {}
    # Second, case-insensitive index so "Save changes" also matches "SAVE CHANGES"
    # coming out of a CSS-uppercased button whose markup is title-cased.
    out = {str(k): str(v) for k, v in data.items() if isinstance(v, str) and v}
    for key, value in list(out.items()):
        out.setdefault(key.lower(), value)
    return out


def reload_catalogs():
    """Drop the cached catalogs so the next lookup re-reads the JSON files."""
    catalog.cache_clear()


def translate_phrase(text, language):
    """Translate one whole phrase, or return it unchanged."""
    table = catalog(language)
    if not table:
        return text
    return table.get(text) or table.get(text.lower()) or text


# ---------------------------------------------------------------------------
# The rewrite
# ---------------------------------------------------------------------------
def translate_html(html, language):
    """Return ``html`` with its visible text translated into ``language``."""
    table = catalog(language)
    if not table:
        return html

    def lookup(value):
        return table.get(value) or table.get(value.lower())

    def do_text(match):
        raw = match.group(1)
        stripped = raw.strip()
        if not stripped or not _HAS_LETTERS.search(stripped):
            return match.group(0)
        # Collapse internal whitespace for the lookup — templates wrap lines
        # mid-sentence — but keep the node's own leading/trailing padding.
        key = ' '.join(stripped.split())
        hit = lookup(key)
        if hit is None:
            return match.group(0)
        lead = raw[:len(raw) - len(raw.lstrip())]
        trail = raw[len(raw.rstrip()):]
        return f'>{lead}{hit}{trail}<'

    def do_attr(match):
        name, value = match.group(1), match.group(2)
        key = ' '.join(value.split())
        hit = lookup(key)
        return match.group(0) if hit is None else f'{name}="{hit}"'

    # Cut the protected regions out, translate what is left, put them back.
    parts, guards = [], []

    def stash(match):
        guards.append(match.group(0))
        return f'\x00{len(guards) - 1}\x00'

    body = _PROTECTED.sub(stash, html)
    body = _TEXT_NODE.sub(do_text, body)
    body = _ATTR.sub(do_attr, body)
    parts.append(body)
    out = ''.join(parts)
    return re.sub(r'\x00(\d+)\x00', lambda m: guards[int(m.group(1))], out)


# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------
class RuntimeTranslationMiddleware:
    """Translate rendered HTML for non-English users.

    Sits directly after
    :class:`~apps.accounts.middleware.UserPreferenceMiddleware`, which has
    already activated the user's language, so this only has to ask what the
    active language is.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if not getattr(settings, 'RUNTIME_TRANSLATION', True):
            return response

        language = translation.get_language() or 'en'
        if language.split('-')[0] == 'en':
            return response
        # Streaming responses (file downloads, exports) have no rendered body to
        # rewrite, and a PDF or CSV is not front-end text.
        if getattr(response, 'streaming', False):
            return response
        content_type = response.headers.get('Content-Type', '')
        if 'text/html' not in content_type:
            return response
        # A TemplateResponse has not been rendered yet at this point in the
        # chain; hook its render instead of reading an empty body.
        if hasattr(response, 'render') and callable(response.render) and not response.is_rendered:
            response.add_post_render_callback(
                lambda r: self._rewrite(r, language))
            return response
        return self._rewrite(response, language) or response

    @staticmethod
    def _rewrite(response, language):
        try:
            charset = response.charset or 'utf-8'
            html = response.content.decode(charset)
            translated = translate_html(html, language)
            if translated != html:
                response.content = translated.encode(charset)
                if response.has_header('Content-Length'):
                    response['Content-Length'] = str(len(response.content))
        except Exception:                                # pragma: no cover
            # A translation pass must never be the reason a page fails to load.
            logger.exception('runtime translation failed (%s)', language)
        return response
