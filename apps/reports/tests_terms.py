"""Term reporting (GDE four terms): automatic marks, mark sheets, report cards.

Covers: the automatic % only counts assessments dated inside the term; the
subject educator saves and publishes; learners and parents never see drafts; a
parent only ever sees their own child; an educator who does not teach the
subject is refused; and the year summary / ``final_marks_for`` follow the CAPS
SBA : exam weights (Grade 8 — Senior Phase — is SBA 40 / exam 60).
"""
import datetime

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import ParentLink, Person
from core.testing import enrol, make_module, make_programme

from . import term_results as tr
from . import terms
from .models import TermResult

User = get_user_model()
LOCMEM_CACHE = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}


def _at(y, m, d):
    return timezone.make_aware(datetime.datetime(y, m, d, 12, 0))


@override_settings(CACHES=LOCMEM_CACHE)
class TermFixture(TestCase):
    YEAR = 2026

    def setUp(self):
        cache.clear()
        self.addCleanup(cache.clear)
        self.programme = make_programme('UCS', 'GR08', grade=8, name='Grade 8')
        self.math = make_module('Mathematics', 'MATH', programme=self.programme)
        self.eng = make_module('English Home Language', 'ENG-HL', programme=self.programme)

        self.learner = self._user('learner@example.com', 'Lerato', 'Mokoena', 'student')
        self.other = self._user('other@example.com', 'Thabo', 'Nkosi', 'student')
        self.parent = self._user('parent@example.com', 'Palesa', 'Mokoena', 'parent')
        self.teacher = self._user('teacher@example.com', 'Tess', 'Maths', 'educator')
        self.stranger = self._user('stranger@example.com', 'Sam', 'Other', 'educator')
        self.office = self._user('office@example.com', 'Olive', 'Office', 'staff')

        for who in (self.learner, self.other):
            enrol(who.profile, self.math)
            enrol(who.profile, self.eng)
        self.math.educators.add(self.teacher.profile)
        ParentLink.objects.create(parent=self.parent, student=self.learner)

    def _user(self, email, first, last, role):
        user = User.objects.create_user(username=email, email=email, password='x',
                                        first_name=first, last_name=last)
        person = Person.objects.get(user=user)
        person.first_name, person.last_name, person.user_type = first, last, role
        person.registered = person.profile_status = True
        person.save()
        return User.objects.get(pk=user.pk)

    def _assessment(self, kind, when, module=None, total=100):
        from apps.assessments.models import Assessment
        return Assessment.objects.create(module=module or self.math, title=f'{kind} {when:%d %b}',
                                         kind=kind, total_marks=total, status='closed',
                                         available_from=when, available_to=when)

    def _mark(self, assessment, student, score):
        from apps.assessments.models import AssessmentAttempt
        AssessmentAttempt.objects.create(assessment=assessment, student=student, status='marked',
                                         score=score, submitted_at=timezone.now())

    def sheet_url(self, term, module=None):
        return reverse('reports:mark-sheet', args=[(module or self.math).pk, self.YEAR, term])


class TermCalendarTests(TestCase):
    def test_term_for_dates(self):
        self.assertEqual(terms.term_for(datetime.date(2026, 2, 10)), (2026, 1))
        self.assertEqual(terms.term_for(datetime.date(2026, 5, 10)), (2026, 2))
        # The July holiday belongs to the term that has just ended.
        self.assertEqual(terms.term_for(datetime.date(2026, 7, 5)), (2026, 2))
        self.assertEqual(terms.term_for(datetime.date(2026, 11, 1)), (2026, 4))

    def test_labels(self):
        self.assertEqual(terms.exam_label(2), 'Mid-year exam')
        self.assertEqual(terms.exam_label(4), 'Final exam')
        self.assertEqual(terms.exam_label(1), '')


