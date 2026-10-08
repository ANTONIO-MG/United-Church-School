"""United Church School's academic spine, asserted.

These tests are the check that the seeded spine still says what the school's
own documents say (www.ucs.org.za and the UCS Application Form 2026, via
``core/school.py``): one school, Grade 1 to Grade 12 in their CAPS phases with
the 2026 fee schedule, the subjects offered in each grade with the Grade
10 – 12 choice rules, a class per grade, and the published term dates.

They also assert the properties the structure exists to guarantee:

* every grade's offering owns its topics, so editing Grade 10 Mathematics
  leaves Grade 11's untouched — while the shared topic **code** still reports
  them together; and
* a subject in a fee-paying grade is locked until the learner's fees are paid.
"""
from decimal import Decimal

from django.core.management import call_command
from django.db.utils import IntegrityError
from django.test import TestCase

from apps.learning.models import (
    DEPTH_ADVANCED, DEPTH_FOUNDATIONAL,
    AcademicCalendar, CalendarEvent, Cohort, Institution, Lesson, Module, ModuleEnrolment,
    Programme, ProgrammeModule, Topic,
)
from core import academic_spine, school

ADV, FND = DEPTH_ADVANCED, DEPTH_FOUNDATIONAL


def grade(n):
    return Programme.objects.get(institution__code='UCS', code=school.grade_code(n))


def subject_codes(n, group=None):
    qs = grade(n).modules.order_by('order')
    if group is not None:
        qs = qs.filter(subject_group=group)
    return list(qs.values_list('code', flat=True))


