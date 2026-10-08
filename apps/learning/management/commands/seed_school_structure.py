"""Install United Church School's academic spine.

The school, Grade 1 to Grade 12 with their 2026 fee schedule, the CAPS
subjects offered in each grade (with the Grade 10 – 12 subject choices), a
class per grade for the year, and the school calendar. The facts live in
``core/school.py``; the builder is ``core/academic_spine.py``.

    python manage.py seed_school_structure
    python manage.py seed_school_structure --update          # re-apply fees/subjects from core/school.py
    python manage.py seed_school_structure --year 2027 --no-calendar

Idempotent: re-running creates what is missing and, without ``--update``,
leaves admin edits alone.
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from core import academic_spine


class Command(BaseCommand):
    help = "Install United Church School's grades, subjects, fees and calendar."

    def add_arguments(self, parser):
        parser.add_argument('--year', type=int, default=None,
                            help='School year for the class and calendar (default: core.school.YEAR).')
        parser.add_argument('--update', action='store_true',
                            help='Re-apply the facts from core/school.py over existing rows.')
        parser.add_argument('--no-calendar', action='store_true', help='Skip the school calendar.')
        parser.add_argument('--publish', action='store_true',
                            help='Publish the template examination windows as well.')

    @transaction.atomic
    def handle(self, *args, **options):
        result = academic_spine.seed(
            year=options['year'], update=options['update'], calendar=not options['no_calendar'],
            publish=options['publish'], verbose=options['verbosity'] > 0)
        self.stdout.write(self.style.SUCCESS(
            f"United Church School: {len(result['programmes'])} grades, "
            f"{len(result['modules'])} subjects, {len(result['offerings'])} subject offerings, "
            f"{result['events_total']} calendar events for {result['year']}."))
