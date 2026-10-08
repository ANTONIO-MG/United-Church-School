"""Tests for the academic staff-desk pages: grades & certificates, at-risk
triage, content imports and the AI archive."""

from decimal import Decimal
from unittest import mock

from django.test import TestCase
from django.urls import reverse

from apps.ai_assistant.models import AiInsight, AiReport
from apps.analytics.models import ReportSnapshot, RiskFlag
from apps.livesessions.tests import make_user
from apps.reports import services as report_services
from apps.reports.models import Certificate, Grade, ModuleWeighting
from core.testing import enrol, make_module

from . import views_academic
from .models import ImportRun, RiskTriage


class AcademicFixture(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.staff = make_user('sda-staff', 'staff', first_name='Sam', last_name='Staff')
        cls.educator = make_user('sda-edu', 'educator', first_name='Eve', last_name='Educator')
        cls.student = make_user('sda-stu', 'student', first_name='Stu', last_name='Dent')
        cls.module = make_module('Financial Reporting', code='SDAFR')
        cls.module.educators.add(cls.educator.profile)
        enrol(cls.student.profile, cls.module)
        cls.grade = Grade.objects.create(student=cls.student, module=cls.module, final_pct=Decimal('42'),
                                         computed_pct=Decimal('42'), letter='F', passed=False)

    def setUp(self):
        self.client.force_login(self.staff)


class AccessTests(AcademicFixture):
    URLS = ['staffdesk:grades', 'staffdesk:certificates', 'staffdesk:weightings', 'staffdesk:at-risk',
            'staffdesk:snapshots', 'staffdesk:imports', 'staffdesk:ai-reports', 'staffdesk:ai-insights',
            'staffdesk:certificate-issue']

    def test_staff_can_open_every_page(self):
        for name in self.URLS:
            with self.subTest(name=name):
                self.assertEqual(self.client.get(reverse(name)).status_code, 200)

    def test_students_and_educators_are_turned_away(self):
        for user in (self.student, self.educator):
            self.client.force_login(user)
            for name in self.URLS:
                with self.subTest(user=user.username, name=name):
                    response = self.client.get(reverse(name))
                    self.assertRedirects(response, reverse('myhub:index'), fetch_redirect_response=False)

    def test_actions_are_post_only(self):
        url = reverse('staffdesk:grade-recompute', args=[self.grade.pk])
        self.assertEqual(self.client.get(url).status_code, 405)


class GradeTests(AcademicFixture):
    def test_grades_page_filters_by_module_and_lists_the_grade(self):
        response = self.client.get(reverse('staffdesk:grades'), {'module': self.module.pk})
        self.assertContains(response, 'sda-stu@example.com')
        other = make_module('Tax', code='SDATAX')
        response = self.client.get(reverse('staffdesk:grades'), {'module': other.pk})
        self.assertNotContains(response, 'sda-stu@example.com')

    def test_override_becomes_the_final_mark_and_survives_a_recompute(self):
        response = self.client.post(reverse('staffdesk:grade-override', args=[self.grade.pk]),
                                    {'value': '65', 'reason': 'Remark after appeal'})
        self.assertRedirects(response, reverse('staffdesk:grade-detail', args=[self.grade.pk]))
        grade = Grade.objects.get(pk=self.grade.pk)
        self.assertEqual(grade.final_pct, Decimal('65.00'))
        self.assertTrue(grade.passed)
        self.assertEqual(grade.letter, 'C')
        self.assertEqual(grade.overridden_by, self.staff)

        # Nothing is marked, so the computed mark is 0 — but the override stands.
        report_services.compute_grade(self.student, self.module)
        grade.refresh_from_db()
        self.assertEqual(grade.computed_pct, Decimal('0'))
        self.assertEqual(grade.final_pct, Decimal('65.00'))
        self.assertTrue(grade.passed)

    def test_override_needs_a_reason(self):
        self.client.post(reverse('staffdesk:grade-override', args=[self.grade.pk]), {'value': '65', 'reason': ''})
        self.assertIsNone(Grade.objects.get(pk=self.grade.pk).override_pct)

    def test_clearing_the_override_restores_the_computed_mark(self):
        report_services.override_grade(self.grade, value=90, reason='x', by=self.staff)
        self.client.post(reverse('staffdesk:grade-override-clear', args=[self.grade.pk]))
        grade = Grade.objects.get(pk=self.grade.pk)
        self.assertIsNone(grade.override_pct)
        self.assertEqual(grade.final_pct, grade.computed_pct)

    def test_a_certificate_issued_after_an_override_carries_the_override(self):
        report_services.override_grade(self.grade, value=77, reason='Moderated', by=self.staff)
        self.client.post(reverse('staffdesk:certificate-issue'),
                         {'student': self.student.pk, 'kind': 'module', 'module': self.module.pk})
        cert = Certificate.objects.get(student=self.student, module=self.module)
        self.assertEqual(cert.final_mark, Decimal('77.00'))

    def test_detail_page_shows_the_override(self):
        report_services.override_grade(self.grade, value=55, reason='Late medical certificate', by=self.staff)
        response = self.client.get(reverse('staffdesk:grade-detail', args=[self.grade.pk]))
        self.assertContains(response, 'Late medical certificate')

    def test_recompute_module_grades_every_enrolled_student(self):
        Grade.objects.all().delete()
        self.client.post(reverse('staffdesk:grades-recompute-module'), {'module': self.module.pk})
        self.assertTrue(Grade.objects.filter(student=self.student, module=self.module).exists())


class WeightingTests(AcademicFixture):
    def _post(self, **overrides):
        data = {'assignments_pct': 20, 'quizzes_pct': 10, 'tests_pct': 20, 'exams_pct': 40, 'tasks_pct': 10,
                'pass_mark_pct': 60, 'extra_credit_pct': 0, 'grade_scale': ''}
        data.update(overrides)
        return self.client.post(reverse('staffdesk:weighting-edit', args=[self.module.pk]), data)

    def test_saving_a_weighting(self):
        self.assertRedirects(self._post(), reverse('staffdesk:weightings'))
        self.assertEqual(ModuleWeighting.objects.get(module=self.module).pass_mark_pct, 60)

    def test_weights_must_total_100(self):
        response = self._post(exams_pct=50)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'add up to 100')
        self.assertFalse(ModuleWeighting.objects.filter(module=self.module).exists())


