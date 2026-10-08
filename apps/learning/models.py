"""Study content + study-session timers (the "Study" and "Task/session" apps
from the My Learning Hub plan).

**The academic spine of United Church School** is school → grade → subject:

    Institution → Programme → ProgrammeModule → Topic → Lesson / Assessment
    (the school)  (a grade)   (a subject in that grade)

* :class:`Institution` — United Church School (code ``UCS``), the one school
  on the platform. The model keeps its name so the spine stays generic.
* :class:`Programme` — a **grade**, Grade 1 to Grade 12 (``UCS-GR01`` …
  ``UCS-GR12``), in its CAPS phase (:attr:`~Programme.level`) and carrying the
  year's fee schedule (registration, levy, monthly school fees).
* :class:`ProgrammePhase` — an optional phase of a phased programme.
* :class:`Cohort` — the grade's class for a year (``2026``), or a named class.
* :class:`Module` — the **canonical** subject catalogue: English Home Language,
  Mathematics, Life Sciences … one row per subject however many grades teach it,
  which is what lets the platform ask "how is Mathematics going across the
  school?".
* :class:`ProgrammeModule` — that subject *as offered in one grade*, with its
  Grade 10 – 12 choice group (:attr:`~ProgrammeModule.subject_group`).
* :class:`Topic` — the syllabus, **owned by the offering**: Grade 10
  Mathematics' topics are separate rows from Grade 11's, so each grade's content
  is controlled on its own. The topic :attr:`~Topic.code` is the shared
  vocabulary that still reports them together — see :meth:`Topic.siblings`.

Content hangs off the topic, and therefore off exactly one offering: the study
guide is a :class:`Lesson`, the mock and the challenge are
``assessments.Assessment`` rows. A lesson is **versioned**; a
:class:`StudySession` records how long a student actually spends on one
(start/pause/resume/finish), feeding reporting & analytics.

How that material is *scheduled* is a second structure over the top —
:class:`ModulePhase` → :class:`ModuleWeek` → :class:`ModuleMaterial` — because
the same topic is taught in a different week at each institution. A material row
points at the lesson or assessment; the topic owns it.

"""

import re
import uuid
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.utils.text import slugify

from core import validators as v

from core.storage import files_storage   # lesson material (documents/media) → file server


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# ---------------------------------------------------------------------------
# The academic spine
#
#   Institution → Programme → ProgrammeModule → Topic
#                             (the offering)     (owned by the offering)
#
# Every offering owns its topics outright. Grade 10 Mathematics' algebra topic and
# Grade 11 Mathematics' are two rows, editable independently — which is the point: the
# same standard is examined differently at each institution, and the topic's
# wording, ordering, depth and mark weighting should be controllable per
# institution without touching anyone else's.
#
# What ties them together for reporting is the topic **code**. ``FR-01`` means
# deferred tax on every offering that teaches it, so "how is FR-01 going across
# every institution?" is still one query — see :meth:`Topic.siblings`. The
# trade-off is real and worth knowing: correcting a topic's description has to
# be done per offering, or the copies drift apart.
# ---------------------------------------------------------------------------

# Depth is set per topic and defaults down the spine: a programme's
# ``depth_default`` seeds its offerings, an offering's seeds its topics.
DEPTH_FOUNDATIONAL = 'FND'
DEPTH_ADVANCED = 'ADV'
DEPTH_INTEGRATED = 'INT'
DEPTH_UNDERGRADUATE = 'UG'
DEPTH_CHOICES = [
    (DEPTH_FOUNDATIONAL, 'Foundational — core concepts and basic application'),
    (DEPTH_ADVANCED, 'Grade level — full CAPS depth for the grade'),
    (DEPTH_INTEGRATED, 'Extension — enrichment and cross-subject application'),
    (DEPTH_UNDERGRADUATE, 'Support — remedial, below grade level'),
]


class Institution(TimeStampedModel):
    """The school — United Church School (``UCS``).

    The top of the spine. The platform runs one school; the model stays general
    so the rest of the spine (grades, subjects, calendars) hangs off one row.
    :attr:`accent_colour` is the school's navy, carried into the LMS.
    """

    code = models.CharField(max_length=20, unique=True,
                            help_text='School code used throughout — "UCS".')
    name = models.CharField(max_length=160, unique=True)
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    accent_colour = models.CharField(max_length=9, blank=True, default='#1F3864',
                                     help_text='Hex colour used for this school across the LMS.')
    accent_name = models.CharField(max_length=40, blank=True, help_text='e.g. "UCS Navy".')
    logo = models.ImageField(upload_to='institutions/', blank=True, null=True,
                             validators=v.validate_image)
    website = models.URLField(max_length=300, blank=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'School'
        verbose_name_plural = 'Schools'

    def __str__(self):
        return self.display_name

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = slugify(self.name).split('-')[0].upper()[:20]
        if not self.slug:
            self.slug = slugify(self.name)[:180] or 'institution'
        super().save(*args, **kwargs)

    @property
    def label(self):
        """The school as it appears in a content title — ``UCS``."""
        return self.code.upper()

    @property
    def display_name(self):
        """``United Church School`` — the school as it is
        written for a human being: full name first, abbreviation in brackets.

        Mirrors :attr:`Programme.display_name`. The bracket is dropped when the
        abbreviation is already a word of the name, so a name that already
        contains its code is not repeated as "Name (CODE)".
        """
        name = (self.name or '').strip()
        short = (self.code or '').strip()
        if not short:
            return name
        if not name:
            return short.upper()
        if re.search(rf'\b{re.escape(short)}\b', name, re.IGNORECASE):
            return name
        return f'{name} ({short.upper()})'

    def calendar_for(self, year=None):
        """This institution's :class:`AcademicCalendar` for ``year``, creating it
        if the year has not been opened yet. Defaults to the current year."""
        year = year or timezone.now().year
        calendar, _ = AcademicCalendar.objects.get_or_create(institution=self, year=year)
        return calendar


class Programme(TimeStampedModel):
    """A **grade** at the school — Grade 1 to Grade 12.

    :attr:`code` is the grade's short code (``GR05``); the record's identifier
    across the school's documents is :attr:`full_code`, school and grade
    together — ``UCS-GR05``. :attr:`grade` is the number itself, :attr:`level`
    the CAPS phase it belongs to.

    The fee schedule lives here because UCS charges per learner per grade band,
    not per subject: :attr:`registration_fee` once for a new learner,
    :attr:`annual_levy` once a year, and :attr:`monthly_fee` on the first of
    every month, January to December. A grade with a monthly fee keeps its
    subjects locked until the learner's fees are paid (see
    :attr:`ProgrammeModule.is_free`).

    :attr:`depth_default` is the depth this grade's material is normally pitched
    at. It seeds each subject offering, which in turn seeds each topic.
    """

    LEVEL_FOUNDATION = 'foundation'
    LEVEL_INTERMEDIATE = 'intermediate'
    LEVEL_SENIOR = 'senior'
    LEVEL_FET = 'fet'
    LEVEL_CHOICES = [
        (LEVEL_FOUNDATION, 'Foundation Phase (Grade 1 – 3)'),
        (LEVEL_INTERMEDIATE, 'Intermediate Phase (Grade 4 – 6)'),
        (LEVEL_SENIOR, 'Senior Phase (Grade 7 – 9)'),
        (LEVEL_FET, 'FET Phase (Grade 10 – 12)'),
    ]

    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='programmes')
    code = models.CharField(max_length=30, help_text='Short code, e.g. "GR05". Prefixed with the school '
                                                     'code to give the full code, "UCS-GR05".')
    # The abbreviation people actually search and filter on. It is normally the
    # same string as ``code``, and is kept as its own field because the two are
    # different jobs: ``code`` is the record's identity (it builds ``full_code``
    # and must not drift), while this is a label — searchable, filterable, and
    # safe to say "Grade 5" in where the code says "GR05".
    abbreviation = models.CharField(max_length=30, blank=True, db_index=True,
                                    help_text='Short form shown in brackets after the full name. '
                                              'Blank = use the code.')
    name = models.CharField(max_length=160, help_text='Short display name, e.g. "Grade 5".')
    full_name = models.CharField(max_length=250, blank=True,
                                 help_text='Full title, e.g. "Grade 5". Shown everywhere the grade '
                                           'is named.')
    slug = models.SlugField(max_length=180, blank=True)
    grade = models.PositiveSmallIntegerField(
        null=True, blank=True, db_index=True, help_text='The grade number, 1 – 12.')
    level = models.CharField(max_length=16, choices=LEVEL_CHOICES, default=LEVEL_FOUNDATION,
                             db_index=True, help_text='CAPS phase.')
    depth_default = models.CharField(max_length=4, choices=DEPTH_CHOICES, default=DEPTH_ADVANCED,
                                     help_text='Depth this grade is normally pitched at.')
    # Kept for a competency-structured programme; no grade at UCS uses it.
    is_competency_based = models.BooleanField(
        default=False, help_text='Structured around competency areas rather than examined subjects.')
    # The year's fee schedule (United Church School Fees 2026), in rand.
    registration_fee = models.DecimalField(
        max_digits=8, decimal_places=2, default=0,
        help_text='Once-off registration fee for a NEW learner (non-refundable). 0 = none.')
    annual_levy = models.DecimalField(
        max_digits=8, decimal_places=2, default=0,
        help_text='Annual levy, due on enrolment and settled in full by 25 January.')
    monthly_fee = models.DecimalField(
        max_digits=8, decimal_places=2, default=0,
        help_text='Monthly school fees, payable in advance on the 1st, January to December. '
                  '0 = no fees (subjects always unlocked).')
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['institution', 'order', 'name']
        constraints = [
            models.UniqueConstraint(fields=['institution', 'code'], name='uniq_programme_code_per_institution'),
        ]
        verbose_name = 'Grade'
        verbose_name_plural = 'Grades'

    def __str__(self):
        """``UCS · Grade 5`` — what every dropdown, autocomplete and admin list shows."""
        return f'{self.institution.label} · {self.display_name}'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f'{self.institution.code}-{self.code}')[:180] or 'programme'
        if not self.abbreviation:
            self.abbreviation = (self.code or '')[:30]
        super().save(*args, **kwargs)

    @property
    def short_code(self):
        """The abbreviation to show — falls back to the code if none is set."""
        return (self.abbreviation or self.code or '').strip()

    @property
    def display_name(self):
        """``Grade 5`` — the grade's name
        as it is written for a human being.

        Full title first, abbreviation in brackets. Where there is no full title
        the abbreviation stands alone rather than rendering "(GR05)" with
        nothing in front of it.
        """
        full = (self.full_name or self.name or '').strip()
        short = self.short_code
        if full and short and full.lower() != short.lower():
            return f'{full} ({short})'
        return full or short

    @property
    def full_code(self):
        """``UCS-GR05`` — the grade's identifier across the school."""
        return f'{self.institution.code}-{self.code}'

    @property
    def label(self):
        """``UCS Grade 5`` — the first field of the LMS naming convention.

        Deliberately the abbreviation, not :attr:`display_name`: this builds
        content titles and filenames ("UCS Grade 5 | MATH | Worksheet | v3"),
        where the whole point is that it sorts short and tight.
        """
        return f'{self.institution.label} {self.short_code}'.strip()

    # -- fees ----------------------------------------------------------------
    @property
    def has_fees(self):
        """True when this grade charges school fees (its subjects are then
        unlocked by paying them rather than being open to everyone)."""
        return bool(self.monthly_fee or self.annual_levy or self.registration_fee)

    @property
    def annual_fees(self):
        """Levy plus twelve months' school fees — "Total fees (including Levy)"."""
        return (self.annual_levy or 0) + (self.monthly_fee or 0) * 12

    @property
    def annual_fees_new_learner(self):
        """:attr:`annual_fees` plus registration — the new-learner total."""
        return self.annual_fees + (self.registration_fee or 0)


