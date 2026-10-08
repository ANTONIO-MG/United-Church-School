"""Tests for revision: card creation on marking, Leitner scheduling, the gates
(module access, memo release) and the review pages."""

from datetime import timedelta
from io import StringIO
from unittest import mock

from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from apps.assessments import models as am
from apps.assessments.marking import grade_attempt
from apps.livesessions.tests import make_user
from core.testing import enrol, make_module

from . import services
from .models import ReviewCard, ReviewLog

LOCMEM_CACHE = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}


@override_settings(CACHES=LOCMEM_CACHE)
class RevisionBase(TestCase):

    def setUp(self):
        cache.clear()
        self.addCleanup(cache.clear)
        self.module = make_module('Taxation', 'TAXR', price=500)
        self.educator = make_user('rv_ed', 'educator')
        self.student = make_user('rv_stu', 'student')
        enrol(self.student.profile, self.module)
        self.assessment = self.make_assessment()
        self.section = am.Section.objects.create(assessment=self.assessment, title='S', order=0)
        self.mcq = am.Question.objects.create(section=self.section, type='mcq', text='Rate of VAT?',
                                              marks=2, order=1, config={'explanation': 'Fifteen percent since 2018.'})
        self.right = am.Choice.objects.create(question=self.mcq, text='15%', is_correct=True, order=1)
        self.wrong = am.Choice.objects.create(question=self.mcq, text='14%', order=2)
        self.easy = am.Question.objects.create(section=self.section, type='tf', text='Sky is blue?',
                                               marks=1, order=2)
        self.easy_true = am.Choice.objects.create(question=self.easy, text='True', is_correct=True)
        am.Choice.objects.create(question=self.easy, text='False')
        self.essay = am.Question.objects.create(section=self.section, type='long', text='Discuss s8(4)(a).',
                                                marks=10, order=3, marking_mode='manual',
                                                guidance='Recoupment of allowances previously claimed.')

    def make_assessment(self, **extra):
        defaults = dict(module=self.module, title='Tax quiz', kind=am.Assessment.KIND_QUIZ,
                        total_marks=13, status=am.Assessment.STATUS_OPEN, created_by=self.educator)
        defaults.update(extra)
        return am.Assessment.objects.create(**defaults)

    def sit(self, *, mcq_choice=None, essay_marks=None, student=None, assessment=None):
        """Submit an attempt and mark it, running on_commit callbacks."""
        student = student or self.student
        assessment = assessment or self.assessment
        attempt = am.AssessmentAttempt.objects.create(
            assessment=assessment, student=student,
            attempt_no=assessment.attempts.filter(student=student).count() + 1)
        a = am.Answer.objects.create(attempt=attempt, question=self.mcq)
        a.selected_choices.add(mcq_choice or self.wrong)
        b = am.Answer.objects.create(attempt=attempt, question=self.easy)
        b.selected_choices.add(self.easy_true)
        essay = am.Answer.objects.create(attempt=attempt, question=self.essay, response={'text': 'Something'})
        with self.captureOnCommitCallbacks(execute=True):
            grade_attempt(attempt)  # → submitted (essay pending)
        if essay_marks is not None:
            essay.awarded_marks = essay_marks
            essay.marked = True
            essay.save()
            with self.captureOnCommitCallbacks(execute=True):
                grade_attempt(attempt)  # → marked
        attempt.refresh_from_db()
        return attempt


