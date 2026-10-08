"""Tests for the assessment lifecycle and the assessments list.

The lifecycle is the security-relevant part: before it existed, the create form
took ``status`` straight from a POST field, so an assessment could go from Draft
to Open — visible to learners, markable, feeding the gradebook — in one hop with
no questions in it. These tests pin every legal move and, more importantly,
every illegal one.
"""

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.accounts.models import Person

from . import models
from core.testing import enrol, make_module, make_programme

User = get_user_model()

LOCMEM_CACHE = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}
A = models.Assessment


@override_settings(CACHES=LOCMEM_CACHE)
class AssessmentFixtureMixin(TestCase):

    def setUp(self):
        super().setUp()
        cache.clear()
        self.addCleanup(cache.clear)

        self.programme = make_programme('UCS', 'GR10')
        self.module = make_module('Advanced Auditing', 'AUDA', programme=self.programme)

        self.educator = self._user('ed@example.com', 'educator')
        self.student = self._user('stu@example.com', 'student')
        self.module.educators.add(self.educator.profile)
        enrol(self.student.profile, self.module)

        self.assessment = A.objects.create(
            module=self.module, title='Auditing Quiz 1', kind=A.KIND_QUIZ,
            total_marks=20, pass_mark_pct=50, status=A.STATUS_DRAFT,
            created_by=self.educator)

    def _user(self, email, role):
        user = User.objects.create_user(username=email, email=email, password='x',
                                        first_name=role.title(), last_name='User')
        person = Person.objects.get(user=user)
        person.user_type = role
        person.registered = True
        person.profile_status = True
        person.save()
        return user

    def add_question(self, assessment=None):
        assessment = assessment or self.assessment
        section, _ = models.Section.objects.get_or_create(
            assessment=assessment, title='Questions', defaults={'order': 0})
        return models.Question.objects.create(section=section, type='tf', text='True?', marks=1)


class LifecycleModelTests(AssessmentFixtureMixin):

    def test_a_new_assessment_starts_as_a_draft(self):
        self.assertEqual(self.assessment.status, A.STATUS_DRAFT)

    def test_the_review_state_exists_between_draft_and_publication(self):
        self.assertIn((A.STATUS_REVIEW, 'In review'), A.STATUS_CHOICES)

    def test_a_draft_may_only_go_to_review_or_be_archived(self):
        self.assertEqual(A.STATUS_TRANSITIONS[A.STATUS_DRAFT],
                         {A.STATUS_REVIEW, A.STATUS_ARCHIVED})

    def test_a_draft_cannot_jump_straight_to_open(self):
        self.add_question()
        self.assertFalse(self.assessment.can_transition_to(A.STATUS_OPEN))
        with self.assertRaises(ValidationError):
            self.assessment.transition_to(A.STATUS_OPEN)
        self.assessment.refresh_from_db()
        self.assertEqual(self.assessment.status, A.STATUS_DRAFT,
                         'a refused transition must not be persisted')

    def test_the_full_happy_path_draft_review_open_closed_archived(self):
        self.add_question()
        for target in (A.STATUS_REVIEW, A.STATUS_OPEN, A.STATUS_CLOSED, A.STATUS_ARCHIVED):
            self.assessment.transition_to(target)
            self.assertEqual(self.assessment.status, target)
        self.assessment.refresh_from_db()
        self.assertEqual(self.assessment.status, A.STATUS_ARCHIVED)

    def test_review_can_send_work_back_to_draft(self):
        self.assessment.transition_to(A.STATUS_REVIEW)
        self.assessment.transition_to(A.STATUS_DRAFT)
        self.assertEqual(self.assessment.status, A.STATUS_DRAFT)

    def test_an_archived_assessment_reopens_as_a_draft_not_as_open(self):
        self.assessment.transition_to(A.STATUS_ARCHIVED)
        self.assertEqual(A.STATUS_TRANSITIONS[A.STATUS_ARCHIVED], {A.STATUS_DRAFT})
        with self.assertRaises(ValidationError):
            self.assessment.transition_to(A.STATUS_OPEN)

    def test_an_empty_assessment_cannot_be_opened(self):
        self.assessment.transition_to(A.STATUS_REVIEW)
        with self.assertRaises(ValidationError) as ctx:
            self.assessment.transition_to(A.STATUS_OPEN)
        self.assertIn('question', ' '.join(ctx.exception.messages).lower())
        self.assessment.refresh_from_db()
        self.assertEqual(self.assessment.status, A.STATUS_REVIEW)

    def test_an_empty_assessment_cannot_be_scheduled_either(self):
        self.assessment.transition_to(A.STATUS_REVIEW)
        with self.assertRaises(ValidationError):
            self.assessment.transition_to(A.STATUS_SCHEDULED)

    def test_transitioning_to_the_current_state_is_a_no_op_not_an_error(self):
        self.assessment.transition_to(A.STATUS_DRAFT)
        self.assertEqual(self.assessment.status, A.STATUS_DRAFT)

    def test_an_unknown_state_is_refused(self):
        with self.assertRaises(ValidationError):
            self.assessment.transition_to('published-ish')

    def test_available_transitions_only_offers_legal_moves(self):
        offered = dict(self.assessment.available_transitions())
        self.assertEqual(set(offered), {A.STATUS_REVIEW, A.STATUS_ARCHIVED})
        for value, label in self.assessment.available_transitions():
            self.assertTrue(self.assessment.can_transition_to(value))
            self.assertIsInstance(label, str)

    def test_every_state_declares_its_transitions(self):
        """A state missing from the map would be a dead end nobody could leave."""
        for value, _ in A.STATUS_CHOICES:
            self.assertIn(value, A.STATUS_TRANSITIONS, f'{value} has no way out')
        for targets in A.STATUS_TRANSITIONS.values():
            for target in targets:
                self.assertIn(target, dict(A.STATUS_CHOICES),
                              f'{target} is not a real state')


