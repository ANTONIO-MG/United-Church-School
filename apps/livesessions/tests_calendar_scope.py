"""Grade-only visibility on the school calendar (apps.livesessions.academic).

A learner sees the whole-school dates plus their own grade's; a parent their
children's grades; an educator the grades they teach; admin and staff
everything. Estimated (unpublished) dates stay staff-only.
"""

from datetime import datetime

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from apps.accounts.models import ParentLink
from apps.learning.models import CalendarEvent, Programme, ProgrammeEnrolment

from . import sources
from .academic import grades_label, visible_events
from .tests import make_user


def grade(n):
    return Programme.objects.get(institution__code='UCS', grade=n)


def titles(user, **kwargs):
    return set(visible_events(user, **kwargs).values_list('title', flat=True))


def programme_grades(user, title):
    return set(visible_events(user).filter(title=title)
               .values_list('programme__grade', flat=True))


class GradeVisibilityTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed_school_structure', verbosity=0)
        cls.matric = make_user('cal-matric')
        ProgrammeEnrolment.objects.create(person=cls.matric.profile, programme=grade(12))
        cls.grade5 = make_user('cal-grade5')
        ProgrammeEnrolment.objects.create(person=cls.grade5.profile, programme=grade(5))
        cls.grade2 = make_user('cal-grade2')
        ProgrammeEnrolment.objects.create(person=cls.grade2.profile, programme=grade(2))
        cls.parent = make_user('cal-parent', 'parent')
        ParentLink.objects.create(parent=cls.parent, student=cls.grade5)
        ParentLink.objects.create(parent=cls.parent, student=cls.grade2)
        cls.teacher = make_user('cal-teacher', 'educator')
        grade(12).modules.get(code='MATH').educators.add(cls.teacher.profile)
        cls.admin = make_user('cal-admin', 'admin')
        cls.unenrolled = make_user('cal-nobody')

    def test_a_matric_sees_the_nsc_and_whole_school_dates_only(self):
        seen = titles(self.matric)
        self.assertIn('NSC (matric) final examinations', seen)
        self.assertIn('Preliminary (trial) examinations', seen)
        self.assertIn('Term 1 begins', seen)
        self.assertIn('Local Government Elections Day', seen)
        self.assertEqual(programme_grades(self.matric, 'NSC (matric) final examinations'), {12})
        self.assertFalse(visible_events(self.matric).filter(programme__grade__lt=12).exists())

    def test_a_grade_5_learner_does_not_see_matric_dates(self):
        seen = titles(self.grade5)
        self.assertNotIn('NSC (matric) final examinations', seen)
        self.assertNotIn('Preliminary (trial) examinations', seen)
        self.assertIn('Term 4 ends', seen)
        # Once the school confirms its own exam dates, Grade 5 sees Grade 5's.
        CalendarEvent.objects.update(is_published=True)
        self.assertIn('Final examinations', titles(self.grade5))
        self.assertEqual(set(visible_events(self.grade5).exclude(programme__isnull=True)
                             .values_list('programme__grade', flat=True)), {5})

    def test_estimates_stay_hidden_from_learners_and_parents(self):
        for user in (self.grade5, self.parent, self.matric):
            self.assertFalse(visible_events(user).filter(is_published=False).exists())
        self.assertNotIn('Mid-year examinations', titles(self.grade5))

    def test_a_parent_sees_each_childs_grade(self):
        CalendarEvent.objects.update(is_published=True)
        grades = set(visible_events(self.parent).exclude(programme__isnull=True)
                     .values_list('programme__grade', flat=True))
        self.assertEqual(grades, {2, 5})
        self.assertNotIn('NSC (matric) final examinations', titles(self.parent))

    def test_an_educator_sees_the_grades_they_teach(self):
        self.assertIn('NSC (matric) final examinations', titles(self.teacher))
        grades = set(visible_events(self.teacher).exclude(programme__isnull=True)
                     .values_list('programme__grade', flat=True))
        self.assertEqual(grades, {12})

    def test_admin_sees_everything_and_can_filter_by_grade(self):
        self.assertEqual(visible_events(self.admin).count(), CalendarEvent.objects.count())
        only_3 = visible_events(self.admin, grade=3)
        self.assertEqual(set(only_3.exclude(programme__isnull=True)
                             .values_list('programme__grade', flat=True)), {3})
        self.assertTrue(only_3.filter(is_published=False).exists())

    def test_someone_with_no_grade_sees_whole_school_dates_only(self):
        self.assertFalse(visible_events(self.unenrolled).exclude(programme__isnull=True).exists())
        self.assertIn('Term 1 begins', titles(self.unenrolled))

    def test_the_calendar_folds_a_multi_grade_date_into_one_entry(self):
        start = timezone.make_aware(datetime(2026, 5, 25))
        end = timezone.make_aware(datetime(2026, 6, 5))
        entries = [e for e in sources.entries_for(self.admin, start, end, kinds=['academic'])
                   if 'Mid-year examinations' in e.title]
        self.assertEqual(len(entries), 1)
        self.assertIn('Grades 4–12', entries[0].title)

    def test_the_2027_calendar_reaches_the_right_grade(self):
        start = timezone.make_aware(datetime(2027, 1, 1))
        end = timezone.make_aware(datetime(2027, 12, 31))
        seen = {e.title for e in sources.entries_for(self.matric, start, end, kinds=['academic'])}
        self.assertTrue(any('Term 1 begins' in t for t in seen))
        self.assertFalse(any('Foundation Phase' in t for t in seen))

    def test_the_calendar_page_and_feed_respect_the_grade(self):
        self.client.force_login(self.grade5)
        response = self.client.get('/calendar/feed.json?from=2026-10-01T00:00:00&to=2026-12-31T00:00:00')
        self.assertEqual(response.status_code, 200)
        body = response.content.decode()
        self.assertNotIn('NSC (matric)', body)
        self.assertIn('Term 4 ends', body)
        self.client.force_login(self.admin)
        page = self.client.get('/calendar/?m=2026-10&grade=12')
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, 'name="grade"')

    def test_a_parent_can_open_the_calendar(self):
        self.client.force_login(self.parent)
        self.assertEqual(self.client.get('/calendar/?m=2026-11').status_code, 200)


class GradesLabelTests(TestCase):
    def test_ranges(self):
        self.assertEqual(grades_label([12]), 'Grade 12')
        self.assertEqual(grades_label(range(4, 12)), 'Grades 4–11')
        self.assertEqual(grades_label([1, 2, 3, 7]), 'Grades 1–3, 7')
        self.assertEqual(grades_label([5, 6]), 'Grades 5 & 6')