class ProgrammePhase(TimeStampedModel):
    """One phase of a phased programme — the APC's Foundation → Integration →
    Simulation → Exam-ready run from March to November.

    A phase is a period with a focus, not a container of content: it tells a
    candidate what this stretch of the year is *for*, which is the difference
    between a nine-month programme and nine months of sessions.
    """

    programme = models.ForeignKey(Programme, on_delete=models.CASCADE, related_name='phases')
    name = models.CharField(max_length=120, help_text='e.g. "Foundation".')
    period = models.CharField(max_length=120, blank=True, help_text='e.g. "March – May".')
    focus = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'id']
        constraints = [
            models.UniqueConstraint(fields=['programme', 'name'], name='uniq_phase_name_per_programme'),
        ]

    def __str__(self):
        return f'{self.programme.full_code} · {self.name}'


class Cohort(TimeStampedModel):
    """A grade's class for a year (``2026``), or a named class within it.

    Same programme, same modules, different calendar: test dates, session
    timetable and the sitting a student is preparing for all hang off the cohort
    rather than the programme.
    """

    programme = models.ForeignKey(Programme, on_delete=models.CASCADE, related_name='cohorts')
    code = models.CharField(max_length=30, help_text='e.g. "2026" (the year) or "10A".')
    name = models.CharField(max_length=120, blank=True, help_text='e.g. "Grade 10 · 2026".')
    # The class (register) teacher: takes the daily register and confirms the
    # class's year-end promotion decisions.
    class_teacher = models.ForeignKey(
        'accounts.Person', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='classes_taught', limit_choices_to={'user_type__in': ['educator', 'staff', 'admin']},
        help_text='Class teacher: takes the daily register and records promotion decisions.')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['programme', '-start_date', 'code']
        constraints = [
            models.UniqueConstraint(fields=['programme', 'code'], name='uniq_cohort_code_per_programme'),
        ]
        verbose_name = 'Class'
        verbose_name_plural = 'Classes'

    def __str__(self):
        return f'{self.programme.full_code} · {self.code}'


class Module(TimeStampedModel):
    """The **canonical** subject catalogue — one row per subject.

    Mathematics is one subject (``MATH``). It is taught in every grade from
    Grade 1 to Grade 12 (as the FET alternative to Mathematical Literacy from
    Grade 10); each grade's version is a :class:`ProgrammeModule` pointing here,
    which is what makes "how is Mathematics going across the school?" a
    question the platform can answer even though each grade owns its topics.
    """

    code = models.CharField(max_length=20, unique=True, help_text='Canonical code, e.g. "MATH" or "ENG-HL".')
    name = models.CharField(max_length=160, unique=True)
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    is_competency_area = models.BooleanField(
        default=False, help_text='A competency area rather than an examined subject.')
    description = models.TextField(blank=True, help_text='What the subject covers.')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Subject'
        verbose_name_plural = 'Subjects'

    def __str__(self):
        return f'{self.code} — {self.name}' if self.code else self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:180] or 'module'
        super().save(*args, **kwargs)


class ProgrammeModule(TimeStampedModel):
    """A canonical :class:`Module` (a subject) **as offered in one grade** —
    the "offering", and the owner of its topics.

    Grade 10 and Grade 11 both carry Mathematics; the subject is the same, the
    content is not, so each grade's offering owns its own topics. :attr:`code`
    is unique per grade.

    :attr:`subject_group` carries the CAPS subject-choice rule for Grade 10 –
    12: blank means compulsory for everyone in the grade; ``fal`` / ``maths`` /
    ``elective`` mark the subjects a learner chooses between (one first
    additional language, Mathematics or Mathematical Literacy, three electives —
    see :data:`core.school.SUBJECT_GROUPS`).
    """

    GROUP_COMPULSORY = ''
    GROUP_FAL = 'fal'
    GROUP_MATHS = 'maths'
    GROUP_ELECTIVE = 'elective'
    GROUP_CHOICES = [
        (GROUP_COMPULSORY, 'Compulsory'),
        (GROUP_FAL, 'First Additional Language (choose one)'),
        (GROUP_MATHS, 'Mathematics or Mathematical Literacy (choose one)'),
        (GROUP_ELECTIVE, 'Elective (choose three)'),
    ]

    programme = models.ForeignKey(Programme, on_delete=models.CASCADE, related_name='modules')
    module = models.ForeignKey(Module, on_delete=models.PROTECT, related_name='offerings')
    code = models.CharField(max_length=20,
                            help_text='The subject\'s code in this grade, e.g. "MATH".')
    name = models.CharField(max_length=160, blank=True,
                            help_text='Overrides the canonical subject name when this grade names it '
                                      'differently.')
    depth_level = models.CharField(max_length=4, choices=DEPTH_CHOICES, blank=True,
                                   help_text="Blank = inherit the programme's default depth.")
    description = models.TextField(blank=True, help_text='Coverage of this offering.')
    # Who teaches it. A subject is taught per grade, so the teacher is set on
    # the offering rather than on the canonical subject: the same person may
    # take Grade 10 Mathematics and not Grade 12.
    educators = models.ManyToManyField('accounts.Person', blank=True, related_name='taught_modules',
                                       limit_choices_to={'user_type__in': ['educator', 'staff', 'admin']},
                                       help_text='Teachers who teach this subject in this grade.')
    subject_group = models.CharField(
        max_length=12, choices=GROUP_CHOICES, blank=True, default=GROUP_COMPULSORY,
        help_text='Grade 10 – 12 subject choice: blank = compulsory for every learner in the grade.')
    # The module's group conversation — the Messages tab on the module feed.
    # The FK points learning → communication, the direction the two apps already
    # run in (LessonBlock links a MeetingRoom the same way).
    chat_group = models.OneToOneField(
        'communication.ChatGroup', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='programme_module',
        help_text='Group chat for everyone studying this offering.')
    # Per-subject monthly price. At UCS subjects carry no price of their own —
    # the grade's school fees (Programme.monthly_fee) pay for all of them — so
    # this stays 0; it remains for a stand-alone paid offering (e.g. extra
    # lessons) billed per month.
    price_per_month = models.DecimalField(
        max_digits=8, decimal_places=2, default=0,
        help_text='Extra monthly price (ZAR) for this subject on top of the grade\'s school fees. '
                  'Normally 0.')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['programme', 'order', 'id']
        constraints = [
            models.UniqueConstraint(fields=['programme', 'code'], name='uniq_module_code_per_programme'),
        ]
        verbose_name = 'Grade subject'

    def __str__(self):
        return self.reference

    @property
    def reference(self):
        """``UCS-GR10 / MATH`` — how an offering is written in the records."""
        return f'{self.programme.full_code} / {self.code}'

    @property
    def label(self):
        """``UCS Grade 10 | MATH`` — the LMS naming convention, up to the subject."""
        return f'{self.programme.label} | {self.code}'.strip(' |')

    @property
    def display_name(self):
        return self.name or self.module.name

    @property
    def institution(self):
        return self.programme.institution

    @property
    def resolved_depth(self):
        return self.depth_level or self.programme.depth_default

    def completion_for(self, student):
        """Percentage of this offering's topics the student has completed (0–100)."""
        topics = [topic for topic in self.topics.all() if topic.is_active]
        if not topics:
            return 0
        done = sum(1 for topic in topics if topic.is_completed_by(student))
        return round(done / len(topics) * 100)

    @property
    def is_compulsory(self):
        return not self.subject_group

    @property
    def is_free(self):
        """Open to anyone with no payment — only when neither the subject nor
        its grade charges anything. A subject in a fee-paying grade is unlocked
        by the learner's paid school fees (their ModuleEnrolment), not by being
        free."""
        if self.price_per_month:
            return False
        return not self.programme.has_fees

    @property
    def member_people(self):
        """Everyone attached to this offering — coaches and candidates together.

        The old ``Subject.member_people`` OR-ed two M2Ms. ``students`` here joins
        through ModuleEnrolment and comes back distinct, and a distinct queryset
        cannot be OR-combined, so the union is done on primary keys.
        """
        from apps.accounts.models import Person
        return Person.objects.filter(
            pk__in=set(self.educators.values_list('pk', flat=True))
                   | set(self.students.values_list('pk', flat=True)))

    @property
    def students(self):
        """Everyone registered on this offering, whatever their payment state.

        ``accounts.ProgrammeModule`` carried a plain students M2M; an offering does not,
        because enrolment here is a richer thing — :class:`ModuleEnrolment` holds
        status, price and dates. This gives the call sites that only want "who is
        on this module" the same shape they had, without pretending membership
        and enrolment are the same record.
        """
        from apps.accounts.models import Person
        return Person.objects.filter(module_enrolments__programme_module=self).distinct()

    def enrolment_for(self, person):
        """This person's :class:`ModuleEnrolment` for the offering, or ``None``."""
        if person is None:
            return None
        return self.enrolments.filter(person=person).first()

    def is_unlocked_for(self, person):
        """True when the person may open this module — free, on a live trial, or paid."""
        if self.is_free:
            return True
        enrolment = self.enrolment_for(person)
        return bool(enrolment and enrolment.is_unlocked)


# ---------------------------------------------------------------------------
# The academic calendar — when the year actually happens
#
# The spine above says *what* a student studies. This says *when*: test and exam
# dates, submission deadlines, session blocks and the no-session periods around
# them. It is school-first because that is how the dates arrive: the school
# publishes its term dates and examination timetable for the year.
#
# ``myhub.Event`` already exists and stays where it is: that is the practice's
# own diary (a booked session, a personal reminder). This is the institution's
# published year, which is a different thing with a different owner — nobody at
# the diary decides the school's term dates.
# ---------------------------------------------------------------------------
class AcademicCalendar(TimeStampedModel):
    """One institution's year — the container its dated events hang off.

    One per institution per year, which is the grain the institutions themselves
    publish at. Everything narrower than that (this programme, this module, this
    cohort) is expressed on the individual :class:`CalendarEvent`, because that
    is where it genuinely varies: the year is shared, the Test 2 date is not.
    """

    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='calendars')
    year = models.PositiveIntegerField(db_index=True, help_text='Academic year, e.g. 2026.')
    name = models.CharField(max_length=160, blank=True,
                            help_text='Blank = "<Institution> · <year> academic calendar".')
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-year', 'institution']
        constraints = [
            models.UniqueConstraint(fields=['institution', 'year'], name='uniq_calendar_per_institution_year'),
        ]
        verbose_name = 'Academic calendar'

    def __str__(self):
        return self.name or f'{self.institution.code} · {self.year}'

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = f'{self.institution.name} · {self.year} academic calendar'[:160]
        super().save(*args, **kwargs)

    @property
    def upcoming(self):
        """Published events still ahead of now, soonest first."""
        return self.events.filter(is_published=True, start__gte=timezone.now()).order_by('start')