class LifecycleViewTests(AssessmentFixtureMixin):

    def setUp(self):
        super().setUp()
        self.client.force_login(self.educator)
        self.url = reverse('assessments:status-change', args=[self.assessment.pk])

    def test_creating_an_assessment_ignores_a_status_in_the_form(self):
        response = self.client.post(reverse('assessments:create'), {
            'module': self.module.pk, 'title': 'Sneaky', 'kind': A.KIND_QUIZ,
            'status': 'open',
        })
        self.assertEqual(response.status_code, 302)
        created = A.objects.get(title='Sneaky')
        self.assertEqual(created.status, A.STATUS_DRAFT,
                         'the create form must not be able to publish')

    def test_a_legal_move_is_applied(self):
        self.client.post(self.url, {'status': A.STATUS_REVIEW})
        self.assessment.refresh_from_db()
        self.assertEqual(self.assessment.status, A.STATUS_REVIEW)

    def test_an_illegal_move_posted_by_hand_is_refused(self):
        self.add_question()
        self.client.post(self.url, {'status': A.STATUS_OPEN})
        self.assessment.refresh_from_db()
        self.assertEqual(self.assessment.status, A.STATUS_DRAFT)

    def test_someone_who_does_not_teach_the_module_cannot_move_it(self):
        self.client.force_login(self.student)
        response = self.client.post(self.url, {'status': A.STATUS_REVIEW})
        self.assertEqual(response.status_code, 403)
        self.assessment.refresh_from_db()
        self.assertEqual(self.assessment.status, A.STATUS_DRAFT)

    def test_a_get_does_not_change_state(self):
        self.client.get(self.url, {'status': A.STATUS_REVIEW})
        self.assessment.refresh_from_db()
        self.assertEqual(self.assessment.status, A.STATUS_DRAFT)

    def test_the_builder_only_offers_moves_that_will_be_accepted(self):
        html = self.client.get(reverse('assessments:builder',
                                       args=[self.assessment.pk])).content.decode()
        self.assertIn(f'value="{A.STATUS_REVIEW}"', html)
        self.assertNotIn(f'value="{A.STATUS_OPEN}"', html,
                         'a draft cannot open, so the button must not be offered')


class AssessmentIndexTests(AssessmentFixtureMixin):

    def setUp(self):
        super().setUp()
        self.add_question()
        self.assessment.transition_to(A.STATUS_REVIEW)
        self.assessment.transition_to(A.STATUS_OPEN)
        self.client.force_login(self.student)

    def html(self):
        response = self.client.get(reverse('assessments:index'))
        self.assertEqual(response.status_code, 200)
        return response.content.decode()

    def test_every_column_carries_a_filter_control(self):
        html = self.html()
        for index in range(7):      # Title, Type, Subject, Total, Pass, Time, Status
            self.assertIn(f'data-col="{index}"', html,
                          f'column {index} has no filter')
        self.assertEqual(html.count('class="dropdown-menu filter-menu"'), 7)

    def test_the_filter_columns_are_the_ones_the_user_named(self):
        """Each named column must be a real header cell, in order."""
        import re
        headers = re.findall(r'<th class="col-filter" data-col="\d+">\s*(\w+)', self.html())
        self.assertEqual(headers,
                         ['Title', 'Type', 'Subject', 'Total', 'Pass', 'Time', 'Status'])

    # The class name always appears in the page's <style> block, so these two
    # assert on the *rendered badge* instead — otherwise both would pass forever.
    BADGE = 'class="badge badge-completed'

    def test_the_completed_badge_is_green_and_low_contrast_not_white(self):
        models.AssessmentAttempt.objects.create(
            assessment=self.assessment, student=self.student, status='submitted', score=18)
        html = self.html()
        self.assertIn(self.BADGE, html)
        self.assertNotIn('bg-success-soft', html,
                         'the old class rendered as an invisible white pill')
        # The style must actually be a translucent green.
        self.assertIn('rgba(25,135,84,.14)', html)

    def test_the_completed_badge_only_shows_once_the_learner_has_finished(self):
        self.assertNotIn(self.BADGE, self.html())

    def test_a_learner_only_sees_open_assessments_for_their_own_modules(self):
        other_module = make_module('Not Mine', 'NOTM', programme=self.programme)
        A.objects.create(module=other_module, title='Hidden paper',
                         kind=A.KIND_QUIZ, status=A.STATUS_OPEN)
        draft = A.objects.create(module=self.module, title='Unfinished paper',
                                 kind=A.KIND_QUIZ, status=A.STATUS_DRAFT)
        html = self.html()
        self.assertIn('Auditing Quiz 1', html)
        self.assertNotIn('Hidden paper', html)
        self.assertNotIn(draft.title, html)
