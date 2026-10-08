"""Operations dashboard, Student 360 and the educator desk (``/staff/``)."""

from datetime import timedelta
from decimal import Decimal
from unittest import mock

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.livesessions.tests import make_user
from core.testing import enrol, make_module

from . import dashboards as dash
from .models import Nudge


def _stale(user, days=30):
    """Make ``user`` look like they last signed in ``days`` ago."""
    type(user).objects.filter(pk=user.pk).update(last_login=timezone.now() - timedelta(days=days))


class AccessTests(TestCase):
    def setUp(self):
        self.admin = make_user('ops-admin', 'admin')
        self.staff = make_user('ops-staff', 'staff')
        self.educator = make_user('ops-coach', 'educator')
        self.student = make_user('ops-student')
        self.parent = make_user('ops-parent', 'parent')

    def test_operations_and_360_are_admin_staff_only(self):
        for name, args in (('staffdesk:home', []), ('staffdesk:students', []),
                           ('staffdesk:student', [self.student.profile.pk])):
            url = reverse(name, args=args)
            for user in (self.admin, self.staff):
                self.client.force_login(user)
                self.assertEqual(self.client.get(url).status_code, 200, (name, user))
            for user in (self.educator, self.student, self.parent):
                self.client.force_login(user)
                self.assertRedirects(self.client.get(url), reverse('myhub:index'), fetch_redirect_response=False)

    def test_anonymous_is_sent_to_login(self):
        response = self.client.get(reverse('staffdesk:home'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response['Location'])

    def test_teaching_is_for_educators_and_admin_staff(self):
        url = reverse('staffdesk:teaching')
        for user in (self.educator, self.admin, self.staff):
            self.client.force_login(user)
            self.assertEqual(self.client.get(url).status_code, 200)
        for user in (self.student, self.parent):
            self.client.force_login(user)
            self.assertRedirects(self.client.get(url), reverse('myhub:index'), fetch_redirect_response=False)

    def test_unknown_person_is_404(self):
        self.client.force_login(self.admin)
        self.assertEqual(self.client.get(reverse('staffdesk:student', args=[999999])).status_code, 404)


class EmptyDatabaseTests(TestCase):
    """Every page renders with nothing but the viewer in the database."""

    def setUp(self):
        self.admin = make_user('empty-admin', 'admin')
        self.client.force_login(self.admin)

    def test_pages_render(self):
        response = self.client.get(reverse('staffdesk:home'))
        self.assertContains(response, 'Operations')
        self.assertContains(response, 'Nothing broadcast yet')
        self.assertContains(self.client.get(reverse('staffdesk:students')), 'Student 360')
        self.assertContains(self.client.get(reverse('staffdesk:student', args=[self.admin.profile.pk])),
                            'Not enrolled on anything yet')
        self.assertContains(self.client.get(reverse('staffdesk:teaching')), 'teaching any subjects yet')

    def test_a_broken_panel_does_not_break_the_page(self):
        with mock.patch.object(dash, '_ops_money', side_effect=RuntimeError('boom')):
            response = self.client.get(reverse('staffdesk:home'))
        self.assertEqual(response.status_code, 200)


class WithDataTests(TestCase):
    def setUp(self):
        from apps.accounts.models import ActivityLog, ParentLink
        from apps.analytics.models import RiskFlag
        from apps.assessments.models import Assessment, AssessmentAttempt
        from apps.communication.models import (Announcement, Attendance, ClassSession, MeetingRoom,
                                               Notification)
        from apps.diagnostics.models import ErrorEvent
        from apps.finance.models import Invoice, InvoicePayment
        from apps.reports.models import Grade
        from apps.tasks.models import Task, TaskAssignment

        now = timezone.now()
        self.admin = make_user('data-admin', 'admin')
        self.coach = make_user('data-coach', 'educator', first_name='Cora', last_name='Coach')
        self.student = make_user('data-student', first_name='Thandi', last_name='Mokoena')
        self.quiet = make_user('data-quiet', first_name='Quinn', last_name='Quiet')
        self.parent = make_user('data-parent', 'parent')
        _stale(self.quiet)
        type(self.student).objects.filter(pk=self.student.pk).update(last_login=now)

        self.module = make_module('Financial Reporting', 'FREP')
        self.module.educators.add(self.coach.profile)
        enrol(self.student.profile, self.module)
        enrol(self.quiet.profile, self.module)

        assessment = Assessment.objects.create(title='Test 1', module=self.module, total_marks=50)
        AssessmentAttempt.objects.create(assessment=assessment, student=self.student, status='marked',
                                         score=40, submitted_at=now - timedelta(days=1))
        AssessmentAttempt.objects.create(assessment=assessment, student=self.quiet, status='submitted',
                                         submitted_at=now - timedelta(days=2))
        Grade.objects.update_or_create(student=self.student, module=self.module,
                                       defaults={'final_pct': 80, 'passed': True})

        invoice = Invoice.objects.create(customer=self.student, status='sent', total=Decimal('1000'),
                                         due_date=timezone.localdate() - timedelta(days=5))
        InvoicePayment.objects.create(invoice=invoice, amount=Decimal('400'))
        task = Task.objects.create(title='Read chapter 3', due_date=now - timedelta(days=1))
        TaskAssignment.objects.create(task=task, user=self.student)

        session = ClassSession.objects.create(module=self.module, title='Week 1',
                                              session_date=timezone.localdate() - timedelta(days=1))
        Attendance.objects.create(session=session, student=self.student, status='present')
        MeetingRoom.objects.create(title='Revision class', module=self.module, host=self.coach,
                                   scheduled_start=now + timedelta(hours=1),
                                   scheduled_end=now + timedelta(hours=2))
        announcement = Announcement.objects.create(title='Exam timetable', body='x', sender=self.admin,
                                                   status='sent', sent_at=now, recipient_count=2)
        Notification.objects.create(recipient=self.student, announcement=announcement, title='Exam timetable',
                                    is_read=True)
        Notification.objects.create(recipient=self.quiet, announcement=announcement, title='Exam timetable')
        RiskFlag.objects.create(student=self.quiet, module=self.module, score=85, reasons=['No logins'])
        ErrorEvent.objects.create(code='TEST-0001', fingerprint='abc', message='kaboom')
        ActivityLog.objects.create(actor=self.admin.profile, target_user=self.student.profile,
                                   action='update', description='Edited profile')
        ParentLink.objects.create(parent=self.parent, student=self.student, relationship='Mother')

    def test_operations(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('staffdesk:home'))
        self.assertContains(response, 'Revision class')
        self.assertContains(response, 'Exam timetable')
        self.assertContains(response, '50%')                       # 1 of 2 read
        self.assertContains(response, 'R600.00')                   # overdue balance
        self.assertContains(response, 'R400.00')                   # collected this month
        self.assertContains(response, 'Quinn Quiet')               # at risk
        self.assertContains(response, 'Edited profile')
        ops = response.context['ops']
        self.assertEqual(ops['marking']['total'], 1)
        self.assertEqual(ops['errors']['count'], 1)
        self.assertEqual(ops['people']['total'], 2)

    def test_operations_query_count_is_flat(self):
        """More students must not mean more queries."""
        self.client.force_login(self.admin)
        self.client.get(reverse('staffdesk:home'))
        from django.db import connection
        from django.test.utils import CaptureQueriesContext
        with CaptureQueriesContext(connection) as before:
            self.client.get(reverse('staffdesk:home'))
        for i in range(15):
            enrol(make_user(f'bulk-{i}').profile, self.module)
        with CaptureQueriesContext(connection) as after:
            self.client.get(reverse('staffdesk:home'))
        self.assertLessEqual(len(after), len(before) + 6)  # the new-member list grows to its cap of 6

    def test_student_360(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('staffdesk:student', args=[self.student.profile.pk]))
        self.assertContains(response, 'Thandi Mokoena')
        self.assertContains(response, 'FREP')
        self.assertContains(response, 'Test 1')
        self.assertContains(response, 'Read chapter 3')
        self.assertContains(response, 'Mother')
        self.assertContains(response, f'/communication/announcements/new/?user={self.student.pk}')
        self.assertContains(response, f'?customer={self.student.pk}')
        self.assertContains(response, reverse('communication:chat-direct', args=[self.student.pk]))
        d = response.context['d']
        self.assertEqual(d['money']['balance'], Decimal('600'))
        self.assertEqual(d['attendance']['rate'], 100)
        self.assertEqual(round(d['attempts']['avg']), 80)
        self.assertEqual(d['tasks']['overdue'], 1)
        self.assertEqual(d['notifications']['rate'], 100)

    def test_student_search(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('staffdesk:students'), {'q': 'mokoena'})
        self.assertContains(response, 'Thandi Mokoena')
        self.assertNotContains(response, 'Quinn Quiet')

    def test_teaching(self):
        self.client.force_login(self.coach)
        response = self.client.get(reverse('staffdesk:teaching'))
        self.assertContains(response, 'Financial Reporting')
        self.assertContains(response, 'Revision class')
        t = response.context['t']
        self.assertEqual(t['modules'][0].n_students, 2)
        self.assertEqual(t['modules'][0].inactive_count, 1)
        self.assertEqual(t['marking']['total'], 1)
        flagged = {row['user_id']: row for row in t['behind']['rows']}
        self.assertIn(self.quiet.pk, flagged)                  # inactive
        self.assertIn(self.student.pk, flagged)                # overdue task
        self.assertEqual(flagged[self.student.pk]['overdue'], 1)
        self.assertEqual(t['attendance'][0]['pct'], 50)        # 1 of 2 enrolled

    def test_admin_can_view_an_educators_desk(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('staffdesk:teaching'), {'educator': self.coach.pk})
        self.assertTrue(response.context['viewing_other'])
        self.assertContains(response, 'Financial Reporting')

    def test_educator_cannot_view_another_educators_desk(self):
        other = make_user('data-coach-2', 'educator')
        self.client.force_login(other)
        response = self.client.get(reverse('staffdesk:teaching'), {'educator': self.coach.pk})
        self.assertFalse(response.context['viewing_other'])
        self.assertNotContains(response, 'Financial Reporting')


@mock.patch('apps.communication.services._email_notification')
class NudgeTests(TestCase):
    def setUp(self):
        self.admin = make_user('nudge-admin', 'admin')
        self.coach = make_user('nudge-coach', 'educator')
        self.other_coach = make_user('nudge-other', 'educator')
        self.active = make_user('nudge-active')
        self.quiet = make_user('nudge-quiet')
        type(self.active).objects.filter(pk=self.active.pk).update(last_login=timezone.now())
        _stale(self.quiet)
        self.module = make_module('Taxation', 'TAXA')
        self.module.educators.add(self.coach.profile)
        enrol(self.active.profile, self.module)
        enrol(self.quiet.profile, self.module)
        self.url = reverse('staffdesk:teaching-nudge', args=[self.module.pk])

    def _notified(self):
        from apps.communication.models import Notification
        return set(Notification.objects.values_list('recipient_id', flat=True))

    def test_get_is_not_allowed(self, _email):
        self.client.force_login(self.coach)
        self.assertEqual(self.client.get(self.url).status_code, 405)
        self.assertFalse(Nudge.objects.exists())

    def test_only_inactive_students_are_nudged(self, _email):
        self.client.force_login(self.coach)
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse('staffdesk:teaching'), fetch_redirect_response=False)
        self.assertEqual(self._notified(), {self.quiet.pk})
        nudge = Nudge.objects.get()
        self.assertEqual((nudge.recipients, nudge.sent_by), (1, self.coach))
        _email.assert_called_once()

    def test_educator_cannot_nudge_a_module_they_do_not_teach(self, _email):
        self.client.force_login(self.other_coach)
        self.assertEqual(self.client.post(self.url).status_code, 403)
        self.assertFalse(Nudge.objects.exists())
        self.assertEqual(self._notified(), set())

    def test_students_cannot_nudge(self, _email):
        self.client.force_login(self.active)
        self.client.post(self.url)
        self.assertFalse(Nudge.objects.exists())

    def test_admin_can_nudge_any_module(self, _email):
        self.client.force_login(self.admin)
        response = self.client.post(self.url, {'educator': self.coach.pk})
        self.assertRedirects(response, reverse('staffdesk:teaching') + f'?educator={self.coach.pk}',
                             fetch_redirect_response=False)
        self.assertEqual(Nudge.objects.count(), 1)

    def test_once_per_module_per_day(self, _email):
        self.client.force_login(self.coach)
        self.client.post(self.url)
        self.client.post(self.url)
        self.assertEqual(Nudge.objects.count(), 1)
        from apps.communication.models import Notification
        self.assertEqual(Notification.objects.count(), 1)

        # A day later the button works again.
        Nudge.objects.update(sent_at=timezone.now() - timedelta(hours=25))
        self.client.post(self.url)
        self.assertEqual(Nudge.objects.count(), 2)

    def test_nobody_to_nudge_does_not_start_the_cooldown(self, _email):
        type(self.quiet).objects.filter(pk=self.quiet.pk).update(last_login=timezone.now())
        self.client.force_login(self.coach)
        self.client.post(self.url)
        self.assertFalse(Nudge.objects.exists())
        self.assertTrue(dash.can_nudge(self.module)[0])

    def test_the_desk_shows_the_cooldown(self, _email):
        self.client.force_login(self.coach)
        self.client.post(self.url)
        response = self.client.get(reverse('staffdesk:teaching'))
        module = response.context['t']['modules'][0]
        self.assertFalse(module.can_nudge)
        self.assertContains(response, 'again after')