class CalendarEvent(TimeStampedModel):
    """A dated thing on an institution's calendar — a test, an exam, a deadline.

    Scope is set by how many of the optional links are filled in. A public
    holiday is just the calendar; "Grade 12 prelims" adds the grade;
    "FREP Test 2" adds the offering; and a date that only one intake sits adds
    the cohort. Nothing is required beyond the calendar itself, so a date can be
    captured the moment it is announced and narrowed later.
    """

    KIND_TEST = 'test'
    KIND_EXAM = 'exam'
    KIND_SUPPLEMENTARY = 'supp'
    KIND_ASSIGNMENT = 'assignment'
    KIND_DEADLINE = 'deadline'
    KIND_SESSION = 'session'
    KIND_INTENSIVE = 'intensive'
    KIND_MOCK = 'mock'
    KIND_RESULT = 'result'
    KIND_ORIENTATION = 'orientation'
    KIND_HOLIDAY = 'holiday'
    KIND_OTHER = 'other'
    KIND_CHOICES = [
        (KIND_TEST, 'Test'),
        (KIND_EXAM, 'Examination'),
        (KIND_SUPPLEMENTARY, 'Supplementary / re-assessment'),
        (KIND_ASSIGNMENT, 'Assignment due'),
        (KIND_DEADLINE, 'Administrative deadline'),
        (KIND_SESSION, 'Coaching session'),
        (KIND_INTENSIVE, 'Test / exam intensive'),
        (KIND_MOCK, 'Mock assessment'),
        (KIND_RESULT, 'Results released'),
        (KIND_ORIENTATION, 'Orientation'),
        (KIND_HOLIDAY, 'Holiday / no session'),
        (KIND_OTHER, 'Other'),
    ]

    # The colour each kind draws in on the calendar. Deadlines and exams take the
    # brand's alert red, coaching takes the gold accent — the same semantics the
    # student guides already use, so the calendar reads like the rest of the
    # material rather than like a generic scheduler.
    KIND_COLOURS = {
        KIND_TEST: '#C00000',
        KIND_EXAM: '#8B0000',
        KIND_SUPPLEMENTARY: '#C0504D',
        KIND_ASSIGNMENT: '#1F3864',
        KIND_DEADLINE: '#C00000',
        KIND_SESSION: '#C9A84C',
        KIND_INTENSIVE: '#B8860B',
        KIND_MOCK: '#1D6A4E',
        KIND_RESULT: '#1D6A4E',
        KIND_ORIENTATION: '#4682B4',
        KIND_HOLIDAY: '#555555',
        KIND_OTHER: '#1F3864',
    }

    calendar = models.ForeignKey(AcademicCalendar, on_delete=models.CASCADE, related_name='events')
    # Optional narrowing — each one filled in makes the event apply to fewer people.
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE, null=True, blank=True,
                                  related_name='calendar_events')
    programme_module = models.ForeignKey(ProgrammeModule, on_delete=models.CASCADE, null=True, blank=True,
                                         related_name='calendar_events',
                                         verbose_name='Subject')
    cohort = models.ForeignKey(Cohort, on_delete=models.CASCADE, null=True, blank=True,
                               related_name='calendar_events')

    title = models.CharField(max_length=200)
    kind = models.CharField(max_length=12, choices=KIND_CHOICES, default=KIND_OTHER, db_index=True)
    start = models.DateTimeField(db_index=True)
    end = models.DateTimeField(null=True, blank=True)
    all_day = models.BooleanField(default=True,
                                  help_text='A published date with no fixed time — most institution dates.')
    location = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    # Somewhere to record what the date is worth / what it covers, without
    # forcing a separate assessment record for a date that has only been announced.
    weight_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                     help_text='Contribution to the final mark, if published.')
    is_published = models.BooleanField(default=True,
                                       help_text='Unpublished events are visible to staff only.')

    class Meta:
        ordering = ['start', 'id']
        indexes = [
            models.Index(fields=['calendar', 'start']),
            # The dashboard's exam countdown asks the same question on every
            # page load: "next exam/test on this institution's calendar". That
            # filters calendar + kind and orders by start, so the two-column
            # index above still forces a scan-and-filter on kind. Ordering the
            # columns calendar → kind → start lets one index serve the whole
            # clause, and serve the reverse ("last one that passed") too.
            models.Index(fields=['calendar', 'kind', 'start'],
                         name='learning_calev_cal_kind_start'),
            # The same lookup narrowed to a programme — the countdown discards
            # dates scoped to a programme the candidate is not on.
            models.Index(fields=['programme', 'start'],
                         name='learning_calev_prog_start'),
        ]
        verbose_name = 'Calendar event'

    def __str__(self):
        return f'{self.label} · {self.start:%Y-%m-%d}'

    @property
    def label(self):
        """``UCS Grade 10 | MATH | Test 1`` — the LMS naming convention."""
        if self.programme_module_id:
            return f'{self.programme_module.label} | {self.title}'
        if self.programme_id:
            return f'{self.programme.label} | {self.title}'
        return f'{self.calendar.institution.label} | {self.title}'

    @property
    def colour(self):
        return self.KIND_COLOURS.get(self.kind, '#1F3864')

    @property
    def is_upcoming(self):
        return self.start >= timezone.now()

    @property
    def days_away(self):
        """Whole days from now until it happens; negative once it has passed."""
        return (self.start.date() - timezone.now().date()).days


# ---------------------------------------------------------------------------
# Enrolment, pricing & access — the lock / unlock + billing records
#
# A student registers for a Programme (ProgrammeEnrolment) and then for the
# individual ProgrammeModules they want (ModuleEnrolment). Pricing is per module
# per month (ProgrammeModule.price_per_month); a module stays LOCKED until it is
# paid for, with an optional 7-day free trial ("week one"). These live in the
# learning app (which already depends on accounts); accounts.Person exposes them
# as the ``enrolled_programmes`` / ``enrolled_modules`` convenience properties.
# ---------------------------------------------------------------------------
class ProgrammeEnrolment(TimeStampedModel):
    """A student registered for a programme, optionally on a specific cohort."""
    person = models.ForeignKey('accounts.Person', on_delete=models.CASCADE, related_name='programme_enrolments')
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE, related_name='enrolments')
    cohort = models.ForeignKey(Cohort, on_delete=models.SET_NULL, null=True, blank=True, related_name='enrolments')
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['person', 'programme'], name='uniq_programme_enrolment_per_person'),
        ]
        verbose_name = 'Grade enrolment'

    def __str__(self):
        return f'{self.person} · {self.programme.full_code}'


class ModuleEnrolment(TimeStampedModel):
    """A student's access to one :class:`ProgrammeModule` — the lock/unlock and
    billing record.

    Pricing is **per module per month** (``ProgrammeModule.price_per_month``). A
    row is created LOCKED (selected + invoiced, not yet paid); the payment hook
    flips it to ACTIVE, or the student can start a 7-day free TRIAL ("week one").
    ``invoice_uid`` links the raised invoice by its ``public_id`` (a UUID, not an
    FK, to avoid a learning↔finance import cycle — the same pattern
    ``accounts.Person.pending_invoice_uid`` uses).
    """
    STATUS_LOCKED = 'locked'
    STATUS_TRIAL = 'trial'
    STATUS_ACTIVE = 'active'
    STATUS_EXPIRED = 'expired'
    STATUS_CHOICES = [
        (STATUS_LOCKED, 'Locked — awaiting payment'),
        (STATUS_TRIAL, 'Free trial'),
        (STATUS_ACTIVE, 'Active — paid'),
        (STATUS_EXPIRED, 'Expired'),
    ]

    TRIAL_DAYS = 7

    person = models.ForeignKey('accounts.Person', on_delete=models.CASCADE, related_name='module_enrolments')
    programme_module = models.ForeignKey(ProgrammeModule, on_delete=models.CASCADE, related_name='enrolments')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_LOCKED, db_index=True)
    price_at_enrolment = models.DecimalField(
        max_digits=8, decimal_places=2, default=0,
        help_text='Monthly price captured at enrolment (so later price changes do not rewrite history).')
    started_at = models.DateTimeField(null=True, blank=True)
    trial_ends_at = models.DateTimeField(null=True, blank=True)
    paid_until = models.DateField(null=True, blank=True, help_text='Access is paid up to this date.')
    invoice_uid = models.UUIDField(null=True, blank=True,
                                   help_text='public_id of the invoice raised for this module.')

    class Meta:
        ordering = ['programme_module', 'person']
        constraints = [
            models.UniqueConstraint(fields=['person', 'programme_module'], name='uniq_module_enrolment_per_person'),
        ]
        verbose_name = 'Subject enrolment'

    def __str__(self):
        return f'{self.person} · {self.programme_module.code} ({self.status})'

    @property
    def price(self):
        """Monthly price for this enrolment (captured value, else the module's)."""
        return self.price_at_enrolment or self.programme_module.price_per_month or 0

    @property
    def is_trial_valid(self):
        return self.status == self.STATUS_TRIAL and (
            self.trial_ends_at is None or self.trial_ends_at >= timezone.now())

    @property
    def trial_days_left(self):
        """Whole days remaining on a live trial, rounded up so any part of the
        final day still reads as "1 day left". ``None`` when not on a live trial.
        """
        if not self.is_trial_valid or self.trial_ends_at is None:
            return None
        delta = self.trial_ends_at - timezone.now()
        if delta.total_seconds() <= 0:
            return 0
        return delta.days + (1 if (delta.seconds or delta.microseconds) else 0)

    @staticmethod
    def grace_days():
        from django.conf import settings as dj_settings
        from core.school import FEES_GRACE_DAYS
        return getattr(dj_settings, 'FEES_GRACE_DAYS', FEES_GRACE_DAYS)

    @property
    def is_unlocked(self):
        """True when the learner may open the subject — school fees paid up to
        the current month (allowing the grace period into an unpaid month), or
        on a live trial."""
        if self.status == self.STATUS_ACTIVE:
            if self.paid_until is None:
                return True
            return self.paid_until + timedelta(days=self.grace_days()) >= timezone.now().date()
        return self.is_trial_valid

    def start_trial(self, now=None):
        """Begin the 7-day free trial ("week one")."""
        now = now or timezone.now()
        self.status = self.STATUS_TRIAL
        self.started_at = self.started_at or now
        self.trial_ends_at = now + timedelta(days=self.TRIAL_DAYS)
        self.save(update_fields=['status', 'started_at', 'trial_ends_at', 'updated_at'])
        return self

    def activate(self, months=1, now=None, start=None):
        """Unlock as paid (called by the payment hook) for ``months`` whole
        **calendar months**: fees are paid per month, in advance.

        Access runs to the last day of the final month paid. Without ``start``
        the months follow on from what is already paid (or begin with the
        current month); with ``start`` (the first month an invoice covers) they
        cover exactly those months — never shortening access already paid."""
        from core.school import add_months, month_end, month_start
        now = now or timezone.now()
        today = timezone.localdate(now) if timezone.is_aware(now) else now.date()
        if start is None:
            if self.paid_until and self.paid_until >= today:
                start = self.paid_until + timedelta(days=1)
            else:
                start = today
        first = month_start(start)
        until = month_end(add_months(first, max(int(months or 1), 1) - 1))
        self.status = self.STATUS_ACTIVE
        self.started_at = self.started_at or now
        self.paid_until = max(until, self.paid_until) if self.paid_until else until
        self.save(update_fields=['status', 'started_at', 'paid_until', 'updated_at'])
        return self

    def lock(self):
        self.status = self.STATUS_LOCKED
        self.save(update_fields=['status', 'updated_at'])
        return self


