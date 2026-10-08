"""Write the Claude follow-up pack (summary, next agenda, action items) for sessions.

Runs on the admin Claude layer only — see :mod:`apps.livesessions.ai_followup`.
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Generate post-session summaries, agendas and action items with the admin AI.'

    def add_arguments(self, parser):
        parser.add_argument('--session', type=int, default=None, help='Only this MeetingRoom id.')
        parser.add_argument('--limit', type=int, default=5, help='Maximum sessions per run.')
        parser.add_argument('--force', action='store_true',
                            help='Regenerate even if a pack already exists.')

    def handle(self, *args, **options):
        from apps.livesessions import ai_followup
        from apps.livesessions.models import SessionArtifact

        if not ai_followup.is_enabled():
            self.stderr.write(self.style.WARNING(
                'AI follow-up is off, or ADMIN_AI_ENABLED / ANTHROPIC_API_KEY are not set.'))
            return

        if options['session']:
            artifact = SessionArtifact.objects.filter(meeting_id=options['session']).first()
            if artifact is None:
                self.stderr.write(self.style.ERROR('That session has no pipeline record yet.'))
                return
            if options['force']:
                artifact.ai_followup_done = False
                artifact.save(update_fields=['ai_followup_done', 'updated_at'])
            wrote = ai_followup.process(artifact)
            self.stdout.write(self.style.SUCCESS('Pack written.') if wrote
                              else self.style.WARNING('Nothing written — see the log.'))
            return

        self.stdout.write(self.style.SUCCESS(ai_followup.run(limit=options['limit'])))
