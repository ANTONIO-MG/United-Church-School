"""Import a ``thrive-pack/1`` JSON file into a module's syllabus.

    python manage.py import_content_pack fixtures/content_packs/tax-t5.json
    python manage.py import_content_pack pack.json --check      # validate only

Everything lands as a draft. Publishing is a separate, deliberate act in the
builder — this command never opens a paper to candidates.
"""

import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from core import content_pack
from core.content_pack.importer import PackImportError


class Command(BaseCommand):
    help = 'Import a content-pack JSON file (study guide, worksheet, test, exam) as drafts.'

    def add_arguments(self, parser):
        parser.add_argument('path', help='Path to the pack JSON file.')
        parser.add_argument('--check', action='store_true',
                            help='Validate only — touch nothing in the database.')

    def handle(self, *args, **options):
        path = Path(options['path'])
        if not path.is_file():
            raise CommandError(f'No such file: {path}')
        try:
            pack = json.loads(path.read_text(encoding='utf-8'))
        except json.JSONDecodeError as exc:
            raise CommandError(f'{path} is not valid JSON — {exc}')

        problems = content_pack.validate(pack)
        if problems:
            self.stderr.write(self.style.ERROR(
                f'{len(problems)} problem(s) in {path.name}:'))
            for problem in problems:
                self.stderr.write(f'  · {problem}')
            raise CommandError('Nothing was imported.')

        self.stdout.write(self.style.SUCCESS(f'{path.name} is valid.'))
        if options['check']:
            return

        try:
            result = content_pack.import_pack(pack, validate=False)
        except PackImportError as exc:
            raise CommandError(str(exc))

        self.stdout.write(self.style.SUCCESS(f'Imported into {result.topic}:'))
        self.stdout.write(f'  {result}')
        for warning in result.warnings:
            self.stdout.write(self.style.WARNING(f'  ! {warning}'))
        self.stdout.write('  Everything is in DRAFT — review and publish it in the builder.')