class Topic(TimeStampedModel):
    """One topic of one offering's syllabus — **owned by the offering**.

    Grade 10 MATH's ``MATH-ALG`` algebra and Grade 11 MATH's ``MATH-ALG``
    are two rows. Editing one never touches the other, which is what makes the
    exact content of each institution controllable: its wording, its ordering,
    the depth it is taken to, and what the past papers say about it.

    :attr:`code` is the shared vocabulary across those copies. ``FR-01`` means
    deferred tax everywhere, so cross-institution reporting groups on the code —
    see :meth:`siblings`. Codes come from the curriculum reference's topic
    library (``FR-01``–``FR-14``, ``TX-01``–``TX-15``, ``GA-01``–``GA-09``,
    ``MA-01``–``MA-13``), and the seed command creates every offering's copy
    from it so they start identical.

    :attr:`reference` is the authority behind the topic (``IAS 12``, ``ITA s1,
    s10``, ``ISA 700 series``). Citing properly is a brand commitment, so it is
    a field, not something buried in prose.

    :attr:`frequency` and :attr:`avg_marks` are this institution's own
    past-paper trend analysis, and stay blank until that analysis has actually
    been run — one grade's pattern is not evidence about another's paper.

    A topic holds the material for one week of the programme: the study guide
    as a :class:`Lesson`, and the mock / challenge as ``assessments.Assessment``
    rows. That is exactly the shape the source documents come in.
    """

    FREQ_EVERY_SITTING = 'every_sitting'
    FREQ_MOST_SITTINGS = 'most_sittings'
    FREQ_RECURRING = 'recurring'
    FREQ_PERIODIC = 'periodic'
    FREQ_RARE = 'rare'
    FREQUENCY_CHOICES = [
        (FREQ_EVERY_SITTING, 'Every sitting'),
        (FREQ_MOST_SITTINGS, 'Most sittings'),
        (FREQ_RECURRING, 'Recurring'),
        (FREQ_PERIODIC, 'Periodic'),
        (FREQ_RARE, 'Rarely tested'),
    ]
    # label · bootstrap tone, per frequency — the trend analysis, shown as a badge.
    FREQUENCY_META = {
        FREQ_EVERY_SITTING: ('Every sitting', 'danger'),
        FREQ_MOST_SITTINGS: ('Most sittings', 'warning'),
        FREQ_RECURRING: ('Recurring', 'primary'),
        FREQ_PERIODIC: ('Periodic', 'info'),
        FREQ_RARE: ('Rarely tested', 'secondary'),
    }

    programme_module = models.ForeignKey(ProgrammeModule, on_delete=models.CASCADE, related_name='topics')
    code = models.CharField(max_length=20, db_index=True,
                            help_text='Topic code from the curriculum reference, e.g. "FR-01". Shared with '
                                      'the same topic on other institutions — that is how they are reported '
                                      'together.')
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=270, blank=True)
    reference = models.CharField(max_length=160, blank=True,
                                 help_text='Standard / legislation behind the topic — "IAS 12", "VAT Act s16(3)".')
    description = models.TextField(blank=True)
    depth = models.CharField(max_length=4, choices=DEPTH_CHOICES, blank=True,
                             help_text="Blank = inherit the offering's depth.")
    # Both weighting columns stay blank until this institution's own past papers
    # have been analysed — see the class docstring.
    frequency = models.CharField(max_length=16, choices=FREQUENCY_CHOICES, blank=True, db_index=True,
                                 help_text="How often the topic appears in this institution's papers. "
                                           'Blank = not yet analysed.')
    avg_marks = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True,
                                    help_text="🎯 Average marks the topic carries in this institution's papers.")
    # 📌 in the brand's callout system: a topic that appears in every sitting and
    # is therefore not optional preparation.
    is_non_negotiable = models.BooleanField(default=False, help_text='📌 Non-negotiable — prepare this every time.')
    notes = models.TextField(blank=True, help_text='How this offering treats the topic.')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        # Order on the raw column only — following the ``programme_module`` FK
        # pulls in its ordering and Django raises "Infinite loop caused by
        # ordering". Topics are always queried per offering, so ``order`` is enough.
        ordering = ['order', 'id']
        constraints = [
            models.UniqueConstraint(fields=['programme_module', 'code'],
                                    name='uniq_topic_code_per_programme_module'),
        ]
        indexes = [models.Index(fields=['programme_module', 'order'])]

    def __str__(self):
        return f'{self.programme_module.reference} / {self.code}'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f'{self.code}-{self.title}')[:270] or 'topic'
        if not self.depth:
            self.depth = self.programme_module.resolved_depth
        super().save(*args, **kwargs)

    # --- where this topic sits ----------------------------------------------
    @property
    def programme(self):
        return self.programme_module.programme

    @property
    def institution(self):
        return self.programme_module.programme.institution

    @property
    def module(self):
        """The canonical module behind this offering."""
        return self.programme_module.module

    @property
    def label(self):
        """``UCS Grade 10 | MATH | Algebra`` — the naming convention."""
        return f'{self.programme_module.label} | {self.title}'

    @property
    def resolved_depth(self):
        return self.depth or self.programme_module.resolved_depth

    def siblings(self):
        """The same topic as taught everywhere else.

        Each offering owns its own copy, so this is how the platform still
        answers "how is deferred tax going across every institution?" — the
        :attr:`code` is the shared key.
        """
        return (Topic.objects.filter(code=self.code)
                .exclude(pk=self.pk)
                .select_related('programme_module__programme__institution'))

    # --- trend analysis -----------------------------------------------------
    @property
    def is_analysed(self):
        """False until this institution's own past papers have been worked."""
        return bool(self.frequency)

    @property
    def frequency_label(self):
        return self.FREQUENCY_META.get(self.frequency, ('Not yet analysed', 'secondary'))[0]

    @property
    def frequency_tone(self):
        return self.FREQUENCY_META.get(self.frequency, ('Not yet analysed', 'secondary'))[1]

    # --- progress -----------------------------------------------------------
    # A topic used to hold an ordered run of ``CourseItem``s and was "played"
    # like a course chapter. That layer went with the MyHub course player. What
    # a topic holds now is what the source documents hold: published lessons
    # (the study guide) and assessments (the mock, the challenge). Progress is
    # measured against those.
    @property
    def has_content(self):
        """True once the topic has any published lesson or open assessment."""
        from apps.assessments.models import Assessment
        return (self.lessons.filter(status=Lesson.STATUS_PUBLISHED).exists()
                or self.assessments.filter(status=Assessment.STATUS_OPEN).exists())

    def required_lessons(self):
        """The published lessons a candidate is expected to work through."""
        return list(self.lessons.filter(status=Lesson.STATUS_PUBLISHED))

    def completion_for(self, student):
        """Percentage of this topic's published lessons completed (0–100)."""
        lessons = self.required_lessons()
        if not lessons:
            return 0
        from .models import StudySession
        done = (StudySession.objects
                .filter(student=student, lesson__in=lessons,
                        status=StudySession.STATUS_COMPLETED)
                .values('lesson_id').distinct().count())
        return round(min(done, len(lessons)) / len(lessons) * 100)

    def is_completed_by(self, student):
        lessons = self.required_lessons()
        return bool(lessons) and self.completion_for(student) >= 100

class LessonQuerySet(models.QuerySet):
    """Query helpers shared by every surface that lists lessons."""

    def for_role(self, user):
        """Drop lessons written for a different role than ``user``'s.

        A lesson with an empty :attr:`Lesson.target_roles` is for everyone; one
        that names roles is only ever returned to a user holding one of them.
        Staff and admins are *not* exempt here — a lesson written for parents
        would only confuse an educator's list, and they can still open it
        directly from the manager.
        """
        person = getattr(user, 'profile', None)
        role = getattr(person, 'user_type', None) or 'student'
        return self.filter(models.Q(target_roles=[]) | models.Q(target_roles__contains=[role]))


