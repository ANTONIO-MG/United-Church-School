"""Reporting & certificates (My Learning Hub plan, sections 8–9).

* :class:`ModuleWeighting` — how a module's 100% is split across assignments,
  quizzes, tests, exams and study tasks (validated to total 100).
* :class:`Grade` — a computed report-card row per student per module.
* :class:`Certificate` — auto-issued when a student passes a module/module/etc.,
  with a unique number + verification UUID (PDF rendered in a later phase).
"""

import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from core import validators as v


# The CAPS national 7-point achievement scale used on South African school
# reports (Grade 1 – 12): the "letter" is the achievement level, 7 = outstanding
# (80 – 100%) down to 1 = not achieved (0 – 29%). Teachers can override it per
# subject via ModuleWeighting.grade_scale.
DEFAULT_GRADE_SCALE = [
    {'min': 80, 'letter': '7', 'label': 'Outstanding achievement'},
    {'min': 70, 'letter': '6', 'label': 'Meritorious achievement'},
    {'min': 60, 'letter': '5', 'label': 'Substantial achievement'},
    {'min': 50, 'letter': '4', 'label': 'Adequate achievement'},
    {'min': 40, 'letter': '3', 'label': 'Moderate achievement'},
    {'min': 30, 'letter': '2', 'label': 'Elementary achievement'},
    {'min': 0, 'letter': '1', 'label': 'Not achieved'},
]


def letter_for(pct, scale=None):
    """Map a percentage to a letter grade using ``scale`` (or the default)."""
    scale = scale or DEFAULT_GRADE_SCALE
    try:
        ordered = sorted(scale, key=lambda band: -float(band.get('min', 0)))
    except (TypeError, ValueError):
        ordered = DEFAULT_GRADE_SCALE
    for band in ordered:
        if float(pct) >= float(band.get('min', 0)):
            return band.get('letter', '')
    return ordered[-1].get('letter', '') if ordered else ''


class ModuleWeighting(models.Model):
    module = models.OneToOneField('learning.ProgrammeModule', on_delete=models.CASCADE, related_name='weighting')
    assignments_pct = models.PositiveIntegerField(default=20)
    quizzes_pct = models.PositiveIntegerField(default=10)
    tests_pct = models.PositiveIntegerField(default=20)
    exams_pct = models.PositiveIntegerField(default=40)
    tasks_pct = models.PositiveIntegerField(default=10)
    pass_mark_pct = models.PositiveIntegerField(default=50)

    # Flexible grading: bonus % added on top of the weighted score (capped at
    # this value), and a custom letter-grade scale (list of {min, letter}).
    extra_credit_pct = models.PositiveIntegerField(
        default=0, help_text='Maximum bonus % that extra-credit work can add on top of the final mark.')
    grade_scale = models.JSONField(
        default=list, blank=True,
        help_text='Letter-grade bands, e.g. [{"min":80,"letter":"A"}, …]. Blank = default A–F scale.')

    def total(self):
        return (self.assignments_pct + self.quizzes_pct + self.tests_pct
                + self.exams_pct + self.tasks_pct)

    def clean(self):
        if self.total() != 100:
            raise ValidationError('Weightings must add up to 100%.')

    def scale(self):
        return self.grade_scale or DEFAULT_GRADE_SCALE

    def __str__(self):
        return f'Weighting · {self.module}'


class Grade(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='grades')
    module = models.ForeignKey('learning.ProgrammeModule', on_delete=models.CASCADE,
                               null=True, blank=True, related_name='grades')
    # Per-component breakdown {assignments, quizzes, tests, exams, tasks} (percentages).
    components = models.JSONField(default=dict, blank=True)
    final_pct = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    letter = models.CharField(max_length=4, blank=True)
    extra_credit_pct = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    passed = models.BooleanField(default=False)

    # --- Cohort standing, written together by services.rank_module ---
    # Competition ranking (1, 2, 2, 4): equal marks share a position and the
    # next distinct mark skips the tie. ``cohort_size`` is how many graded
    # students the position is out of, ``cohort_average`` their mean mark — both
    # stored so a report or dashboard can show "3rd of 24, class average 61%"
    # from this row alone instead of re-reading the whole module.
    class_position = models.PositiveIntegerField(null=True, blank=True)
    cohort_size = models.PositiveIntegerField(default=0)
    cohort_average = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    ranked_at = models.DateTimeField(null=True, blank=True)

    attendance_pct = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    study_hours = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    computed_at = models.DateTimeField(auto_now=True)

    # --- Staff override (set from the staff desk, /staff/grades/) ---
    # ``computed_pct`` is always what services.compute_grade worked out from the
    # marks. When ``override_pct`` is set it *becomes* ``final_pct`` (and the
    # letter and pass/fail follow it), so everything downstream — ranking, the
    # report card, certificates — honours the override without knowing about it.
    # Recomputing keeps the override until a person clears it.
    computed_pct = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    override_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    override_reason = models.TextField(blank=True)
    overridden_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                      null=True, blank=True, related_name='+')
    overridden_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('student', 'module')
        ordering = ['module', '-final_pct']

    def __str__(self):
        return f'{self.student} · {self.module} — {self.final_pct}%'

    @property
    def percentile(self):
        """Share of the cohort this student is at or above (0–100), or ``None``
        when the module has not been ranked or the cohort is a single student."""
        if not self.class_position or self.cohort_size < 2:
            return None
        # position 1 of 20 → 100th percentile; position 20 of 20 → 5th.
        return round((self.cohort_size - self.class_position + 1) / self.cohort_size * 100)

    @property
    def cohort_delta(self):
        """Points above (+) or below (−) the class average, or ``None``."""
        if self.cohort_size < 2:
            return None
        return round(float(self.final_pct) - float(self.cohort_average))

    @property
    def is_overridden(self):
        return self.override_pct is not None


