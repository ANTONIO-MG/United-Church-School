"""Data models for the tasks app.

A :class:`Task` is created once and *assigned* to a target — a single user, a
module, a course, or everyone. When the task is saved
the signal handler fans the target out into one :class:`TaskAssignment` per
resolved user, so each person gets their own copy to progress / be graded on.

**A task is not a separate kind of work.** It is the *scheduling and tracking
wrapper* around a piece of content: a lesson, a quiz or an assessment.
Opening a task therefore opens the thing it delivers (:attr:`Task.target_url`), and completing that thing drives the
:class:`TaskAssignment`. A task with nothing linked is a plain to-do — still
useful, just not delivering anything.

The link runs both ways: :mod:`apps.tasks.activities` creates/updates a task
whenever a lesson or assessment is published with a deadline, so a due date set
anywhere in the hub shows up in the task list and on the calendar without anyone
re-typing it.
"""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone

from core import validators as v


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Task(TimeStampedModel):
    ASSIGN_USER = 'user'
    ASSIGN_SUBJECT = 'module'
    ASSIGN_PROGRAMME = 'programme'
    ASSIGN_ALL = 'all'
    ASSIGN_CHOICES = [
        (ASSIGN_USER, 'A single user'),
        (ASSIGN_SUBJECT, 'A module'),
        (ASSIGN_PROGRAMME, 'A whole programme'),
        (ASSIGN_ALL, 'All users'),
    ]
    PRIORITY_CHOICES = [('low', 'Low'), ('normal', 'Normal'), ('high', 'High')]
    STATUS_CHOICES = [('open', 'Open'), ('closed', 'Closed')]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='created_tasks',
    )

    assign_to = models.CharField(max_length=12, choices=ASSIGN_CHOICES, default=ASSIGN_USER)
    assignee = models.ForeignKey(
        'accounts.Person', on_delete=models.SET_NULL, null=True, blank=True, related_name='+',
        help_text='Used when "Assign to" is a single user.',
    )
    module = models.ForeignKey(
        'learning.ProgrammeModule', on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks',
    )
    programme = models.ForeignKey(
        'learning.Programme', on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks',
        help_text='Used when "Assign to" is a whole programme — every module under it.',
    )
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    due_date = models.DateTimeField(null=True, blank=True)
    max_score = models.DecimalField(max_digits=6, decimal_places=2, default=100)
    attachment = models.FileField(upload_to='tasks/', blank=True, null=True,
                                  validators=v.validate_attachment)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')

    # --- What this task delivers (optional) ---------------------------------
    # A task can simply *be* a lesson or a quiz/assessment. When one is set,
    # opening the task opens that thing, and completing it drives the assignee's
    # TaskAssignment (progress/score/status) automatically — see
    # apps.tasks.activities. Leave both blank for a plain, manually-progressed
    # to-do.
    #
    # At most one should be set; `activity` resolves them in a fixed order so a
    # task with two links still behaves predictably rather than ambiguously.
    lesson = models.ForeignKey(
        'learning.Lesson', on_delete=models.CASCADE, null=True, blank=True, related_name='tasks',
        help_text='Deliver a lesson as this task; opening the task opens the lesson.',
    )
    assessment = models.ForeignKey(
        'assessments.Assessment', on_delete=models.CASCADE, null=True, blank=True, related_name='tasks',
        help_text='Deliver a quiz / test / assignment as this task.',
    )
    # (SCORM and LTI delivery were removed with those apps — the platform is a support
    #  and insight platform, not a content runtime. A task delivers a lesson, an
    #  assessment, or is simply a piece of work to do.)

    # Kinds, in the order `activity` resolves them.
    KIND_LESSON = 'lesson'
    KIND_QUIZ = 'quiz'
    KIND_ASSESSMENT = 'assessment'
    KIND_PLAIN = 'plain'

    # kind → (label, bootstrap icon, tone) for the badge shown in lists/calendar.
    KIND_META = {
        KIND_LESSON: ('Lesson', 'bi-journal-richtext', 'info'),
        KIND_QUIZ: ('Quiz', 'bi-ui-checks', 'warning'),
        KIND_ASSESSMENT: ('Assessment', 'bi-clipboard-check', 'danger'),
        KIND_PLAIN: ('Task', 'bi-check2-square', 'success'),
    }

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """Where clicking this task goes.

        For a delivering task that is the activity itself — a learner opening a
        task called "Chapter 3 quiz" wants the quiz, not a page describing it.
        Plain to-dos keep the task detail page. Educators reach the management
        view through :attr:`manage_url` regardless.
        """
        return self.target_url or self.manage_url

    @property
    def manage_url(self):
        """The task's own page — meta, every assignment, and grading."""
        return reverse('orgtasks:task-detail', args=[self.pk])

    # --- delivered activity -------------------------------------------------
    @property
    def activity(self):
        """The object this task delivers, or ``None`` for a plain to-do."""
        return self.lesson or self.assessment or None

    @property
    def activity_kind(self):
        """``lesson`` / ``quiz`` / ``assessment`` / ``plain``.

        Quiz and assessment are the same model — the distinction comes from
        ``Assessment.kind``, so the badge a learner sees matches what they are
        actually about to sit.
        """
        if self.lesson_id:
            return self.KIND_LESSON
        if self.assessment_id:
            from apps.assessments.models import Assessment
            return (self.KIND_QUIZ if self.assessment.kind == Assessment.KIND_QUIZ
                    else self.KIND_ASSESSMENT)
        return self.KIND_PLAIN

    @property
    def kind_label(self):
        return self.KIND_META[self.activity_kind][0]

    @property
    def kind_icon(self):
        return self.KIND_META[self.activity_kind][1]

    @property
    def kind_tone(self):
        return self.KIND_META[self.activity_kind][2]

    @property
    def is_interactive(self):
        """True when the task delivers something rather than being a bare to-do."""
        return self.activity_kind != self.KIND_PLAIN

    @property
    def target_url(self):
        """URL that opens the delivered activity ('' for a plain to-do)."""
        if self.lesson_id:
            return reverse('learning:lesson-view', args=[self.lesson_id])
        if self.assessment_id:
            return reverse('assessments:take', args=[self.assessment_id])
        return ''

    # --- progress summary ---
    @property
    def assignment_count(self):
        return self.assignments.count()

    @property
    def completed_count(self):
        return self.assignments.filter(status=TaskAssignment.STATUS_COMPLETED).count()

    @property
    def progress_avg(self):
        aggregated = self.assignments.aggregate(average=models.Avg('progress'))
        return round(aggregated['average'] or 0)

    @property
    def is_overdue(self):
        return bool(self.due_date and self.due_date < timezone.now() and self.status == 'open')

    # --- target resolution ---
    def resolve_users(self):
        """Return a de-duplicated list of ``User`` objects this task targets."""
        User = get_user_model()
        users = set()

        def add_people(people):
            for person in people:
                if person and person.user_id:
                    users.add(person.user)

        if self.assign_to == self.ASSIGN_USER:
            if self.assignee and self.assignee.user_id:
                users.add(self.assignee.user)

        elif self.assign_to == self.ASSIGN_SUBJECT and self.module_id:
            add_people(self.module.member_people)

        elif self.assign_to == self.ASSIGN_PROGRAMME and self.programme_id:
            for module in self.programme.modules.filter(is_active=True):
                add_people(module.member_people)

        elif self.assign_to == self.ASSIGN_ALL:
            users.update(User.objects.filter(is_active=True))

        # ``member_people`` includes a module's educators, which is right for a
        # plain to-do ("upload your scheme of work") but wrong for delivered
        # work: the person who set a quiz should not be assigned to sit it.
        if self.is_interactive and self.created_by_id:
            users.discard(self.created_by)

        return list(users)


class TaskAssignment(TimeStampedModel):
    STATUS_NOT_STARTED = 'not_started'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_SUBMITTED = 'submitted'
    STATUS_COMPLETED = 'completed'
    STATUS_CHOICES = [
        (STATUS_NOT_STARTED, 'Not started'),
        (STATUS_IN_PROGRESS, 'In progress'),
        (STATUS_SUBMITTED, 'Submitted'),
        (STATUS_COMPLETED, 'Completed'),
    ]

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='assignments')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='task_assignments',
    )
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=STATUS_NOT_STARTED)
    progress = models.PositiveIntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    score = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    feedback = models.TextField(blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('task', 'user')
        ordering = ['task', 'user']

    def __str__(self):
        return f'{self.user} · {self.task}'

    def save(self, *args, **kwargs):
        # Keep the timeline stamps in sync with status / progress.
        if self.status == self.STATUS_SUBMITTED and not self.submitted_at:
            self.submitted_at = timezone.now()
        if self.progress >= 100 and self.status not in (self.STATUS_SUBMITTED,):
            self.status = self.STATUS_COMPLETED
        if self.status == self.STATUS_COMPLETED and not self.completed_at:
            self.completed_at = timezone.now()
        super().save(*args, **kwargs)
