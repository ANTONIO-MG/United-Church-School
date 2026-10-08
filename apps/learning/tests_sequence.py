"""The weekly teaching sequence, and the gate that enforces it.

The rule under test is the one the whole taught-subject sequence rests on: a
candidate may not read the solution before they have attempted the question.
Everything else here exists to make sure that rule cannot be walked around —
through a filter tab, through a direct URL, or by another candidate submitting.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import Person
from apps.assessments.models import Assessment, AssessmentAttempt
from core.testing import enrol, make_module, make_programme

from . import models
from .access import Gate
from .sequence import LOCK_SEQUENCE, LOCK_SOLUTION, SequenceGate

User = get_user_model()


class WeekFixture(TestCase):
    """One week laid out the way the source documents lay it out: a study guide,
    a mock built from the question paper, and the solution workbook."""

    def setUp(self):
        super().setUp()
        self.programme = make_programme('UCS', 'GR10')
        self.offering = make_module('Mathematics', 'MATH', programme=self.programme)

        self.student = self._user('sam@example.com', 'student')
        enrol(self.student.profile, self.offering)
        self.educator = self._user('ed@example.com', 'educator')
        self.offering.educators.add(self.educator.profile)

        self.topic = models.Topic.objects.create(
            programme_module=self.offering, code='ALG', title='Algebraic expressions')
        self.phase = models.ModulePhase.objects.create(
            programme_module=self.offering, kind=models.ModulePhase.KIND_TEST, sequence=1)
        self.week = models.ModuleWeek.objects.create(
            phase=self.phase, number=1, title='Algebraic expressions')
        # A week covers its topics through WeekTopic (the single ``topic`` FK
        # was replaced by this ordered series in migration 0027).
        models.WeekTopic.objects.create(week=self.week, topic=self.topic, order=0)

        self.lesson = models.Lesson.objects.create(
            module=self.offering, topic=self.topic, title='Topic 5 guide',
            status=models.Lesson.STATUS_PUBLISHED)
        self.paper = Assessment.objects.create(
            module=self.offering, topic=self.topic, title='Topic 5 Mock',
            kind='test', total_marks=50, status=Assessment.STATUS_OPEN,
            release_solution=Assessment.RELEASE_ON_SUBMIT)

        self.guide = self._material(models.ModuleMaterial.KIND_STUDY_GUIDE,
                                    'Study guide', lesson=self.lesson, order=0)
        self.mock = self._material(models.ModuleMaterial.KIND_QUESTIONS,
                                   'Topic 5 Mock', assessment=self.paper, order=1)
        self.solution = self._material(models.ModuleMaterial.KIND_ANSWERS,
                                       'Topic 5 Solution', order=2)

    def _user(self, email, role):
        """A user of ``role``, re-fetched so ``user.profile`` is not stale.

        The post-save signal that creates the ``Person`` populates the reverse
        one-to-one cache on the very ``User`` instance it was handed, so editing
        the profile afterwards leaves ``user.profile`` holding the *old* row.
        Requests never hit this — auth middleware loads the user fresh — but a
        test that calls a model method directly does, and would silently assert
        against a role nobody has.
        """
        user = User.objects.create_user(username=email, email=email, password='x')
        person = Person.objects.get(user=user)
        person.user_type = role
        person.registered = True
        person.profile_status = True
        person.save()
        return User.objects.get(pk=user.pk)

    def _material(self, kind, title, *, lesson=None, assessment=None, order=0):
        return models.ModuleMaterial.objects.create(
            phase=self.phase, week=self.week, kind=kind, title=title,
            lesson=lesson, assessment=assessment, order=order)

    # -- helpers -----------------------------------------------------------
    def gate_for(self, user):
        materials = list(self.week.materials.all())
        commercial = Gate(user, self.offering)
        return SequenceGate(user, materials, bypass=commercial.can_author), materials

    def open_guide(self):
        models.StudySession.objects.create(student=self.student, lesson=self.lesson)

    def submit_mock(self, student=None):
        return AssessmentAttempt.objects.create(
            assessment=self.paper, student=student or self.student,
            status=AssessmentAttempt.STATUS_SUBMITTED)


class SolutionGateTests(WeekFixture):
    """The rule the product exists for."""

    def test_the_solution_is_shut_until_the_candidate_submits(self):
        sequence, materials = self.gate_for(self.student)
        is_open, reason = sequence.check(self.solution, materials)
        self.assertFalse(is_open)
        self.assertEqual(reason, LOCK_SOLUTION)

    def test_submitting_the_mock_opens_the_solution(self):
        self.open_guide()
        self.submit_mock()
        sequence, materials = self.gate_for(self.student)
        is_open, _ = sequence.check(self.solution, materials)
        self.assertTrue(is_open)

    def test_starting_an_attempt_is_not_submitting_it(self):
        """Opening the paper and abandoning it must not release the memo —
        otherwise the gate is one click wide."""
        AssessmentAttempt.objects.create(
            assessment=self.paper, student=self.student,
            status=AssessmentAttempt.STATUS_IN_PROGRESS)
        sequence, materials = self.gate_for(self.student)
        is_open, reason = sequence.check(self.solution, materials)
        self.assertFalse(is_open)
        self.assertEqual(reason, LOCK_SOLUTION)

    def test_another_candidates_submission_does_not_open_it(self):
        classmate = self._user('other@example.com', 'student')
        enrol(classmate.profile, self.offering)
        self.submit_mock(student=classmate)

        sequence, materials = self.gate_for(self.student)
        is_open, _ = sequence.check(self.solution, materials)
        self.assertFalse(is_open, 'the gate is per candidate, not per cohort')

    def test_a_solution_with_no_paper_beside_it_stays_open(self):
        """Reference material must not be locked behind a paper that does not
        exist — there would be no way to earn it."""
        loose_week = models.ModuleWeek.objects.create(
            phase=self.phase, number=9, title='Reference')
        loose = models.ModuleMaterial.objects.create(
            phase=self.phase, week=loose_week,
            kind=models.ModuleMaterial.KIND_ANSWERS, title='Worked examples')
        sequence = SequenceGate(self.student, [loose])
        is_open, _ = sequence.check(loose, [loose])
        self.assertTrue(is_open)


class SequenceOrderTests(WeekFixture):
    """Guide → mock → challenge, in that order."""

    def test_the_study_guide_is_always_open(self):
        sequence, materials = self.gate_for(self.student)
        is_open, _ = sequence.check(self.guide, materials)
        self.assertTrue(is_open)

    def test_the_mock_waits_for_the_guide(self):
        sequence, materials = self.gate_for(self.student)
        is_open, reason = sequence.check(self.mock, materials)
        self.assertFalse(is_open)
        self.assertEqual(reason, LOCK_SEQUENCE)

    def test_opening_the_guide_unlocks_the_mock(self):
        self.open_guide()
        sequence, materials = self.gate_for(self.student)
        is_open, _ = sequence.check(self.mock, materials)
        self.assertTrue(is_open)

    def test_reference_material_is_never_sequenced(self):
        blueprint = self._material(models.ModuleMaterial.KIND_BLUEPRINT, 'Test 1 blueprint')
        sequence, materials = self.gate_for(self.student)
        is_open, _ = sequence.check(blueprint, materials)
        self.assertTrue(is_open, 'a blueprint is reference, not a step')

    def test_next_step_points_at_the_guide_first_then_the_mock(self):
        sequence, materials = self.gate_for(self.student)
        self.assertEqual(sequence.next_step(materials), self.guide)

        self.open_guide()
        sequence, materials = self.gate_for(self.student)
        self.assertEqual(sequence.next_step(materials), self.mock)

    def test_a_week_in_another_week_does_not_gate_this_one(self):
        """Sequencing is within a week. Week 2's guide must not lock week 1."""
        week2 = models.ModuleWeek.objects.create(phase=self.phase, number=2, title='Next')
        later_guide = models.ModuleMaterial.objects.create(
            phase=self.phase, week=week2,
            kind=models.ModuleMaterial.KIND_STUDY_GUIDE, title='Week 2 guide')
        self.open_guide()
        sequence, materials = self.gate_for(self.student)
        is_open, _ = sequence.check(self.mock, materials)
        self.assertTrue(is_open)
        self.assertNotIn(later_guide, materials)


