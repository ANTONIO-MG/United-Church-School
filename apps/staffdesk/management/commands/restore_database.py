"""Restore a backup over the live database (started by the Backups page).

``manage.py restore_database <backup name> [--by "who"]``

Takes a safety backup first, restores all-or-nothing, then migrates the restored
database forward so it matches the code that is running. Progress goes to
backups/db/restore-status.json, which the Backups page polls.
"""

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from apps.staffdesk import backups


class Command(BaseCommand):
    help = 'Restore the database from a backup in backups/db/ (a safety backup is taken first).'

    def add_arguments(self, parser):
        parser.add_argument('name')
        parser.add_argument('--by', default='command line')

    def handle(self, *args, **opts):
        from core.errors import report
        try:
            safety = backups.restore_backup(opts['name'], by=opts['by'])
        except backups.BackupError as exc:
            backups._set_status(state='failed', error=f'{exc} {exc.detail[-800:]}')
            report(exc.code, exc, context={'backup': opts['name'], 'detail': exc.detail[-500:]})
            raise CommandError(f'{exc} [{exc.code}]')
        except Exception as exc:
            backups._set_status(state='failed', error=str(exc)[:800])
            report('BKP-5002', exc, context={'backup': opts['name']})
            raise
        # An older restore point has an older schema; bring it up to the running code.
        try:
            call_command('migrate', interactive=False, verbosity=0)
            backups._set_status(migrated=True)
        except Exception as exc:
            backups._set_status(migrated=False, error=f'Restored, but migrating it failed: {exc}'[:800])
            report('BKP-5002', exc, context={'backup': opts['name'], 'step': 'migrate'})
        self.stdout.write(self.style.SUCCESS(
            f'Restored {opts["name"]}. Safety backup: {safety["name"]}'))
