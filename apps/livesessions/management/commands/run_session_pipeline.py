"""Advance finished sessions through the after-class pipeline.

Normally run by the scheduler every five minutes. Run by hand when you are
debugging a session that has not produced a recording:

    manage.py run_session_pipeline --session 42 --verbosity 2
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Advance finished live sessions one pipeline step each.'

    def add_arguments(self, parser):
        parser.add_argument('--session', type=int, default=None,
                            help='Only this MeetingRoom id.')
        parser.add_argument('--limit', type=int, default=25,
                            help='Maximum sessions to advance in one run.')
        parser.add_argument('--steps', type=int, default=1,
                            help='Advance each session this many steps (use with --session).')

    def handle(self, *args, **options):
        from apps.livesessions import pipeline
        from apps.livesessions.models import SessionArtifact

        if options['session']:
            from apps.communication.models import MeetingRoom
            meeting = MeetingRoom.objects.filter(pk=options['session']).first()
            if meeting is None:
                self.stderr.write(self.style.ERROR(f'No session {options["session"]}'))
                return
            artifact = pipeline.artifact_for(meeting)
            for _ in range(max(1, options['steps'])):
                before = artifact.state
                changed = pipeline.step(artifact)
                artifact.refresh_from_db()
                self.stdout.write(f'{before} → {artifact.state}'
                                  + ('' if changed else '  (no change)'))
                if not changed or artifact.is_terminal:
                    break
            if artifact.last_error:
                self.stdout.write(self.style.WARNING(f'last error: {artifact.last_error[:400]}'))
            return

        summary = pipeline.run(limit=options['limit'])
        self.stdout.write(self.style.SUCCESS(summary))

        if options['verbosity'] > 1:
            for artifact in SessionArtifact.objects.exclude(
                    state__in=[SessionArtifact.STATE_PUBLISHED,
                               SessionArtifact.STATE_SKIPPED])[:20]:
                self.stdout.write(f'  {artifact.state:<12} {artifact.meeting} '
                                  f'(attempt {artifact.attempts})')