class CardCreationTests(RevisionBase):

    def test_cards_created_for_answers_below_full_marks_when_marked(self):
        attempt = self.sit(essay_marks=6)
        self.assertEqual(attempt.status, 'marked')
        qids = set(ReviewCard.objects.filter(user=self.student).values_list('question_id', flat=True))
        self.assertEqual(qids, {self.mcq.id, self.essay.id})  # tf was right
        card = ReviewCard.objects.get(user=self.student, question=self.mcq)
        self.assertEqual(card.box, 1)
        self.assertEqual(card.source_attempt, attempt)

    def test_no_cards_while_attempt_only_submitted(self):
        attempt = self.sit()
        self.assertEqual(attempt.status, 'submitted')
        self.assertFalse(ReviewCard.objects.exists())

    def test_full_marks_make_no_card(self):
        self.sit(mcq_choice=self.right, essay_marks=10)
        self.assertFalse(ReviewCard.objects.exists())

    def test_signal_fires_on_transition_only(self):
        attempt = self.sit(essay_marks=6)
        ReviewCard.objects.all().delete()
        with self.captureOnCommitCallbacks(execute=True):
            attempt.save()  # already marked: no transition
        self.assertFalse(ReviewCard.objects.exists())

    def test_failure_never_breaks_marking(self):
        with mock.patch('apps.revision.services.cards_from_attempt', side_effect=RuntimeError('boom')):
            attempt = self.sit(essay_marks=6)
        self.assertEqual(attempt.status, 'marked')
        self.assertFalse(ReviewCard.objects.exists())

    def test_later_wrong_attempt_lapses_card(self):
        first = self.sit(essay_marks=10)
        card = ReviewCard.objects.get(question=self.mcq)
        card.box = 4
        card.due_at = timezone.now() + timedelta(days=10)
        card.save()
        second = self.sit(essay_marks=10)
        card.refresh_from_db()
        self.assertEqual((card.box, card.lapses, card.source_attempt_id), (1, 1, second.id))
        self.assertLessEqual(card.due_at, timezone.now())
        # Re-processing the older attempt does not undo that.
        self.assertEqual(services.cards_from_attempt(first), (0, 0))

    def test_backfill_command_is_idempotent(self):
        with mock.patch('apps.revision.signals.transaction.on_commit'):
            self.sit(essay_marks=3)
        self.assertFalse(ReviewCard.objects.exists())
        out = StringIO()
        call_command('build_review_cards', stdout=out)
        self.assertIn('2 card(s) created', out.getvalue())
        call_command('build_review_cards', stdout=StringIO())
        self.assertEqual(ReviewCard.objects.count(), 2)


class SchedulingTests(RevisionBase):

    def setUp(self):
        super().setUp()
        self.card = ReviewCard.objects.create(user=self.student, question=self.mcq, box=3)
        self.now = timezone.now()

    def test_intervals(self):
        self.assertEqual([ReviewCard.interval_for(b).days for b in range(1, 6)], [1, 3, 7, 16, 35])

    def test_again_drops_to_box_one(self):
        services.grade_card(self.card, 'again', now=self.now)
        self.assertEqual((self.card.box, self.card.lapses, self.card.streak), (1, 1, 0))
        self.assertEqual(self.card.due_at, self.now + timedelta(days=1))

    def test_hard_keeps_box(self):
        services.grade_card(self.card, 'hard', now=self.now)
        self.assertEqual(self.card.box, 3)
        self.assertEqual(self.card.due_at, self.now + timedelta(days=7))

    def test_good_and_easy_climb_and_cap(self):
        services.grade_card(self.card, 'good', now=self.now)
        self.assertEqual(self.card.box, 4)
        self.assertEqual(self.card.due_at, self.now + timedelta(days=16))
        services.grade_card(self.card, 'easy', now=self.now)
        self.assertEqual(self.card.box, 5)
        self.assertEqual(self.card.due_at, self.now + timedelta(days=35))
        self.assertEqual(self.card.streak, 2)
        self.assertEqual(ReviewLog.objects.filter(card=self.card).count(), 2)

    def test_day_streak(self):
        today = timezone.localdate()
        for days_ago in (1, 2, 4):
            ReviewLog.objects.create(card=self.card, user=self.student, grade='good', box_before=1,
                                     box_after=2, reviewed_at=timezone.now() - timedelta(days=days_ago))
        self.assertEqual(services.day_streak(self.student, today=today), (2, 0))
        services.grade_card(self.card, 'good')
        self.assertEqual(services.day_streak(self.student, today=today), (3, 1))


class GateTests(RevisionBase):

    def setUp(self):
        super().setUp()
        self.sit(essay_marks=5)

    def test_due_count_counts_due_cards(self):
        self.assertEqual(services.due_count(self.student), 2)
        self.assertEqual(services.due_count(AnonymousUser()), 0)

    def test_future_and_suspended_cards_excluded(self):
        ReviewCard.objects.filter(question=self.mcq).update(due_at=timezone.now() + timedelta(days=1))
        ReviewCard.objects.filter(question=self.essay).update(suspended=True)
        self.assertEqual(services.due_count(self.student), 0)

    def test_locked_module_hides_cards(self):
        enrolment = self.module.enrolments.get(person=self.student.profile)
        enrolment.lock()
        self.assertEqual(services.due_count(self.student), 0)
        self.assertEqual(services.overview(self.student)['held']['locked'], 2)

    def test_unreleased_memo_holds_cards_until_released(self):
        self.assessment.release_solution = am.Assessment.RELEASE_MANUAL
        self.assessment.save()
        self.assertEqual(services.due_count(self.student), 0)
        self.assertEqual(services.overview(self.student)['held']['memo'], 2)
        self.assessment.solution_notes = {'released': True}
        self.assessment.save()
        self.assertEqual(services.due_count(self.student), 2)


