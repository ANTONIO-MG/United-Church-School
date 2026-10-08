"""The daily register: automatic presence, teacher marks the exceptions."""

from datetime import date, datetime, timedelta
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import ParentLink, Person
from apps.communication.models import Notification
from apps.learning.models import Cohort, ProgrammeEnrolment
from core.testing import make_programme

from . import services
from .calendar import SCHOOL_TZ, is_school_day
from .models import AttendanceMark, DailyRegister

User = get_user_model()

# Term 4 2026 (Oct 6 – Dec 11). Thursday 8 Oct 2026 is an ordinary school day.
SCHOOL_DAY = date(2026, 10, 8)
SATURDAY = date(2026, 10, 10)


def _user(email, user_type, **names):
    user = User.objects.create_user(username=email, email=email, password='x')
    person = Person.objects.get(user=user)
    person.user_type = user_type
    person.registered = True
    person.profile_status = True
    for k, v in names.items():
        setattr(person, k, v)
    person.save()
    return User.objects.get(pk=user.pk)


class Fixture(TestCase):
    def setUp(self):
        self.g5 = make_programme('UCS', 'GR05', grade=5, name='Grade 5')
        self.g6 = make_programme('UCS', 'GR06', grade=6, name='Grade 6')
        self.teacher = _user('t5@example.com', 'educator', first_name='Thandi')
        self.other_teacher = _user('t6@example.com', 'educator', first_name='Sipho')
        self.c5 = Cohort.objects.create(programme=self.g5, code='2026', name='Grade 5 · 2026',
                                        class_teacher=self.teacher.profile)
        self.c6 = Cohort.objects.create(programme=self.g6, code='2026', name='Grade 6 · 2026',
                                        class_teacher=self.other_teacher.profile)
        self.amy = _user('amy@example.com', 'student', first_name='Amy')
        self.ben = _user('ben@example.com', 'student', first_name='Ben')
        self.cara = _user('cara@example.com', 'student', first_name='Cara')
        for s in (self.amy, self.ben):
            ProgrammeEnrolment.objects.create(person=s.profile, programme=self.g5, cohort=self.c5)
        ProgrammeEnrolment.objects.create(person=self.cara.profile, programme=self.g6, cohort=self.c6)
        self.parent = _user('mom@example.com', 'parent')
        ParentLink.objects.create(parent=self.parent, student=self.amy)
        self.cara_parent = _user('dad@example.com', 'parent')
        ParentLink.objects.create(parent=self.cara_parent, student=self.cara)
        self.admin = _user('office@example.com', 'admin')

    def today(self, day=SCHOOL_DAY):
        return mock.patch('apps.attendance.services.local_today', return_value=day)


class OpeningTests(Fixture):
    def test_calendar(self):
        self.assertTrue(is_school_day(SCHOOL_DAY))
        self.assertFalse(is_school_day(SATURDAY))
        self.assertFalse(is_school_day(date(2026, 12, 25)))
        self.assertFalse(is_school_day(date(2026, 10, 1)))      # between terms

    def test_registers_open_only_on_school_days_with_everyone_present(self):
        self.assertEqual(services.open_registers(SATURDAY), [])
        self.assertFalse(DailyRegister.objects.exists())

        opened = services.open_registers(SCHOOL_DAY)
        self.assertEqual(len(opened), 2)
        reg = DailyRegister.objects.get(cohort=self.c5, date=SCHOOL_DAY)
        self.assertEqual(reg.marks.count(), 2)
        self.assertFalse(reg.marks.exclude(status=AttendanceMark.PRESENT).exists())
        # The class teacher is asked to take it.
        self.assertTrue(Notification.objects.filter(recipient=self.teacher,
                                                    title__contains='Grade 5 · 2026').exists())
        self.assertIsNotNone(reg.task_id)
        # Idempotent.
        self.assertEqual(services.open_registers(SCHOOL_DAY), [])
        self.assertEqual(DailyRegister.objects.count(), 2)

    def test_job_opens_after_0630_and_auto_submits_after_close(self):
        early = datetime(2026, 10, 8, 6, 0, tzinfo=SCHOOL_TZ)
        services.run_daily(early)
        self.assertFalse(DailyRegister.objects.exists())
        services.run_daily(datetime(2026, 10, 8, 7, 0, tzinfo=SCHOOL_TZ))
        self.assertEqual(DailyRegister.objects.filter(status='open').count(), 2)
        services.run_daily(datetime(2026, 10, 8, 17, 30, tzinfo=SCHOOL_TZ))
        reg = DailyRegister.objects.get(cohort=self.c5)
        self.assertEqual(reg.status, 'submitted')
        self.assertTrue(reg.auto_submitted)
        self.assertEqual(reg.marks.filter(status='present').count(), 2)


