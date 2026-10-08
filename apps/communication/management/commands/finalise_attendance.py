"""Close out the register for class sessions that have ended.

Attendance accrues live from the presence heartbeat, but a session still needs a
final pass once it is over: students who never crossed the threshold become
absent, and anyone on the roster with no row at all gets one. Until that runs, a
no-show simply has no record — which reads as "not marked yet", not "absent".

Run it from cron / Celery beat, e.g. every 15 minutes::

    python manage.py finalise_attendance
    python manage.py finalise_attendance --session 42     # just this one
    python manage.py finalise_attendance --dry-run

Idempotent: an already-finalised session is skipped unless ``--force`` is given.
Manual and excused marks are never touched.
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction


class Command(BaseCommand):
    help = 'Finalise attendance for ended class sessions (auto-mark absent below threshold).'

    def add_arguments(self, parser):
        parser.add_argument('--session', type=int, default=None,
                            help='Finalise only this class-session id.')
        parser.add_argument('--force', action='store_true',
                            help='Re-finalise sessions already closed out.')
        parser.add_argument('--dry-run', action='store_true',
                            help='Report what would change without writing.')

    def handle(self, *args, **options):
        from apps.communication import models, services

        verbosity = options.get('verbosity', 1)
        dry_run = options['dry_run']

        qs = models.ClassSession.objects.select_related('module', 'meeting')
        if options['session']:
            qs = qs.filter(pk=options['session'])
            if not qs.exists():
                raise CommandError(f"No class session with id {options['session']}.")
        elif not options['force']:
            qs = qs.filter(finalised_at__isnull=True)

        sessions = [s for s in qs[:1000] if s.has_ended or options['session']]
        if not sessions:
            if verbosity:
                self.stdout.write(self.style.WARNING('No ended sessions awaiting finalisation.'))
            return

        closed = 0
        try:
            with transaction.atomic():
                for session in sessions:
                    present, late, absent, excused = services.finalise_session_attendance(session)
                    closed += 1
                    if verbosity >= 2:
                        self.stdout.write(
                            f'  {session}: {present} present, {late} late, '
                            f'{absent} absent, {excused} excused')
                if dry_run:
                    raise _Rollback()
        except _Rollback:
            if verbosity:
                self.stdout.write(self.style.WARNING(
                    f'Dry run — rolled back. Would have finalised {closed} session(s).'))
            return

        if verbosity:
            self.stdout.write(self.style.SUCCESS(f'Finalised {closed} session(s).'))


class _Rollback(Exception):
    """Internal sentinel used to abort the transaction on --dry-run."""
