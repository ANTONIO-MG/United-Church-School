"""Write the SA-SAMS export workbook (or the CSV zip) to a file.

    python manage.py sasams_export --year 2026 --term 3 [--grade 10] [--drafts]
                                   [--csv] [--out exports/sasams_2026_T3.xlsx]
"""
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.reports.terms import current_year_term
from apps.sasams import exports


class Command(BaseCommand):
    help = 'Export learners, parents, mark schedules and attendance in SA-SAMS layout (XLSX or CSV zip).'

    def add_arguments(self, parser):
        year, term = current_year_term()
        parser.add_argument('--year', type=int, default=year)
        parser.add_argument('--term', type=int, default=term, choices=[1, 2, 3, 4])
        parser.add_argument('--grade', type=int, default=None, help='Only this grade (1 - 12).')
        parser.add_argument('--drafts', action='store_true', help='Include draft (unpublished) marks.')
        parser.add_argument('--csv', action='store_true', help='Write a ZIP of CSV files instead of XLSX.')
        parser.add_argument('--out', default='', help='Output file (default: ./<sasams_YEAR_Tn>.xlsx|.zip).')

    def handle(self, *args, **opts):
        year, term, grade = opts['year'], opts['term'], opts['grade']
        if grade is not None and not 1 <= grade <= 12:
            raise CommandError('--grade must be 1 - 12')
        ext = '.zip' if opts['csv'] else '.xlsx'
        out = Path(opts['out'] or exports.file_stem(year, term, grade) + ext)
        if out.is_dir():
            out = out / (exports.file_stem(year, term, grade) + ext)
        maker = exports.csv_zip_bytes if opts['csv'] else exports.workbook_bytes
        out.write_bytes(maker(year, term, grade, opts['drafts']))
        records = exports.collect(year, grade)
        issues = exports.data_quality(records)
        errors = sum(1 for i in issues if i['Severity'] == exports.ERROR)
        self.stdout.write(self.style.SUCCESS(
            f'Wrote {out} — {len(records)} learners; data quality: {errors} errors, '
            f'{len(issues) - errors} warnings.'))