class Certificate(models.Model):
    KIND_CHOICES = [
        ('module', 'Module'), ('programme', 'Programme'), ('class', 'Class'),
    ]

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='certificates')
    module = models.ForeignKey('learning.ProgrammeModule', on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='certificates')
    kind = models.CharField(max_length=10, choices=KIND_CHOICES, default='module')
    title = models.CharField(max_length=200)
    final_mark = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    number = models.CharField(max_length=40, unique=True, blank=True)
    verification_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    signature = models.CharField(max_length=200, blank=True)
    pdf = models.FileField(upload_to='certificates/', blank=True, null=True,
                           validators=v.validate_document)
    issued_at = models.DateTimeField(default=timezone.now)

    # Revocation. A revoked certificate is kept (its number and verification
    # link stay resolvable) so the public verify page can say it was withdrawn
    # rather than pretend it never existed.
    revoked_at = models.DateTimeField(null=True, blank=True)
    revoked_reason = models.TextField(blank=True)
    revoked_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                   null=True, blank=True, related_name='+')

    class Meta:
        ordering = ['-issued_at']

    @property
    def is_revoked(self):
        return self.revoked_at is not None

    def __str__(self):
        return f'{self.number} — {self.student}'

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = f'CERT-{uuid.uuid4().hex[:10].upper()}'
        super().save(*args, **kwargs)


class TermResult(models.Model):
    """One learner's result in one subject for one school term (GDE / CAPS).

    * :attr:`auto_pct` — computed from the learner's quizzes, tests and
      assignments in that subject dated within the term (automatic marking).
    * :attr:`sba_pct` — the term's School-Based Assessment mark the educator
      records (defaults to :attr:`auto_pct` when they accept it).
    * :attr:`exam_pct` — the mid-year (Term 2) or final (Term 4) examination.
    * :attr:`term_pct` — the reported term mark: SBA and exam weighted by the
      phase's CAPS SBA weight (core.school.final_mark).

    Learners and parents see a result only once the educator **publishes** it.
    """
    STATUS_DRAFT = 'draft'
    STATUS_PUBLISHED = 'published'
    STATUS_CHOICES = [(STATUS_DRAFT, 'Draft — educator only'), (STATUS_PUBLISHED, 'Published')]
    TERM_CHOICES = [(1, 'Term 1'), (2, 'Term 2'), (3, 'Term 3'), (4, 'Term 4')]

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name='term_results')
    module = models.ForeignKey('learning.ProgrammeModule', on_delete=models.CASCADE,
                               related_name='term_results', verbose_name='Subject')
    year = models.PositiveSmallIntegerField(db_index=True)
    term = models.PositiveSmallIntegerField(choices=TERM_CHOICES, db_index=True)
    auto_pct = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True,
                                   help_text='From marked quizzes, tests and assignments this term.')
    sba_pct = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True,
                                  verbose_name='SBA %', help_text='School-Based Assessment mark for the term.')
    exam_pct = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True,
                                   verbose_name='Exam %', help_text='Mid-year (Term 2) / final (Term 4) exam.')
    term_pct = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True,
                                   verbose_name='Term mark %')
    level = models.PositiveSmallIntegerField(null=True, blank=True, help_text='CAPS achievement level 1 – 7.')
    comment = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_DRAFT, db_index=True)
    entered_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                                   blank=True, related_name='+')
    published_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['year', 'term', 'module__order']
        constraints = [models.UniqueConstraint(fields=['student', 'module', 'year', 'term'],
                                               name='uniq_term_result')]

    def __str__(self):
        return f'{self.student} · {self.module.code} · {self.year} T{self.term}: {self.term_pct}'

    def recompute(self):
        """Refresh :attr:`term_pct` and :attr:`level` from the SBA and exam marks."""
        from core.school import achievement_level, final_mark
        grade = self.module.programme.grade or 1
        sba = float(self.sba_pct) if self.sba_pct is not None else (
            float(self.auto_pct) if self.auto_pct is not None else None)
        exam = float(self.exam_pct) if self.exam_pct is not None else None
        mark = final_mark(grade, self.module.code, sba, exam)
        self.term_pct = None if mark is None else round(mark, 1)
        self.level = None if mark is None else achievement_level(mark)
        return self.term_pct
