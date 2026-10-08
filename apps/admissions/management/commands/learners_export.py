"""Export learners to Excel in the bulk-import format.

    python manage.py learners_export                       # the school year, every grade
    python manage.py learners_export --year 2026 --grade 10 --out grade10.xlsx
"""
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.admissions import bulk
from core import school


class Command(BaseCommand):
    help = 'Export learners (applications, parents, enrolment) to an .xlsx that can be re-imported.'

    def add_arguments(self, parser):
        parser.add_argument('--year', type=int, default=school.YEAR)
        parser.add_argument('--grade', type=int, default=None, help='1 – 12; omit for every grade.')
        parser.add_argument('--out', default=None,
                            help='Output file (default UCS-learners-<year>[-grade-N].xlsx).')

    def handle(self, *args, **options):
        year, grade = options['year'], options['grade']
        if grade is not None and grade not in school.GRADES:
            raise CommandError('--grade must be 1 – 12.')
        out = Path(options['out'] or f'UCS-learners-{year}{f"-grade-{grade}" if grade else ""}.xlsx')
        rows = bulk.export_rows(year=year, grade=grade)
        data = bulk.export_workbook(rows=rows)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(data)
        self.stdout.write(self.style.SUCCESS(f'{len(rows)} learner(s) exported to {out}.'))
