"""Backups: real pg_dump restore points, retention, and the admin-only page."""

import shutil
import tempfile
from pathlib import Path
from unittest import mock

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.accounts.models import ActivityLog
from apps.diagnostics.models import ErrorEvent
from apps.livesessions.tests import make_user

from . import backups

ROOT = tempfile.mkdtemp(prefix='ucs-backup-test-')


@override_settings(BACKUP_ROOT=ROOT)
class BackupTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.admin = make_user('boss', 'admin')
        cls.admin.set_password('s3cret-pass!')
        cls.admin.save()
        cls.staff = make_user('staffer', 'staff')

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(ROOT, ignore_errors=True)

    def tearDown(self):
        for p in Path(ROOT).glob('*'):
            p.unlink()

    def test_backup_is_a_real_readable_dump_with_metadata(self):
        meta = backups.create_backup(backups.KIND_MANUAL, by='Test', note='before import')
        path = backups.path_for(meta['name'])
        self.assertTrue(backups.validate_dump(path))
        self.assertEqual(meta['note'], 'before import')
        self.assertEqual(len(meta['sha256']), 64)
        self.assertEqual(oct(path.stat().st_mode & 0o777), '0o600')
        self.assertEqual([m['name'] for m in backups.list_backups()], [meta['name']])

    def test_retention_keeps_the_newest_scheduled(self):
        with mock.patch.dict(backups.RETENTION, {backups.KIND_SCHEDULED: 2}):
            names = [backups.create_backup(backups.KIND_SCHEDULED)['name'] for _ in range(3)]
        kept = {m['name'] for m in backups.list_backups()}
        self.assertEqual(kept, set(names[1:]))

    def test_names_outside_the_folder_are_refused(self):
        for bad in ('../../etc/passwd', 'ucs-x.dump', '/tmp/a.dump', 'ucs-20260101-000000-manual.dump'):
            with self.assertRaises(backups.BackupError):
                backups.path_for(bad)

    def test_upload_must_be_a_dump(self):
        with self.assertRaises(backups.BackupError) as ctx:
            backups.import_upload(SimpleUploadedFile('x.dump', b'not a dump'))
        self.assertEqual(ctx.exception.code, 'BKP-1001')

    def test_page_is_for_admins_only(self):
        self.client.force_login(self.staff)
        self.assertRedirects(self.client.get(reverse('staffdesk:backups')), reverse('myhub:index'),
                             fetch_redirect_response=False)
        self.assertTrue(ErrorEvent.objects.filter(code='BKP-2001').exists())
        self.client.force_login(self.admin)
        self.assertEqual(self.client.get(reverse('staffdesk:backups')).status_code, 200)

    def test_back_up_now_download_and_audit(self):
        self.client.force_login(self.admin)
        self.client.post(reverse('staffdesk:backup-create'), {'note': 'test'})
        name = backups.list_backups()[0]['name']
        r = self.client.get(reverse('staffdesk:backup-download', args=[name]))
        self.assertEqual(r.status_code, 200)
        self.assertTrue(ActivityLog.objects.filter(description__contains=f'downloaded {name}').exists())
        self.assertIn('downloaded', (Path(ROOT) / 'audit.log').read_text())

    def test_restore_needs_the_word_and_the_password(self):
        name = backups.create_backup()['name']
        self.client.force_login(self.admin)
        url = reverse('staffdesk:backup-restore', args=[name])
        with mock.patch.object(backups, 'start_restore') as start:
            self.client.post(url, {'confirm': 'restore', 'password': 's3cret-pass!'})
            self.client.post(url, {'confirm': 'RESTORE', 'password': 'wrong'})
            start.assert_not_called()
            self.client.post(url, {'confirm': 'RESTORE', 'password': 's3cret-pass!'})
            start.assert_called_once()

    def test_scheduled_job_entry_point(self):
        self.assertIn('backed up to ucs-', backups.scheduled_backup())