class Lesson(TimeStampedModel):
    """A single study lesson: rich body + attached resources, versioned and
    publishable to a chosen audience."""

    objects = LessonQuerySet.as_manager()

    STATUS_DRAFT = 'draft'
    STATUS_PUBLISHED = 'published'
    STATUS_ARCHIVED = 'archived'
    STATUS_SCHEDULED = 'scheduled'
    STATUS_EXPIRED = 'expired'
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_PUBLISHED, 'Published'),
        (STATUS_ARCHIVED, 'Archived'),
        (STATUS_SCHEDULED, 'Scheduled'),
        (STATUS_EXPIRED, 'Expired'),
    ]

    VIS_INSTITUTION = 'institution'
    VIS_PROGRAMME = 'programme'
    VIS_MODULE = 'module'
    VIS_GROUP = 'group'
    VIS_INDIVIDUAL = 'individual'
    VISIBILITY_CHOICES = [
        (VIS_INSTITUTION, 'Entire institution'),
        (VIS_PROGRAMME, 'Specific programme'),
        (VIS_MODULE, 'Specific module'),
        (VIS_GROUP, 'Study group'),
        (VIS_INDIVIDUAL, 'Individual students'),
    ]

    # Where the lesson sits. ``topic`` is the institution-first spine; ``unit`` /
    # ``module`` are the legacy course spine, kept while content moves across.
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='lessons')
    module = models.ForeignKey('learning.ProgrammeModule', on_delete=models.CASCADE, null=True, blank=True,
                                related_name='lessons')
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True)
    slug = models.SlugField(max_length=220, blank=True)
    # Legacy single-blob content. New lessons are authored as ordered LessonBlocks
    # (see ``blocks`` related_name); ``body`` is kept for backward compatibility and
    # as an export fallback.
    body = models.TextField(blank=True, help_text='Legacy rich-text content (block editor preferred).')
    cover_image = models.ImageField(upload_to='lessons/covers/', blank=True, null=True,
                                    validators=v.validate_image)

    # --- Author / attribution + references (shown on the lecture) ---
    author_name = models.CharField(max_length=160, blank=True)
    author_role = models.CharField(max_length=160, blank=True, help_text='e.g. "Senior Lecturer, Physics".')
    author_bio = models.TextField(blank=True)
    author_avatar = models.ImageField(upload_to='lessons/authors/', blank=True, null=True,
                                      validators=v.validate_avatar)
    # Bibliography: a list of {"text": str, "url": str, "authors": str, "year": str}.
    references = models.JSONField(default=list, blank=True)

    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=STATUS_DRAFT, db_index=True)
    visibility = models.CharField(max_length=12, choices=VISIBILITY_CHOICES, default=VIS_MODULE)
    # Optional targeting when visibility is narrower than the lesson's own place
    # in the spine: a lesson can be aimed at whole programmes, at specific
    # module offerings, or at named individuals.
    target_programmes = models.ManyToManyField(Programme, blank=True, related_name='targeted_lessons')
    target_modules = models.ManyToManyField('learning.ProgrammeModule', blank=True, related_name='targeted_lessons')
    target_users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='targeted_lessons')

    # Roles this lesson is written for, e.g. ``["student"]`` or
    # ``["educator", "staff"]``. Empty = everyone in the audience above sees it.
    # A module can therefore carry one lesson per role — the same topic told
    # to a learner, to the educator teaching it, and to a parent following along
    # — with each role only ever seeing their own.
    target_roles = models.JSONField(default=list, blank=True)

    publish_at = models.DateTimeField(null=True, blank=True)
    expire_at = models.DateTimeField(null=True, blank=True)
    estimated_minutes = models.PositiveIntegerField(default=30, help_text='Estimated study time.')
    version = models.PositiveIntegerField(default=1)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='lessons_created')

    class Meta:
        ordering = ['module', 'title']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:220] or 'lesson'
        super().save(*args, **kwargs)

    # --- where this lesson sits ---------------------------------------------
    @property
    def programme_module(self):
        """The offering this lesson belongs to (via its topic), if any."""
        return self.topic.programme_module if self.topic_id else None

    @property
    def programme(self):
        return self.topic.programme if self.topic_id else None

    @property
    def institution(self):
        return self.topic.institution if self.topic_id else None

    # --- rendering / authoring helpers ---
    @property
    def uses_blocks(self):
        """True when the lesson has structured block content."""
        return self.blocks.exists()

    def body_blocks(self):
        """The lesson's main body: top-level blocks in order.

        A ``section`` block in this list renders as a collapsible panel holding
        its own children (``block.child_blocks``) — the body is one continuous
        flow, not a preamble followed by an accordion.
        """
        return (self.blocks.filter(section__isnull=True)
                .select_related('assessment', 'meeting',
                                'holds_section')
                .order_by('order', 'id'))

    @property
    def author_display(self):
        if self.author_name:
            return self.author_name
        if self.created_by_id:
            return self.created_by.get_full_name() or self.created_by.get_username()
        return ''

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('learning:lesson-view', args=[self.pk])

    def get_edit_url(self):
        from django.urls import reverse
        return reverse('learning:lesson-editor', args=[self.pk])

    @property
    def is_live(self):
        """Published and within its publish/expire window."""
        if self.status != self.STATUS_PUBLISHED:
            return False
        now = timezone.now()
        if self.publish_at and self.publish_at > now:
            return False
        if self.expire_at and self.expire_at < now:
            return False
        return True


class LessonSection(TimeStampedModel):
    """One collapsible **section** of a lesson — the "tear-drop" the learner opens.

    A lesson is presented as an ordered list of sections; each is a labelled,
    timed, optionally *locked* accordion panel holding a run of
    :class:`LessonBlock`s. The label comes from :attr:`section_type` (reading /
    video / quiz / assessment / live / interactive / resources) which the author
    can set explicitly or leave on ``auto`` to be inferred from the blocks
    inside. Likewise :attr:`duration_minutes` is either authored or estimated
    (reading speed for prose, the assessment's time limit for a quiz, the media
    duration for video).

    Sections created before this model existed do not exist: blocks with a null
    ``section`` render *above* the accordion as the lesson's intro, so older
    lessons keep working untouched.
    """

    TYPE_AUTO = 'auto'
    TYPE_READING = 'reading'
    TYPE_VIDEO = 'video'
    TYPE_QUIZ = 'quiz'
    TYPE_ASSESSMENT = 'assessment'
    TYPE_LIVE = 'live'
    TYPE_INTERACTIVE = 'interactive'
    TYPE_RESOURCES = 'resources'
    TYPE_CHOICES = [
        (TYPE_AUTO, 'Auto — detect from content'),
        (TYPE_READING, 'Reading'),
        (TYPE_VIDEO, 'Video'),
        (TYPE_QUIZ, 'Quiz'),
        (TYPE_ASSESSMENT, 'Assessment'),
        (TYPE_LIVE, 'Live session'),
        (TYPE_INTERACTIVE, 'Interactive'),
        (TYPE_RESOURCES, 'Resources'),
    ]

    # label · icon · bootstrap tone · unit shown after the number, per resolved type.
    TYPE_META = {
        TYPE_READING: ('Reading', 'bi-book', 'info', 'min read'),
        TYPE_VIDEO: ('Video', 'bi-play-btn', 'primary', 'min watch'),
        TYPE_QUIZ: ('Quiz', 'bi-ui-checks', 'warning', 'min quiz'),
        TYPE_ASSESSMENT: ('Assessment', 'bi-clipboard-check', 'danger', 'min'),
        TYPE_LIVE: ('Live class', 'bi-camera-video', 'success', 'min live'),
        TYPE_INTERACTIVE: ('Interactive', 'bi-boxes', 'primary', 'min'),
        TYPE_RESOURCES: ('Resources', 'bi-paperclip', 'secondary', 'min'),
    }

    # Words a learner reads per minute — used to estimate a reading section.
    WORDS_PER_MINUTE = 200

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='sections')
    order = models.PositiveIntegerField(default=0)
    title = models.CharField(max_length=200, default='New section')
    summary = models.CharField(max_length=300, blank=True,
                               help_text='One line shown under the title when the section is open.')
    section_type = models.CharField(max_length=12, choices=TYPE_CHOICES, default=TYPE_AUTO)
    # 0 = estimate from the content (reading speed / media length / quiz limit).
    duration_minutes = models.PositiveIntegerField(default=0, help_text='0 = estimate automatically.')

    is_required = models.BooleanField(default=True, help_text='Counts toward lesson completion.')
    requires_previous = models.BooleanField(
        default=False, help_text='Locked until every earlier required section is completed.')
    open_by_default = models.BooleanField(default=False)

    class Meta:
        # Order by the raw column only — ordering by the ``lesson`` FK follows
        # Lesson→Module→ProgrammeModule ordering into an infinite loop (see LessonBlock).
        ordering = ['order', 'id']
        indexes = [models.Index(fields=['lesson', 'order'])]

    def __str__(self):
        return f'{self.title} ({self.lesson_id})'

    # --- type ---------------------------------------------------------------
    @property
    def resolved_type(self):
        """The authored type, or the one inferred from the blocks inside."""
        if self.section_type != self.TYPE_AUTO:
            return self.section_type
        return self.infer_type()

    def infer_type(self):
        """Detect the section's kind from its blocks, most specific first."""
        types = {b.block_type for b in self.blocks.all()}
        if LessonBlock.TYPE_QUIZ in types:
            # A "quiz" block can point at a test/assignment — that reads as an
            # assessment to the learner, so let the linked object decide.
            kinds = {b.assessment.kind for b in self.blocks.all()
                     if b.block_type == LessonBlock.TYPE_QUIZ and b.assessment_id}
            if kinds - {'quiz'}:
                return self.TYPE_ASSESSMENT
            return self.TYPE_QUIZ
        if LessonBlock.TYPE_MEETING in types:
            return self.TYPE_LIVE
        if types & {LessonBlock.TYPE_VIDEO, LessonBlock.TYPE_AUDIO}:
            return self.TYPE_VIDEO
        if types and not (types - {LessonBlock.TYPE_FILE, LessonBlock.TYPE_IMAGE, LessonBlock.TYPE_DIVIDER}):
            return self.TYPE_RESOURCES
        return self.TYPE_READING

    @property
    def type_label(self):
        return self.TYPE_META.get(self.resolved_type, self.TYPE_META[self.TYPE_READING])[0]

    @property
    def type_icon(self):
        return self.TYPE_META.get(self.resolved_type, self.TYPE_META[self.TYPE_READING])[1]

    @property
    def type_tone(self):
        return self.TYPE_META.get(self.resolved_type, self.TYPE_META[self.TYPE_READING])[2]

    # --- duration -----------------------------------------------------------
    @property
    def minutes(self):
        """Authored duration, else an estimate from the content (never 0)."""
        if self.duration_minutes:
            return self.duration_minutes
        return max(1, self.estimate_minutes())

    def estimate_minutes(self):
        """Estimate how long this section takes: media length + quiz time limit
        + reading time for the prose."""
        total, words = 0, 0
        for block in self.blocks.all():
            data = block.data or {}
            if block.block_type in (LessonBlock.TYPE_VIDEO, LessonBlock.TYPE_AUDIO):
                # ``seconds`` is written by the editor once the media loads.
                total += int(round((data.get('seconds') or 0) / 60)) or 5
            elif block.block_type == LessonBlock.TYPE_QUIZ and block.assessment_id:
                total += block.assessment.time_limit_minutes or 10
            elif block.block_type == LessonBlock.TYPE_MEETING:
                total += int(data.get('duration') or 60)
            else:
                words += _count_words(block)
        return total + round(words / self.WORDS_PER_MINUTE)

    @property
    def duration_label(self):
        unit = self.TYPE_META.get(self.resolved_type, self.TYPE_META[self.TYPE_READING])[3]
        return f'{self.minutes} {unit}'

    # --- per-learner state --------------------------------------------------
    @property
    def assessments(self):
        """The assessments a learner must sit inside this section."""
        return [b.assessment for b in self.blocks.all()
                if b.block_type == LessonBlock.TYPE_QUIZ and b.assessment_id]

    def is_completed_by(self, student):
        """Quiz/assessment sections derive completion from real attempts so work
        done anywhere in the hub counts; everything else uses
        :class:`LessonSectionProgress`."""
        graded = self.assessments
        if graded:
            from apps.assessments.models import AssessmentAttempt
            return AssessmentAttempt.objects.filter(
                assessment__in=graded, student=student,
                status__in=('submitted', 'marked')).exists()
        progress = self.progress.filter(student=student).first()
        return bool(progress and progress.status == LessonSectionProgress.STATUS_COMPLETED)

    def best_attempt_for(self, student):
        """The learner's best attempt across this section's assessments."""
        graded = self.assessments
        if not graded:
            return None
        from apps.assessments.models import AssessmentAttempt
        return (AssessmentAttempt.objects
                .filter(assessment__in=graded, student=student,
                        status__in=('submitted', 'marked'))
                .select_related('assessment')
                .order_by('-score', '-created_at')
                .first())


