"""Purge soft-closed accounts whose 30-day grace period has elapsed.

For every user whose ``UserSettings.purge_at`` is in the past, the account is
parked in the archive park and then removed from the live system — see
:mod:`apps.accounts.archiving` for what "parked" means and what deliberately
stays behind (other people's threads, attributed to a discontinued user).

Run it from cron / Celery beat. ``--dry-run`` reports without changing anything.
All time comparisons use :func:`django.utils.timezone.now`.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts import archiving, models


class Command(BaseCommand):
    help = 'Archive and permanently purge accounts whose 30-day grace period has elapsed.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run', action='store_true',
            help='Report what would be purged without changing anything.')

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        now = timezone.now()

        due = (models.UserSettings.objects
               .filter(is_closing=True, purge_at__isnull=False, purge_at__lte=now)
               .select_related('user'))

        if not due.exists():
            self.stdout.write(self.style.SUCCESS('No accounts are due for purge.'))
            return

        count = 0
        for user_settings in due:
            user = user_settings.user
            username = user.get_username()

            if dry_run:
                self.stdout.write(
                    f'[dry-run] WOULD purge "{username}" <{user.email}> '
                    f'(closed {user_settings.closed_at:%Y-%m-%d}, '
                    f'purge due {user_settings.purge_at:%Y-%m-%d}).')
                count += 1
                continue

            archive = archiving.purge_account(user)
            self.stdout.write(self.style.SUCCESS(
                f'Purged "{username}" — {archive.content_rows} row(s) parked in '
                f'{archive.archive_dir}'))
            count += 1

        verb = 'would be purged' if dry_run else 'purged'
        self.stdout.write(self.style.SUCCESS(f'Done. {count} account(s) {verb}.'))