class ViewTests(RevisionBase):

    def setUp(self):
        super().setUp()
        self.sit(essay_marks=5)
        self.client.force_login(self.student)
        self.url = reverse('revision:session')

    def test_home(self):
        r = self.client.get(reverse('revision:home'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Start review')
        self.assertContains(r, 'TAXR')

    def test_mcq_first_and_no_answer_leaks(self):
        r = self.client.get(self.url)
        self.assertContains(r, 'Rate of VAT?')
        self.assertNotContains(r, 'Fifteen percent')

    def test_mcq_correct_answer_promotes(self):
        card = ReviewCard.objects.get(question=self.mcq)
        r = self.client.post(self.url, {'card': card.pk, 'action': 'answer', 'choice': self.right.pk})
        self.assertContains(r, 'Correct')
        self.assertContains(r, 'Fifteen percent')
        card.refresh_from_db()
        self.assertEqual(card.box, 2)

    def test_mcq_wrong_answer_resets(self):
        card = ReviewCard.objects.get(question=self.mcq)
        r = self.client.post(self.url, {'card': card.pk, 'action': 'answer', 'choice': self.wrong.pk})
        self.assertContains(r, 'Not quite')
        card.refresh_from_db()
        self.assertEqual((card.box, card.lapses), (1, 1))
        # A resubmit of a card no longer due changes nothing.
        r = self.client.post(self.url, {'card': card.pk, 'action': 'answer', 'choice': self.right.pk})
        self.assertEqual(r.status_code, 302)
        card.refresh_from_db()
        self.assertEqual(card.box, 1)

    def test_written_reveal_and_self_grade(self):
        ReviewCard.objects.filter(question=self.mcq).update(due_at=timezone.now() + timedelta(days=2))
        card = ReviewCard.objects.get(question=self.essay)
        r = self.client.get(self.url)
        self.assertContains(r, 'Show answer')
        self.assertNotContains(r, 'Recoupment')
        r = self.client.get(self.url, {'reveal': card.pk})
        self.assertContains(r, 'Recoupment')
        self.assertContains(r, 'data-key="4"')
        r = self.client.post(self.url, {'card': card.pk, 'action': 'grade', 'grade': 'easy'})
        self.assertRedirects(r, self.url, fetch_redirect_response=False)
        card.refresh_from_db()
        self.assertEqual(card.box, 3)
        r = self.client.get(self.url)
        self.assertContains(r, 'Session complete')

    def test_unreleased_card_not_shown(self):
        self.assessment.release_solution = am.Assessment.RELEASE_MANUAL
        self.assessment.save()
        r = self.client.get(self.url)
        self.assertContains(r, 'Nothing due right now')
        self.assertNotContains(r, 'Recoupment')
        card = ReviewCard.objects.get(question=self.essay)
        self.client.post(self.url, {'card': card.pk, 'action': 'grade', 'grade': 'easy'})
        card.refresh_from_db()
        self.assertEqual(card.box, 1)

    def test_cannot_grade_someone_elses_card(self):
        other = make_user('rv_other', 'student')
        self.client.force_login(other)
        card = ReviewCard.objects.get(question=self.essay)
        self.client.post(self.url, {'card': card.pk, 'action': 'grade', 'grade': 'easy'})
        card.refresh_from_db()
        self.assertEqual(card.box, 1)

    def test_suspend(self):
        card = ReviewCard.objects.get(question=self.mcq)
        self.client.post(self.url, {'card': card.pk, 'action': 'suspend'})
        card.refresh_from_db()
        self.assertTrue(card.suspended)
        self.assertEqual(services.due_count(self.student), 1)

    def test_module_filter(self):
        r = self.client.get(self.url, {'module': self.module.pk + 999})
        self.assertContains(r, 'Nothing due right now')
        self.assertContains(r, 'Review the other 2 due')
