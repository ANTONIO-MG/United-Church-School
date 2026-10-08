"""Unified assessment engine (My Learning Hub plan, sections 4–6).

One :class:`Assessment` model covers **quizzes, tests, exam-sections and
assignments** (``kind``). An assessment has Sections → Questions (+ Choices for
objective questions). An :class:`Exam` is a *container* that bundles several
assessments (``ExamSection``). Students take an :class:`AssessmentAttempt`
(autosave draft, timer, attempt limits, pass mark); each :class:`Answer` is
auto-marked where possible. Assignments use :class:`AssignmentSubmission`.

Flexible bits (per-question config, marking keys, attempt drafts) use JSONField
to avoid over-normalising the ~15 question types.
"""

import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

from core import validators as v


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Assessment(TimeStampedModel):
    KIND_QUIZ = 'quiz'
    KIND_TEST = 'test'
    KIND_EXAM_SECTION = 'exam_section'
    KIND_ASSIGNMENT = 'assignment'
    # A past/mock paper sat under exam conditions. It marks and weights like a
    # test, but it is worth its own kind because readiness reads it differently:
    # a mock is the closest signal there is to how the real exam will go.
    KIND_MOCK_EXAM = 'mock_exam'
    KIND_CHOICES = [
        (KIND_QUIZ, 'Quiz'),
        (KIND_TEST, 'Class / controlled test'),
        (KIND_MOCK_EXAM, 'Practice exam / past paper'),
        (KIND_EXAM_SECTION, 'Examination paper'),
        (KIND_ASSIGNMENT, 'Assignment'),
    ]

    # Which report-card component (see reports.ModuleWeighting) this assessment
    # feeds. Historically the weighting bucket was *inferred* from ``kind``;
    # decoupling it lets a new kind — or a quiz an educator wants counted as a
    # test — map into any bucket without new enum values.
    COMPONENT_ASSIGNMENTS = 'assignments'
    COMPONENT_QUIZZES = 'quizzes'
    COMPONENT_TESTS = 'tests'
    COMPONENT_EXAMS = 'exams'
    COMPONENT_CHOICES = [
        (COMPONENT_ASSIGNMENTS, 'Assignments'),
        (COMPONENT_QUIZZES, 'Quizzes'),
        (COMPONENT_TESTS, 'Tests'),
        (COMPONENT_EXAMS, 'Exams'),
    ]
    # Default bucket per kind when ``component`` is left blank (keeps every
    # existing assessment grading exactly as before).
    DEFAULT_COMPONENT_BY_KIND = {
        KIND_QUIZ: COMPONENT_QUIZZES,
        KIND_TEST: COMPONENT_TESTS,
        KIND_EXAM_SECTION: COMPONENT_EXAMS,
        KIND_ASSIGNMENT: COMPONENT_ASSIGNMENTS,
        KIND_MOCK_EXAM: COMPONENT_EXAMS,
    }

    TIMER_CONTINUE = 'continue'
    TIMER_PAUSE = 'pause'
    TIMER_AUTOSUBMIT = 'autosubmit'
    TIMER_CHOICES = [
        (TIMER_CONTINUE, 'Continue if browser closes'),
        (TIMER_PAUSE, 'Pause'),
        (TIMER_AUTOSUBMIT, 'Auto submit'),
    ]

    # --- Lifecycle ---------------------------------------------------------
    # Draft → Review → Scheduled/Open → Closed → Archived. ``review`` is where a
    # second pair of eyes signs an assessment off before learners can ever see
    # it; everything before this change let an educator publish straight from a
    # form field with no check at all.
    STATUS_DRAFT = 'draft'
    STATUS_REVIEW = 'review'
    STATUS_SCHEDULED = 'scheduled'
    STATUS_OPEN = 'open'
    STATUS_CLOSED = 'closed'
    STATUS_ARCHIVED = 'archived'
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'), (STATUS_REVIEW, 'In review'), (STATUS_SCHEDULED, 'Scheduled'),
        (STATUS_OPEN, 'Open'), (STATUS_CLOSED, 'Closed'), (STATUS_ARCHIVED, 'Archived'),
    ]
    # Which states each state may move to. Anything not listed is refused by
    # :meth:`transition_to`, so a bad value in a POST can no longer put an
    # assessment straight from Draft to Open.
    STATUS_TRANSITIONS = {
        STATUS_DRAFT: {STATUS_REVIEW, STATUS_ARCHIVED},
        STATUS_REVIEW: {STATUS_DRAFT, STATUS_SCHEDULED, STATUS_OPEN, STATUS_ARCHIVED},
        STATUS_SCHEDULED: {STATUS_OPEN, STATUS_REVIEW, STATUS_CLOSED, STATUS_ARCHIVED},
        STATUS_OPEN: {STATUS_CLOSED, STATUS_ARCHIVED},
        STATUS_CLOSED: {STATUS_OPEN, STATUS_ARCHIVED},
        STATUS_ARCHIVED: {STATUS_DRAFT},
    }

    # Where this paper sits. ``topic`` is the academic spine — an offering's
    # syllabus topic — and is how everything created from a content pack is
    # anchored. ``module`` is the older course/module route, kept nullable for
    # the papers that predate the spine; a paper needs one or the other.
    topic = models.ForeignKey('learning.Topic', on_delete=models.CASCADE, null=True, blank=True,
                              related_name='assessments')
    module = models.ForeignKey('learning.ProgrammeModule', on_delete=models.CASCADE, null=True, blank=True,
                                related_name='assessments')
    lesson = models.ForeignKey('learning.Lesson', on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='assessments')

    title = models.CharField(max_length=200)
    kind = models.CharField(max_length=12, choices=KIND_CHOICES, default=KIND_QUIZ, db_index=True)
    # Blank → derive from ``kind`` via DEFAULT_COMPONENT_BY_KIND (see grade_component).
    component = models.CharField(
        max_length=12, choices=COMPONENT_CHOICES, blank=True,
        help_text='Report-card bucket this feeds. Blank = auto from the kind.')
    description = models.TextField(blank=True)

    total_marks = models.DecimalField(max_digits=7, decimal_places=2, default=100)
    pass_mark_pct = models.PositiveIntegerField(default=50)
    # Flexible grading: relative weight of this assessment within its component
    # (e.g. a big test counts double a small one). Extra-credit assessments are
    # excluded from the component average and instead add bonus marks.
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=1,
                                 help_text='Relative weight within its component (quizzes/tests/…).')
    is_extra_credit = models.BooleanField(
        default=False, help_text='Score counts as bonus on top of the final mark, not part of a component.')
    time_limit_minutes = models.PositiveIntegerField(default=0, help_text='0 = no limit.')
    attempts_allowed = models.PositiveIntegerField(default=1, help_text='0 = unlimited.')
    timer_behaviour = models.CharField(max_length=12, choices=TIMER_CHOICES, default=TIMER_AUTOSUBMIT)
    shuffle_questions = models.BooleanField(default=False)

    # --- Solution release -----------------------------------------------
    # A candidate who reads the solution before attempting learns nothing, so
    # the memo is withheld until they have committed an answer. Enforced in the
    # view layer, not by asking nicely.
    RELEASE_ON_SUBMIT = 'on_submit'
    RELEASE_ON_CLOSE = 'on_close'
    RELEASE_MANUAL = 'manual'
    RELEASE_CHOICES = [
        (RELEASE_ON_SUBMIT, 'As soon as the learner submits'),
        (RELEASE_ON_CLOSE, 'When the paper closes'),
        (RELEASE_MANUAL, 'Only when a teacher releases it'),
    ]
    release_solution = models.CharField(max_length=10, choices=RELEASE_CHOICES,
                                        default=RELEASE_ON_SUBMIT)
    # The solution's narrative zones — recap, triggers & legislation, traps,
    # mark summary — as they appear in the source workbook. The per-part marking
    # data lives on the questions; this is the surrounding commentary.
    solution_notes = models.JSONField(default=dict, blank=True)

    # Where this came from, when it was imported rather than typed. Lets a
    # re-import find the same row instead of making a second one.
    source_ref = models.CharField(max_length=120, blank=True, db_index=True,
                                  help_text='Stable key from the content pack that created this.')

    # --- Exam-integrity ("focus guard") settings ---------------------------
    # When enabled, the take page watches for the learner leaving the
    # assessment window — switching tab, alt-tabbing to another program,
    # dragging the pointer out of the page, leaving fullscreen — and records
    # each occurrence against the attempt. See :mod:`apps.assessments.proctoring`.
    ACTION_WARN = 'warn'
    ACTION_FLAG = 'flag'
    ACTION_AUTOSUBMIT = 'autosubmit'
    ACTION_CHOICES = [
        (ACTION_WARN, 'Keep warning the student'),
        (ACTION_FLAG, 'Flag the attempt for the educator'),
        (ACTION_AUTOSUBMIT, 'End the attempt and submit it'),
    ]

    proctoring_enabled = models.BooleanField(
        default=False, help_text='Watch for the student leaving the assessment window.')
    proctor_warn_limit = models.PositiveSmallIntegerField(
        default=3, help_text='Warnings allowed before the action below is taken. 0 = warn forever.')
    proctor_action = models.CharField(max_length=12, choices=ACTION_CHOICES, default=ACTION_FLAG)
    proctor_block_copy = models.BooleanField(
        default=True, help_text='Block copy, paste, right-click and printing during the attempt.')
    proctor_require_fullscreen = models.BooleanField(
        default=False, help_text='Ask for fullscreen and count leaving it as a warning.')
    proctor_grace_seconds = models.PositiveSmallIntegerField(
        default=3, help_text='Seconds the pointer may sit outside the window before it counts.')
    proctor_blur_content = models.BooleanField(
        default=True, help_text='Hide the questions while the window is not focused.')

    available_from = models.DateTimeField(null=True, blank=True)
    available_to = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft', db_index=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='assessments_created')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} ({self.get_kind_display()})'

    # --- Solution release ---------------------------------------------------
    def solution_released_for(self, user):
        """Whether ``user`` may see this paper's model answer and marking rubric.

        The rule the practice actually runs on. A candidate who reads the memo
        before attempting the question learns nothing, so the memo is withheld
        until they have committed an answer — and this is where that is decided,
        not in a template.

        * ``on_submit`` — as soon as *this* candidate has submitted an attempt.
          Their own attempt: someone else submitting does not open it for them.
        * ``on_close`` — when the paper's window has passed for everyone.
        * ``manual``  — only when a coach has released it (``solution_notes
          ["released"]``), whatever anyone has submitted.

        Staff and the assessment's author always see it; they are marking with it.
        """
        from django.utils import timezone as _tz

        if not getattr(user, 'is_authenticated', False):
            return False
        if user.is_staff or user.is_superuser or self.created_by_id == user.id:
            return True
        if getattr(getattr(user, 'profile', None), 'user_type', '') in ('admin', 'staff'):
            return True

        if self.release_solution == self.RELEASE_MANUAL:
            return bool((self.solution_notes or {}).get('released'))
        if self.release_solution == self.RELEASE_ON_CLOSE:
            return bool(self.available_to and self.available_to <= _tz.now())
        # on_submit — the default, and the one the imported packs use.
        return self.attempts.filter(
            student=user,
            status__in=[AssessmentAttempt.STATUS_SUBMITTED,
                        AssessmentAttempt.STATUS_MARKED],
        ).exists()

    @property
    def grade_component(self):
        """The report-card component this assessment contributes to — the
        explicit ``component`` if set, otherwise inferred from ``kind``."""
        return self.component or self.DEFAULT_COMPONENT_BY_KIND.get(self.kind, self.COMPONENT_QUIZZES)

    # --- Lifecycle ---------------------------------------------------------
    def can_transition_to(self, status):
        """Whether ``status`` is reachable from the current one."""
        return status in self.STATUS_TRANSITIONS.get(self.status, set())

    def available_transitions(self):
        """The states this assessment may move to next, as (value, label)."""
        allowed = self.STATUS_TRANSITIONS.get(self.status, set())
        return [(value, label) for value, label in self.STATUS_CHOICES if value in allowed]

    def transition_to(self, status, *, by=None):
        """Move to ``status``, refusing anything the lifecycle does not allow.

        Raises :class:`~django.core.exceptions.ValidationError` on an illegal
        move — including publishing an assessment that has no questions, which
        would otherwise present learners with an empty paper.
        """
        from django.core.exceptions import ValidationError

        if status == self.status:
            return self
        if not self.can_transition_to(status):
            from core.errors import fail
            fail('ASMT-4001',
                 f'An assessment that is {self.get_status_display().lower()} cannot become '
                 f'{dict(self.STATUS_CHOICES).get(status, status).lower()}',
                 assessment=self.pk, current=self.status, requested=status)
        # Questions hang off sections, so count through them.
        if (status in (self.STATUS_OPEN, self.STATUS_SCHEDULED)
                and not Question.objects.filter(section__assessment=self).exists()):
            from core.errors import fail
            fail('ASMT-4002', 'Add at least one question before opening this assessment',
                 assessment=self.pk, requested=status)
        self.status = status
        self.save(update_fields=['status'])
        return self


