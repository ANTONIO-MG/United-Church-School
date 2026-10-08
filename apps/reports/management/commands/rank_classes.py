"""Recompute persisted class positions for every module that has grades.

Positions are normally kept current by :mod:`apps.reports.signals` whenever a
grade is recomputed. Run this to backfill rows that predate ranking, or after a
bulk import / data fix that wrote grades without going through the signal.

    python manage.py rank_classes                 # every module with grades
    python manage.py rank_classes --module 12    # one module
    python manage.py rank_classes --dry-run       # report only, write nothing
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction


class Command(BaseCommand):
    help = 'Recompute and persist Grade.class_position / cohort_size / cohort_average.'

    def add_arguments(self, parser):
        parser.add_argument('--module', type=int, default=None,
                            help='Rank only this subject id (default: all subjects with marks).')
        parser.add_argument('--dry-run', action='store_true',
                            help='Show what would change without writing.')

    def handle(self, *args, **options):
        from apps.learning.models import ProgrammeModule
        from apps.reports import models, services

        module_id = options['module']
        dry_run = options['dry_run']
        verbosity = options.get('verbosity', 1)

        if module_id:
            try:
                modules = [ProgrammeModule.objects.get(pk=module_id)]
            except ProgrammeModule.DoesNotExist:
                raise CommandError(f'No subject with id {module_id}.')
        else:
            ids = models.Grade.objects.values_list('module_id', flat=True).distinct()
            modules = list(ProgrammeModule.objects.filter(id__in=list(ids)).order_by('name'))

        if not modules:
            if verbosity:
                self.stdout.write(self.style.WARNING('No subjects have marks yet — nothing to rank.'))
            return

        total_rows = 0
        try:
            with transaction.atomic():
                for module in modules:
                    rows = services.rank_module(module)
                    total_rows += rows
                    if verbosity >= 2:
                        top = (models.Grade.objects.filter(module=module, class_position=1)
                               .select_related('student').first())
                        self.stdout.write(
                            f'  {module.name}: ranked {rows} student{"s" if rows != 1 else ""}'
                            + (f' — top {top.final_pct}%' if top else ''))
                if dry_run:
                    raise _Rollback()
        except _Rollback:
            if verbosity:
                self.stdout.write(self.style.WARNING(
                    f'Dry run — rolled back. Would have ranked {total_rows} rows '
                    f'across {len(modules)} module(s).'))
            return

        if verbosity:
            self.stdout.write(self.style.SUCCESS(
                f'Ranked {total_rows} grade row(s) across {len(modules)} module(s).'))


class _Rollback(Exception):
    """Internal sentinel used to abort the transaction on --dry-run."""