class CertificateTests(AcademicFixture):
    def setUp(self):
        super().setUp()
        self.cert = Certificate.objects.create(student=self.student, module=self.module, title='Module Completion',
                                               final_mark=Decimal('70'))

    def test_issue_a_programme_certificate(self):
        response = self.client.post(reverse('staffdesk:certificate-issue'), {
            'student': self.student.pk, 'kind': 'programme', 'programme': self.module.programme.pk})
        self.assertEqual(response.status_code, 302)
        cert = Certificate.objects.get(student=self.student, kind='programme')
        self.assertEqual(cert.final_mark, Decimal('42.00'))   # the average of their grades

    def test_a_second_module_certificate_is_not_issued(self):
        self.client.post(reverse('staffdesk:certificate-issue'),
                         {'student': self.student.pk, 'kind': 'module', 'module': self.module.pk})
        self.assertEqual(Certificate.objects.filter(student=self.student, module=self.module).count(), 1)

    def test_revoked_certificate_shows_as_revoked_on_the_public_verify_page(self):
        self.client.post(reverse('staffdesk:certificate-revoke', args=[self.cert.pk]), {'reason': 'Plagiarism'})
        self.cert.refresh_from_db()
        self.assertTrue(self.cert.is_revoked)
        self.assertEqual(self.cert.revoked_by, self.staff)

        self.client.logout()
        response = self.client.get(reverse('reports:verify', args=[self.cert.verification_uuid]))
        self.assertContains(response, 'Certificate revoked')
        self.assertNotContains(response, 'Certificate verified')
        self.assertFalse(response.context['valid'])

    def test_revoke_needs_a_reason(self):
        self.client.post(reverse('staffdesk:certificate-revoke', args=[self.cert.pk]), {'reason': ' '})
        self.cert.refresh_from_db()
        self.assertFalse(self.cert.is_revoked)

    def test_reinstate_makes_it_valid_again(self):
        report_services.revoke_certificate(self.cert, reason='Mistake', by=self.staff)
        self.client.post(reverse('staffdesk:certificate-reinstate', args=[self.cert.pk]))
        self.cert.refresh_from_db()
        self.assertFalse(self.cert.is_revoked)
        response = self.client.get(reverse('reports:verify', args=[self.cert.verification_uuid]))
        self.assertContains(response, 'Certificate verified')

    def test_regenerate_refreshes_the_mark_from_the_grade(self):
        report_services.override_grade(self.grade, value=81, reason='Moderated', by=self.staff)
        self.client.post(reverse('staffdesk:certificate-regenerate', args=[self.cert.pk]))
        self.cert.refresh_from_db()
        self.assertEqual(self.cert.final_mark, Decimal('81.00'))

    def test_revoked_tab_lists_only_revoked(self):
        report_services.revoke_certificate(self.cert, reason='x', by=self.staff)
        self.assertContains(self.client.get(reverse('staffdesk:certificates'), {'tab': 'revoked'}),
                            self.cert.number)
        self.assertNotContains(self.client.get(reverse('staffdesk:certificates')), self.cert.number)

    def test_a_revoked_certificate_is_not_reinstated_by_a_new_pass(self):
        report_services.revoke_certificate(self.cert, reason='x', by=self.staff)
        again = report_services.issue_certificate(self.student, module=self.module, kind='module')
        self.assertEqual(again.pk, self.cert.pk)
        self.assertTrue(again.is_revoked)


