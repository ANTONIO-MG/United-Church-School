"""Run the hub's unattended background jobs.

Two ways to run it — pick one, don't run both against the same database:

**Cron / Task Scheduler (recommended).** One entry, ticking every minute; each
job's own interval decides whether it is due::

    * * * * * cd /path/to/ucs-lms && /path/to/python manage.py run_scheduled_jobs >> /var/log/ucs-lms-jobs.log 2>&1

**Loop mode.** For a container or a machine without cron, run it as a
long-lived process (systemd / launchd / supervisor keeps it alive)::

    python manage.py run_scheduled_jobs --loop --interval 60

Other usage::

    python manage.py run_scheduled_jobs --list            # health of every job
    python manage.py run_scheduled_jobs --job rank-classes --force
    python manage.py run_scheduled_jobs --dry-run         # show what is due

Overlapping runs are safe: each job takes a database lock for the duration.
"""

import signal
import time

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone


class Command(BaseCommand):
    help = 'Run due background jobs (attendance finalisation, Teams sync, ranking, reminders).'

    def add_arguments(self, parser):
        parser.add_argument('--job', default=None,
                            help='Run only these jobs (one name, or several separated by commas).')
        parser.add_argument('--force', action='store_true',
                            help='Run regardless of whether the interval has elapsed.')
        parser.add_argument('--loop', action='store_true',
                            help='Keep ticking instead of exiting after one pass.')
        parser.add_argument('--interval', type=int, default=60,
                            help='Seconds between ticks in --loop mode (default 60).')
        parser.add_argument('--list', action='store_true',
                            help='Show every job with its schedule and last result, then exit.')
        parser.add_argument('--dry-run', action='store_true',
                            help='Report which jobs are due without running them.')

    # -- helpers ---------------------------------------------------------
    def _describe(self, seconds):
        if seconds % 3600 == 0:
            return f'{seconds // 3600}h'
        if seconds % 60 == 0:
            return f'{seconds // 60}m'
        return f'{seconds}s'

    def _show_list(self):
        from apps.scheduler.jobs import JOBS
        from apps.scheduler.models import JobRun
        from apps.scheduler.runner import is_due

        states = {j.name: j for j in JobRun.objects.all()}
        self.stdout.write(f'{"JOB":24} {"EVERY":>6}  {"LAST RUN":>12}  {"STATUS":8} DETAIL')
        for job in JOBS:
            state = states.get(job.name)
            if state is None or state.last_started_at is None:
                last, status, due = 'never', '—', True
            else:
                age = state.seconds_since_run()
                last = f'{self._describe(age)} ago'
                status = state.last_status or '—'
                due = is_due(job, state)
            detail = (state.last_output.splitlines()[0][:52] if state and state.last_output else '')
            if due:
                detail = (detail + '  (due)').strip()
            style = self.style.ERROR if status == 'failed' else (
                self.style.SUCCESS if status == 'ok' else self.style.WARNING)
            self.stdout.write(
                f'{job.name:24} {self._describe(job.every):>6}  {last:>12}  '
                + style(f'{status:8}') + f' {detail}')

    def _show_due(self):
        from apps.scheduler.jobs import JOBS
        from apps.scheduler.models import JobRun
        from apps.scheduler.runner import is_due

        states = {j.name: j for j in JobRun.objects.all()}
        due = []
        for job in JOBS:
            state = states.get(job.name) or JobRun(name=job.name)
            if is_due(job, state):
                due.append(job.name)
        if due:
            self.stdout.write('Due now: ' + ', '.join(due))
        else:
            self.stdout.write('Nothing is due.')

    def _tick(self, *, only, force, verbosity):
        from apps.scheduler.runner import tick

        for name, ran, ok, output in tick(only=only, force=force):
            if not ran:
                if verbosity >= 2:
                    self.stdout.write(f'  skipped: {name}' + (f' ({output})' if output else ''))
                continue
            stamp = timezone.localtime().strftime('%H:%M:%S')
            if ok:
                first = output.splitlines()[0] if output else 'done'
                self.stdout.write(self.style.SUCCESS(f'[{stamp}] {name}: {first}'))
            else:
                self.stderr.write(self.style.ERROR(f'[{stamp}] {name}: FAILED'))
                if verbosity >= 1 and output:
                    for line in output.splitlines()[-6:]:
                        self.stderr.write(f'    {line}')

    # -- entry point -----------------------------------------------------
    def handle(self, *args, **options):
        from apps.scheduler.jobs import JOBS_BY_NAME

        verbosity = options.get('verbosity', 1)
        only = [n.strip() for n in (options['job'] or '').split(',') if n.strip()] or None
        unknown = [n for n in (only or []) if n not in JOBS_BY_NAME]
        if unknown:
            raise CommandError(
                f'Unknown job {unknown[0]!r}. Known jobs: ' + ', '.join(sorted(JOBS_BY_NAME)))

        if options['list']:
            self._show_list()
            return
        if options['dry_run']:
            self._show_due()
            return

        if not options['loop']:
            self._tick(only=only, force=options['force'], verbosity=verbosity)
            return

        # --- loop mode: tick until told to stop ---
        interval = max(5, options['interval'])
        stopping = {'flag': False}

        def _stop(signum, frame):
            stopping['flag'] = True
            self.stdout.write(self.style.WARNING('\nStopping after the current tick…'))

        signal.signal(signal.SIGINT, _stop)
        signal.signal(signal.SIGTERM, _stop)

        self.stdout.write(self.style.SUCCESS(
            f'Scheduler running — ticking every {interval}s. Ctrl-C to stop.'))
        while not stopping['flag']:
            try:
                self._tick(only=only, force=options['force'], verbosity=verbosity)
            except Exception as exc:      # a bad tick must not kill the loop
                self.stderr.write(self.style.ERROR(f'tick failed: {exc}'))
            # Sleep in short slices so a stop signal is honoured promptly.
            for _ in range(interval):
                if stopping['flag']:
                    break
                time.sleep(1)
        self.stdout.write('Scheduler stopped.')