class Section(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=200)
    instructions = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['assessment', 'order']

    def __str__(self):
        return f'{self.title} — {self.assessment}'


class Question(models.Model):
    TYPE_CHOICES = [
        ('mcq', 'Multiple choice'), ('multi', 'Multiple select'), ('tf', 'True / False'),
        ('matching', 'Matching'), ('ordering', 'Ordering'), ('fill', 'Fill in the blank'),
        ('short', 'Short answer'), ('long', 'Long answer'), ('essay', 'Essay'),
        # A computation the candidate fills in line by line — the estate-duty
        # ladder, a materiality calculation. Each line carries its own expected
        # figure and its own marks, so it auto-marks exactly.
        ('schedule', 'Numeric schedule'),
        ('image_select', 'Image selection'), ('diagram', 'Diagram labeling'),
        ('audio_resp', 'Audio response'), ('video_resp', 'Video response'),
        ('file_upload', 'File upload'), ('project', 'Project submission'), ('coding', 'Coding exercise'),
    ]

    # How a question is graded. ``auto`` uses the per-question builder key
    # (choices / keywords / config); ``manual`` flags it for an educator to grade
    # with the ``guidance`` rubric (the "promptable manual" path). Left as ``auto``
    # by default — if the educator doesn't flag it manual, the builder marks it.
    MARKING_AUTO = 'auto'
    MARKING_MANUAL = 'manual'
    MARKING_CHOICES = [
        (MARKING_AUTO, 'Auto-marked (per-question key)'),
        (MARKING_MANUAL, 'Manual marking (educator)'),
    ]
    # Types the auto-marker can actually score. A question in ``auto`` mode whose
    # type isn't here effectively falls back to manual.
    AUTO_MARKABLE_TYPES = {'mcq', 'multi', 'tf', 'matching', 'ordering', 'fill', 'short',
                           'schedule'}

    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='questions')
    type = models.CharField(max_length=14, choices=TYPE_CHOICES, default='mcq')
    text = models.TextField()
    marks = models.DecimalField(max_digits=6, decimal_places=2, default=1)
    order = models.PositiveIntegerField(default=0)
    media = models.FileField(upload_to='questions/', blank=True, null=True,
                             validators=v.validate_media)
    # Free-form config (e.g. matching pairs, ordering items, blanks).
    config = models.JSONField(default=dict, blank=True)
    # Auto-marking key for word answers: {keywords, synonyms, alt_spellings, required_phrases}.
    marking = models.JSONField(default=dict, blank=True)

    marking_mode = models.CharField(max_length=8, choices=MARKING_CHOICES, default=MARKING_AUTO)
    guidance = models.TextField(
        blank=True, help_text='Rubric / model answer shown to the marker (manual marking).')

    class Meta:
        ordering = ['section', 'order']

    def __str__(self):
        return f'[{self.get_type_display()}] {self.text[:50]}'

    @property
    def is_objective(self):
        return self.type in ('mcq', 'multi', 'tf', 'matching', 'ordering', 'fill', 'short',
                             'schedule')

    @property
    def is_auto_marked(self):
        """True when this question should be scored by the auto-marker (mode is
        ``auto`` *and* the type is machine-markable); otherwise it is graded by a
        human via the marking queue."""
        return self.marking_mode == self.MARKING_AUTO and self.type in self.AUTO_MARKABLE_TYPES


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=400)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['question', 'order']

    def __str__(self):
        return self.text[:50]


