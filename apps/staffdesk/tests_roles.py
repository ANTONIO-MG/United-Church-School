"""Who may open what: learners, parents, educators, staff and the administrator.

Each role is checked against the pages that are *not* theirs — the office,
the system pages, another grade's learners — and the class-teacher page is
checked end to end.
"""

from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import ParentLink
from apps.learning.models import Cohort
from apps.livesessions.tests import make_user
from apps.myhub.models import Event
from core.scoping import can_view_person
from core.testing import enrol, make_module, make_programme


class RoleAccessTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.gr5 = make_programme('UCS', 'GR05', grade=5)
        cls.gr6 = make_programme('UCS', 'GR06', grade=6)
        cls.math5 = make_module('Mathematics Gr5', 'MATH5', programme=cls.gr5)
        cls.math6 = make_module('Mathematics Gr6', 'MATH6', programme=cls.gr6)
        cls.admin = make_user('root', 'admin')
        cls.staff = make_user('office', 'staff')
        cls.teacher = make_user('teach', 'educator', first_name='Thandi', last_name='Mokoena')
        cls.teacher.profile.taught_modules.add(cls.math5)
        cls.learner = make_user('lerato', 'student', first_name='Lerato', last_name='Dube')
        cls.other = make_user('sipho', 'student', first_name='Sipho', last_name='Nkosi')
        enrol(cls.learner.profile, cls.math5)
        enrol(cls.other.profile, cls.math6)
        cls.parent = make_user('mum', 'parent')
        ParentLink.objects.create(parent=cls.parent, student=cls.learner)

    def get(self, who, name, *args):
        self.client.force_login(who)
        return self.client.get(reverse(name, args=args))

    def test_event_management_is_for_the_office(self):
        for who in (self.teacher, self.learner, self.parent):
            r = self.get(who, 'myhub:event-management')
            self.assertEqual(r.status_code, 302, who.username)
        self.assertEqual(self.get(self.staff, 'myhub:event-management').status_code, 200)

    def test_someone_elses_reminder_is_private(self):
        mine = Event.objects.create(title='Dentist', start='2026-03-02T09:00+02:00',
                                    owner=self.learner, category=Event.CATEGORY_REMINDER)
        self.assertEqual(self.get(self.other, 'myhub:event-detail', mine.pk).status_code, 404)
        self.assertEqual(self.get(self.learner, 'myhub:event-detail', mine.pk).status_code, 200)

    def test_promotion_pages_are_closed_to_learners(self):
        self.assertEqual(self.get(self.learner, 'admissions:promotion').status_code, 404)
        self.assertEqual(self.get(self.teacher, 'admissions:promotion').status_code, 200)

    def test_analytics_is_for_the_office(self):
        self.assertEqual(self.get(self.teacher, 'analytics:dashboard').status_code, 302)
        self.assertEqual(self.get(self.staff, 'analytics:dashboard').status_code, 200)

    def test_system_pages_are_for_the_administrator(self):
        for name in ('staffdesk:ops-audit', 'staffdesk:ops-jobs', 'accounts:closed-accounts',
                     'diagnostics:log'):
            refused = 404 if name.startswith('diagnostics') else 302
            self.assertEqual(self.get(self.staff, name).status_code, refused, name)
            self.assertEqual(self.get(self.admin, name).status_code, 200, name)

    def test_learners_see_their_own_grade_and_teachers_only(self):
        self.assertTrue(can_view_person(self.learner, self.teacher.profile))
        self.assertFalse(can_view_person(self.learner, self.other.profile))
        self.assertFalse(can_view_person(self.teacher, self.other.profile))
        self.assertTrue(can_view_person(self.teacher, self.learner.profile))
        self.assertTrue(can_view_person(self.parent, self.learner.profile))
        self.assertFalse(can_view_person(self.parent, self.other.profile))
        r = self.get(self.learner, 'accounts:person-card', self.other.profile.pk)
        self.assertEqual(r.status_code, 404)

    def test_teacher_announcements_reach_only_their_subjects(self):
        self.client.force_login(self.teacher)
        r = self.client.post(reverse('communication:announcement-audience'),
                             {'audience': 'all'})
        self.assertEqual(r.json().get('total', 0), 0)
        r = self.client.post(reverse('communication:announcement-audience'),
                             {'audience': 'targeted', 'modules': [self.math6.pk]})
        self.assertEqual(r.json().get('total', 0), 0)
        r = self.client.post(reverse('communication:announcement-audience'),
                             {'audience': 'targeted', 'modules': [self.math5.pk]})
        self.assertEqual(r.json().get('total'), 2)            # the teacher and Lerato
        self.assertEqual(self.client.get(reverse('communication:announcement-compose')).status_code, 200)

    def test_a_teacher_cannot_open_someone_elses_notification(self):
        from apps.communication.models import Announcement
        office = Announcement.objects.create(title='Fees reminder', body='x', sender=self.staff)
        self.client.force_login(self.teacher)
        r = self.client.get(reverse('communication:announcement-detail', args=[office.pk]))
        self.assertEqual(r.status_code, 404)
        self.assertNotContains(self.client.get(reverse('communication:announcements')), 'Fees reminder')


class ClassTeacherPageTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.gr7 = make_programme('UCS', 'GR07', grade=7)
        cls.eng = make_module('English', 'ENG7', programme=cls.gr7)
        cls.staff = make_user('office', 'staff')
        cls.teacher = make_user('teach', 'educator', first_name='Thandi')
        cls.learner = make_user('lerato', 'student')

    def test_staff_set_class_and_subject_teachers_in_one_save(self):
        self.client.force_login(self.staff)
        url = reverse('staffdesk:class-teachers') + '?year=2027'
        self.assertContains(self.client.get(url), 'new 2027 class')
        self.client.post(url, {'year': '2027', f'new_class_{self.gr7.pk}': self.teacher.profile.pk,
                               f'subject_{self.eng.pk}': self.teacher.profile.pk})
        cohort = Cohort.objects.get(programme=self.gr7, code='2027')
        self.assertEqual(cohort.class_teacher, self.teacher.profile)
        self.assertIn(self.teacher.profile, self.eng.educators.all())
        self.client.post(url, {'year': '2027', f'class_{cohort.pk}': ''})
        cohort.refresh_from_db()
        self.assertIsNone(cohort.class_teacher)
        self.assertIn(self.teacher.profile, self.eng.educators.all())  # not posted → untouched

    def test_only_the_office_opens_it(self):
        for who in (self.teacher, self.learner):
            self.client.force_login(who)
            self.assertEqual(self.client.get(reverse('staffdesk:class-teachers')).status_code, 302)
