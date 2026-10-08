"""Import the bundled content packs in ``core/seed_packs/`` into the schedule.

    python manage.py import_seed_packs

These are validated ``thrive-pack`` JSON files (e.g. the Grade 10 Mathematics
material) saved so the content SURVIVES a destructive reset. ``.admin_wipe_and_create``
drops all tables and reseeds only the academic *structure* — it creates no
coursework — so this command re-lays the packed content onto the fresh spine.

It is deterministic (no language model, no cost) and idempotent: ``import_pack``
is keyed on ``source_ref`` and topic code, so running it twice updates the same
rows rather than duplicating them. Imported content lands unpublished/undated —
publishing it stays a human's decision on the module schedule.
"""

import glob
import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from core import content_pack


class Command(BaseCommand):
    help = 'Import the bundled thrive-pack JSON files in core/seed_packs/.'

    def add_arguments(self, parser):
        parser.add_argument('--dir', default=None,
                            help='Directory of *.json packs (default: core/seed_packs/).')

    def handle(self, *args, **opts):
        base = opts.get('dir') or os.path.join(settings.BASE_DIR, 'core', 'seed_packs')
        files = sorted(glob.glob(os.path.join(base, '*.json')))
        if not files:
            self.stdout.write(self.style.WARNING(f'No packs found in {base}.'))
            return

        imported = skipped = 0
        for path in files:
            name = os.path.basename(path)
            try:
                pack = json.load(open(path, encoding='utf-8'))
            except Exception as exc:
                self.stderr.write(self.style.ERROR(f'  {name}: unreadable ({exc})'))
                skipped += 1
                continue
            problems = content_pack.validate(pack)
            if problems:
                self.stderr.write(self.style.ERROR(
                    f'  {name}: {len(problems)} validation problem(s) — skipped'))
                skipped += 1
                continue
            try:
                result = content_pack.import_pack(pack, actor=None, validate=False)
            except content_pack.PackImportError as exc:
                # A pack whose module/programme is not on the spine yet (e.g. the
                # spine changed) is skipped, not fatal.
                self.stderr.write(self.style.WARNING(f'  {name}: {exc}'))
                skipped += 1
                continue
            imported += 1
            self.stdout.write(f'  {name}: {result}')

        self.stdout.write(self.style.SUCCESS(
            f'Seed packs done — {imported} imported, {skipped} skipped.'))
