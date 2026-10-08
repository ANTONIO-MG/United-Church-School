"""Send the due session reminders (24 hours and 30 minutes before, by default)."""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Send reminders for upcoming live sessions.'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true',
                            help='Report what would be sent, without sending or recording it.')

    def handle(self, *args, **options):
        from apps.livesessions import reminders
        from apps.livesessions.audience import recipients_for
        from apps.livesessions.models import LiveSessionSettings, SessionReminder

        if options['dry_run']:
            from datetime import timedelta

            from django.utils import timezone

            from apps.communication.models import MeetingRoom

            conf = LiveSessionSettings.load()
            now = timezone.now()
            horizon = now + timedelta(minutes=max(conf.lead_minutes))
            upcoming = MeetingRoom.objects.filter(
                is_active=True, scheduled_start__gt=now, scheduled_start__lte=horizon)
            for meeting in upcoming:
                for lead in conf.lead_minutes:
                    if meeting.scheduled_start - now > timedelta(minutes=lead):
                        continue
                    already = set(SessionReminder.objects
                                  .filter(meeting=meeting, lead_minutes=lead)
                                  .values_list('recipient_id', flat=True))
                    pending = recipients_for(meeting).exclude(pk__in=already).count()
                    self.stdout.write(f'{meeting} · {lead}m lead → {pending} to remind')
            return

        self.stdout.write(self.style.SUCCESS(reminders.run()))