def _count_words(block):
    """Rough word count of a block's text, HTML tags stripped."""
    import re
    data = block.data or {}
    parts = [data.get('html') or '', data.get('text') or '', data.get('caption') or '']
    for row in (data.get('rows') or []):
        parts.extend(str(c) for c in (row or []))
    text = re.sub(r'<[^>]+>', ' ', ' '.join(parts))
    return len([w for w in text.split() if w])


class LessonSectionProgress(TimeStampedModel):
    """Per-student completion + time-on-section for a :class:`LessonSection`."""

    STATUS_NOT_STARTED = 'not_started'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_COMPLETED = 'completed'
    STATUS_CHOICES = [
        (STATUS_NOT_STARTED, 'Not started'),
        (STATUS_IN_PROGRESS, 'In progress'),
        (STATUS_COMPLETED, 'Completed'),
    ]

    section = models.ForeignKey(LessonSection, on_delete=models.CASCADE, related_name='progress')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name='lesson_section_progress')
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=STATUS_NOT_STARTED)
    seconds_spent = models.PositiveIntegerField(default=0)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('section', 'student')

    def __str__(self):
        return f'{self.student} · {self.section} ({self.status})'


class LessonNote(TimeStampedModel):
    """A private note a student keeps against one section of a lesson.

    Notes are per-student and per-section — the right-hand rail always shows the
    note for whichever tear-drop is open, so a learner's thinking stays attached
    to the piece of content that prompted it."""

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='notes')
    section = models.ForeignKey(LessonSection, on_delete=models.CASCADE, null=True, blank=True,
                                related_name='notes')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name='lesson_notes')
    body = models.TextField(blank=True)

    class Meta:
        unique_together = ('lesson', 'section', 'student')
        ordering = ['-updated_at']

    def __str__(self):
        return f'Note · {self.student} · {self.section or self.lesson}'


class LessonBookmark(TimeStampedModel):
    """A place in a lesson a student saved to come back to.

    ``anchor`` locates the spot *within* the block: ``{"text": "…"}`` for a
    highlighted passage, ``{"seconds": 132.4}`` for a moment in a video/audio,
    ``{"question_id": 12}`` for a quiz question. The player uses it to scroll,
    seek or highlight when the bookmark is clicked.
    """

    KIND_SECTION = 'section'
    KIND_TEXT = 'text'
    KIND_MEDIA = 'media'
    KIND_QUESTION = 'question'
    KIND_CHOICES = [
        (KIND_SECTION, 'Section'),
        (KIND_TEXT, 'Passage'),
        (KIND_MEDIA, 'Moment in media'),
        (KIND_QUESTION, 'Question'),
    ]

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='bookmarks')
    section = models.ForeignKey(LessonSection, on_delete=models.CASCADE, null=True, blank=True,
                                related_name='bookmarks')
    block = models.ForeignKey('LessonBlock', on_delete=models.CASCADE, null=True, blank=True,
                              related_name='bookmarks')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name='lesson_bookmarks')
    kind = models.CharField(max_length=10, choices=KIND_CHOICES, default=KIND_TEXT)
    label = models.CharField(max_length=300, blank=True, help_text='What was saved (excerpt / timestamp).')
    note = models.CharField(max_length=500, blank=True)
    anchor = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['lesson', 'student'])]

    def __str__(self):
        return f'{self.get_kind_display()} · {self.label[:40]}'

    @property
    def icon(self):
        return {self.KIND_SECTION: 'bi-bookmark', self.KIND_TEXT: 'bi-quote',
                self.KIND_MEDIA: 'bi-play-circle', self.KIND_QUESTION: 'bi-patch-question'}.get(
                    self.kind, 'bi-bookmark')

    @property
    def timestamp_label(self):
        """``mm:ss`` for a media bookmark, else ''."""
        seconds = (self.anchor or {}).get('seconds')
        if seconds is None:
            return ''
        seconds = int(seconds)
        return f'{seconds // 60}:{seconds % 60:02d}'


class LessonBlock(TimeStampedModel):
    """One ordered content block of a :class:`Lesson` — the unit the block editor
    creates, reorders (drag-and-drop) and renders.

    A block is a typed piece of content. Simple blocks keep everything in the
    ``data`` JSON (text/heading/callout/reference/divider); media blocks also use
    the ``media`` FileField (uploaded image/video/audio/file) or a ``data['url']``
    (external/YouTube/Vimeo); interactive blocks link a real object —
    ``assessment`` (a quiz/test) or ``meeting`` (a live session). ``track``
    marks embed/video blocks whose viewing time is recorded.

    **The lesson is one continuous body.** Blocks with ``section = NULL`` are the
    main flow, in ``order``. A collapsible section is not a separate structure
    sitting underneath — it is a block of type ``section`` in that same flow,
    linked to its :class:`LessonSection` through :attr:`holds_section`; the blocks
    *inside* it are the ones whose ``section`` points back at it. So an author
    writes a lesson like a blog post and drops in a dropdown section wherever they
    want one, rather than being forced to structure everything into panels.

    Note the two section fields are deliberately different questions:

    * ``section``      — "which section does this block live **in**?" (NULL = top level)
    * ``holds_section`` — "is this block **itself** a section?" (NULL for ordinary blocks)

    :attr:`style` carries the author's per-block formatting (font, colour, size,
    alignment, width, spacing). It is whitelisted on both save and render by
    :mod:`apps.learning.styles`.
    """

    TYPE_HEADING = 'heading'
    TYPE_TEXT = 'text'
    TYPE_IMAGE = 'image'
    TYPE_VIDEO = 'video'
    TYPE_AUDIO = 'audio'
    TYPE_EMBED = 'embed'
    TYPE_FILE = 'file'
    TYPE_REFERENCE = 'reference'
    TYPE_QUIZ = 'quiz'
    TYPE_MEETING = 'meeting'
    TYPE_CALLOUT = 'callout'
    TYPE_TABLE = 'table'
    TYPE_DIAGRAM = 'diagram'
    TYPE_DIVIDER = 'divider'
    TYPE_SECTION = 'section'
    TYPE_CHOICES = [
        (TYPE_HEADING, 'Heading'),
        (TYPE_TEXT, 'Text'),
        (TYPE_IMAGE, 'Image'),
        (TYPE_VIDEO, 'Video'),
        (TYPE_AUDIO, 'Audio'),
        (TYPE_EMBED, 'Embedded page / link'),
        (TYPE_FILE, 'File / download'),
        (TYPE_REFERENCE, 'Reference'),
        (TYPE_QUIZ, 'Quiz / test'),
        (TYPE_MEETING, 'Live session'),
        (TYPE_CALLOUT, 'Callout'),
        (TYPE_TABLE, 'Table'),
        (TYPE_DIAGRAM, 'Diagram'),
        (TYPE_DIVIDER, 'Divider'),
        (TYPE_SECTION, 'Dropdown section'),
    ]
    # Types whose media is uploaded to the server (vs an external URL). A diagram
    # is a labelled image, so its base picture is an uploaded file too.
    UPLOAD_TYPES = {TYPE_IMAGE, TYPE_VIDEO, TYPE_AUDIO, TYPE_FILE, TYPE_DIAGRAM}
    # Blocks that carry prose the toolkit's type controls apply to.
    TEXTUAL_TYPES = {TYPE_HEADING, TYPE_TEXT, TYPE_CALLOUT, TYPE_REFERENCE, TYPE_TABLE}

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='blocks')
    # Which section this block lives *in*. Null = it sits in the lesson's main
    # body, which is where most blocks are.
    section = models.ForeignKey(LessonSection, on_delete=models.CASCADE, null=True, blank=True,
                                related_name='blocks')
    # Set only on a `section`-type block: the section this block *is*.
    #
    # The cascade here handles section → block (deleting a section removes the
    # element that showed it). The other direction — an author deleting the
    # element from the body — is handled by ``_delete_orphaned_section`` below,
    # because a foreign key cannot cascade from child to parent.
    holds_section = models.OneToOneField(LessonSection, on_delete=models.CASCADE, null=True, blank=True,
                                         related_name='anchor_block')
    order = models.PositiveIntegerField(default=0)
    block_type = models.CharField(max_length=12, choices=TYPE_CHOICES, default=TYPE_TEXT)
    data = models.JSONField(default=dict, blank=True)
    # Author's formatting for this block — see apps.learning.styles for the
    # whitelist. Never rendered raw.
    style = models.JSONField(default=dict, blank=True)

    media = models.FileField(upload_to='lessons/blocks/', blank=True, null=True, storage=files_storage,
                             validators=v.validate_media)
    assessment = models.ForeignKey('assessments.Assessment', on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='lesson_blocks')
    meeting = models.ForeignKey('communication.MeetingRoom', on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='lesson_blocks')
    # Time-on-content used to be reported to the LRS; the flag is kept because
    # the block editor still offers "track this block" and local progress reads it.
    track = models.BooleanField(default=False)

    class Meta:
        # Order by the raw column only — ordering by the ``lesson`` FK would follow
        # Lesson→Module→ProgrammeModule ordering into an infinite loop. Blocks are always
        # queried per-lesson, so ``order`` is the meaningful sort.
        ordering = ['order', 'id']
        indexes = [models.Index(fields=['lesson', 'order'])]

    def __str__(self):
        return f'{self.get_block_type_display()} #{self.order} · {self.lesson_id}'

    @property
    def media_url(self):
        """The best source URL for this block: uploaded file or external URL."""
        if self.media:
            try:
                return self.media.url
            except Exception:
                return ''
        return (self.data or {}).get('url', '')

    # --- section blocks -----------------------------------------------------
    @property
    def is_section(self):
        """True when this block *is* a collapsible section in the body."""
        return self.block_type == self.TYPE_SECTION and self.holds_section_id is not None

    @property
    def child_blocks(self):
        """The blocks inside this section block (empty for any other type)."""
        if not self.is_section:
            return self.__class__.objects.none()
        return self.holds_section.blocks.select_related(
            'assessment', 'meeting').order_by('order', 'id')

    # --- presentation -------------------------------------------------------
    @property
    def css(self):
        """This block's author styling as a safe inline ``style`` value."""
        from . import styles
        return styles.to_css(self.style or {})

    def to_dict(self):
        """Serialisable form the editor + player JS consume."""
        return {
            'id': self.pk,
            'type': self.block_type,
            'block_type': self.block_type,
            'section_id': self.section_id,
            'holds_section_id': self.holds_section_id,
            'order': self.order,
            'data': self.data or {},
            'style': self.style or {},
            'css': self.css,
            'media_url': self.media_url,
            'track': self.track,
            'assessment_id': self.assessment_id,
            'meeting_id': self.meeting_id,
        }

    # --- viewer helpers ---
    @property
    def embed_src(self):
        """A URL safe to drop into an <iframe> for embed/video blocks — YouTube &
        Vimeo watch links are normalised to their embeddable form."""
        url = (self.data or {}).get('url', '') or ''
        if not url:
            return ''
        import re
        m = re.search(r'(?:youtube\.com/(?:watch\?v=|embed/|shorts/)|youtu\.be/)([\w-]{11})', url)
        if m:
            return f'https://www.youtube.com/embed/{m.group(1)}'
        m = re.search(r'vimeo\.com/(?:video/)?(\d+)', url)
        if m:
            return f'https://player.vimeo.com/video/{m.group(1)}'
        return url

    @property
    def is_iframe_video(self):
        """Video block that should render as an iframe (YouTube/Vimeo) vs <video>."""
        return self.block_type == self.TYPE_VIDEO and (self.data or {}).get('provider') in ('youtube', 'vimeo')

    # --- media player (Plyr) -------------------------------------------------
    @property
    def player_provider(self):
        """``youtube`` / ``vimeo`` for an externally-hosted video, else ``''``.

        Detected from the URL rather than trusting ``data['provider']``, so a
        YouTube link pasted under "Direct URL" still plays in the real player.
        """
        url = (self.data or {}).get('url', '') or ''
        if not url:
            return ''
        import re
        if re.search(r'(?:youtube\.com|youtu\.be)', url):
            return 'youtube'
        if 'vimeo.com' in url:
            return 'vimeo'
        return ''

    @property
    def player_embed_id(self):
        """The provider's video id — what Plyr needs to build the player."""
        url = (self.data or {}).get('url', '') or ''
        if not url:
            return ''
        import re
        match = re.search(
            r'(?:youtube\.com/(?:watch\?v=|embed/|shorts/|live/)|youtu\.be/)([\w-]{11})', url)
        if match:
            return match.group(1)
        match = re.search(r'vimeo\.com/(?:video/)?(\d+)', url)
        if match:
            return match.group(1)
        return ''


