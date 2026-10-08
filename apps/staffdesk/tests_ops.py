"""Ops pages: access, rendering and every state-changing action."""

from datetime import datetime, timedelta
from unittest import mock

from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import ActivityLog, Invitation, ParentLink
from apps.communication.models import (
    Appeal, ChatGroup, Message, Notification, Penalty, ReputationScore, Violation)
from apps.livesessions.tests import make_user
from apps.scheduler import jobs as job_registry
from apps.scheduler.jobs import Job
from apps.scheduler.models import JobRun
from apps.staffdesk import views_ops

CALLS = []


def noop_job():
    CALLS.append(1)
    return 'did the thing'


FAKE_JOB = Job(name='test-job', every=3600, description='A test job.', dotted='apps.staffdesk.tests_ops:noop_job')


def inline(fn, *args):
    """Stand-in for the background thread, so the test can see the result."""
    fn(*args)


class OpsTestBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.staff = make_user('ops-staff', 'staff', first_name='Sam', last_name='Staff')
        cls.student = make_user('ops-student', 'student', first_name='Stu', last_name='Dent')
        cls.parent = make_user('ops-parent', 'parent', first_name='Pat', last_name='Rent')
        cls.educator = make_user('ops-educator', 'educator')

    def setUp(self):
        self.client.force_login(self.staff)


class AccessTests(OpsTestBase):
    PAGES = ['ops-jobs', 'ops-moderation', 'ops-audit', 'ops-audit-export', 'ops-invitations', 'ops-parent-links']

    def test_student_and_educator_are_refused(self):
        for user in (self.student, self.educator):
            self.client.force_login(user)
            for name in self.PAGES:
                resp = self.client.get(reverse(f'staffdesk:{name}'))
                self.assertRedirects(resp, reverse('myhub:index'), fetch_redirect_response=False,
                                     msg_prefix=f'{user.username} {name}')

    def test_refused_post_changes_nothing(self):
        link = ParentLink.objects.create(parent=self.parent, student=self.student)
        self.client.force_login(self.student)
        self.client.post(reverse('staffdesk:ops-parent-link-remove', args=[link.pk]))
        self.assertTrue(ParentLink.objects.filter(pk=link.pk).exists())

    def test_anonymous_goes_to_login(self):
        self.client.logout()
        resp = self.client.get(reverse('staffdesk:ops-jobs'))
        self.assertEqual(resp.status_code, 302)
        self.assertNotIn('/staff/', resp.url.split('?')[0])

    def test_actions_need_post(self):
        self.assertEqual(self.client.get(reverse('staffdesk:ops-jobs-run-due')).status_code, 405)