class AuthorBypassTests(WeekFixture):
    """Whoever is writing the week sees all of it."""

    def test_an_educator_is_not_sequenced(self):
        sequence, materials = self.gate_for(self.educator)
        for material in (self.guide, self.mock, self.solution):
            is_open, _ = sequence.check(material, materials)
            self.assertTrue(is_open, f'{material.title} must be open to its author')

    def test_an_educator_has_no_next_step(self):
        sequence, materials = self.gate_for(self.educator)
        self.assertIsNone(sequence.next_step(materials))


class MaterialDoorTests(WeekFixture):
    """The gated door is the only way in — including for files."""

    def test_a_locked_solution_redirects_rather_than_serving(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse('learning:material-open', args=[self.solution.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(self.offering.pk), response.url)

    def test_the_same_url_serves_once_the_attempt_is_in(self):
        self.open_guide()
        self.submit_mock()
        self.client.force_login(self.student)
        response = self.client.get(reverse('learning:material-open', args=[self.solution.pk]))
        # No file attached in the fixture, so it lands back on the module page
        # with an "empty" notice rather than a refusal — the gate let it through.
        self.assertEqual(response.status_code, 302)

    def test_a_material_state_links_through_the_door_not_at_storage(self):
        gate = Gate(self.student, self.offering)
        state = gate.for_material(self.guide)
        self.assertTrue(state.open)
        self.assertEqual(state.url, reverse('learning:material-open', args=[self.guide.pk]))

    def test_a_sequence_lock_never_offers_to_sell_the_row(self):
        gate = Gate(self.student, self.offering)
        states = gate.states_for(list(self.week.materials.all()),
                                 sequence=SequenceGate(self.student, list(self.week.materials.all())),
                                 week_materials=list(self.week.materials.all()))
        locked = [s for s in states if s.locked]
        self.assertTrue(locked)
        for state in locked:
            self.assertTrue(state.is_sequence_lock)
            self.assertFalse(state.can_buy_single,
                             'they already own it — they have not earned it yet')


class SolutionReleaseTests(WeekFixture):
    """``Assessment.solution_released_for`` — the same rule, at the paper."""

    def test_not_released_before_submission(self):
        self.assertFalse(self.paper.solution_released_for(self.student))

    def test_released_after_submission(self):
        self.submit_mock()
        self.assertTrue(self.paper.solution_released_for(self.student))

    def test_staff_always_see_it(self):
        admin = self._user('boss@example.com', 'admin')
        self.assertTrue(self.paper.solution_released_for(admin))

    def test_manual_release_ignores_submission(self):
        self.paper.release_solution = Assessment.RELEASE_MANUAL
        self.paper.save(update_fields=['release_solution'])
        self.submit_mock()
        self.assertFalse(self.paper.solution_released_for(self.student))

        self.paper.solution_notes = {'released': True}
        self.paper.save(update_fields=['solution_notes'])
        self.assertTrue(self.paper.solution_released_for(self.student))

    def test_the_result_page_withholds_the_memo_until_submission(self):
        attempt = AssessmentAttempt.objects.create(
            assessment=self.paper, student=self.student,
            status=AssessmentAttempt.STATUS_IN_PROGRESS)
        self.client.force_login(self.student)
        response = self.client.get(reverse('assessments:result', args=[attempt.public_id]))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['show_solution'])
        for row in response.context['rows']:
            self.assertIsNone(row['solution'],
                              'an unreleased memo must not reach the page at all')