@receiver(post_delete, sender=LessonBlock)
def _delete_orphaned_section(sender, instance, **kwargs):
    """Removing a section element from the body removes the section itself.

    A foreign key can only cascade parent → child, so ``holds_section`` takes
    care of "section deleted ⇒ its element goes". This is the other direction:
    an author deleting the element from the page means the section is gone, and
    a section with no element would linger invisibly — owning progress rows for
    something nobody can see. Works for ``queryset.delete()`` too, which never
    calls ``Model.delete()``.
    """
    if instance.holds_section_id:
        LessonSection.objects.filter(pk=instance.holds_section_id).delete()


class LessonResource(models.Model):
    """A file/link/embed attached to a lesson (PDF, video, YouTube, audio, …)."""

    KIND_CHOICES = [
        ('text', 'Text'), ('pdf', 'PDF'), ('word', 'Word'), ('ppt', 'PowerPoint'),
        ('image', 'Image'), ('audio', 'Audio'), ('video', 'Video'),
        ('youtube', 'YouTube'), ('link', 'External link'), ('embed', 'Embed'),
        ('download', 'Download'),
    ]

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='resources')
    kind = models.CharField(max_length=10, choices=KIND_CHOICES, default='pdf')
    title = models.CharField(max_length=200, blank=True)
    file = models.FileField(upload_to='lessons/', blank=True, null=True, storage=files_storage,
                            validators=v.validate_attachment)
    url = models.URLField(max_length=500, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        # Order by the raw ``lesson_id`` column, not the ``lesson`` relation —
        # following the FK pulls in Lesson→Module→ProgrammeModule→Course ordering and
        # Django raises "Infinite loop caused by ordering". Same grouping, no loop.
        ordering = ['lesson_id', 'order']

    def __str__(self):
        return self.title or f'{self.get_kind_display()} for {self.lesson}'


class LessonVersion(models.Model):
    """An immutable snapshot of a lesson's content — restore / reuse next year."""

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='versions')
    version = models.PositiveIntegerField(default=1)
    body = models.TextField(blank=True)
    resources_json = models.JSONField(default=list, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='lesson_versions')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # ``lesson_id`` not ``lesson`` — see LessonResource.Meta above.
        ordering = ['lesson_id', '-version']
        unique_together = ('lesson', 'version')

    def __str__(self):
        return f'{self.lesson} v{self.version}'


class StudySession(TimeStampedModel):
    """Measures actual studying of a lesson with a start/pause/resume/finish timer."""

    STATUS_NOT_STARTED = 'not_started'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_PAUSED = 'paused'
    STATUS_SUBMITTED = 'submitted'
    STATUS_COMPLETED = 'completed'
    STATUS_OVERDUE = 'overdue'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (STATUS_NOT_STARTED, 'Not started'),
        (STATUS_IN_PROGRESS, 'In progress'),
        (STATUS_PAUSED, 'Paused'),
        (STATUS_SUBMITTED, 'Submitted'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_OVERDUE, 'Overdue'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='study_sessions')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='study_sessions')

    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=STATUS_NOT_STARTED, db_index=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    last_resumed_at = models.DateTimeField(null=True, blank=True)
    total_seconds = models.PositiveIntegerField(default=0)
    completion_pct = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.student} · {self.lesson} ({self.get_status_display()})'

    @property
    def minutes(self):
        return round(self.total_seconds / 60, 1)

    def start(self):
        now = timezone.now()
        if self.start_time is None:
            self.start_time = now
        self.last_resumed_at = now
        self.status = self.STATUS_IN_PROGRESS
        self.save(update_fields=['start_time', 'last_resumed_at', 'status', 'updated_at'])

    def _accumulate(self):
        if self.last_resumed_at:
            self.total_seconds += int((timezone.now() - self.last_resumed_at).total_seconds())
            self.last_resumed_at = None

    def pause(self):
        self._accumulate()
        self.status = self.STATUS_PAUSED
        self.save(update_fields=['total_seconds', 'last_resumed_at', 'status', 'updated_at'])

    def finish(self, completion_pct=100):
        self._accumulate()
        self.end_time = timezone.now()
        self.completion_pct = min(100, max(0, completion_pct))
        self.status = self.STATUS_COMPLETED if self.completion_pct >= 100 else self.STATUS_SUBMITTED
        self.save()


# ---------------------------------------------------------------------------
# The module schedule — how a module is actually studied
#
# The spine above says *what* a student studies (Institution → Programme →
# offering → Topic) and the calendar says *when* the institution's dates fall.
# This says **how the work is organised between those dates**, which is how the
# practice already coaches: you do not study "Financial Reporting", you study
# *towards Test 2*, week by week, off a blueprint.
#
#     ProgrammeModule                     "UCS Grade 10 | MATH"
#       └── ModulePhase        ×6         "Test 1 preparation" … "Exam 2 preparation"
#             └── ModuleWeek   ×n         "Week 3 · Deferred tax"
#                   └── ModuleMaterial    blueprint · study guide · Q&A ·
#                                         live session · assessment · mock paper
#
# A phase also owns material directly (``week=None``) — a test preparation has
# its own blueprint that spans all of its weeks rather than belonging to one.
#
# ACCESS is deliberately two-sided, because the practice sells two ways:
#   * pay for the **module** (ModuleEnrolment active/trial) → everything in it;
#   * buy a **single item** from the shop (ModuleMaterial.product) → that item.
# Neither knows about the other; :mod:`apps.learning.access` resolves both.
# ---------------------------------------------------------------------------
class ModulePhase(TimeStampedModel):
    """One preparation block of an offering — "Test 2 preparation".

    Six per module by default (four tests, two exams), which is the shape of a
    CTA year. It is a *preparation* period, not the assessment itself: the
    assessment is a :class:`CalendarEvent` on the institution's calendar, and
    :attr:`calendar_event` points at it so the schedule can count down to the
    date the institution actually published.
    """

    KIND_TERM = 'term'
    KIND_TEST = 'test'
    KIND_EXAM = 'exam'
    KIND_SUPPLEMENTARY = 'supp'
    KIND_OTHER = 'other'
    KIND_CHOICES = [
        (KIND_TERM, 'School term'),
        (KIND_TEST, 'Test preparation'),
        (KIND_EXAM, 'Examination preparation'),
        (KIND_SUPPLEMENTARY, 'Supplementary / revision'),
        (KIND_OTHER, 'Other'),
    ]

    # The default subject year follows the GDE school calendar: Term 1 – 4,
    # each with its weeks (Term 2 ends with the mid-year exams, Term 4 with the
    # final exams). `scaffold_module_schedule` builds exactly this, and the
    # teacher edits from there.
    DEFAULT_PLAN = [(KIND_TERM, 1), (KIND_TERM, 2), (KIND_TERM, 3), (KIND_TERM, 4)]

    programme_module = models.ForeignKey(ProgrammeModule, on_delete=models.CASCADE,
                                         related_name='phases', verbose_name='Subject')
    # Per-cohort content: each intake (P25F, P26S …) can run its own schedule —
    # its own weeks, materials, blueprints, mocks and tests. Blank = a shared
    # template shown to every cohort; set = this cohort only. The weeks/materials
    # hang off the phase, so scoping the phase scopes the whole block.
    cohort = models.ForeignKey(
        'Cohort', on_delete=models.CASCADE, null=True, blank=True, related_name='module_phases',
        help_text='Which intake this block is for. Blank = shared by every cohort of the module.')
    kind = models.CharField(max_length=8, choices=KIND_CHOICES, default=KIND_TEST, db_index=True)
    sequence = models.PositiveSmallIntegerField(
        default=1, help_text='Which term (1–4), or which test/exam this prepares for.')
    title = models.CharField(max_length=160, blank=True,
                             help_text='Blank = built from kind + sequence ("Term 2").')
    summary = models.CharField(max_length=300, blank=True,
                               help_text='One line on what this block covers.')
    # The institution's own date for the assessment this block prepares for.
    calendar_event = models.ForeignKey(CalendarEvent, on_delete=models.SET_NULL, null=True, blank=True,
                                       related_name='prep_phases',
                                       help_text='The test/exam on the academic calendar this prepares for.')
    starts_on = models.DateField(null=True, blank=True)
    ends_on = models.DateField(null=True, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True,
                                       help_text='Unpublished blocks are visible to staff only.')
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['programme_module', 'order', 'id']
        constraints = [
            models.UniqueConstraint(fields=['programme_module', 'kind', 'sequence'],
                                    name='uniq_phase_per_module'),
        ]
        verbose_name = 'Subject term / block'

    def __str__(self):
        return f'{self.programme_module.label} | {self.display_title}'

    def save(self, *args, **kwargs):
        if not self.title:
            self.title = self.build_title(self.kind, self.sequence)
        super().save(*args, **kwargs)

    @staticmethod
    def build_title(kind, sequence):
        """``Term 2`` / ``Test 2 preparation`` / ``Exam 1 preparation``."""
        if kind == ModulePhase.KIND_TERM:
            return f'Term {sequence}'
        noun = {ModulePhase.KIND_TEST: 'Test', ModulePhase.KIND_EXAM: 'Exam',
                ModulePhase.KIND_SUPPLEMENTARY: 'Supplementary'}.get(kind, 'Block')
        return f'{noun} {sequence} preparation'

    @property
    def display_title(self):
        return self.title or self.build_title(self.kind, self.sequence)

    @property
    def short_label(self):
        """``Test 2`` — for chips and countdowns, where "preparation" is noise."""
        noun = {self.KIND_TERM: 'Term', self.KIND_TEST: 'Test', self.KIND_EXAM: 'Exam',
                self.KIND_SUPPLEMENTARY: 'Supp'}.get(self.kind, 'Block')
        return f'{noun} {self.sequence}'

    @property
    def tone(self):
        """Bootstrap-ish tone used by the chips on the schedule."""
        return {self.KIND_TEST: 'info', self.KIND_EXAM: 'danger',
                self.KIND_SUPPLEMENTARY: 'warning'}.get(self.kind, 'secondary')

    @property
    def assessment_date(self):
        """The date being prepared for, from the calendar event or ``ends_on``."""
        if self.calendar_event_id:
            return self.calendar_event.start.date()
        return self.ends_on

    @property
    def days_away(self):
        """Whole days until the assessment; negative once it has passed, None if undated."""
        target = self.assessment_date
        return None if target is None else (target - timezone.now().date()).days

    @property
    def is_current(self):
        """True while today falls inside the preparation window."""
        today = timezone.now().date()
        if self.starts_on and today < self.starts_on:
            return False
        end = self.ends_on or self.assessment_date
        if end and today > end:
            return False
        return bool(self.starts_on or end)


