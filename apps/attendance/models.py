"""The daily school register.

One :class:`DailyRegister` per class (``learning.Cohort``) per school day. When
it opens, every enrolled learner gets an :class:`AttendanceMark` set to
*present* — attendance is automatic, and the class teacher only marks the
exceptions (absent / late / excused). A register left open at the end of the
day is submitted automatically, with everyone not marked otherwise present.
"""

from django.db import models
from django.urls import reverse
from django.utils import timezone


class DailyRegister(models.Model):
    STATUS_OPEN = 'open'
    STATUS_SUBMITTED = 'submitted'
    STATUS_CHOICES = [(STATUS_OPEN, 'Open'), (STATUS_SUBMITTED, 'Submitted')]

    cohort = models.ForeignKey('learning.Cohort', on_delete=models.CASCADE, related_name='daily_registers')
    date = models.DateField(db_index=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_OPEN)
    opened_at = models.DateTimeField(default=timezone.now)
    submitted_by = models.ForeignKey(
        'accounts.Person', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    submitted_at = models.DateTimeField(null=True, blank=True)
    auto_submitted = models.BooleanField(
        default=False, help_text='Closed by the end-of-day job: nobody submitted it, so everyone '
                                 'not marked otherwise was kept present.')
    # The to-do the class teacher was given when the register opened.
    task = models.ForeignKey('orgtasks.Task', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')

    class Meta:
        ordering = ['-date', 'cohort__programme__grade', 'cohort__code']
        constraints = [
            models.UniqueConstraint(fields=['cohort', 'date'], name='uniq_daily_register_per_cohort_day'),
        ]
        verbose_name = 'Daily register'

    def __str__(self):
        return f'{self.cohort_label} · {self.date:%a %d %b %Y}'

    @property
    def cohort_label(self):
        return cohort_label(self.cohort)

    @property
    def is_open(self):
        return self.status == self.STATUS_OPEN

    def get_absolute_url(self):
        return reverse('attendance:register', args=[self.pk])

    def counts(self):
        out = {s: 0 for s, _ in AttendanceMark.STATUS_CHOICES}
        for row in self.marks.values('status').annotate(n=models.Count('id')):
            out[row['status']] = row['n']
        out['total'] = sum(out.values())
        return out


class AttendanceMark(models.Model):
    PRESENT = 'present'
    ABSENT = 'absent'
    LATE = 'late'
    EXCUSED = 'excused'
    STATUS_CHOICES = [
        (PRESENT, 'Present'),
        (ABSENT, 'Absent'),
        (LATE, 'Late'),
        (EXCUSED, 'Excused'),
    ]
    #: One-letter codes for the monthly grid and the CSV.
    CODES = {PRESENT: 'P', ABSENT: 'A', LATE: 'L', EXCUSED: 'E'}

    register = models.ForeignKey(DailyRegister, on_delete=models.CASCADE, related_name='marks')
    learner = models.ForeignKey('accounts.Person', on_delete=models.CASCADE, related_name='attendance_marks')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PRESENT, db_index=True)
    reason = models.CharField(max_length=200, blank=True, help_text='e.g. "Sick", "Family emergency".')
    marked_by = models.ForeignKey(
        'accounts.Person', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    updated_at = models.DateTimeField(auto_now=True)
    # Set once the learner's parents were told about the absence (once per day).
    parents_notified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['learner__first_name', 'learner__last_name']
        constraints = [
            models.UniqueConstraint(fields=['register', 'learner'], name='uniq_attendance_mark_per_learner'),
        ]
        verbose_name = 'Attendance mark'

    def __str__(self):
        return f'{self.learner} · {self.register.date} · {self.get_status_display()}'

    @property
    def code(self):
        return self.CODES.get(self.status, '?')


def cohort_label(cohort):
    """``Grade 5 · 2026``."""
    if cohort is None:
        return ''
    if cohort.name:
        return cohort.name
    return f'{cohort.programme.name} · {cohort.code}'
