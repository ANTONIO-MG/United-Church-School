"""The demo lesson seed: Term 1, Week 1 — three days for every grade and subject.

Two halves. The **data** tests run without the database: every offering on the
spine has three well-formed days, every quiz answer key points at a real option
and every video is either a YouTube id or a search fallback. The **build** tests
seed a few offerings onto a real spine and walk them the way a learner and a
member of staff would — lesson page, schedule, quiz, homework, PDF.
"""
import re
import shutil
import tempfile

from django.core.files.storage import FileSystemStorage
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse

from apps.accounts.models import Person
from apps.assessments.models import Assessment, Question
from core import seed_lessons
from core.seed_lessons import build

from . import models

User = get_user_model()
TMP_MEDIA = tempfile.mkdtemp(prefix='ucs-seed-lessons-')
SAMPLE = [(1, 'MATH'), (10, 'PHYS-SCI'), (12, 'ZUL-FAL')]


class LessonDataTests(SimpleTestCase):
    """The content itself — no database needed."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.data = seed_lessons.load()

    def test_data_is_valid(self):
        self.assertEqual(seed_lessons.validate(self.data), [])

    def test_every_offering_on_the_spine_has_content(self):
        missing = [key for key in seed_lessons.expected_keys() if key not in self.data]
        self.assertEqual(missing, [], f'no lesson data for {missing}')
        self.assertEqual(len(seed_lessons.expected_keys()), 103)

    def test_three_days_with_quiz_and_homework(self):
        for key, spec in self.data.items():
            self.assertEqual(len(spec['days']), 3, key)
            for day in spec['days']:
                self.assertGreaterEqual(len(day['quiz']), 3, key)
                self.assertTrue(day['homework']['tasks'], key)

    def test_videos_are_youtube_ids_or_search_links(self):
        for key, spec in self.data.items():
            for day in spec['days']:
                video = day['video']
                if 'id' in video:
                    self.assertRegex(video['id'], r'^[A-Za-z0-9_-]{11}$', key)
                else:
                    self.assertTrue(video['search'].strip(), key)

    def test_worksheet_renders_as_pdf(self):
        from core.seed_lessons.pdf import worksheet_pdf
        spec = self.data[(4, 'ENG-HL')] if (4, 'ENG-HL') in self.data else next(iter(self.data.values()))
        pdf = worksheet_pdf(grade=4, subject='English Home Language', day_number=1,
                            day=spec['days'][0], topic=spec['topic'], date_label='Wednesday 14 January 2026')
        self.assertTrue(pdf.startswith(b'%PDF'))


def _file_fields():
    """The FileFields the seeder writes to. Their storage is resolved once, when
    the model loads, so ``override_settings`` cannot move it — swap it here."""
    return [models.LessonResource._meta.get_field('file'),
            models.LessonBlock._meta.get_field('media'),
            models.ModuleMaterial._meta.get_field('file')]


@override_settings(MEDIA_ROOT=TMP_MEDIA)
class SeedLessonsBuildTests(TestCase):
    """Seeding onto the real spine, then opening it as a learner and as staff."""

    @classmethod
    def setUpClass(cls):
        cls._storages = [(f, f.storage) for f in _file_fields()]
        scratch = FileSystemStorage(location=TMP_MEDIA, base_url='/media/')
        for f in _file_fields():
            f.storage = scratch
        super().setUpClass()

    @classmethod
    def setUpTestData(cls):
        from core import academic_spine
        academic_spine.seed(calendar=False, verbose=False, logos=False)
        # Only the sample pairs, not every code in every sample grade.
        cls.stats = build.Stats()
        for grade, code in SAMPLE:
            stats = build.seed(grades=[grade], subjects=[code])
            cls.stats.offerings += stats.offerings
            cls.stats.lessons += stats.lessons
            cls.stats.pdfs += stats.pdfs

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        for f, storage in cls._storages:
            f.storage = storage
        shutil.rmtree(TMP_MEDIA, ignore_errors=True)

    # -- helpers ---------------------------------------------------------------
    def offering(self, grade, code):
        return models.ProgrammeModule.objects.get(
            programme__institution__code='UCS', programme__grade=grade, code=code)

    def user(self, username, role, *, superuser=False):
        user = User.objects.create_user(username=username, email=f'{username}@example.com',
                                        password='x', is_staff=superuser,
                                        is_superuser=superuser)
        person = Person.objects.get(user=user)
        person.user_type = role
        person.registered = True
        person.profile_status = True
        person.save()
        return User.objects.get(pk=user.pk)

    def learner_on(self, offering):
        from core import academic_spine
        learner = self.user(f'learner-{offering.pk}', 'student')
        academic_spine.enrol_student(learner.profile, offering.programme, offerings=[offering])
        return User.objects.get(pk=learner.pk)

    # -- structure -------------------------------------------------------------
    def test_counts(self):
        self.assertEqual(self.stats.offerings, len(SAMPLE))
        self.assertEqual(self.stats.lessons, 3 * len(SAMPLE))
        self.assertEqual(self.stats.pdfs, 3 * len(SAMPLE))

    def test_topic_schedule_and_lessons(self):
        for grade, code in SAMPLE:
            offering = self.offering(grade, code)
            topic = models.Topic.objects.get(programme_module=offering, code='T1W1')
            week = models.ModuleWeek.objects.get(phase__programme_module=offering, number=1)
            self.assertEqual((week.phase.kind, week.phase.sequence), ('term', 1))
            self.assertEqual(week.phase.display_title, 'Term 1')
            self.assertIsNone(week.phase.cohort_id)
            self.assertTrue(week.phase.is_published and week.is_published)
            self.assertIn(topic, week.topic_list)
            lessons = list(models.Lesson.objects.filter(topic=topic).order_by('title'))
            self.assertEqual([lesson.title[:5] for lesson in lessons], ['Day 1', 'Day 2', 'Day 3'])
            for lesson in lessons:
                self.assertTrue(lesson.is_live)
                self.assertEqual(lesson.module, offering)
                types = set(lesson.blocks.values_list('block_type', flat=True))
                self.assertTrue({'text', 'callout', 'file', 'quiz', 'section'} <= types, types)
                self.assertTrue(types & {'video', 'callout'})
                pdf = lesson.resources.get(kind='pdf')
                with pdf.file.open('rb') as handle:
                    self.assertEqual(handle.read(4), b'%PDF')
            # Four schedule items a day: lesson, worksheet, quiz, homework.
            self.assertEqual(week.materials.filter(is_published=True).count(), 12)

    def test_quiz_and_homework(self):
        offering = self.offering(10, 'PHYS-SCI')
        quizzes = Assessment.objects.filter(module=offering, kind='quiz')
        homework = Assessment.objects.filter(module=offering, kind='assignment')
        self.assertEqual(quizzes.count(), 3)
        self.assertEqual(homework.count(), 3)
        for quiz in quizzes:
            self.assertEqual(quiz.status, Assessment.STATUS_OPEN)
            self.assertIsNotNone(quiz.lesson_id)
            questions = Question.objects.filter(section__assessment=quiz)
            self.assertTrue(questions.exists())
            for question in questions:
                self.assertTrue(question.is_auto_marked)
                self.assertEqual(question.choices.filter(is_correct=True).count(), 1)
            self.assertEqual(quiz.total_marks, questions.count())
        for task in homework:
            self.assertEqual(task.status, Assessment.STATUS_OPEN)
            self.assertIn('Due', task.description)
            self.assertTrue(Question.objects.filter(section__assessment=task).exists())

    def test_rerun_is_idempotent_and_clear_rebuilds(self):
        offering = self.offering(1, 'MATH')
        before = models.Lesson.objects.filter(module=offering).count()
        again = build.seed(grades=[1], subjects=['MATH'])
        self.assertEqual((again.offerings, again.skipped), (0, 1))
        self.assertEqual(models.Lesson.objects.filter(module=offering).count(), before)
        rebuilt = build.seed(grades=[1], subjects=['MATH'], clear_first=True)
        self.assertEqual(rebuilt.lessons, 3)
        self.assertEqual(models.Lesson.objects.filter(module=offering).count(), before)
        self.assertEqual(Assessment.objects.filter(module=offering).count(), 6)
        self.assertEqual(models.ModuleMaterial.objects.filter(phase__programme_module=offering)
                         .count(), 12)

    def test_command(self):
        call_command('seed_lessons', grade=[2], subject=['ENG-HL'], verbosity=0)
        offering = self.offering(2, 'ENG-HL')
        self.assertEqual(models.Lesson.objects.filter(topic__programme_module=offering,
                                                      topic__code='T1W1').count(), 3)

    # -- rendering -------------------------------------------------------------
    def test_learner_can_open_everything(self):
        for grade, code in SAMPLE:
            offering = self.offering(grade, code)
            learner = self.learner_on(offering)
            self.client.force_login(learner)
            for lesson in models.Lesson.objects.filter(module=offering):
                response = self.client.get(reverse('learning:lesson-view', args=[lesson.pk]))
                self.assertEqual(response.status_code, 200, lesson.title)
                html = response.content.decode()
                self.assertIn('lv-filecard', html)                       # the PDF worksheet
                self.assertRegex(html, r'worksheet[\w-]*\.pdf')
                self.assertTrue('data-plyr-embed-id' in html
                                or 'youtube.com/results' in html)        # the video
                for assessment in lesson.assessments.all():              # quiz + homework
                    self.assertIn(reverse('assessments:take', args=[assessment.pk]), html)
            feed = self.client.get(reverse('learning:module-feed', args=[offering.pk]))
            self.assertEqual(feed.status_code, 200)
            self.assertIn('Day 1', feed.content.decode())
            for assessment in Assessment.objects.filter(module=offering):
                response = self.client.get(reverse('assessments:take', args=[assessment.pk]))
                self.assertEqual(response.status_code, 200, assessment.title)
            self.client.logout()

    def test_staff_can_open_lessons(self):
        staff = self.user('seed-staff', 'admin', superuser=True)
        self.client.force_login(staff)
        offering = self.offering(12, 'ZUL-FAL')
        for lesson in models.Lesson.objects.filter(module=offering):
            response = self.client.get(reverse('learning:lesson-view', args=[lesson.pk]))
            self.assertEqual(response.status_code, 200)
            self.assertTrue(re.search(r'Day \d', response.content.decode()))
        feed = self.client.get(reverse('learning:module-feed', args=[offering.pk]))
        self.assertEqual(feed.status_code, 200)
        self.assertIn('Term 1', feed.content.decode())