class SchoolSeedTests(TestCase):
    """What ``manage.py seed_school_structure`` builds."""

    @classmethod
    def setUpTestData(cls):
        call_command('seed_school_structure', verbosity=0)

    def test_there_is_exactly_one_school(self):
        self.assertEqual(list(Institution.objects.values_list('code', 'name')),
                         [('UCS', 'United Church School')])
        self.assertEqual(Institution.objects.get().accent_colour, '#00498B')

    def test_the_school_carries_its_crest(self):
        self.assertTrue(Institution.objects.get().logo)

    def test_grade_1_to_12_exist_in_order(self):
        programmes = Programme.objects.order_by('grade')
        self.assertEqual([p.grade for p in programmes], list(range(1, 13)))
        self.assertEqual(programmes.first().full_code, 'UCS-GR01')
        self.assertEqual(programmes.first().display_name, 'Grade 1')
        self.assertEqual(str(programmes.last()), 'UCS · Grade 12')

    def test_each_grade_sits_in_its_caps_phase(self):
        expected = {1: Programme.LEVEL_FOUNDATION, 3: Programme.LEVEL_FOUNDATION,
                    4: Programme.LEVEL_INTERMEDIATE, 6: Programme.LEVEL_INTERMEDIATE,
                    7: Programme.LEVEL_SENIOR, 9: Programme.LEVEL_SENIOR,
                    10: Programme.LEVEL_FET, 12: Programme.LEVEL_FET}
        for n, level in expected.items():
            self.assertEqual(grade(n).level, level, n)

    def test_the_2026_fee_schedule(self):
        """United Church School Fees 2026, band by band."""
        expected = {
            1: ('550', '1900', '1200', '16300'), 3: ('550', '1900', '1200', '16300'),
            4: ('550', '1900', '1250', '16900'), 6: ('550', '1900', '1250', '16900'),
            7: ('550', '2200', '1800', '23800'), 10: ('550', '2200', '1800', '23800'),
            11: ('550', '2200', '2200', '28600'),
            12: ('0', '2200', '2750', '35200'),
        }
        for n, (registration, levy, monthly, annual) in expected.items():
            g = grade(n)
            self.assertEqual(g.registration_fee, Decimal(registration), n)
            self.assertEqual(g.annual_levy, Decimal(levy), n)
            self.assertEqual(g.monthly_fee, Decimal(monthly), n)
            self.assertEqual(g.annual_fees, Decimal(annual), n)

    def test_the_new_learner_totals(self):
        self.assertEqual(grade(1).annual_fees_new_learner, Decimal('16850'))
        self.assertEqual(grade(5).annual_fees_new_learner, Decimal('17450'))
        self.assertEqual(grade(8).annual_fees_new_learner, Decimal('24350'))

    def test_foundation_phase_subjects(self):
        self.assertEqual(subject_codes(1), ['ENG-HL', 'ZUL-FAL', 'MATH', 'LIFE-SK', 'CODING'])

    def test_intermediate_phase_adds_the_sciences(self):
        self.assertEqual(subject_codes(5), ['ENG-HL', 'ZUL-FAL', 'MATH', 'NST', 'SOC-SCI',
                                            'LIFE-SK', 'CODING'])

    def test_coding_is_taught_in_grade_7_only_in_the_senior_phase(self):
        self.assertIn('CODING', subject_codes(7))
        self.assertNotIn('CODING', subject_codes(8))
        self.assertNotIn('CODING', subject_codes(9))
        for code in ('EMS', 'TECH', 'CREATIVE-ARTS', 'NAT-SCI', 'LO'):
            self.assertIn(code, subject_codes(8))

    def test_fet_subject_choices(self):
        for n in (10, 11, 12):
            self.assertEqual(subject_codes(n, ''), ['ENG-HL', 'LO'])
            self.assertEqual(subject_codes(n, 'fal'), ['AFR-FAL', 'ZUL-FAL'])
            self.assertEqual(subject_codes(n, 'maths'), ['MATH', 'MLIT'])
            self.assertEqual(sorted(subject_codes(n, 'elective')),
                             sorted(['PHYS-SCI', 'LIFE-SCI', 'HIST', 'GEOG', 'ACC',
                                     'BUS-STUD', 'ECON']))

    def test_below_grade_10_every_subject_is_compulsory(self):
        self.assertFalse(ProgrammeModule.objects.filter(programme__grade__lt=10)
                         .exclude(subject_group='').exists())

    def test_mathematics_is_one_canonical_subject_across_grades(self):
        maths = Module.objects.get(code='MATH')
        self.assertEqual(maths.offerings.count(), 12)

    def test_subjects_carry_no_price_of_their_own(self):
        self.assertFalse(ProgrammeModule.objects.exclude(price_per_month=0).exists())

    def test_subjects_in_a_fee_paying_grade_are_not_free(self):
        self.assertFalse(grade(4).modules.first().is_free)

    def test_every_grade_has_its_class_for_the_year(self):
        for programme in Programme.objects.all():
            cohort = programme.cohorts.get(code=str(school.YEAR))
            self.assertEqual(cohort.name, f'{programme.display_name} · {school.YEAR}')

    def test_the_term_dates_are_published(self):
        calendar = AcademicCalendar.objects.get(year=school.YEAR)
        term1 = calendar.events.get(title='Term 1 begins')
        self.assertTrue(term1.is_published)
        self.assertEqual((term1.start.month, term1.start.day), (1, 14))
        term4 = calendar.events.get(title='Term 4 ends')
        self.assertEqual((term4.start.month, term4.start.day), (12, 11))

    def test_exam_windows_are_unpublished_templates(self):
        exams = CalendarEvent.objects.filter(kind=CalendarEvent.KIND_EXAM)
        self.assertTrue(exams.exists())
        self.assertFalse(exams.filter(is_published=True).exists())
        self.assertTrue(exams.filter(programme__grade=12, title__startswith='NSC').exists())
        self.assertFalse(exams.filter(programme__grade__lte=3).exists())

    def test_seeding_twice_changes_nothing(self):
        counts = (Programme.objects.count(), ProgrammeModule.objects.count(),
                  Cohort.objects.count(), CalendarEvent.objects.count())
        call_command('seed_school_structure', verbosity=0)
        self.assertEqual(counts, (Programme.objects.count(), ProgrammeModule.objects.count(),
                                  Cohort.objects.count(), CalendarEvent.objects.count()))

    def test_an_admin_edit_survives_a_reseed_unless_update_is_asked_for(self):
        g = grade(3)
        g.monthly_fee = Decimal('1300')
        g.save()
        call_command('seed_school_structure', verbosity=0)
        self.assertEqual(grade(3).monthly_fee, Decimal('1300'))
        call_command('seed_school_structure', '--update', verbosity=0)
        self.assertEqual(grade(3).monthly_fee, Decimal('1200'))

    def test_the_lms_naming_convention_reads_correctly(self):
        offering = grade(10).modules.get(code='MATH')
        self.assertEqual(offering.reference, 'UCS-GR10 / MATH')
        self.assertEqual(offering.label, 'UCS Grade 10 | MATH')


class EnrolmentOnTheSpineTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        academic_spine.seed(verbose=False, calendar=False)

    def _person(self, email):
        from django.contrib.auth import get_user_model
        user = get_user_model().objects.create_user(username=email, email=email, password='x')
        return user.profile

    def test_a_grade_10_learner_gets_the_compulsory_subjects_and_one_per_choice(self):
        person = self._person('g10@example.com')
        _enrolment, rows = academic_spine.enrol_student(person, grade(10), activate=False)
        codes = sorted(r.programme_module.code for r in rows)
        self.assertEqual(len(codes), 7)                       # CAPS: seven subjects
        self.assertIn('ENG-HL', codes)
        self.assertIn('LO', codes)
        self.assertEqual(person.enrolled_class, 'Grade 10')

    def test_a_locked_subject_raises_the_months_school_fees(self):
        from apps.learning import enrolment as enrol
        person = self._person('g4@example.com')
        _enrolment, rows = academic_spine.enrol_student(person, grade(4), activate=False)
        self.assertFalse(rows[0].programme_module.is_unlocked_for(person))
        _row, invoice = enrol.unlock_single_module(person, rows[0].programme_module)
        self.assertEqual(invoice.total, Decimal('1250.00'))
        # One invoice covers every subject in the grade, and asking again reuses it.
        self.assertEqual(ModuleEnrolment.objects.filter(invoice_uid=invoice.public_id).count(),
                         len(rows))
        _row, again = enrol.unlock_single_module(person, rows[-1].programme_module)
        self.assertEqual(again.pk, invoice.pk)

    def test_learners_are_spread_across_all_twelve_grades(self):
        people = [self._person(f'l{i}@example.com') for i in range(24)]
        pairs = academic_spine.allocate_students(people)
        self.assertEqual(len(pairs), 24)
        self.assertEqual({programme.grade for _person, programme in pairs}, set(range(1, 13)))

    def test_the_school_blueprint_builds_the_grades_under_a_new_school(self):
        other = Institution.objects.create(code='SCH2', name='Second Campus')
        result = academic_spine.apply_blueprint(other, 'school', calendar=False)
        self.assertEqual(len(result['programmes']), 12)
        self.assertEqual(other.programmes.get(code='GR12').monthly_fee, Decimal('2750'))