class Exam(TimeStampedModel):
    """A container that bundles several assessments into one examination."""

    STATUS_CHOICES = [('draft', 'Draft'), ('scheduled', 'Scheduled'), ('open', 'Open'),
                      ('closed', 'Closed'), ('archived', 'Archived')]

    module = models.ForeignKey('learning.ProgrammeModule', on_delete=models.CASCADE,
                               null=True, blank=True, related_name='exams')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    available_from = models.DateTimeField(null=True, blank=True)
    available_to = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft', db_index=True)
    lock_after_submit = models.BooleanField(default=True)
    invigilator_mode = models.BooleanField(default=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='exams_created')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class ExamSection(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='exam_sections')
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='exam_sections')
    order = models.PositiveIntegerField(default=0)
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=1)

    class Meta:
        ordering = ['exam', 'order']
        unique_together = ('exam', 'assessment')

    def __str__(self):
        return f'{self.exam} · {self.assessment}'


class AssessmentAttempt(TimeStampedModel):
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_SUBMITTED = 'submitted'
    STATUS_MARKED = 'marked'
    STATUS_CHOICES = [
        (STATUS_IN_PROGRESS, 'In progress'),
        (STATUS_SUBMITTED, 'Submitted'),
        (STATUS_MARKED, 'Marked'),
    ]

    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='attempts')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='assessment_attempts')

    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=STATUS_IN_PROGRESS, db_index=True)
    attempt_no = models.PositiveIntegerField(default=1)
    started_at = models.DateTimeField(default=timezone.now)
    submitted_at = models.DateTimeField(null=True, blank=True)
    time_spent_seconds = models.PositiveIntegerField(default=0)

    score = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    passed = models.BooleanField(default=False)
    # Autosave: per-question working answers before final submission.
    draft = models.JSONField(default=dict, blank=True)

    # --- Exam integrity ----------------------------------------------------
    # Counted warnings (the tally the student sees), total time the window was
    # not focused, and whether the attempt needs an educator's eye. These are
    # written only by apps.assessments.proctoring — never by the browser — so a
    # tampered client cannot lower its own count.
    focus_warnings = models.PositiveIntegerField(default=0)
    away_seconds = models.PositiveIntegerField(default=0)
    integrity_flagged = models.BooleanField(default=False, db_index=True)
    integrity_note = models.CharField(max_length=255, blank=True)
    # Set when the warning limit was hit under the "end the attempt" policy —
    # the attempt cannot be resumed after this.
    terminated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('assessment', 'student', 'attempt_no')

    def __str__(self):
        return f'{self.student} · {self.assessment} (#{self.attempt_no})'

    @property
    def away_label(self):
        """``away_seconds`` as ``m:ss`` for the integrity report."""
        seconds = int(self.away_seconds or 0)
        return f'{seconds // 60}:{seconds % 60:02d}'