class JobsTests(OpsTestBase):
    def test_page_lists_every_registered_job(self):
        resp = self.client.get(reverse('staffdesk:ops-jobs'))
        self.assertEqual(resp.status_code, 200)
        for job in job_registry.JOBS:
            self.assertContains(resp, job.name)
        self.assertContains(resp, 'Quick tick')

    def test_running_failing_and_output_are_shown(self):
        now = timezone.now()
        JobRun.objects.create(name='send-broadcasts', locked_at=now, last_started_at=now,
                              last_status=JobRun.STATUS_RUNNING)
        JobRun.objects.create(name='rank-classes', last_started_at=now, last_finished_at=now,
                              last_status=JobRun.STATUS_FAILED, consecutive_failures=2,
                              last_output='Traceback: boom')
        resp = self.client.get(reverse('staffdesk:ops-jobs'))
        rows = {r['job'].name: r for r in resp.context['rows']}
        self.assertTrue(rows['send-broadcasts']['running'])
        self.assertTrue(rows['rank-classes']['failing'])
        self.assertContains(resp, 'Traceback: boom')
        self.assertContains(resp, '2 failures in a row')

    @mock.patch.object(views_ops, '_background', inline)
    def test_run_now_runs_the_job(self):
        CALLS.clear()
        with mock.patch.dict(job_registry.JOBS_BY_NAME, {'test-job': FAKE_JOB}):
            resp = self.client.post(reverse('staffdesk:ops-job-run', args=['test-job']))
        self.assertRedirects(resp, reverse('staffdesk:ops-jobs'), fetch_redirect_response=False)
        self.assertEqual(CALLS, [1])
        state = JobRun.objects.get(name='test-job')
        self.assertEqual((state.last_status, state.run_count, state.last_output), ('ok', 1, 'did the thing'))
        self.assertIsNone(state.locked_at)

    @mock.patch.object(views_ops, '_background', inline)
    def test_run_now_skips_a_job_that_is_already_running(self):
        CALLS.clear()
        JobRun.objects.create(name='test-job', locked_at=timezone.now())
        with mock.patch.dict(job_registry.JOBS_BY_NAME, {'test-job': FAKE_JOB}):
            self.client.post(reverse('staffdesk:ops-job-run', args=['test-job']))
        self.assertEqual(CALLS, [])

    def test_unknown_job_is_404(self):
        self.assertEqual(self.client.post(reverse('staffdesk:ops-job-run', args=['nope'])).status_code, 404)

    @mock.patch.object(views_ops, '_background', inline)
    def test_run_all_due_ticks_without_forcing(self):
        with mock.patch.object(views_ops.runner, 'tick') as tick:
            self.client.post(reverse('staffdesk:ops-jobs-run-due'))
        tick.assert_called_once_with()

    def test_next_expected_run_follows_the_production_timers(self):
        sast = views_ops.SAST
        hourly = Job(name='x', every=3600, dotted='a:b')
        state = JobRun(name='x', last_started_at=datetime(2026, 10, 7, 22, 5, tzinfo=sast))
        # The last tick of the day was 22:05, so the next run is tomorrow's first.
        self.assertEqual(views_ops.next_expected_run(hourly, state, timezone.now()),
                         datetime(2026, 10, 8, 6, 5, tzinfo=sast))
        quick = Job(name='send-broadcasts', every=60, dotted='a:b')
        state = JobRun(name='send-broadcasts', last_started_at=datetime(2026, 10, 7, 10, 5, tzinfo=sast))
        self.assertEqual(views_ops.next_expected_run(quick, state, timezone.now()),
                         datetime(2026, 10, 7, 10, 15, tzinfo=sast))

    def test_a_job_that_missed_its_tick_is_overdue(self):
        JobRun.objects.create(name='rank-classes', last_status='ok',
                              last_started_at=timezone.now() - timedelta(days=3),
                              last_finished_at=timezone.now() - timedelta(days=3))
        resp = self.client.get(reverse('staffdesk:ops-jobs'))
        rows = {r['job'].name: r for r in resp.context['rows']}
        self.assertTrue(rows['rank-classes']['overdue'])
        self.assertContains(resp, 'Overdue')