class AtRiskTests(AcademicFixture):
    def setUp(self):
        super().setUp()
        self.flag = RiskFlag.objects.create(student=self.student, module=self.module, score=75,
                                            reasons=['1 failing module(s)'])

    def test_triage_list_shows_severity_and_reason(self):
        response = self.client.get(reverse('staffdesk:at-risk'))
        self.assertContains(response, 'High · 75')
        self.assertContains(response, '1 failing module(s)')

    def test_acknowledge_moves_it_out_of_the_open_queue(self):
        self.client.post(reverse('staffdesk:at-risk-triage', args=[self.flag.pk]),
                         {'action': 'ack', 'note': 'Looking into it'})
        response = self.client.get(reverse('staffdesk:at-risk'))
        self.assertEqual(response.context['counts']['open'], 0)
        self.assertEqual(response.context['counts']['acknowledged'], 1)
        self.assertEqual(RiskTriage.objects.get(flag=self.flag).note, 'Looking into it')

    def test_resolve_and_reopen(self):
        self.client.post(reverse('staffdesk:at-risk-triage', args=[self.flag.pk]), {'action': 'resolve'})
        self.flag.refresh_from_db()
        self.assertTrue(self.flag.resolved)
        self.client.post(reverse('staffdesk:at-risk-triage', args=[self.flag.pk]), {'action': 'reopen'})
        self.flag.refresh_from_db()
        self.assertFalse(self.flag.resolved)

    def test_notify_student_and_educator_use_the_notification_service(self):
        with mock.patch('apps.communication.services.notify') as notify:
            self.client.post(reverse('staffdesk:at-risk-notify', args=[self.flag.pk, 'student']),
                             {'student-title': 'Hello', 'student-body': 'Checking in'})
            notify.assert_called_once()
            self.assertEqual(notify.call_args.args[0], self.student)
            self.assertEqual(notify.call_args.kwargs['category'], 'grades')
            self.assertTrue(notify.call_args.kwargs['email'])

            notify.reset_mock()
            self.client.post(reverse('staffdesk:at-risk-notify', args=[self.flag.pk, 'educator']),
                             {'educator-title': 'Heads up', 'educator-body': 'Please check in'})
            notify.assert_called_once()
            self.assertEqual(notify.call_args.args[0], self.educator)
        self.assertEqual(RiskTriage.objects.filter(flag=self.flag).count(), 2)

    def test_detail_page_links_the_composer(self):
        response = self.client.get(reverse('staffdesk:at-risk-detail', args=[self.flag.pk]))
        self.assertContains(response, f'/communication/announcements/new/?user={self.student.pk}')

    def test_scan_opens_one_flag_per_student_and_refreshes_it(self):
        RiskFlag.objects.all().delete()
        with mock.patch('apps.analytics.services.compute_risk', return_value=(60, ['No study'])):
            self.client.post(reverse('staffdesk:at-risk-scan'))
            self.client.post(reverse('staffdesk:at-risk-scan'))
        self.assertEqual(RiskFlag.objects.filter(student=self.student).count(), 1)

    def test_snapshot_take_and_view(self):
        response = self.client.post(reverse('staffdesk:snapshot-take'), {'period': 'weekly'})
        snap = ReportSnapshot.objects.get()
        self.assertRedirects(response, reverse('staffdesk:snapshot-detail', args=[snap.pk]))
        self.assertEqual(self.client.get(reverse('staffdesk:snapshot-detail', args=[snap.pk])).status_code, 200)