class ProctorEvent(models.Model):
    """One integrity event detected while a student sat an attempt.

    The row is the evidence: what happened, when, how long the student was away
    and whether it counted toward the warning limit (rapid duplicates — a tab
    switch fires both a blur and a visibility change — are recorded but counted
    once). Educators see the list on the marking screen.
    """

    KIND_BLUR = 'blur'
    KIND_HIDDEN = 'hidden'
    KIND_POINTER_OUT = 'pointer_out'
    KIND_FULLSCREEN_EXIT = 'fullscreen'
    KIND_COPY = 'copy'
    KIND_PASTE = 'paste'
    KIND_CONTEXTMENU = 'contextmenu'
    KIND_PRINT = 'print'
    KIND_CHOICES = [
        (KIND_BLUR, 'Left the window (another app or window)'),
        (KIND_HIDDEN, 'Switched tab or minimised'),
        (KIND_POINTER_OUT, 'Pointer left the assessment window'),
        (KIND_FULLSCREEN_EXIT, 'Left fullscreen'),
        (KIND_COPY, 'Tried to copy'),
        (KIND_PASTE, 'Tried to paste'),
        (KIND_CONTEXTMENU, 'Opened the right-click menu'),
        (KIND_PRINT, 'Tried to print'),
    ]

    # Kinds that mean the student was genuinely away from the page (as opposed
    # to a blocked copy/paste, which never removes focus).
    AWAY_KINDS = (KIND_BLUR, KIND_HIDDEN, KIND_POINTER_OUT, KIND_FULLSCREEN_EXIT)

    ICONS = {
        KIND_BLUR: 'bi-box-arrow-up-right', KIND_HIDDEN: 'bi-eye-slash',
        KIND_POINTER_OUT: 'bi-cursor', KIND_FULLSCREEN_EXIT: 'bi-fullscreen-exit',
        KIND_COPY: 'bi-clipboard', KIND_PASTE: 'bi-clipboard-plus',
        KIND_CONTEXTMENU: 'bi-menu-button-wide', KIND_PRINT: 'bi-printer',
    }

    attempt = models.ForeignKey(AssessmentAttempt, on_delete=models.CASCADE, related_name='proctor_events')
    kind = models.CharField(max_length=14, choices=KIND_CHOICES, default=KIND_BLUR)
    counted = models.BooleanField(default=True, help_text='Whether this incremented the warning tally.')
    seconds_away = models.PositiveIntegerField(default=0)
    detail = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['created_at']
        indexes = [models.Index(fields=['attempt', 'created_at'])]

    def __str__(self):
        return f'{self.get_kind_display()} · attempt {self.attempt_id}'

    @property
    def icon(self):
        return self.ICONS.get(self.kind, 'bi-exclamation-triangle')