class ModuleWeek(TimeStampedModel):
    """One week inside a preparation phase — the "tear-drop" on the schedule.

    A week works through a *series* of topics off the study guide (deferred tax,
    then leases, …). :attr:`topics` is that ordered series — each an offering-owned
    :class:`Topic`, linked through :class:`WeekTopic` so the order is explicit and
    a topic can carry its own materials for the week. Weeks that are revision,
    consolidation or a mock sitting simply have no topics.
    """

    phase = models.ForeignKey(ModulePhase, on_delete=models.CASCADE, related_name='weeks')
    number = models.PositiveSmallIntegerField(default=1, help_text='Week number within this phase.')
    title = models.CharField(max_length=200, blank=True,
                             help_text="Blank = the topics' names, else \"Week n\".")
    topics = models.ManyToManyField('Topic', through='WeekTopic', related_name='in_weeks',
                                    blank=True,
                                    help_text='The study-guide topics covered this week, in order.')
    summary = models.TextField(blank=True)
    starts_on = models.DateField(null=True, blank=True)
    ends_on = models.DateField(null=True, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['phase', 'order', 'number', 'id']
        constraints = [
            models.UniqueConstraint(fields=['phase', 'number'], name='uniq_week_per_phase'),
        ]
        verbose_name = 'Subject week'

    def __str__(self):
        return f'{self.phase.display_title} · {self.display_title}'

    @property
    def topic_list(self):
        """The week's topics in order (uses the WeekTopic through, prefetch-friendly)."""
        return [wt.topic for wt in self.week_topics.all()]

    @property
    def primary_topic(self):
        """The first topic of the series, or None (revision/mock weeks have none)."""
        topics = self.topic_list
        return topics[0] if topics else None

    @property
    def display_title(self):
        if self.title:
            return self.title
        topics = self.topic_list
        if topics:
            return f'Week {self.number} · ' + ', '.join(t.title for t in topics)
        return f'Week {self.number}'

    @property
    def reference(self):
        """The authority behind the week's first topic — ``IAS 12`` — or blank."""
        return getattr(self.primary_topic, 'reference', '')

    @property
    def is_current(self):
        today = timezone.now().date()
        if self.starts_on and self.ends_on:
            return self.starts_on <= today <= self.ends_on
        return False


class WeekTopic(TimeStampedModel):
    """One topic taught in one week — the ordered series a week works through.

    A week used to point at a single :class:`Topic`; now it covers a *series*
    (deferred tax → leases → …), each carrying its own materials for that week.
    :class:`Topic` stays owned by the offering and shared across cohorts by
    ``code``; this row is only *which* topics a given week works through, and in
    what order. Deleting either side removes the link, never the topic itself.
    """

    week = models.ForeignKey(ModuleWeek, on_delete=models.CASCADE, related_name='week_topics')
    topic = models.ForeignKey('Topic', on_delete=models.CASCADE, related_name='week_links')
    order = models.PositiveSmallIntegerField(default=0, help_text='Order of this topic within the week.')

    class Meta:
        ordering = ['week', 'order', 'id']
        constraints = [
            models.UniqueConstraint(fields=['week', 'topic'], name='uniq_topic_per_week'),
        ]
        verbose_name = 'Week topic'

    def __str__(self):
        return f'{self.week.display_title} · {self.topic.code}'


class ModuleMaterial(TimeStampedModel):
    """One studiable thing — the row a student actually clicks.

    Hangs off a :class:`ModuleWeek`, or off the :class:`ModulePhase` directly
    when it spans the whole block (``week=None``) — which is how a test
    preparation carries "its own blueprint".

    What it *is* comes from :attr:`kind`; what it *points at* is whichever link
    is filled in — an uploaded file, a :class:`Lesson`, an
    ``assessments.Assessment``, a live :class:`~apps.communication.models.MeetingRoom`,
    or an external URL. One row, many shapes, so the schedule renders uniformly
    and the tabs (Blueprints / Documents / Mock exams / …) are just filters.

    :attr:`product` is the standalone purchase route: an educator publishes a
    blueprint or a mock paper to the shop, and someone who has not paid for the
    module can buy that item alone. Students who *have* paid for the module get
    it without buying anything — see :mod:`apps.learning.access`.
    """

    KIND_BLUEPRINT = 'blueprint'
    KIND_STUDY_GUIDE = 'study_guide'
    KIND_QUESTIONS = 'questions'
    KIND_ANSWERS = 'answers'
    KIND_MOCK_EXAM = 'mock_exam'
    KIND_ASSESSMENT = 'assessment'
    KIND_LIVE = 'live'
    KIND_RECORDING = 'recording'
    KIND_DOCUMENT = 'document'
    KIND_CHOICES = [
        (KIND_BLUEPRINT, 'Assessment guide'),
        (KIND_STUDY_GUIDE, 'Topic study guide'),
        (KIND_QUESTIONS, 'Questions'),
        (KIND_ANSWERS, 'Answers / solutions'),
        (KIND_MOCK_EXAM, 'Practice exam / past paper'),
        (KIND_ASSESSMENT, 'Assessment'),
        (KIND_LIVE, 'Live session'),
        (KIND_RECORDING, 'Recording'),
        (KIND_DOCUMENT, 'Document'),
    ]

    # Icon + tone per kind, so the schedule, the Documents tab and the shop card
    # all label an item the same way.
    KIND_ICONS = {
        KIND_BLUEPRINT: 'bi-diagram-3',
        KIND_STUDY_GUIDE: 'bi-journal-richtext',
        KIND_QUESTIONS: 'bi-patch-question',
        KIND_ANSWERS: 'bi-check2-square',
        KIND_MOCK_EXAM: 'bi-file-earmark-ruled',
        KIND_ASSESSMENT: 'bi-ui-checks',
        KIND_LIVE: 'bi-camera-video',
        KIND_RECORDING: 'bi-play-btn',
        KIND_DOCUMENT: 'bi-file-earmark-text',
    }
    KIND_TONES = {
        KIND_BLUEPRINT: 'primary',
        KIND_STUDY_GUIDE: 'info',
        KIND_QUESTIONS: 'warning',
        KIND_ANSWERS: 'success',
        KIND_MOCK_EXAM: 'danger',
        KIND_ASSESSMENT: 'warning',
        KIND_LIVE: 'success',
        KIND_RECORDING: 'secondary',
        KIND_DOCUMENT: 'secondary',
    }

    phase = models.ForeignKey(ModulePhase, on_delete=models.CASCADE, related_name='materials')
    week = models.ForeignKey(ModuleWeek, on_delete=models.CASCADE, null=True, blank=True,
                             related_name='materials',
                             help_text='Leave blank for material that covers the whole phase '
                                       '(e.g. the test blueprint).')
    topic = models.ForeignKey('Topic', on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='materials',
                              help_text='Which topic within the week this material belongs to. '
                                        'Blank = it covers the whole week/phase, not one topic.')
    kind = models.CharField(max_length=12, choices=KIND_CHOICES, default=KIND_DOCUMENT, db_index=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # --- What it points at. Exactly one is normally set. ---
    file = models.FileField(upload_to='modules/materials/', blank=True, null=True,
                            storage=files_storage, validators=v.validate_attachment)
    lesson = models.ForeignKey('Lesson', on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='module_materials')
    assessment = models.ForeignKey('assessments.Assessment', on_delete=models.SET_NULL,
                                   null=True, blank=True, related_name='module_materials')
    meeting = models.ForeignKey('communication.MeetingRoom', on_delete=models.SET_NULL,
                                null=True, blank=True, related_name='module_materials')
    url = models.URLField(max_length=500, blank=True)

    # --- Shop ---
    product = models.ForeignKey('shop.Product', on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='module_materials',
                                help_text='Set when this item is also sold on its own in the shop.')

    # --- Availability ---
    available_from = models.DateTimeField(null=True, blank=True,
                                          help_text='Hidden from students until this moment.')
    is_published = models.BooleanField(default=True)
    is_preview = models.BooleanField(default=False,
                                     help_text='Open to everyone, even on a locked module — the taster.')
    order = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                   null=True, blank=True, related_name='+')
    # Where this came from, when a content pack placed it rather than a person.
    # Lets a re-import correct the same row instead of stacking a second copy.
    source_ref = models.CharField(max_length=140, blank=True, db_index=True,
                                  help_text='Stable key from the content pack that placed this.')

    class Meta:
        ordering = ['phase', 'week', 'order', 'id']
        indexes = [
            models.Index(fields=['phase', 'kind'], name='learning_material_phase_kind'),
        ]
        verbose_name = 'Subject material'

    def __str__(self):
        return f'{self.get_kind_display()} · {self.title}'

    @property
    def icon(self):
        return self.KIND_ICONS.get(self.kind, 'bi-file-earmark')

    @property
    def tone(self):
        return self.KIND_TONES.get(self.kind, 'secondary')

    @property
    def programme_module(self):
        return self.phase.programme_module

    @property
    def is_released(self):
        """False while an embargo (``available_from``) is still in the future."""
        return not (self.available_from and self.available_from > timezone.now())

    @property
    def target_url(self):
        """Where clicking it goes — resolved in the order the links are ranked."""
        from django.urls import reverse
        if self.lesson_id:
            return reverse('learning:lesson-view', args=[self.lesson_id])
        if self.assessment_id:
            return reverse('assessments:take', args=[self.assessment_id])
        if self.meeting_id:
            return self.meeting.get_join_url()
        if self.file:
            try:
                return self.file.url
            except Exception:      # storage not configured / file missing
                return ''
        return self.url or ''

    @property
    def is_purchasable(self):
        """True when it is listed in the shop on its own."""
        return bool(self.product_id and getattr(self.product, 'status', '') == 'active')
