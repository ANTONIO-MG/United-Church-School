"""Tests for the tasks app.

Two things are worth defending here, because both are easy to break silently:

* **A task is the activity it delivers.** Opening one must land on the lesson /
  quiz / assessment, not on a page describing it — and the link must survive
  someone editing the task.
* **An educator's reach is their own classes.** Scoping that only exists in the
  form's dropdowns is decoration; these tests post *around* the dropdowns to
  prove the server refuses.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import Person
from apps.assessments.models import Assessment
from apps.learning.models import Lesson

from . import activities, forms, models
from .scoping import manageable_tasks
from core.testing import enrol, make_module, make_programme

User = get_user_model()


class TaskFixtureMixin(TestCase):
    """Two programmes. ``educator`` teaches Auditing only; ``outsider`` teaches Law."""

    def setUp(self):
        super().setUp()
        self.cta = make_programme('UCS', 'GR10')
        self.law = make_programme('LAWSCH', 'LLB')
        self.audit = make_module('Advanced Auditing', 'AUDA', programme=self.cta)
        self.contracts = make_module('Contracts', 'CONT', programme=self.law)

        self.educator = self._user('ed@example.com', 'educator')
        self.audit.educators.add(self.educator.profile)
        self.outsider = self._user('other-ed@example.com', 'educator')
        self.contracts.educators.add(self.outsider.profile)
        self.student = self._user('sam@example.com', 'student')
        enrol(self.student.profile, self.audit)
        self.admin = self._user('boss@example.com', 'admin')

    def _user(self, email, user_type):
        user = User.objects.create_user(username=email, email=email, password='x')
        person = Person.objects.get(user=user)
        person.user_type = user_type
        person.registered = True
        person.profile_status = True
        person.save()
        # Re-fetch: the signal that created the Person left a stale copy cached on
        # ``user.profile``, so the in-memory object would still read 'student'.
        # A real request loads the user fresh, and these tests must too.
        return User.objects.get(pk=user.pk)


class TaskDeliversActivityTests(TaskFixtureMixin):
    """A task points at content; opening it opens that content."""

    def test_a_plain_task_opens_its_own_page(self):
        task = models.Task.objects.create(title='Bring your textbook')
        self.assertEqual(task.activity_kind, models.Task.KIND_PLAIN)
        self.assertEqual(task.get_absolute_url(), task.manage_url)

    def test_a_lesson_task_opens_the_lesson(self):
        lesson = Lesson.objects.create(title='Sampling', module=self.audit)
        task = models.Task.objects.create(title='Read sampling', lesson=lesson)
        self.assertEqual(task.activity_kind, models.Task.KIND_LESSON)
        self.assertEqual(task.get_absolute_url(),
                         reverse('learning:lesson-view', args=[lesson.pk]))

    def test_a_quiz_and_an_assignment_are_labelled_differently(self):
        """Both are Assessments — the badge must follow ``kind``, so a learner
        knows whether they are about to sit a quiz or hand in an assignment."""
        quiz = Assessment.objects.create(title='Quick check', module=self.audit,
                                         kind=Assessment.KIND_QUIZ)
        essay = Assessment.objects.create(title='Case study', module=self.audit,
                                          kind=Assessment.KIND_ASSIGNMENT)
        self.assertEqual(models.Task(assessment=quiz).activity_kind, models.Task.KIND_QUIZ)
        self.assertEqual(models.Task(assessment=essay).activity_kind,
                         models.Task.KIND_ASSESSMENT)

    def test_the_task_page_stays_reachable_for_management(self):
        """``get_absolute_url`` redirects away, so grading needs its own link."""
        lesson = Lesson.objects.create(title='Sampling', module=self.audit)
        task = models.Task.objects.create(title='Read sampling', lesson=lesson)
        self.assertEqual(task.manage_url, reverse('orgtasks:task-detail', args=[task.pk]))
        self.assertNotEqual(task.manage_url, task.get_absolute_url())

    def test_the_setter_is_not_assigned_their_own_activity(self):
        """A subject's educators are 'members', but the person who set a quiz
        should not find it sitting in their own task list."""
        quiz = Assessment.objects.create(title='Quick check', module=self.audit,
                                         kind=Assessment.KIND_QUIZ)
        task = models.Task.objects.create(
            title='Quick check', assessment=quiz, created_by=self.educator,
            assign_to=models.Task.ASSIGN_SUBJECT, module=self.audit)
        assigned = set(task.assignments.values_list('user_id', flat=True))
        self.assertIn(self.student.pk, assigned)
        self.assertNotIn(self.educator.pk, assigned)

    def test_a_plain_task_still_reaches_the_educator(self):
        """The exclusion above is only for delivered work, not every task."""
        task = models.Task.objects.create(
            title='Submit your scheme of work', created_by=self.admin,
            assign_to=models.Task.ASSIGN_SUBJECT, module=self.audit)
        self.assertIn(self.educator.pk,
                      set(task.assignments.values_list('user_id', flat=True)))


class ActivitySyncTests(TaskFixtureMixin):
    """Publishing content with a deadline produces the task that tracks it."""

    def test_publishing_an_assessment_creates_one_task(self):
        quiz = Assessment.objects.create(
            title='Chapter 3 quiz', module=self.audit, kind=Assessment.KIND_QUIZ,
            status=Assessment.STATUS_OPEN, created_by=self.educator)
        task = models.Task.objects.filter(assessment=quiz).first()
        self.assertIsNotNone(task)
        self.assertEqual(task.title, 'Chapter 3 quiz')
        self.assertEqual(task.module, self.audit)

    def test_re_saving_does_not_duplicate_the_task(self):
        quiz = Assessment.objects.create(
            title='Chapter 3 quiz', module=self.audit, status=Assessment.STATUS_OPEN)
        quiz.title = 'Chapter 3 quiz (revised)'
        quiz.save()
        tasks = models.Task.objects.filter(assessment=quiz)
        self.assertEqual(tasks.count(), 1)
        self.assertEqual(tasks.first().title, 'Chapter 3 quiz (revised)')

    def test_a_draft_assessment_makes_no_task(self):
        draft = Assessment.objects.create(
            title='Not ready', module=self.audit, status=Assessment.STATUS_DRAFT)
        self.assertFalse(models.Task.objects.filter(assessment=draft).exists())

    def test_unpublishing_closes_the_task_rather_than_deleting_it(self):
        """Deleting would take the learners' submissions and marks with it."""
        quiz = Assessment.objects.create(
            title='Chapter 3 quiz', module=self.audit, status=Assessment.STATUS_OPEN)
        quiz.status = Assessment.STATUS_CLOSED
        quiz.save()
        task = models.Task.objects.get(assessment=quiz)
        self.assertEqual(task.status, 'closed')

    def test_progress_ratchets_up_and_never_back_down(self):
        quiz = Assessment.objects.create(
            title='Chapter 3 quiz', module=self.audit, status=Assessment.STATUS_OPEN,
            total_marks=10)
        task = models.Task.objects.get(assessment=quiz)
        assignment = task.assignments.get(user=self.student)
        assignment.progress = 100
        assignment.status = models.TaskAssignment.STATUS_COMPLETED
        assignment.save()

        from apps.assessments.models import AssessmentAttempt
        AssessmentAttempt.objects.create(
            assessment=quiz, student=self.student, score=2,
            status=AssessmentAttempt.STATUS_IN_PROGRESS)
        activities.record_attempt(AssessmentAttempt.objects.get(
            assessment=quiz, student=self.student))

        assignment.refresh_from_db()
        self.assertEqual(assignment.progress, 100)
        self.assertEqual(assignment.status, models.TaskAssignment.STATUS_COMPLETED)