class MarkingTests(Fixture):
    def setUp(self):
        super().setUp()
        services.open_registers(SCHOOL_DAY)
        self.reg = DailyRegister.objects.get(cohort=self.c5, date=SCHOOL_DAY)
        self.amy_mark = self.reg.marks.get(learner=self.amy.profile)
        self.ben_mark = self.reg.marks.get(learner=self.ben.profile)

    def _submit(self, user, data):
        self.client.force_login(user)
        with self.today(), mock.patch('apps.attendance.views.local_today', return_value=SCHOOL_DAY):
            return self.client.post(reverse('attendance:register', args=[self.reg.pk]), data)

    def test_teacher_marks_absentees_others_stay_present(self):
        self.client.force_login(self.teacher)
        with mock.patch('apps.attendance.services.local_today', return_value=SCHOOL_DAY):
            page = self.client.get(reverse('attendance:register', args=[self.reg.pk]))
        self.assertContains(page, 'Submit register')
        self.assertContains(page, 'Amy')
        resp = self._submit(self.teacher, {
            f'status_{self.amy_mark.pk}': 'absent', f'reason_{self.amy_mark.pk}': 'Sick',
            'action': 'submit'})
        self.assertEqual(resp.status_code, 302)
        self.reg.refresh_from_db()
        self.assertEqual(self.reg.status, 'submitted')
        self.assertFalse(self.reg.auto_submitted)
        self.assertEqual(self.reg.submitted_by, self.teacher.profile)
        self.amy_mark.refresh_from_db()
        self.ben_mark.refresh_from_db()
        self.assertEqual((self.amy_mark.status, self.amy_mark.reason), ('absent', 'Sick'))
        self.assertEqual(self.ben_mark.status, 'present')

    def test_other_teacher_cannot_open_or_mark_this_class(self):
        self.client.force_login(self.other_teacher)
        self.assertEqual(self.client.get(reverse('attendance:register', args=[self.reg.pk])).status_code, 403)
        resp = self._submit(self.other_teacher, {f'status_{self.amy_mark.pk}': 'absent', 'action': 'submit'})
        self.assertEqual(resp.status_code, 403)
        self.amy_mark.refresh_from_db()
        self.assertEqual(self.amy_mark.status, 'present')
        # And a learner cannot reach the register at all.
        self.client.force_login(self.amy)
        self.assertEqual(self.client.get(reverse('attendance:register', args=[self.reg.pk])).status_code, 403)

    def test_teacher_index_lists_own_classes_only(self):
        self.client.force_login(self.teacher)
        with mock.patch('apps.attendance.views.local_today', return_value=SCHOOL_DAY):
            resp = self.client.get(reverse('attendance:index'))
        self.assertContains(resp, 'Grade 5 · 2026')
        self.assertNotContains(resp, 'Grade 6 · 2026')

    def test_parents_notified_once_per_day(self):
        self._submit(self.teacher, {f'status_{self.amy_mark.pk}': 'absent', 'action': 'submit'})
        notes = Notification.objects.filter(recipient=self.parent, title__contains='marked absent')
        self.assertEqual(notes.count(), 1)
        self.assertFalse(Notification.objects.filter(recipient=self.cara_parent).exists())
        # Editing / re-saving the register the same day does not send it again.
        self._submit(self.teacher, {f'status_{self.amy_mark.pk}': 'absent',
                                    f'reason_{self.amy_mark.pk}': 'Flu', 'action': 'submit'})
        self.assertEqual(notes.count(), 1)

    def test_teacher_cannot_edit_last_weeks_register(self):
        old = DailyRegister.objects.create(cohort=self.c5, date=SCHOOL_DAY - timedelta(days=7))
        self.assertFalse(services.can_edit(self.teacher, old, today=SCHOOL_DAY))
        self.assertTrue(services.can_edit(self.admin, old, today=SCHOOL_DAY))
        self.assertTrue(services.can_edit(self.teacher, self.reg, today=SCHOOL_DAY))


class ReportTests(Fixture):
    def _absent_streak(self, person, days):
        day, n = SCHOOL_DAY, 0
        while n < days:
            if is_school_day(day):
                reg, _ = services.ensure_register(self.c5, day)
                reg.marks.filter(learner=person).update(status=AttendanceMark.ABSENT)
                n += 1
            day -= timedelta(days=1)

    def test_consecutive_absence_flag(self):
        self._absent_streak(self.amy.profile, 10)
        self._absent_streak(self.ben.profile, 9)
        with mock.patch('apps.attendance.services.local_today', return_value=SCHOOL_DAY):
            flagged = [p for p, _streak, _since in services.flagged_learners()]
        self.assertEqual(flagged, [self.amy.profile])
        summary = services.learner_summary(self.amy.profile)
        self.assertEqual(summary['absent'], 10)
        self.assertEqual(summary['pct'], 0)

        self.client.force_login(self.admin)
        resp = self.client.get(reverse('attendance:reports') + f'?cohort={self.c5.pk}&month=2026-10')
        self.assertContains(resp, 'consecutive school days absent')
        csv = self.client.get(reverse('attendance:reports-csv') + f'?cohort={self.c5.pk}&month=2026-10')
        self.assertEqual(csv.status_code, 200)
        self.assertIn('Amy', csv.content.decode())

    def test_reports_staff_only(self):
        self.client.force_login(self.teacher)
        self.assertEqual(self.client.get(reverse('attendance:reports')).status_code, 403)

    def test_parent_sees_only_own_child(self):
        services.open_registers(SCHOOL_DAY)
        AttendanceMark.objects.filter(learner=self.amy.profile).update(status='absent', reason='Amy-sick')
        AttendanceMark.objects.filter(learner=self.cara.profile).update(status='absent', reason='Cara-dentist')
        self.client.force_login(self.parent)
        resp = self.client.get(reverse('attendance:my'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Amy-sick')
        # Asking for somebody else's child returns their own child instead.
        resp = self.client.get(reverse('attendance:my') + f'?student={self.cara.pk}')
        self.assertContains(resp, 'Amy-sick')
        self.assertNotContains(resp, 'Cara-dentist')
        # Parents cannot reach the teacher pages.
        self.assertNotEqual(self.client.get(reverse('attendance:index')).status_code, 200)

    def test_learner_sees_own_record(self):
        services.open_registers(SCHOOL_DAY)
        self.client.force_login(self.ben)
        resp = self.client.get(reverse('attendance:my'))
        self.assertContains(resp, 'My attendance')
