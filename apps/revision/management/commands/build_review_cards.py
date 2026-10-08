"""Back-fill review cards from attempts that were marked before revision existed.

Safe to re-run: cards are unique per (user, question) and an attempt already
recorded on a card is skipped.
"""

from django.core.management.base import BaseCommand

from apps.assessments.models import AssessmentAttempt
from apps.revision.services import cards_from_attempt


class Command(BaseCommand):
    help = 'Create review cards from every marked attempt with answers below full marks.'

    def add_arguments(self, parser):
        parser.add_argument('--user', type=int, help='Only this user id.')
        parser.add_argument('--dry-run', action='store_true', help='Count attempts only.')

    def handle(self, *args, **options):
        attempts = AssessmentAttempt.objects.filter(status=AssessmentAttempt.STATUS_MARKED)
        if options.get('user'):
            attempts = attempts.filter(student_id=options['user'])
        # Oldest first, so a later wrong answer is the one recorded on the card.
        attempts = attempts.order_by('submitted_at', 'created_at', 'id')
        if options.get('dry_run'):
            self.stdout.write(f'{attempts.count()} marked attempt(s) would be scanned.')
            return
        created = lapsed = scanned = 0
        for attempt in attempts.iterator():
            c, l = cards_from_attempt(attempt)
            created += c
            lapsed += l
            scanned += 1
        self.stdout.write(self.style.SUCCESS(
            f'Scanned {scanned} attempt(s): {created} card(s) created, {lapsed} reset by a later attempt.'))
