"""Year-end promotion → pre-registration → confirmation → the new school year."""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.learning.models import ModuleEnrolment, Programme, ProgrammeEnrolment
from apps.reports.models import Grade
from core import academic_spine

from . import promotion
from .models import Application, Guardian, PromotionDecision

User = get_user_model()


def person(email, kind='student'):
    user = User.objects.create_user(username=email, email=email, password='x-Pass-1234')
    p = user.profile
    p.user_type, p.registered, p.profile_status = kind, True, True
    p.first_name = email.split('@')[0].title()
    p.save()
    return p


def grade(n):
    return Programme.objects.get(institution__code='UCS', grade=n)


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class PromotionTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        academic_spine.seed(verbose=False, calendar=False)

    def setUp(self):
        self.g5 = grade(5)
        self.cohort = promotion.class_for(self.g5, 2026)
        self.teacher = person('teacher@example.com', 'educator')
        self.cohort.class_teacher = self.teacher
        self.cohort.save()
        self.office = person('office@example.com', 'staff')
        self.passer = self.learner('pass@example.com', {'ENG-HL': 62, 'ZUL-FAL': 48, 'MATH': 55,
                                                         'NST': 40, 'SOC-SCI': 35})
        self.failer = self.learner('fail@example.com', {'ENG-HL': 44, 'ZUL-FAL': 48, 'MATH': 55,
                                                         'NST': 40, 'SOC-SCI': 35})

    def learner(self, email, marks):
        learner = person(email)
        academic_spine.enrol_student(learner, self.g5, cohort=self.cohort, activate=False)
        app = Application.objects.create(person=learner, year=2026, programme=self.g5,
                                         status=Application.STATUS_ADMITTED, home_language='isiZulu')
        Guardian.objects.create(application=app, role='mother', full_name=f'Mother of {email}',
                                cell_phone='082 000 0000')
        for code, pct in marks.items():
            Grade.objects.create(student=learner.user, module=self.g5.modules.get(code=code),
                                 final_pct=Decimal(pct))
        return learner

    def test_the_caps_rule_recommends_an_outcome(self):
        decisions = {d.person_id: d for d in promotion.build_decisions(self.g5, 2026)}
        self.assertEqual(decisions[self.passer.pk].recommended, 'promote')
        self.assertEqual(decisions[self.failer.pk].recommended, 'retain')   # Home Language < 50%

    def test_the_class_teacher_decides_and_learners_are_preregistered(self):
        self.client.force_login(self.teacher.user)
        url = reverse('admissions:promotion-class', args=[self.g5.pk, 2026])
        self.assertContains(self.client.get(url), 'Home Language')
        d_pass = PromotionDecision.objects.get(person=self.passer)
        d_fail = PromotionDecision.objects.get(person=self.failer)
        self.client.post(url, {f'outcome_{d_pass.pk}': 'promote', f'outcome_{d_fail.pk}': 'retain'})
        nxt = Application.objects.get(person=self.passer, year=2027)
        self.assertEqual((nxt.programme.grade, nxt.status, nxt.is_new_learner), (6, 'preregistered', False))
        self.assertEqual(nxt.home_language, 'isiZulu')                         # details carried over
        self.assertTrue(nxt.guardians.filter(role='mother').exists())           # parents carried over
        self.assertEqual(Application.objects.get(person=self.failer, year=2027).programme.grade, 5)

    def test_another_teacher_cannot_decide(self):
        other = person('other@example.com', 'educator')
        self.client.force_login(other.user)
        url = reverse('admissions:promotion-class', args=[self.g5.pk, 2026])
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_confirming_and_starting_the_new_year(self):
        promotion.build_decisions(self.g5, 2026)
        promotion.decide(PromotionDecision.objects.get(person=self.passer), 'promote', self.teacher.user)
        app = Application.objects.get(person=self.passer, year=2027)
        invoice = promotion.confirm_returning(app, self.office.user)
        app.refresh_from_db()
        self.assertEqual(app.status, 'admitted')
        self.assertEqual(invoice.total, Decimal('3150.00'))   # Grade 6: levy R1 900 + January R1 250
        self.assertEqual(invoice.fee_start.isoformat(), '2027-01-01')
        self.assertEqual(promotion.start_school_year(2027), 1)
        active = ProgrammeEnrolment.objects.get(person=self.passer, is_active=True)
        self.assertEqual((active.programme.grade, active.cohort.code), (6, '2027'))
        self.assertFalse(ProgrammeEnrolment.objects.filter(person=self.passer, programme=self.g5,
                                                           is_active=True).exists())
        self.assertTrue(ModuleEnrolment.objects.filter(person=self.passer,
                                                       programme_module__programme__grade=6).exists())

    def test_the_office_pages(self):
        self.client.force_login(self.office.user)
        self.assertEqual(self.client.get(reverse('admissions:promotion') + '?year=2026').status_code, 200)
        self.assertEqual(self.client.get(reverse('admissions:new-year') + '?year=2027').status_code, 200)
