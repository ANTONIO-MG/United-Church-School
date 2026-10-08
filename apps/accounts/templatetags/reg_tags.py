"""Template helpers for the registration pages.

Currently one tag: :func:`country_dial_json`, which hands the phone field's
country picker its data. Kept as a tag rather than view context so any template
that includes ``accounts/register/_phonefield.html`` gets the list without every
view having to remember to pass it.
"""

import json

from django import template
from django.utils.safestring import mark_safe

from core import countries

register = template.Library()


@register.simple_tag
def country_dial_json():
    """Every country as JSON: ``[{"iso","name","dial","flag"}, …]``.

    Safe to mark as-is: the payload is a fixed list from
    :mod:`core.countries`, never user input, and ``json.dumps`` escapes ``<``,
    ``>`` and ``&`` so it cannot break out of the surrounding ``<script>``.
    """
    payload = json.dumps(countries.picker_rows()).replace('<', '\\u003c') \
                                                 .replace('>', '\\u003e') \
                                                 .replace('&', '\\u0026')
    return mark_safe(payload)  # noqa: S308 - fixed data, escaped above


@register.simple_tag
def default_country():
    """The ISO code the picker opens on when nothing is stored yet."""
    return countries.DEFAULT_COUNTRY