class AutoMarkTests(TermFixture):
    def test_only_assessments_dated_in_the_term_count(self):
        t1 = self._assessment('test', _at(2026, 3, 1))
        t1b = self._assessment('quiz', _at(2026, 2, 1), total=20)
        t2 = self._assessment('test', _at(2026, 5, 12))
        self._mark(t1, self.learner, 80)
        self._mark(t1b, self.learner, 10)          # 50 %
        self._mark(t2, self.learner, 40)
        self.assertEqual(tr.compute_auto(self.learner, self.math, 2026, 1), 65.0)
        self.assertEqual(tr.compute_auto(self.learner, self.math, 2026, 2), 40.0)
        self.assertIsNone(tr.compute_auto(self.learner, self.math, 2026, 3))
        self.assertIsNone(tr.compute_auto(self.learner, self.math, 2027, 1))

    def test_assignments_count_and_exam_papers_are_kept_apart(self):
        from apps.assessments.models import AssignmentSubmission
        assignment = self._assessment('assignment', _at(2026, 5, 1), total=50)
        AssignmentSubmission.objects.create(assessment=assignment, student=self.learner, grade=35)
        paper = self._assessment('exam_section', _at(2026, 6, 10))
        self._mark(paper, self.learner, 55)
        self.assertEqual(tr.compute_auto(self.learner, self.math, 2026, 2), 70.0)
        self.assertEqual(tr.compute_auto_exam(self.learner, self.math, 2026, 2), 55.0)
        self.assertIsNone(tr.compute_auto_exam(self.learner, self.math, 2026, 3))

    def test_refresh_creates_a_draft_per_learner_and_keeps_educator_marks(self):
        self._mark(self._assessment('test', _at(2026, 3, 1)), self.learner, 72)
        rows = tr.refresh_term(self.math, 2026, 1)
        self.assertEqual({r.student_id for r in rows}, {self.learner.pk, self.other.pk})
        mine = TermResult.objects.get(student=self.learner, module=self.math, year=2026, term=1)
        self.assertEqual(float(mine.auto_pct), 72.0)
        self.assertEqual(float(mine.term_pct), 72.0)
        self.assertEqual(mine.status, TermResult.STATUS_DRAFT)
        mine.sba_pct, mine.comment = 60, 'Good effort'
        mine.recompute()
        mine.save()
        tr.refresh_term(self.math, 2026, 1)
        mine.refresh_from_db()
        self.assertEqual((float(mine.sba_pct), mine.comment, float(mine.term_pct)), (60.0, 'Good effort', 60.0))


