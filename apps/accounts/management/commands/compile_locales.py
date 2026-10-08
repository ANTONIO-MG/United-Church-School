"""Compile ``locale/runtime/<lang>.json`` into gettext ``.mo`` catalogs.

``manage.py compilemessages`` shells out to GNU ``msgfmt``, which is not
installed on this deployment — so the binary format is written here directly. It
is a simple, stable format: a header, two sorted tables of (length, offset)
pairs, then the string data.

Running this makes the *same* phrases that the runtime HTML pass uses (see
:mod:`core.i18n_runtime`) also resolve through ``gettext()`` and
``{% translate %}``, so a template that has been marked up and one that has not
both end up in the user's language, from one catalog.

    python manage.py compile_locales
    python manage.py compile_locales --lang fr
"""

import array
import json
import struct
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

MAGIC = 0x950412DE


def write_mo(path, catalog):
    """Write ``{msgid: msgstr}`` to ``path`` in gettext's binary ``.mo`` format."""
    # An empty msgid carries the catalog metadata; gettext expects it present.
    entries = dict(catalog)
    entries.setdefault('', 'Content-Type: text/plain; charset=UTF-8\n')
    keys = sorted(entries)

    ids = b''
    strs = b''
    offsets = []
    for key in keys:
        msgid = key.encode('utf-8')
        msgstr = entries[key].encode('utf-8')
        offsets.append((len(ids), len(msgid), len(strs), len(msgstr)))
        ids += msgid + b'\x00'
        strs += msgstr + b'\x00'

    count = len(keys)
    keystart = 7 * 4 + 16 * count          # header + both index tables
    valuestart = keystart + len(ids)
    koffsets, voffsets = [], []
    for o1, l1, o2, l2 in offsets:
        koffsets += [l1, o1 + keystart]
        voffsets += [l2, o2 + valuestart]

    output = struct.pack('Iiiiiii', MAGIC, 0, count,
                         7 * 4, 7 * 4 + count * 8, 0, 0)
    output += array.array('i', koffsets + voffsets).tobytes()
    output += ids + strs

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(output)
    return count


class Command(BaseCommand):
    help = 'Compile locale/runtime/<lang>.json into locale/<lang>/LC_MESSAGES/django.mo'

    def add_arguments(self, parser):
        parser.add_argument('--lang', action='append', dest='langs',
                            help='Only this language code (repeatable). Default: all but English.')

    def handle(self, *args, **options):
        base = Path(settings.BASE_DIR)
        source_dir = base / 'locale' / 'runtime'
        wanted = options.get('langs') or [code for code, _label in settings.LANGUAGES
                                          if code != 'en']

        for code in wanted:
            source = source_dir / f'{code}.json'
            if not source.exists():
                self.stderr.write(self.style.WARNING(f'{source} is missing — skipped.'))
                continue
            with open(source, encoding='utf-8') as fh:
                data = json.load(fh)
            target = base / 'locale' / code / 'LC_MESSAGES' / 'django.mo'
            count = write_mo(target, {k: v for k, v in data.items() if isinstance(v, str)})
            self.stdout.write(self.style.SUCCESS(f'{code}: {count} messages → {target}'))
