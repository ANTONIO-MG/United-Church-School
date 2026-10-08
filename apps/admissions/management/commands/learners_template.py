"""Write the learner bulk-import template.

    python manage.py learners_template            # static/documents/UCS-learner-import-template.xlsx
    python manage.py learners_template --out x.xlsx
"""
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.admissions import bulk

DEFAULT_PATH = Path(settings.BASE_DIR) / 'static' / 'documents' / 'UCS-learner-import-template.xlsx'


class Command(BaseCommand):
    help = 'Write the Excel template for importing learners in bulk (with EXAMPLE rows).'

    def add_arguments(self, parser):
        parser.add_argument('--out', default=str(DEFAULT_PATH), help='Where to write the .xlsx.')

    def handle(self, *args, **options):
        path = Path(options['out'])
        path.parent.mkdir(parents=True, exist_ok=True)
        bulk.write_template(path)
        self.stdout.write(self.style.SUCCESS(
            f'Learner import template written to {path} ({len(bulk.COLUMNS)} columns, '
            f'{len(bulk.EXAMPLES)} example rows).'))