class TaskScopingTests(TaskFixtureMixin):
    """An educator reaches their own classes and nothing else."""

    def setUp(self):
        super().setUp()
        self.mine = models.Task.objects.create(
            title='Audit prep', created_by=self.educator,
            assign_to=models.Task.ASSIGN_SUBJECT, module=self.audit)
        self.theirs = models.Task.objects.create(
            title='Law prep', created_by=self.outsider,
            assign_to=models.Task.ASSIGN_SUBJECT, module=self.contracts)

    def test_an_educator_only_manages_their_own_modules(self):
        visible = set(manageable_tasks(self.educator).values_list('pk', flat=True))
        self.assertIn(self.mine.pk, visible)
        self.assertNotIn(self.theirs.pk, visible)

    def test_an_admin_manages_everything(self):
        visible = set(manageable_tasks(self.admin).values_list('pk', flat=True))
        self.assertIn(self.mine.pk, visible)
        self.assertIn(self.theirs.pk, visible)

    def test_the_list_page_hides_another_educators_task(self):
        self.client.force_login(self.educator)
        html = self.client.get(reverse('orgtasks:all-tasks')).content.decode()
        self.assertIn('Audit prep', html)
        self.assertNotIn('Law prep', html)

    def test_editing_another_educators_task_is_a_404(self):
        self.client.force_login(self.educator)
        response = self.client.get(reverse('orgtasks:edit-task', args=[self.theirs.pk]))
        self.assertEqual(response.status_code, 404)

    def test_the_form_refuses_an_out_of_scope_module(self):
        """The dropdown is a convenience; the queryset is the control. Post the
        id directly and the form must still reject it."""
        form = forms.TaskForm(data={
            'title': 'Sneaky', 'assign_to': models.Task.ASSIGN_SUBJECT,
            'module': self.contracts.pk, 'priority': 'normal',
            'max_score': 100, 'status': 'open',
        }, user=self.educator)
        self.assertFalse(form.is_valid())
        self.assertIn('module', form.errors)

    def test_the_same_form_accepts_a_module_they_teach(self):
        form = forms.TaskForm(data={
            'title': 'Fine', 'assign_to': models.Task.ASSIGN_SUBJECT,
            'module': self.audit.pk, 'priority': 'normal',
            'max_score': 100, 'status': 'open',
        }, user=self.educator)
        self.assertTrue(form.is_valid(), form.errors)

    def test_an_educator_cannot_broadcast_to_everyone(self):
        form = forms.TaskForm(data={
            'title': 'All hands', 'assign_to': models.Task.ASSIGN_ALL,
            'priority': 'normal', 'max_score': 100, 'status': 'open',
        }, user=self.educator)
        self.assertFalse(form.is_valid())
        self.assertIn('assign_to', form.errors)

    def test_an_admin_may_broadcast_to_everyone(self):
        form = forms.TaskForm(data={
            'title': 'All hands', 'assign_to': models.Task.ASSIGN_ALL,
            'priority': 'normal', 'max_score': 100, 'status': 'open',
        }, user=self.admin)
        self.assertTrue(form.is_valid(), form.errors)