class Answer(models.Model):
    attempt = models.ForeignKey(AssessmentAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    response = models.JSONField(default=dict, blank=True)
    selected_choices = models.ManyToManyField(Choice, blank=True, related_name='answers')
    file = models.FileField(upload_to='answers/', blank=True, null=True,
                            validators=v.validate_attachment)
    awarded_marks = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    is_correct = models.BooleanField(default=False)
    # True once scored — automatically (objective) or by an educator (manual).
    # A manual answer with a response stays False until marked, keeping the
    # attempt in the marking queue.
    marked = models.BooleanField(default=False)
    marked_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='answers_marked')
    feedback = models.TextField(blank=True)
    flagged_for_review = models.BooleanField(default=False)

    class Meta:
        unique_together = ('attempt', 'question')

    def __str__(self):
        return f'Answer to {self.question_id} in {self.attempt_id}'

    @property
    def display_response(self):
        """The student's response as text, for review and the marking queue."""
        data = self.response or {}
        if data.get('lines'):
            # A computation: how much of the ladder they filled in. The figures
            # themselves are shown line-by-line against the model, not here.
            filled = len(data['lines'])
            total = len(((self.question.config or {}).get('lines') or []))
            return f'{filled} of {total} line(s) completed'
        return data.get('text') or data.get('value') or ''

    @property
    def schedule_breakdown(self):
        """Per-line marking result for a schedule answer — see
        :mod:`apps.assessments.schedule_marking`. Empty for any other type."""
        return (self.response or {}).get('breakdown') or []


class AssignmentSubmission(TimeStampedModel):
    STATUS_CHOICES = [
        ('assigned', 'Assigned'), ('started', 'Started'), ('draft', 'Draft'),
        ('submitted', 'Submitted'), ('marked', 'Marked'), ('returned', 'Returned'),
        ('resubmission', 'Resubmission requested'), ('completed', 'Completed'),
    ]

    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name='assignment_submissions')
    status = models.CharField(max_length=14, choices=STATUS_CHOICES, default='assigned', db_index=True)
    text = models.TextField(blank=True)
    file = models.FileField(upload_to='assignments/', blank=True, null=True,
                            validators=v.validate_attachment)
    grade = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    feedback = models.TextField(blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    marked_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='assignments_marked')

    class Meta:
        ordering = ['-created_at']
        unique_together = ('assessment', 'student')

    def __str__(self):
        return f'{self.student} · {self.assessment}'