@mock.patch.object(views_academic, 'RUN_IN_THREAD', False)
class ImportTests(AcademicFixture):
    def test_import_page_links_the_existing_importer(self):
        self.assertContains(self.client.get(reverse('staffdesk:imports')), reverse('learning:content-import'))

    def test_running_a_command_records_its_output(self):
        response = self.client.post(reverse('staffdesk:import-run', args=['sync_module_chats']),
                                    {'sync_module_chats-dry_run': 'on'})
        run = ImportRun.objects.get()
        self.assertRedirects(response, reverse('staffdesk:import-run-detail', args=[run.pk]))
        self.assertEqual(run.status, ImportRun.STATUS_OK, run.output)
        self.assertEqual(run.args, ['--dry-run'])
        self.assertEqual(run.started_by, self.staff)
        self.assertIn('SDAFR', run.output)
        self.assertEqual(self.client.get(reverse('staffdesk:import-run-status', args=[run.pk])).json()['status'], 'ok')

    def test_a_failing_command_is_recorded_as_failed(self):
        with mock.patch.object(views_academic, 'call_command', side_effect=RuntimeError('boom')):
            self.client.post(reverse('staffdesk:import-run', args=['import_seed_packs']))
        run = ImportRun.objects.get()
        self.assertEqual(run.status, ImportRun.STATUS_FAILED)
        self.assertIn('boom', run.output)

    def test_paths_must_come_from_the_offered_list(self):
        self.client.post(reverse('staffdesk:import-run', args=['import_content_pack']),
                         {'import_content_pack-path': '/etc/passwd'})
        self.assertFalse(ImportRun.objects.exists())

    def test_unknown_commands_are_404(self):
        self.assertEqual(self.client.post(reverse('staffdesk:import-run', args=['flush'])).status_code, 404)


class AiArchiveTests(AcademicFixture):
    def test_reports_list_filter_and_detail(self):
        report = AiReport.objects.create(kind=AiReport.KIND_MEETING_RECAP, title='Week 3 recap',
                                         content='We covered IFRS 16.', module=self.module)
        AiReport.objects.create(kind=AiReport.KIND_PARENT, title='Parent letter')
        response = self.client.get(reverse('staffdesk:ai-reports'), {'kind': AiReport.KIND_MEETING_RECAP})
        self.assertContains(response, 'Week 3 recap')
        self.assertNotContains(response, 'Parent letter')
        self.assertContains(self.client.get(reverse('staffdesk:ai-report-detail', args=[report.pk])),
                            'We covered IFRS 16.')

    def test_insight_detail_and_status_change(self):
        insight = AiInsight.objects.create(kind='overdue_assessment', title='3 overdue', body='Details')
        self.assertContains(self.client.get(reverse('staffdesk:ai-insights')), '3 overdue')
        self.client.post(reverse('staffdesk:ai-insight-status', args=[insight.pk]), {'status': 'dismissed'})
        insight.refresh_from_db()
        self.assertEqual(insight.status, 'dismissed')