class ModerationTests(OpsTestBase):
    def setUp(self):
        super().setUp()
        self.group = ChatGroup.objects.create(name='Maths chat')

    def _flag(self, body='you idiot', score=3, detected_by=Violation.DETECTED_RULE, penalise=True):
        msg = Message.objects.create(group=self.group, sender=self.student, body=body, is_deleted=score >= 3)
        v = Violation.objects.create(user=self.student, text=body, category='insult', score=score,
                                     message=msg, detected_by=detected_by)
        if penalise:
            Penalty.objects.create(user=self.student, kind=Penalty.KIND_MUTE, violation=v,
                                   ends_at=timezone.now() + timedelta(hours=1))
            ReputationScore.objects.create(user=self.student, score=100 - score * 5)
        return v

    def test_tabs_render(self):
        v = self._flag()
        Appeal.objects.create(penalty=v.penalties.get(), user=self.student, message='It was a joke')
        for tab, text in (('violations', 'you idiot'), ('penalties', 'Temporary mute'),
                          ('appeals', 'It was a joke'), ('reputation', '85/100')):
            resp = self.client.get(reverse('staffdesk:ops-moderation'), {'tab': tab})
            self.assertContains(resp, text, msg_prefix=tab)

    def test_dismiss_undoes_the_automatic_moderation(self):
        v = self._flag()
        self.client.post(reverse('staffdesk:ops-violation-action', args=[v.pk]), {'action': 'dismiss'})
        v.refresh_from_db()
        self.assertTrue(v.handled)
        self.assertEqual(v.evidence['review']['outcome'], 'dismissed')
        self.assertFalse(v.penalties.filter(active=True).exists())
        self.assertEqual(ReputationScore.objects.get(user=self.student).score, 100)
        self.assertFalse(Message.objects.get(pk=v.message_id).is_deleted)

    def test_confirming_a_user_report_applies_the_ladder(self):
        v = self._flag(body='spam spam', score=2, detected_by=Violation.DETECTED_REPORT, penalise=False)
        self.client.post(reverse('staffdesk:ops-violation-action', args=[v.pk]), {'action': 'confirm', 'hide': '1'})
        v.refresh_from_db()
        self.assertTrue(v.handled)
        penalty = v.penalties.get()
        self.assertEqual((penalty.kind, penalty.issued_by), (Penalty.KIND_WARNING, self.staff))
        self.assertEqual(ReputationScore.objects.get(user=self.student).score, 90)
        self.assertTrue(Message.objects.get(pk=v.message_id).is_deleted)

    def test_confirming_an_auto_flag_does_not_penalise_twice(self):
        v = self._flag()
        self.client.post(reverse('staffdesk:ops-violation-action', args=[v.pk]), {'action': 'confirm'})
        self.assertEqual(Penalty.objects.filter(user=self.student).count(), 1)
        self.assertEqual(ReputationScore.objects.get(user=self.student).score, 85)

    def test_lift_penalty(self):
        penalty = self._flag().penalties.get()
        self.client.post(reverse('staffdesk:ops-penalty-lift', args=[penalty.pk]))
        penalty.refresh_from_db()
        self.assertFalse(penalty.active)

    def test_approve_appeal_lifts_penalty_and_tells_the_user(self):
        penalty = self._flag().penalties.get()
        appeal = Appeal.objects.create(penalty=penalty, user=self.student, message='Sorry')
        self.client.post(reverse('staffdesk:ops-appeal-decide', args=[appeal.pk]),
                         {'decision': 'approve', 'note': 'Fair enough this time.'})
        appeal.refresh_from_db()
        penalty.refresh_from_db()
        self.assertEqual((appeal.status, appeal.reviewed_by), (Appeal.STATUS_ACCEPTED, self.staff))
        self.assertFalse(penalty.active)
        note = Notification.objects.get(recipient=self.student)
        self.assertIn('Fair enough this time.', note.body)

    def test_deny_appeal_keeps_penalty(self):
        penalty = self._flag().penalties.get()
        appeal = Appeal.objects.create(penalty=penalty, user=self.student, message='Sorry')
        self.client.post(reverse('staffdesk:ops-appeal-decide', args=[appeal.pk]), {'decision': 'deny'})
        appeal.refresh_from_db()
        penalty.refresh_from_db()
        self.assertEqual(appeal.status, Appeal.STATUS_REJECTED)
        self.assertTrue(penalty.active)
        # A decided appeal cannot be decided again.
        self.client.post(reverse('staffdesk:ops-appeal-decide', args=[appeal.pk]), {'decision': 'approve'})
        appeal.refresh_from_db()
        self.assertEqual(appeal.status, Appeal.STATUS_REJECTED)


class AuditTests(OpsTestBase):
    def setUp(self):
        super().setUp()
        ActivityLog.objects.all().delete()
        old = timezone.now() - timedelta(days=10)
        ActivityLog.objects.create(action='login', actor=self.student.profile, description='Signed in from home')
        ActivityLog.objects.create(action='delete', actor=self.staff.profile, target_user=self.parent.profile,
                                   description='Removed a course', timestamp=old)

    def test_filters(self):
        url = reverse('staffdesk:ops-audit')
        self.assertEqual(self.client.get(url).context['total'], 2)
        self.assertEqual(self.client.get(url, {'action': 'delete'}).context['total'], 1)
        self.assertEqual(self.client.get(url, {'user': 'Rent'}).context['total'], 1)   # target name
        self.assertEqual(self.client.get(url, {'q': 'home'}).context['total'], 1)
        since = (timezone.now() - timedelta(days=2)).date().isoformat()
        resp = self.client.get(url, {'date_from': since})
        self.assertEqual(resp.context['total'], 1)
        self.assertContains(resp, 'Signed in from home')

    def test_pagination(self):
        ActivityLog.objects.bulk_create([ActivityLog(action='update', description=f'row {i}') for i in range(60)])
        resp = self.client.get(reverse('staffdesk:ops-audit'), {'page': 2})
        self.assertEqual(len(resp.context['page'].object_list), 12)

    def test_csv_export_respects_filters(self):
        resp = self.client.get(reverse('staffdesk:ops-audit-export'), {'action': 'delete'})
        self.assertEqual(resp['Content-Type'], 'text/csv')
        body = b''.join(resp.streaming_content).decode()
        lines = body.strip().splitlines()
        self.assertEqual(len(lines), 2)
        self.assertIn('Removed a course', lines[1])
        self.assertIn(self.parent.email, lines[1])