class MarkSheetTests(TermFixture):
    def test_subject_educator_saves_then_publishes(self):
        self.client.force_login(self.teacher)
        self.assertEqual(self.client.get(self.sheet_url(2)).status_code, 200)
        data = {'action': 'save', f'sba_{self.learner.pk}': '70', f'exam_{self.learner.pk}': '50',
                f'comment_{self.learner.pk}': 'Steady progress.'}
        self.assertEqual(self.client.post(self.sheet_url(2), data).status_code, 302)
        result = TermResult.objects.get(student=self.learner, module=self.math, year=2026, term=2)
        # Grade 8 term 2: 40 % SBA + 60 % mid-year exam = 28 + 30.
        self.assertEqual(float(result.term_pct), 58.0)
        self.assertEqual(result.level, 4)
        self.assertEqual(result.status, TermResult.STATUS_DRAFT)
        self.assertEqual(result.entered_by, self.teacher)

        # Drafts are invisible to the learner and the parent.
        self.client.force_login(self.learner)
        page = self.client.get(reverse('reports:report-card') + '?year=2026&term=2').content.decode()
        self.assertNotIn('Steady progress.', page)
        self.client.force_login(self.parent)
        page = self.client.get(reverse('reports:report-card') + '?year=2026&term=2').content.decode()
        self.assertNotIn('Steady progress.', page)

        self.client.force_login(self.teacher)
        data['action'] = 'publish'
        self.client.post(self.sheet_url(2), data)
        result.refresh_from_db()
        self.assertEqual(result.status, TermResult.STATUS_PUBLISHED)
        self.assertIsNotNone(result.published_at)

        from apps.communication.models import Notification
        self.assertTrue(Notification.objects.filter(recipient=self.learner).exists())
        self.assertTrue(Notification.objects.filter(recipient=self.parent).exists())

        self.client.force_login(self.learner)
        page = self.client.get(reverse('reports:report-card') + '?year=2026&term=2').content.decode()
        self.assertIn('Steady progress.', page)
        self.assertIn('58%', page)
        self.client.force_login(self.parent)
        page = self.client.get(reverse('reports:report-card') + '?year=2026&term=2').content.decode()
        self.assertIn('Steady progress.', page)

    def test_invalid_mark_is_rejected_and_nothing_saved(self):
        self.client.force_login(self.teacher)
        self.client.post(self.sheet_url(1), {'action': 'save', f'sba_{self.learner.pk}': '140'})
        result = TermResult.objects.get(student=self.learner, module=self.math, year=2026, term=1)
        self.assertIsNone(result.sba_pct)

    def test_no_exam_field_in_term_1_or_for_foundation_phase(self):
        self.client.force_login(self.teacher)
        self.assertNotContains(self.client.get(self.sheet_url(1)), 'name="exam_')
        self.assertContains(self.client.get(self.sheet_url(4)), 'Final exam')
        gr2 = make_programme('UCS', 'GR02', grade=2, name='Grade 2')
        fp_math = make_module('Mathematics', 'MATH', programme=gr2)
        self.assertFalse(tr.exam_applies(fp_math, 4))

    def test_only_the_subjects_educators_and_staff_may_open_the_sheet(self):
        self.client.force_login(self.stranger)
        self.assertEqual(self.client.get(self.sheet_url(1)).status_code, 404)
        self.assertEqual(self.client.post(self.sheet_url(1), {'action': 'publish'}).status_code, 404)
        self.assertEqual(self.client.get(self.sheet_url(1, self.eng)).status_code, 404)
        self.client.force_login(self.teacher)
        self.assertEqual(self.client.get(self.sheet_url(1, self.eng)).status_code, 404)
        self.client.force_login(self.learner)
        self.assertEqual(self.client.get(self.sheet_url(1)).status_code, 404)
        self.assertEqual(self.client.get(reverse('reports:marks')).status_code, 404)
        self.client.force_login(self.office)
        self.assertEqual(self.client.get(self.sheet_url(1, self.eng)).status_code, 200)

    def test_index_lists_only_taught_subjects(self):
        self.client.force_login(self.teacher)
        page = self.client.get(reverse('reports:marks') + '?year=2026').content.decode()
        self.assertIn('Mathematics', page)
        self.assertNotIn('English Home Language', page)

    def test_csv_export(self):
        self.client.force_login(self.teacher)
        response = self.client.get(reverse('reports:mark-sheet-csv', args=[self.math.pk, 2026, 2]))
        self.assertEqual(response['Content-Type'], 'text/csv; charset=utf-8')
        body = response.content.decode()
        self.assertIn('Mid-year exam %', body.splitlines()[0])
        self.assertIn('Lerato Mokoena', body)


class ReportCardAccessTests(TermFixture):
    def setUp(self):
        super().setUp()
        for student, comment in ((self.learner, 'Lerato comment'), (self.other, 'Thabo comment')):
            r = TermResult(student=student, module=self.math, year=2026, term=1, sba_pct=66, comment=comment)
            tr.publish(r)
            r.save()

    def test_parent_sees_only_their_own_child(self):
        self.client.force_login(self.parent)
        page = self.client.get(reverse('reports:report-card')
                               + f'?student={self.other.pk}&year=2026&term=1').content.decode()
        self.assertIn('Lerato comment', page)
        self.assertNotIn('Thabo comment', page)
        self.assertNotIn('Thabo', page)

    def test_learner_sees_only_their_own(self):
        self.client.force_login(self.learner)
        page = self.client.get(reverse('reports:report-card')
                               + f'?student={self.other.pk}&year=2026&term=1').content.decode()
        self.assertIn('Lerato comment', page)
        self.assertNotIn('Thabo comment', page)

    def test_school_header_and_caps_descriptor(self):
        self.client.force_login(self.learner)
        page = self.client.get(reverse('reports:report-card') + '?year=2026&term=1').content.decode()
        self.assertIn('Grade 8', page)
        self.assertIn('Substantial achievement', page)      # 66 % → level 5

    def test_staff_overview_counts(self):
        self.client.force_login(self.office)
        response = self.client.get(reverse('reports:term-overview') + '?year=2026')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '2 / 0 / 0')
        self.client.force_login(self.teacher)
        self.assertEqual(self.client.get(reverse('reports:term-overview')).status_code, 404)

    def test_pdf_download(self):
        self.client.force_login(self.learner)
        response = self.client.get(reverse('reports:report-card-pdf') + '?year=2026&term=1')
        if response.status_code == 200:
            self.assertEqual(response['Content-Type'], 'application/pdf')
            self.assertTrue(response.content.startswith(b'%PDF'))
        else:                                    # xhtml2pdf missing → back to the page
            self.assertEqual(response.status_code, 302)


