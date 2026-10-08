"""Make a restore point now: ``manage.py backup_database [--kind manual] [--note "..."]``."""

from django.core.management.base import BaseCommand, CommandError

from apps.staffdesk import backups


class Command(BaseCommand):
    help = 'Back up the database to backups/db/ (see apps.staffdesk.backups).'

    def add_arguments(self, parser):
        parser.add_argument('--kind', default=backups.KIND_MANUAL, choices=backups.KINDS)
        parser.add_argument('--note', default='')
        parser.add_argument('--prune-only', action='store_true', help='Only apply the retention rules.')

    def handle(self, *args, **opts):
        if opts['prune_only']:
            self.stdout.write(f'Removed: {", ".join(backups.prune()) or "nothing"}')
            return
        try:
            meta = backups.create_backup(opts['kind'], by='command line', note=opts['note'])
        except backups.BackupError as exc:
            from core.errors import report
            report(exc.code, exc, context={'detail': exc.detail[-500:]})
            raise CommandError(f'{exc} [{exc.code}] {exc.detail[-300:]}')
        self.stdout.write(self.style.SUCCESS(f'{meta["name"]} ({meta["size"] // 1024} KB)'))