class InvitationTests(OpsTestBase):
    def setUp(self):
        super().setUp()
        self.invite = Invitation.objects.create(role=Invitation.ROLE_PARENT, email='mum@example.com',
                                                student=self.student.profile, invited_by=self.staff)

    def test_list(self):
        resp = self.client.get(reverse('staffdesk:ops-invitations'))
        self.assertContains(resp, 'mum@example.com')
        self.assertEqual(resp.context['counts']['pending'], 1)

    def test_resend_uses_the_invite_email(self):
        with mock.patch.object(views_ops.account_emails, 'send_invite', return_value=True) as send:
            self.client.post(reverse('staffdesk:ops-invitation-action', args=[self.invite.pk]), {'action': 'resend'})
        send.assert_called_once_with(self.invite)

    def test_resend_really_sends(self):
        self.client.post(reverse('staffdesk:ops-invitation-action', args=[self.invite.pk]), {'action': 'resend'})
        self.assertEqual([m.to for m in mail.outbox], [['mum@example.com']])

    def test_revoke(self):
        self.client.post(reverse('staffdesk:ops-invitation-action', args=[self.invite.pk]), {'action': 'revoke'})
        self.invite.refresh_from_db()
        self.assertEqual(self.invite.status, Invitation.STATUS_REVOKED)
        # A revoked invite cannot be re-sent.
        with mock.patch.object(views_ops.account_emails, 'send_invite') as send:
            self.client.post(reverse('staffdesk:ops-invitation-action', args=[self.invite.pk]), {'action': 'resend'})
        send.assert_not_called()


class ParentLinkTests(OpsTestBase):
    url = 'staffdesk:ops-parent-links'

    def test_list_and_search(self):
        ParentLink.objects.create(parent=self.parent, student=self.student, relationship='Mother')
        resp = self.client.get(reverse(self.url), {'q': 'Dent'})
        self.assertContains(resp, 'Mother')
        self.assertEqual(len(self.client.get(reverse(self.url), {'q': 'nobody'}).context['page'].object_list), 0)

    def test_add(self):
        resp = self.client.post(reverse(self.url), {'parent_email': self.parent.email,
                                                    'student_email': self.student.email,
                                                    'relationship': 'Sponsor'})
        self.assertRedirects(resp, reverse(self.url), fetch_redirect_response=False)
        self.assertTrue(ParentLink.objects.filter(parent=self.parent, student=self.student,
                                                  relationship='Sponsor').exists())

    def test_add_checks_roles(self):
        resp = self.client.post(reverse(self.url), {'parent_email': self.educator.email,
                                                    'student_email': self.student.email})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'not a parent')
        self.assertFalse(ParentLink.objects.exists())

    def test_add_respects_the_limit(self):
        for i in range(ParentLink.MAX_PER_STUDENT):
            ParentLink.objects.create(parent=make_user(f'ops-p{i}', 'parent'), student=self.student)
        resp = self.client.post(reverse(self.url), {'parent_email': self.parent.email,
                                                    'student_email': self.student.email})
        self.assertContains(resp, 'remove one first')
        self.assertEqual(ParentLink.objects.filter(student=self.student).count(), ParentLink.MAX_PER_STUDENT)

    def test_remove(self):
        link = ParentLink.objects.create(parent=self.parent, student=self.student)
        self.client.post(reverse('staffdesk:ops-parent-link-remove', args=[link.pk]))
        self.assertFalse(ParentLink.objects.filter(pk=link.pk).exists())
