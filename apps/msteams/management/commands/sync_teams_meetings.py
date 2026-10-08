"""Pull artifacts (transcript → recap, recording, attendance) for finished Teams
meetings and file them into the LMS.

Run on a schedule (cron / Task Scheduler), e.g. every 15 minutes::

    python manage.py sync_teams_meetings

Only touches Teams meetings whose scheduled end has passed and that haven't been
synced yet. Safe to run repeatedly (idempotent). No-op when Teams isn't
configured.
"""

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = 'Sync finished Microsoft Teams meetings (recap / recording / attendance) into the LMS.'

    def add_arguments(self, parser):
        parser.add_argument('--claude', action='store_true',
                            help='Use the Claude admin layer for richer recaps.')
        parser.add_argument('--grace-minutes', type=int, default=10,
                            help='Wait this long after a meeting ends before syncing (default 10).')
        parser.add_argument('--limit', type=int, default=50, help='Max meetings per run.')
        parser.add_argument('--force', action='store_true', help='Re-sync even if already synced.')

    def handle(self, *args, **opts):
        from apps.communication.models import MeetingRoom
        from apps.msteams import graph, services

        if not graph.is_configured():
            self.stdout.write('Microsoft Teams is not configured — nothing to do.')
            return

        cutoff = timezone.now() - timedelta(minutes=opts['grace_minutes'])
        qs = (MeetingRoom.objects
              .filter(provider=MeetingRoom.PROVIDER_TEAMS)
              .exclude(teams_meeting_id='')
              .filter(scheduled_end__lte=cutoff))
        if not opts['force']:
            qs = qs.filter(artifacts_synced_at__isnull=True)
        qs = qs.order_by('scheduled_end')[:opts['limit']]

        synced = 0
        for meeting in qs:
            try:
                if services.sync_meeting(meeting, use_claude=opts['claude'], force=opts['force']):
                    synced += 1
                    self.stdout.write(f'  synced: {meeting.title} ({meeting.scheduled_end:%Y-%m-%d %H:%M})')
            except Exception as exc:  # pragma: no cover
                self.stderr.write(f'  FAILED {meeting.pk}: {exc}')
        self.stdout.write(self.style.SUCCESS(f'Done. {synced} meeting(s) synced.'))
