"""(Re)draw session thumbnails — after changing the background or the brand colours."""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Generate the session-detail thumbnail card for live sessions.'

    def add_arguments(self, parser):
        parser.add_argument('--all', action='store_true',
                            help='Redraw every session, not only the ones without a thumbnail.')
        parser.add_argument('--limit', type=int, default=200)

    def handle(self, *args, **options):
        from apps.communication.models import MeetingRoom
        from apps.livesessions import services

        qs = MeetingRoom.objects.filter(is_active=True).order_by('-scheduled_start')
        if not options['all']:
            qs = qs.filter(thumbnail='')

        drawn = 0
        for meeting in qs[:options['limit']]:
            if services.ensure_thumbnail(meeting, force=options['all']):
                drawn += 1
                if options['verbosity'] > 1:
                    self.stdout.write(f'  drew {meeting}')
        self.stdout.write(self.style.SUCCESS(f'{drawn} thumbnail(s) generated.'))
