"""Automatic notifications: what queues, what sends, what is folded or dropped."""

from datetime import timedelta

from django.core import mail
from django.test import TestCase, override_settings
from django.utils import timezone

from apps.assessments.models import Assessment, AssessmentAttempt
from apps.learning.models import Lesson, ModuleEnrolment, ModuleMaterial, ModulePhase, ProgrammeEnrolment
from apps.livesessions.models import YouTubePlaylist, YouTubeVideo
from apps.livesessions.tests import make_user
from apps.tasks.models import Task, TaskAssignment
from core.testing import make_module

from . import auto, weekly
from .models import AutoNotice, Notification, NotificationPreference

LOCMEM = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}


@override_settings(CACHES=LOCMEM, EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class AutoNoticeTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.fac = make_module('Financial Accounting', 'FAC')
        cls.other = make_module('Taxation', 'TAX')
        cls.phase = ModulePhase.objects.create(programme_module=cls.fac, kind=ModulePhase.KIND_TEST, sequence=1)
        cls.educator = make_user('edu', 'educator')
        cls.educator.profile.taught_modules.add(cls.fac)
        cls.student = make_user('stu', 'student')
        ProgrammeEnrolment.objects.create(person=cls.student.profile, programme=cls.fac.programme)
        ModuleEnrolment.objects.create(person=cls.student.profile, programme_module=cls.fac)
        cls.outsider = make_user('out', 'student')
        ModuleEnrolment.objects.create(person=cls.outsider.profile, programme_module=cls.other)

    def material(self, title='Blueprint 2026', **kw):
        with self.captureOnCommitCallbacks(execute=True):
            return ModuleMaterial.objects.create(phase=self.phase, kind=ModuleMaterial.KIND_BLUEPRINT,
                                                 title=title, **kw)

    def notes_for(self, user):
        return Notification.objects.filter(recipient=user)

    def test_new_material_reaches_module_students_and_educators_only(self):
        self.material()
        auto.run()
        self.assertEqual(self.notes_for(self.student).count(), 1)
        self.assertEqual(self.notes_for(self.educator).count(), 1)
        self.assertFalse(self.notes_for(self.outsider).exists())
        self.assertIn('blueprint', self.notes_for(self.student).get().title.lower())
        self.assertTrue(mail.outbox)

    def test_editing_an_old_material_does_not_announce_it_again(self):
        m = self.material()
        auto.run()
        with self.captureOnCommitCallbacks(execute=True):
            m.title = 'Blueprint 2026 (corrected)'
            m.save()
        auto.run()
        self.assertEqual(self.notes_for(self.student).count(), 1)

    def test_several_items_are_folded_into_one_notification(self):
        for t in ('Blueprint', 'Mock exam 1', 'Solutions 1'):
            self.material(t)
        auto.run()
        note = self.notes_for(self.student).get()
        self.assertTrue(note.title.startswith('3 new items'))
        self.assertIn('Solutions 1', note.body)

    def test_embargoed_material_waits_and_unpublished_is_dropped(self):
        self.material('Later', available_from=timezone.now() + timedelta(hours=2))
        gone = self.material('Gone')
        ModuleMaterial.objects.filter(pk=gone.pk).update(is_published=False)
        auto.run()
        self.assertFalse(self.notes_for(self.student).exists())
        self.assertEqual(AutoNotice.objects.get(key=f'material:{gone.pk}').dropped, 'unpublished')
        auto.run(now=timezone.now() + timedelta(hours=3))
        # run() checks release against the real clock, so move the embargo instead.
        ModuleMaterial.objects.filter(title='Later').update(available_from=timezone.now() - timedelta(minutes=1))
        AutoNotice.objects.filter(key__startswith='material:').update(due_at=timezone.now() - timedelta(minutes=1))
        auto.run()
        self.assertEqual(self.notes_for(self.student).count(), 1)

    def test_category_switch_is_respected(self):
        pref = NotificationPreference.for_user(self.student)
        pref.notify_content = False
        pref.save()
        self.material()
        auto.run()
        self.assertFalse(self.notes_for(self.student).exists())
        self.assertTrue(self.notes_for(self.educator).exists())

    def test_lesson_publish_and_assessment_open(self):
        with self.captureOnCommitCallbacks(execute=True):
            lesson = Lesson.objects.create(module=self.fac, title='Consolidations', status=Lesson.STATUS_DRAFT)
        with self.captureOnCommitCallbacks(execute=True):
            lesson.status = Lesson.STATUS_PUBLISHED
            lesson.save()
        with self.captureOnCommitCallbacks(execute=True):
            Assessment.objects.create(module=self.fac, title='Mock 2', kind='test', total_marks=50,
                                      status=Assessment.STATUS_OPEN)
        auto.run()
        titles = sorted(self.notes_for(self.student).values_list('title', flat=True))
        self.assertEqual(titles, ['Mock 2 is open', 'New lesson: Consolidations'])
        # Educators are told about lessons, not about tests opening for students.
        self.assertEqual(list(self.notes_for(self.educator).values_list('title', flat=True)),
                         ['New lesson: Consolidations'])

    def test_task_assigned_but_not_past_ones(self):
        with self.captureOnCommitCallbacks(execute=True):
            task = Task.objects.create(title='Read IFRS 10', due_date=timezone.now() + timedelta(days=3))
            TaskAssignment.objects.get_or_create(task=task, user=self.student)
        with self.captureOnCommitCallbacks(execute=True):
            old = Task.objects.create(title='Old', due_date=timezone.now() - timedelta(days=3))
            TaskAssignment.objects.get_or_create(task=old, user=self.student)
        auto.run()
        self.assertEqual(list(self.notes_for(self.student).values_list('title', flat=True)),
                         ['New task: Read IFRS 10'])

    def test_new_video_but_not_back_catalogue(self):
        pl = YouTubePlaylist.objects.create(youtube_id='PL1', title='FAC lectures', programme_module=self.fac)
        with self.captureOnCommitCallbacks(execute=True):
            YouTubeVideo.objects.create(youtube_id='new00000001', playlist=pl, title='Week 3',
                                        published_at=timezone.now())
            YouTubeVideo.objects.create(youtube_id='old00000001', playlist=pl, title='2024 lecture',
                                        published_at=timezone.now() - timedelta(days=400))
        auto.run()
        self.assertEqual(list(self.notes_for(self.student).values_list('title', flat=True)),
                         ['New video: Week 3'])

    def test_result_is_queued_once(self):
        paper = Assessment.objects.create(module=self.fac, title='Mock 1', kind='test', total_marks=50)
        attempt = AssessmentAttempt.objects.create(assessment=paper, student=self.student, score=34,
                                                   status=AssessmentAttempt.STATUS_MARKED)
        auto.queue_result(attempt, marker=self.educator)
        auto.queue_result(attempt, marker=self.educator)
        auto.run()
        self.assertEqual(list(self.notes_for(self.student).values_list('title', flat=True)),
                         ['Your Mock 1 has been marked — 68%'])

    def test_weekly_summary_once_per_week_and_skips_empty(self):
        Assessment.objects.create(module=self.fac, title='Mock 3', kind='test', total_marks=50,
                                  status=Assessment.STATUS_OPEN)
        weekly.run(force=True)
        weekly.run(force=True)
        note = self.notes_for(self.student).get(title='Your week ahead')
        self.assertIn('Mock 3 is open', note.body)
        self.assertFalse(self.notes_for(self.outsider).filter(title='Your week ahead').exists())

    def test_weekly_only_on_monday_morning(self):
        tuesday = timezone.make_aware(timezone.datetime(2026, 10, 6, 9, 0))
        self.assertEqual(weekly.run(now=tuesday), 'not Monday morning')

    def test_reengagement_nudges_quiet_students_with_work_once(self):
        Assessment.objects.create(module=self.fac, title='Mock 4', kind='test', total_marks=50,
                                  status=Assessment.STATUS_OPEN)
        type(self.student).objects.filter(pk=self.student.pk).update(
            last_login=timezone.now() - timedelta(days=9))
        self.assertEqual(weekly.run_reengage(), 're-engagement nudges: 1')
        self.assertEqual(weekly.run_reengage(), 're-engagement nudges: 0')
        note = self.notes_for(self.student).get()
        self.assertIn('9 days', note.title)
        self.assertIn('Mock 4', note.body)

    def test_whatsapp_week_command(self):
        from .whatsapp_bot import reply_to
        Assessment.objects.create(module=self.fac, title='Mock 5', kind='test', total_marks=50,
                                  status=Assessment.STATUS_OPEN)
        text, command = reply_to('+27000000000', 'week', person=self.student.profile)
        self.assertEqual(command, 'week')
        self.assertIn('Mock 5', text)