class YearSummaryTests(TermFixture):
    def _term(self, module, term, sba, exam=None, status=TermResult.STATUS_PUBLISHED, student=None):
        r = TermResult(student=student or self.learner, module=module, year=2026, term=term,
                       sba_pct=sba, exam_pct=exam, status=status)
        r.recompute()
        r.save()
        return r

    def test_grade_8_final_mark_is_sba_40_exam_60(self):
        for term, sba in ((1, 60), (2, 70), (3, 80), (4, 50)):
            self._term(self.math, term, sba, exam=50 if term == 4 else None)
        for term in (1, 2, 3, 4):
            self._term(self.eng, term, 40, exam=30 if term == 4 else None)
        summary = tr.year_summary(self.learner, 2026)
        math = next(s for s in summary['subjects'] if s['code'] == 'MATH')
        # SBA year mark 65; final = 0.4 × 65 + 0.6 × 50 = 56.
        self.assertEqual((math['sba'], math['exam'], math['final']), (65.0, 50.0, 56.0))
        self.assertEqual(math['level'], 4)
        self.assertTrue(math['passed'])                      # Senior Phase maths ≥ 40
        eng = next(s for s in summary['subjects'] if s['code'] == 'ENG-HL')
        self.assertEqual(eng['final'], 34.0)                 # 16 + 18
        self.assertFalse(eng['passed'])                      # Home Language needs 50
        self.assertEqual(tr.final_marks_for(self.learner, self.programme, 2026),
                         {'MATH': 56.0, 'ENG-HL': 34.0})
        self.assertEqual(summary['promotion']['outcome'], 'retain')

    def test_drafts_count_for_promotion_but_not_on_the_report(self):
        self._term(self.math, 1, 70, status=TermResult.STATUS_DRAFT)
        self.assertEqual(tr.final_marks_for(self.learner, self.programme, 2026), {'MATH': 70.0})
        self.assertEqual(tr.final_marks_for(self.learner, self.programme, 2026, published_only=True), {})
        self.assertEqual(tr.year_summary(self.learner, 2026)['final_marks'], {})

    def test_foundation_phase_is_sba_only(self):
        gr2 = make_programme('UCS', 'GR02', grade=2, name='Grade 2')
        fp = make_module('Mathematics', 'MATH', programme=gr2)
        kid = self._user('kid@example.com', 'Kid', 'One', 'student')
        enrol(kid.profile, fp)
        for term, sba in ((1, 50), (2, 60), (3, 70), (4, 80)):
            self._term(fp, term, sba, exam=10 if term == 4 else None, student=kid)
        self.assertEqual(tr.final_marks_for(kid, gr2, 2026), {'MATH': 65.0})

    def test_term_4_report_card_shows_final_and_promotion(self):
        for term in (1, 2, 3, 4):
            self._term(self.math, term, 60, exam=70 if term == 4 else None)
        self.client.force_login(self.learner)
        page = self.client.get(reverse('reports:report-card') + '?year=2026&term=4').content.decode()
        self.assertIn('Final mark', page)
        self.assertIn('66%', page)                            # 24 + 42
        self.assertIn('Promotion requirements', page)
