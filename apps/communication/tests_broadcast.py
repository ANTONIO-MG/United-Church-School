"""The broadcast composer: audience resolution, sending, scheduling and the pages."""

import shutil
import tempfile
from datetime import timedelta

from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import ParentLink
from apps.learning.models import Cohort, Institution, ModuleEnrolment, Programme, ProgrammeEnrolment
from apps.livesessions.tests import make_user
from core.testing import make_module

from . import broadcast
from .models import Announcement, AnnouncementAttachment, Notification, NotificationPreference

MEDIA = tempfile.mkdtemp(prefix='ucs-broadcast-test-')
LOCMEM = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}


@override_settings(MEDIA_ROOT=MEDIA, CACHES=LOCMEM,
                   EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend', SITE_URL='https://ucs.test')
class BroadcastTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.inst = Institution.objects.create(code='UCS', name='United Church School')
        cls.other_inst = Institution.objects.create(code='UCP', name='United Church Preparatory School')
        cls.prog = Programme.objects.create(institution=cls.inst, code='GR10', name='Grade 10')
        cls.other_prog = Programme.objects.create(institution=cls.other_inst, code='GR07', name='Grade 7')
        cls.cohort = Cohort.objects.create(programme=cls.prog, code='10A')
        cls.fac = make_module('Mathematics', 'MATH', programme=cls.prog)
        cls.tax = make_module('English Home Language', 'ENG', programme=cls.prog)
        cls.other_mod = make_module('Natural Sciences', 'NS', programme=cls.other_prog)

        cls.admin = make_user('admin1', 'admin', first_name='Ada')
        cls.staff = make_user('staff1', 'staff', first_name='Sam')
        cls.educator = make_user('edu1', 'educator', first_name='Eve')
        cls.educator.profile.taught_modules.add(cls.fac)
        cls.student = make_user('stu1', 'student', first_name='Stu')
        ProgrammeEnrolment.objects.create(person=cls.student.profile, programme=cls.prog, cohort=cls.cohort)
        ModuleEnrolment.objects.create(person=cls.student.profile, programme_module=cls.fac)
        cls.tax_student = make_user('stu2', 'student', first_name='Tia')
        ProgrammeEnrolment.objects.create(person=cls.tax_student.profile, programme=cls.prog)
        ModuleEnrolment.objects.create(person=cls.tax_student.profile, programme_module=cls.tax)
        cls.other_student = make_user('stu3', 'student', first_name='Uma')
        ProgrammeEnrolment.objects.create(person=cls.other_student.profile, programme=cls.other_prog)
        ModuleEnrolment.objects.create(person=cls.other_student.profile, programme_module=cls.other_mod)
        cls.parent = make_user('par1', 'parent', first_name='Pat')
        ParentLink.objects.create(parent=cls.parent, student=cls.student)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA, ignore_errors=True)

    def pks(self, qs):
        return set(qs.values_list('pk', flat=True))

    # --- audience -----------------------------------------------------------
    def test_module_reaches_its_students_and_educators_only(self):
        self.assertEqual(self.pks(broadcast.audience_users(modules=[self.fac])),
                         {self.student.pk, self.educator.pk})

    def test_institution_reaches_enrolled_and_teaching(self):
        self.assertEqual(self.pks(broadcast.audience_users(institutions=[self.inst])),
                         {self.student.pk, self.tax_student.pk, self.educator.pk})

    def test_cohort_and_role_filter(self):
        self.assertEqual(self.pks(broadcast.audience_users(cohorts=[self.cohort], roles=['student'])),
                         {self.student.pk})

    def test_named_people_survive_the_role_filter(self):
        got = self.pks(broadcast.audience_users(programmes=[self.other_prog], users=[self.staff],
                                                roles=['student']))
        self.assertEqual(got, {self.other_student.pk, self.staff.pk})

    def test_parents_are_copied_when_asked(self):
        got = self.pks(broadcast.audience_users(modules=[self.fac], include_parents=True))
        self.assertIn(self.parent.pk, got)
        got = self.pks(broadcast.audience_users(modules=[self.fac], roles=['parent']))
        self.assertEqual(got, {self.parent.pk})

    def test_everyone_by_role(self):
        got = self.pks(broadcast.audience_users(everyone=True, roles=['educator']))
        self.assertEqual(got, {self.educator.pk})

    def test_inactive_accounts_are_skipped(self):
        self.student.is_active = False
        self.student.save()
        self.assertNotIn(self.student.pk, self.pks(broadcast.audience_users(modules=[self.fac])))

    # --- sending -------------------------------------------------------------
    def make(self, **kw):
        a = Announcement.objects.create(sender=self.staff, title='New blueprint', body='See https://x.test',
                                        audience=Announcement.AUDIENCE_TARGETED, **kw)
        return a

    def test_send_creates_notifications_and_emails_once(self):
        a = self.make()
        a.modules.add(self.fac)
        AnnouncementAttachment.objects.create(
            announcement=a, file=SimpleUploadedFile('blueprint.pdf', b'%PDF-1.4 x'), original_name='blueprint.pdf')
        self.assertEqual(broadcast.send(a), 2)
        self.assertEqual(a.status, Announcement.STATUS_SENT)
        self.assertEqual(Notification.objects.filter(announcement=a).count(), 2)
        self.assertEqual(len(mail.outbox), 2)
        self.assertIn('blueprint.pdf', [getattr(a, 'filename', None) or (a.get_filename() if hasattr(a, 'get_filename') else None)
                                        for a in mail.outbox[0].attachments])
        self.assertIn('https://ucs.test/communication/notifications/', mail.outbox[0].body)
        # A second call (double click, scheduler) sends nothing more.
        self.assertEqual(broadcast.send(a), 2)
        self.assertEqual(Notification.objects.filter(announcement=a).count(), 2)

    def test_muted_announcements_respected_unless_important(self):
        pref = NotificationPreference.for_user(self.student)
        pref.notify_announcements = False
        pref.save()
        a = self.make(send_email=False)
        a.modules.add(self.fac)
        broadcast.send(a)
        self.assertFalse(Notification.objects.filter(announcement=a, recipient=self.student).exists())
        b = self.make(send_email=False, is_important=True)
        b.modules.add(self.fac)
        broadcast.send(b)
        self.assertTrue(Notification.objects.filter(announcement=b, recipient=self.student).exists())

    def test_retry_after_failure_does_not_repeat(self):
        a = self.make(send_email=False)
        a.modules.add(self.fac)
        Notification.objects.create(recipient=self.student, announcement=a, title='x')
        Announcement.objects.filter(pk=a.pk).update(status=Announcement.STATUS_FAILED)
        a.refresh_from_db()
        self.assertEqual(broadcast.send(a), 2)
        self.assertEqual(Notification.objects.filter(announcement=a, recipient=self.student).count(), 1)

    def test_send_due_only_sends_due(self):
        due = self.make(send_email=False, status=Announcement.STATUS_SCHEDULED,
                        scheduled_for=timezone.now() - timedelta(minutes=1))
        due.users.add(self.student)
        later = self.make(send_email=False, status=Announcement.STATUS_SCHEDULED,
                          scheduled_for=timezone.now() + timedelta(hours=1))
        later.users.add(self.student)
        broadcast.send_due()
        due.refresh_from_db()
        later.refresh_from_db()
        self.assertEqual(due.status, Announcement.STATUS_SENT)
        self.assertEqual(later.status, Announcement.STATUS_SCHEDULED)

    def test_embed_urls(self):
        self.assertEqual(broadcast.embed_url_for('https://youtu.be/dQw4w9WgXcQ'),
                         'https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ?rel=0')
        self.assertIn('dQw4w9WgXcQ', broadcast.embed_url_for('https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=3'))
        self.assertEqual(broadcast.embed_url_for('https://vimeo.com/12345'), 'https://player.vimeo.com/video/12345')
        self.assertEqual(broadcast.embed_url_for('https://example.com/video.mp4'), '')

    # --- pages ---------------------------------------------------------------
    def test_students_and_educators_cannot_open_the_composer(self):
        for user in (self.student, self.educator):
            self.client.force_login(user)
            r = self.client.get(reverse('communication:announcement-compose'))
            self.assertNotEqual(r.status_code, 200)

    def test_compose_send_now_with_file_and_video(self):
        self.client.force_login(self.staff)
        r = self.client.post(reverse('communication:announcement-compose'), {
            'title': 'Mock exam 2 is open', 'body': 'Good luck', 'level': 'info',
            'media_url': 'https://youtu.be/dQw4w9WgXcQ', 'url': '/assessments/', 'url_label': 'Start',
            'audience': 'targeted', 'modules': [self.fac.pk], 'roles': ['student'],
            'send_email': 'on', 'when': 'now',
            'attachments': [SimpleUploadedFile('poster.png', b'\x89PNG\r\n', content_type='image/png')],
        })
        a = Announcement.objects.get(title='Mock exam 2 is open')
        self.assertRedirects(r, reverse('communication:announcement-detail', args=[a.pk]))
        self.assertEqual(a.status, Announcement.STATUS_SENT)
        self.assertEqual(a.recipient_count, 1)
        self.assertEqual(a.attachments.get().kind, 'image')
        note = Notification.objects.get(announcement=a)
        self.client.force_login(self.student)
        page = self.client.get(reverse('communication:notification-detail', args=[note.pk]))
        self.assertContains(page, 'youtube-nocookie.com/embed/dQw4w9WgXcQ')
        self.assertContains(page, 'poster.png')
        self.assertContains(page, 'Start')

    def test_compose_rejects_script_links_and_empty_targets(self):
        self.client.force_login(self.staff)
        r = self.client.post(reverse('communication:announcement-compose'), {
            'title': 'x', 'body': 'y', 'level': 'info', 'url': 'javascript:alert(1)',
            'audience': 'targeted', 'when': 'now'})
        self.assertEqual(r.status_code, 200)
        self.assertFalse(Announcement.objects.filter(title='x').exists())
        self.assertIn('url', r.context['form'].errors)
        self.assertIn('audience', r.context['form'].errors)

    def test_schedule_then_cancel(self):
        self.client.force_login(self.staff)
        when = (timezone.localtime() + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M')
        self.client.post(reverse('communication:announcement-compose'), {
            'title': 'Tomorrow', 'body': 'b', 'level': 'warning', 'audience': 'all',
            'when': 'later', 'scheduled_for': when})
        a = Announcement.objects.get(title='Tomorrow')
        self.assertEqual(a.status, Announcement.STATUS_SCHEDULED)
        self.assertFalse(Notification.objects.filter(announcement=a).exists())
        self.client.post(reverse('communication:announcement-action', args=[a.pk]), {'action': 'cancel'})
        a.refresh_from_db()
        self.assertEqual(a.status, Announcement.STATUS_CANCELLED)

    def test_audience_preview_and_people_search(self):
        self.client.force_login(self.admin)
        r = self.client.post(reverse('communication:announcement-audience'),
                             {'audience': 'targeted', 'institutions': [self.inst.pk], 'roles': ['student']})
        self.assertEqual(r.json()['total'], 2)
        r = self.client.get(reverse('communication:announcement-people'), {'q': 'Uma'})
        self.assertEqual([p['id'] for p in r.json()['results']], [self.other_student.pk])

    def test_list_and_detail_render(self):
        a = self.make(send_email=False)
        a.modules.add(self.fac)
        broadcast.send(a)
        Notification.objects.filter(announcement=a, recipient=self.student).update(is_read=True)
        self.client.force_login(self.staff)
        r = self.client.get(reverse('communication:announcements'))
        self.assertContains(r, 'New blueprint')
        self.assertContains(r, '50%')
        r = self.client.get(reverse('communication:announcement-detail', args=[a.pk]))
        self.assertContains(r, 'Remind unread')
        r = self.client.get(reverse('communication:announcement-compose') + f'?copy={a.pk}&unread=1')
        self.assertEqual(r.context['form'].initial['users'], [self.educator.pk])

    def test_deep_link_preselects_a_person(self):
        self.client.force_login(self.staff)
        r = self.client.get(reverse('communication:announcement-compose') + f'?user={self.student.pk}')
        self.assertContains(r, f'<option value="{self.student.pk}" selected')
