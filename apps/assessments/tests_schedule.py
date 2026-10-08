"""Marking a numeric schedule, line by line.

The estate-duty ladder from the TAX Topic 5 pack is the worked example
throughout: eighteen marks across a handful of lines, some positive, one a
section 4(q) deduction written in brackets.
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import Person
from core.testing import enrol, make_module, make_programme

from . import models
from .marking import grade_attempt, mark_answer
from .schedule_marking import _decimal, mark_schedule

User = get_user_model()

LINES = [
    {'label': 'Primary residence', 'authority': 's3(2)', 'amount': '4500000',
     'marks': '1', 'tolerance': '0.005'},
    {'label': 'Listed shares', 'authority': 's3(2)', 'amount': '1250000',
     'marks': '2', 'tolerance': '0.005'},
    {'label': 'Section 4(q) — accrual to spouse', 'authority': 's4(q)',
     'amount': '-2000000', 'marks': '3', 'tolerance': '0.005'},
    {'label': 'Section 4A abatement', 'authority': 's4A', 'amount': '-3500000',
     'marks': '2', 'tolerance': '0.005'},
]


class ParsingTests(TestCase):
    """A candidate types what an accountant types."""

    def test_plain_numbers(self):
        self.assertEqual(_decimal('4500000'), Decimal('4500000'))
        self.assertEqual(_decimal(4500000), Decimal('4500000'))

    def test_thousands_separators_and_currency(self):
        self.assertEqual(_decimal('R4 500 000'), Decimal('4500000'))
        self.assertEqual(_decimal('4,500,000'), Decimal('4500000'))
        self.assertEqual(_decimal('4 500 000.50'), Decimal('4500000.50'))

    def test_brackets_are_a_deduction(self):
        """Every accounting workbook writes a negative in brackets. Refusing it
        would fail candidates for using their own notation."""
        self.assertEqual(_decimal('(2 000 000)'), Decimal('-2000000'))
        self.assertEqual(_decimal('(R2,000,000)'), Decimal('-2000000'))

    def test_minus_sign_is_the_same_thing(self):
        self.assertEqual(_decimal('-2000000'), Decimal('-2000000'))

    def test_nonsense_is_not_a_figure(self):
        for junk in ('', None, 'about four million', 'R', '-', '()'):
            self.assertIsNone(_decimal(junk), junk)


class ScheduleFixture(TestCase):
    def setUp(self):
        super().setUp()
        self.programme = make_programme('UCS', 'GR10')
        self.offering = make_module('Taxation', 'TAXA', programme=self.programme)
        self.student = User.objects.create_user(username='s@x.com', email='s@x.com', password='x')
        person = Person.objects.get(user=self.student)
        person.user_type = 'student'
        person.registered = True
        person.profile_status = True
        person.save()
        enrol(person, self.offering)

        self.paper = models.Assessment.objects.create(
            module=self.offering, title='Topic 5 Mock', kind='test',
            total_marks=8, pass_mark_pct=50, status=models.Assessment.STATUS_OPEN)
        section = models.Section.objects.create(assessment=self.paper, title='Required', order=0)
        self.question = models.Question.objects.create(
            section=section, type='schedule', order=0,
            text='(a) Calculate the estate duty payable', marks=Decimal('8'),
            config={'kind': 'schedule', 'lines': LINES},
            marking_mode=models.Question.MARKING_AUTO)

        self.attempt = models.AssessmentAttempt.objects.create(
            assessment=self.paper, student=self.student)

    def answer_with(self, lines):
        answer, _ = models.Answer.objects.get_or_create(
            attempt=self.attempt, question=self.question)
        answer.response = {'lines': lines}
        answer.save()
        return answer


class MarkingTests(ScheduleFixture):

    def test_every_line_right_scores_full_marks(self):
        answer = self.answer_with({'0': '4500000', '1': '1250000',
                                   '2': '(2000000)', '3': '-3500000'})
        awarded, correct, breakdown = mark_schedule(answer)
        self.assertEqual(awarded, Decimal('8'))
        self.assertTrue(correct)
        self.assertEqual(len(breakdown), 4)

    def test_one_wrong_line_costs_only_its_own_marks(self):
        """The point of marking a ladder line by line: a wrong abatement does
        not wipe out a correct residence."""
        answer = self.answer_with({'0': '4500000', '1': '999',
                                   '2': '(2000000)', '3': '-3500000'})
        awarded, correct, breakdown = mark_schedule(answer)
        self.assertEqual(awarded, Decimal('6'))     # lost the 2-mark line only
        self.assertFalse(correct)
        self.assertFalse(breakdown[1]['correct'])
        self.assertTrue(breakdown[0]['correct'])

    def test_rounding_to_the_rand_does_not_cost_a_mark(self):
        answer = self.answer_with({'0': '4500000.49'})
        _awarded, _correct, breakdown = mark_schedule(answer)
        self.assertTrue(breakdown[0]['correct'],
                        'half a rand in 4.5 million is inside tolerance')

    def test_a_genuinely_wrong_figure_still_fails(self):
        answer = self.answer_with({'0': '4600000'})   # 2.2% out
        _awarded, _correct, breakdown = mark_schedule(answer)
        self.assertFalse(breakdown[0]['correct'])

    def test_a_blank_line_scores_nothing_and_is_marked_unanswered(self):
        answer = self.answer_with({'0': '4500000'})
        awarded, _correct, breakdown = mark_schedule(answer)
        self.assertEqual(awarded, Decimal('1'))
        self.assertFalse(breakdown[1]['answered'])
        self.assertEqual(breakdown[1]['awarded'], '0')

    def test_a_sign_error_is_wrong(self):
        """Entering the s4(q) accrual as positive is the classic error and must
        be marked as one — it changes the estate value by four million."""
        answer = self.answer_with({'2': '2000000'})
        _awarded, _correct, breakdown = mark_schedule(answer)
        self.assertFalse(breakdown[2]['correct'])

    def test_a_question_with_no_lines_scores_zero_not_everything(self):
        """A schedule whose marking data failed to import must never silently
        award full marks."""
        self.question.config = {'kind': 'schedule', 'lines': []}
        self.question.save(update_fields=['config'])
        answer = self.answer_with({'0': '4500000'})
        awarded, correct, breakdown = mark_schedule(answer)
        self.assertEqual(awarded, Decimal('0'))
        self.assertFalse(correct)
        self.assertEqual(breakdown, [])

    def test_a_positional_list_is_tolerated(self):
        answer = self.answer_with(['4500000', '1250000', '(2000000)', '-3500000'])
        awarded, _correct, _breakdown = mark_schedule(answer)
        self.assertEqual(awarded, Decimal('8'))


class EngineTests(ScheduleFixture):
    """The schedule marker reached through the normal marking path."""

    def test_mark_answer_routes_a_schedule_to_its_marker(self):
        answer = self.answer_with({'0': '4500000', '1': '1250000',
                                   '2': '(2000000)', '3': '-3500000'})
        marks, correct = mark_answer(answer)
        self.assertEqual(marks, 8.0)
        self.assertTrue(correct)

    def test_grading_an_attempt_stores_the_breakdown(self):
        self.answer_with({'0': '4500000', '1': 'nonsense'})
        grade_attempt(self.attempt)
        self.attempt.refresh_from_db()
        answer = self.attempt.answers.get(question=self.question)
        self.assertEqual(answer.awarded_marks, Decimal('1.00'))
        self.assertTrue(answer.marked)
        self.assertEqual(len(answer.schedule_breakdown), 4)

    def test_the_candidates_figures_survive_marking(self):
        """A re-mark has to be able to see what they originally put."""
        self.answer_with({'0': '4500000'})
        grade_attempt(self.attempt)
        answer = self.attempt.answers.get(question=self.question)
        self.assertEqual(answer.response['lines'], {'0': '4500000'})

    def test_a_schedule_does_not_wait_for_a_human(self):
        self.answer_with({'0': '4500000'})
        grade_attempt(self.attempt)
        self.attempt.refresh_from_db()
        self.assertEqual(self.attempt.status, models.AssessmentAttempt.STATUS_MARKED)


class TakeAndSubmitTests(ScheduleFixture):
    """End to end: the page renders a line per row, and the POST is read back."""

    def test_the_take_page_offers_one_input_per_line_and_hides_the_answers(self):
        self.client.force_login(self.student)
        html = self.client.get(reverse('assessments:take', args=[self.paper.pk])).content.decode()
        for index in range(len(LINES)):
            self.assertIn(f'q_{self.question.id}_line_{index}', html)
        self.assertIn('Primary residence', html)
        self.assertNotIn('4500000', html, 'the expected figures must never reach the page')

    def test_submitting_the_sheet_marks_it(self):
        self.client.force_login(self.student)
        self.client.get(reverse('assessments:take', args=[self.paper.pk]))
        attempt = models.AssessmentAttempt.objects.filter(
            assessment=self.paper, student=self.student).latest('created_at')

        field = f'q_{self.question.id}'
        self.client.post(reverse('assessments:submit', args=[attempt.public_id]), {
            f'{field}_line_0': '4 500 000',
            f'{field}_line_1': 'R1,250,000',
            f'{field}_line_2': '(2 000 000)',
            f'{field}_line_3': '-3500000',
        })
        attempt.refresh_from_db()
        self.assertEqual(attempt.score, Decimal('8.00'))
        self.assertEqual(attempt.status, models.AssessmentAttempt.STATUS_MARKED)
