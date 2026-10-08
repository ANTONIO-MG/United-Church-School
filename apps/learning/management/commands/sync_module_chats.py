"""Reconcile every module offering's chat group with who currently has access.

    python manage.py sync_module_chats                 # all active offerings
    python manage.py sync_module_chats --institution UCS
    python manage.py sync_module_chats --dry-run

Signals keep the rooms in step whenever an enrolment is written (paid, trial
started, locked) — see :mod:`apps.learning.signals`. They cannot see a free week
simply *running out*, because nothing is saved when a date passes. Running this
on a schedule (nightly is plenty) closes that gap, and it is also the backfill
for offerings that existed before module chats did.

Idempotent, and it never touches memberships somebody added by hand: only rows
flagged ``is_auto`` are reconciled.
"""

from django.core.management.base import BaseCommand

from apps.learning.models import ProgrammeModule


class Command(BaseCommand):
    help = "Create and reconcile each module offering's chat group."

    def add_arguments(self, parser):
        parser.add_argument('--institution', help='Limit to one institution code, e.g. UCS.')
        parser.add_argument('--programme', help='Limit to one programme code, e.g. GR10.')
        parser.add_argument('--module', help='Limit to one offering code, e.g. FREP.')
        parser.add_argument('--dry-run', action='store_true',
                            help='Report the membership each room would end up with.')

    def handle(self, *args, **options):
        from apps.communication.services import module_chat_users, sync_module_chat_members

        offerings = (ProgrammeModule.objects.filter(is_active=True)
                     .select_related('programme__institution', 'module', 'chat_group'))
        if options['institution']:
            offerings = offerings.filter(programme__institution__code__iexact=options['institution'])
        if options['programme']:
            offerings = offerings.filter(programme__code__iexact=options['programme'])
        if options['module']:
            offerings = offerings.filter(code__iexact=options['module'])

        if not offerings.exists():
            self.stdout.write(self.style.WARNING('No offerings matched.'))
            return

        created = 0
        members = 0
        for offering in offerings:
            people = module_chat_users(offering).count()
            members += people
            if options['dry_run']:
                state = 'has a room' if offering.chat_group_id else 'NEEDS a room'
                self.stdout.write(f'  {offering.reference}: {state}, {people} member(s)')
                continue
            had_room = bool(offering.chat_group_id)
            sync_module_chat_members(offering)
            if not had_room:
                created += 1
            self.stdout.write(f'  {offering.reference}: {people} member(s)')

        verb = 'would reconcile' if options['dry_run'] else 'reconciled'
        self.stdout.write(self.style.SUCCESS(
            f'{verb} {offerings.count()} offering(s), {members} membership(s)'
            + (f'; created {created} new room(s).' if created else '.')))