class SpineIntegrityTests(TestCase):
    """The constraints that stop the structure drifting."""

    @classmethod
    def setUpTestData(cls):
        cls.institution = Institution.objects.create(code='TEST', name='Test School')
        cls.programme = Programme.objects.create(
            institution=cls.institution, code='GR05', name='Grade 5', grade=5, depth_default=ADV)
        cls.module = Module.objects.create(code='XX', name='Test Subject')
        cls.offering = ProgrammeModule.objects.create(
            programme=cls.programme, module=cls.module, code='XXX')
        cls.topic = Topic.objects.create(
            programme_module=cls.offering, code='XX-01', title='A topic')

    def test_a_grade_code_is_unique_within_its_school(self):
        with self.assertRaises(IntegrityError):
            Programme.objects.create(institution=self.institution, code='GR05', name='Duplicate')

    def test_the_same_grade_code_may_be_reused_at_another_school(self):
        other = Institution.objects.create(code='OTHER', name='Other School')
        programme = Programme.objects.create(institution=other, code='GR05', name='Grade 5')
        self.assertEqual(programme.full_code, 'OTHER-GR05')

    def test_a_subject_code_is_unique_within_its_grade(self):
        with self.assertRaises(IntegrityError):
            ProgrammeModule.objects.create(
                programme=self.programme, module=self.module, code='XXX')

    def test_a_topic_code_is_unique_within_its_offering(self):
        with self.assertRaises(IntegrityError):
            Topic.objects.create(programme_module=self.offering, code='XX-01', title='Duplicate')

    def test_the_same_topic_code_may_be_reused_on_another_offering(self):
        other = ProgrammeModule.objects.create(
            programme=self.programme, module=self.module, code='YYY')
        topic = Topic.objects.create(programme_module=other, code='XX-01', title='A topic')
        self.assertEqual(str(topic), 'TEST-GR05 / YYY / XX-01')

    def test_depth_falls_through_from_the_grade_when_not_set(self):
        self.assertEqual(self.offering.resolved_depth, ADV)
        self.assertEqual(self.topic.resolved_depth, ADV)

    def test_an_offering_may_override_the_grades_depth(self):
        self.offering.depth_level = FND
        self.offering.save()
        topic = Topic.objects.create(programme_module=self.offering, code='XX-02', title='Another')
        self.assertEqual(topic.resolved_depth, FND)

    def test_deleting_an_offering_takes_its_topics_with_it(self):
        offering = ProgrammeModule.objects.create(
            programme=self.programme, module=self.module, code='ZZZ')
        Topic.objects.create(programme_module=offering, code='XX-09', title='Doomed')
        offering.delete()
        self.assertFalse(Topic.objects.filter(code='XX-09').exists())

    def test_a_grade_with_no_fees_leaves_its_subjects_open(self):
        self.assertTrue(self.offering.is_free)


class TopicContentTests(TestCase):
    """Content hangs off a topic, and a topic belongs to one offering — so
    Grade 10 Mathematics' material is not Grade 11's."""

    @classmethod
    def setUpTestData(cls):
        academic_spine.seed(verbose=False, calendar=False)
        cls.g10 = Topic.objects.create(programme_module=grade(10).modules.get(code='MATH'),
                                       code='MATH-ALG', title='Algebraic expressions')
        cls.g11 = Topic.objects.create(programme_module=grade(11).modules.get(code='MATH'),
                                       code='MATH-ALG', title='Algebraic expressions')

    def test_a_lesson_knows_its_whole_path_up_the_spine(self):
        lesson = Lesson.objects.create(topic=self.g10, title='Factorising trinomials')
        self.assertEqual(lesson.institution.code, 'UCS')
        self.assertEqual(lesson.programme.full_code, 'UCS-GR10')
        self.assertEqual(lesson.programme_module.code, 'MATH')
        self.assertEqual(lesson.topic.code, 'MATH-ALG')

    def test_two_grades_teach_the_same_topic_with_different_content(self):
        Lesson.objects.create(topic=self.g10, title='Grade 10 algebra')
        Lesson.objects.create(topic=self.g11, title='Grade 11 algebra')
        self.assertEqual(self.g10.code, self.g11.code)
        self.assertNotEqual(self.g10.pk, self.g11.pk)
        self.assertEqual([lesson.title for lesson in self.g10.lessons.all()], ['Grade 10 algebra'])
        self.assertEqual([lesson.title for lesson in self.g11.lessons.all()], ['Grade 11 algebra'])

    def test_a_topic_holds_its_own_lessons(self):
        Lesson.objects.create(topic=self.g10, title='Notes', status=Lesson.STATUS_PUBLISHED)
        Lesson.objects.create(topic=self.g10, title='Practice', status=Lesson.STATUS_DRAFT)
        published = self.g10.lessons.filter(status=Lesson.STATUS_PUBLISHED)
        self.assertEqual([lesson.title for lesson in published], ['Notes'])
        self.assertEqual(self.g10.lessons.count(), 2)
