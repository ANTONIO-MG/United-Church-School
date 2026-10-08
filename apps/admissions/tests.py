"""The online application for admission, end to end.

A family walks the five-step wizard exactly as they would in a browser —
learner, grade & subjects, family, medical & documents, agreements & fees —
and the tests assert what the UCS Application Form 2026 promises: the fees due
on enrolment (registration for new learners, levy, first month), the Grade
10 – 12 subject rules, "pending until payment is received", parents invited to
linked accounts, documents served only to the family and the office, and the
office checklist and decision.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.finance.models import Invoice
from apps.learning.models import ModuleEnrolment, Programme
from core import academic_spine

from .models import Application, ApplicationDocument

User = get_user_model()
PNG = (b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00'
       b'\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00'
       b'\x00IEND\xaeB`\x82')


def make_person(email, user_type='student', **fields):
    user = User.objects.create_user(username=email, email=email, password='x-Pass-1234')
    person = user.profile
    person.user_type = user_type
    for name, value in fields.items():
        setattr(person, name, value)
    person.save()
    return person


def grade(n):
    return Programme.objects.get(institution__code='UCS', grade=n)


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class ApplicationWizardTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        academic_spine.seed(verbose=False, calendar=False)

    def setUp(self):
        self.person = make_person('learner@example.com')
        self.client.force_login(self.person.user)

    # -- the steps --------------------------------------------------------
    def step1(self):
        return self.client.post(reverse('accounts:register'), {
            'basics-first_name': 'Thandi', 'basics-last_name': 'Mokoena',
            'basics-gender': 'female', 'basics-date_of_birth': '2010-03-04',
            'contact-phone_country': 'ZA', 'contact-primary_phone': '082 123 4567',
            'contact-city': 'Johannesburg',
            'consent-privacy_policy_accepted': 'on', 'consent-data_processing_accepted': 'on',
        })

    def fet_choices(self, n=10, electives=('PHYS-SCI', 'LIFE-SCI', 'ACC')):
        g = grade(n)
        by_code = {m.code: m.pk for m in g.modules.all()}
        data = {'programme_id': g.pk, 'is_new_learner': 'yes', 'cohort_id': 'year',
                f'choice_{g.pk}_fal': by_code['ZUL-FAL'], f'choice_{g.pk}_maths': by_code['MATH'],
                'module_ids': [by_code[c] for c in electives]}
        return data

    def step3(self, **extra):
        data = {
            'learner-highest_grade_passed': 'Grade 9', 'learner-is_south_african': 'True',
            'learner-id_document_type': 'sa_id', 'learner-id_number': '1003040800081',
            'learner-physical_address': '12 Raleigh Street, Yeoville', 'learner-home_language': 'isiZulu',
            'learner-previous_school': 'Yeoville Primary',
            'general-has_father': 'True', 'general-has_mother': 'True', 'general-lives_with': 'Mother',
            'general-fee_payer': 'mother', 'general-fee_payer_can_afford': 'True',
            'general-siblings_at_ucs': '0', 'general-smsweb_number': '082 123 4567',
            'mother-title': 'Mrs', 'mother-full_name': 'Lerato Mokoena', 'mother-cell_phone': '082 555 0000',
            'mother-email': 'lerato@example.com',
            'emergency-emergency_name': 'Sipho Dube', 'emergency-emergency_relationship': 'Uncle',
            'emergency-emergency_cell_phone': '083 000 1111',
        }
        data.update(extra)
        return self.client.post(reverse('accounts:register-family'), data)

    def step4(self, files=None):
        data = {'medical-has_medical_condition': 'False',
                'medical-medical_expenses_name': 'Lerato Mokoena',
                'medical-medical_expenses_phone': '082 555 0000'}
        data.update(files or {})
        return self.client.post(reverse('accounts:register-medical'), data)

    def step5(self, action='eft'):
        data = {f'decl-{name}': 'on' for name in (
            'accept_terms', 'accept_indemnity', 'accept_learner_code', 'accept_parent_code',
            'accept_prospectus', 'accept_fees', 'accept_popia', 'acknowledge_documents',
            'media_consent', 'extramural_participation', 'confirm_signature')}
        data.update({'decl-signed_by': 'Lerato Mokoena', 'decl-signed_relationship': 'Mother',
                     'action': action})
        return self.client.post(reverse('accounts:register-review'), data)

    def walk(self, *, n=10, files=None):
        self.assertRedirects(self.step1(), reverse('accounts:register-course'),
                             fetch_redirect_response=False)
        response = self.client.post(reverse('accounts:register-course'), self.fet_choices(n))
        self.assertRedirects(response, reverse('accounts:register-family'),
                             fetch_redirect_response=False)
        self.assertRedirects(self.step3(), reverse('accounts:register-medical'),
                             fetch_redirect_response=False)
        self.assertRedirects(self.step4(files), reverse('accounts:register-review'),
                             fetch_redirect_response=False)
        return self.step5()

    # -- the tests -------------------------------------------------------------
    def test_every_step_renders(self):
        self.step1()
        self.assertContains(self.client.get(reverse('accounts:register-course')), 'Grade 12')
        self.client.post(reverse('accounts:register-course'), self.fet_choices())
        self.assertContains(self.client.get(reverse('accounts:register-family')), 'Parent / guardian')
        self.step3()
        self.assertContains(self.client.get(reverse('accounts:register-medical')), 'Clinic card'
                            if False else 'Learner ID photo')
        self.step4()
        response = self.client.get(reverse('accounts:register-review'))
        self.assertContains(response, 'Registration fee')
        self.assertContains(response, '4,550.00')

    def test_a_grade_10_application_bills_registration_levy_and_the_first_month(self):
        response = self.walk()
        self.assertRedirects(response, reverse('accounts:register-complete') + '?mode=eft',
                             fetch_redirect_response=False)
        application = Application.objects.get(person=self.person)
        invoice = Invoice.objects.get(public_id=application.invoice_uid)
        self.assertEqual(invoice.total, Decimal('4550.00'))          # 550 + 2200 + 1800
        rows = ModuleEnrolment.objects.filter(person=self.person)
        self.assertEqual(rows.count(), 7)                              # CAPS: seven subjects
        self.assertTrue(all(r.status == r.STATUS_LOCKED for r in rows))  # pending payment
        self.assertEqual(set(rows.values_list('invoice_uid', flat=True)), {invoice.public_id})
        self.assertEqual(application.status, Application.STATUS_DOCUMENTS)
        self.assertEqual(application.signed_by, 'Lerato Mokoena')
        self.assertTrue(self.person.__class__.objects.get(pk=self.person.pk).registered)

    def test_the_mother_is_invited_to_a_linked_parent_account(self):
        self.walk()
        self.assertTrue(any('lerato@example.com' in m.to for m in mail.outbox))
        from apps.accounts.models import Invitation
        self.assertTrue(Invitation.objects.filter(email='lerato@example.com',
                                                  student=self.person).exists())

    def test_a_current_learner_pays_no_registration_fee(self):
        self.step1()
        data = self.fet_choices()
        data['is_new_learner'] = 'no'
        self.client.post(reverse('accounts:register-course'), data)
        self.step3()
        self.step4()
        self.step5()
        application = Application.objects.get(person=self.person)
        invoice = Invoice.objects.get(public_id=application.invoice_uid)
        self.assertEqual(invoice.total, Decimal('4000.00'))           # 2200 + 1800

    def test_the_sibling_discount_applies_to_school_fees_only(self):
        self.step1()
        self.client.post(reverse('accounts:register-course'), self.fet_choices())
        self.step3(**{'general-siblings_at_ucs': '1'})
        self.step4()
        self.step5()
        invoice = Invoice.objects.get(public_id=Application.objects.get(person=self.person).invoice_uid)
        self.assertEqual(invoice.total, Decimal('4460.00'))           # 550 + 2200 + 1800 × 95%

    def test_grade_10_needs_three_electives(self):
        self.step1()
        response = self.client.post(reverse('accounts:register-course'),
                                    self.fet_choices(electives=('HIST',)), follow=True)
        self.assertContains(response, 'please choose 3')
        self.assertFalse(Application.objects.filter(person=self.person, programme__isnull=False).exists())

    def test_a_primary_grade_takes_every_subject(self):
        self.step1()
        g = grade(2)
        self.client.post(reverse('accounts:register-course'),
                         {'programme_id': g.pk, 'is_new_learner': 'yes', 'cohort_id': 'year'})
        self.assertEqual(sorted(self.client.session['reg']['module_ids']),
                         sorted(g.modules.values_list('pk', flat=True)))

    def test_at_least_one_parent_is_required(self):
        self.step1()
        self.client.post(reverse('accounts:register-course'), self.fet_choices())
        response = self.step3(**{'mother-full_name': ''})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'at least one parent or guardian')

    def test_declarations_must_be_accepted(self):
        self.step1()
        self.client.post(reverse('accounts:register-course'), self.fet_choices())
        self.step3()
        self.step4()
        response = self.client.post(reverse('accounts:register-review'),
                                    {'decl-signed_by': 'X', 'action': 'eft'})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Invoice.objects.exists())

    def test_paying_unlocks_the_subjects_and_moves_a_documented_application_to_review(self):
        files = {f'doc_{kind}': SimpleUploadedFile(f'{kind}.png', PNG, content_type='image/png')
                 for kind in ('photo', 'id_document', 'report_card', 'transfer_card',
                              'parent_id', 'payslip')}
        self.walk(files=files)
        application = Application.objects.get(person=self.person)
        self.assertEqual(application.missing_documents(), [])
        self.assertEqual(application.status, Application.STATUS_SUBMITTED)   # pending payment
        invoice = Invoice.objects.get(public_id=application.invoice_uid)
        from apps.finance import services as finance_services
        finance_services.settle_payment(invoice, invoice.balance, method='eft')
        application.refresh_from_db()
        self.assertEqual(application.status, Application.STATUS_REVIEW)
        rows = ModuleEnrolment.objects.filter(person=self.person)
        self.assertTrue(all(r.status == r.STATUS_ACTIVE for r in rows))


class OfficeAndPrivacyTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        academic_spine.seed(verbose=False, calendar=False)
        cls.learner = make_person('learner2@example.com', registered=True, profile_status=True)
        cls.application = Application.objects.create(person=cls.learner, programme=grade(3),
                                                     status=Application.STATUS_REVIEW)
        cls.document = ApplicationDocument.objects.create(
            application=cls.application, kind=ApplicationDocument.KIND_PHOTO,
            file=SimpleUploadedFile('p.png', PNG, content_type='image/png'), original_name='p.png')
        cls.staff = make_person('office@example.com', 'staff', registered=True, profile_status=True)
        cls.stranger = make_person('other@example.com', registered=True, profile_status=True)

    def test_the_office_list_is_for_staff_only(self):
        self.client.force_login(self.stranger.user)
        self.assertEqual(self.client.get(reverse('admissions:office-list')).status_code, 404)
        self.client.force_login(self.staff.user)
        response = self.client.get(reverse('admissions:office-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'learner2@example.com')

    def test_grade_3_requires_a_clinic_card(self):
        kinds = self.application.required_document_kinds()
        self.assertIn(ApplicationDocument.KIND_CLINIC_CARD, kinds)
        self.assertIn(ApplicationDocument.KIND_BIRTH_CERT, kinds)

    def test_admitting_from_the_office(self):
        self.client.force_login(self.staff.user)
        url = reverse('admissions:office-detail', args=[self.application.public_id])
        self.assertEqual(self.client.get(url).status_code, 200)
        self.client.post(url, {'action': 'admit', 'decision_note': 'Welcome'})
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, Application.STATUS_ADMITTED)
        self.assertEqual(self.application.decided_by, self.staff.user)

    def test_documents_are_private(self):
        url = reverse('admissions:document-file', args=[self.document.pk])
        self.client.force_login(self.stranger.user)
        self.assertEqual(self.client.get(url).status_code, 404)
        self.client.force_login(self.learner.user)
        self.assertEqual(self.client.get(url).status_code, 200)
        self.client.force_login(self.staff.user)
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_the_family_sees_its_application(self):
        self.client.force_login(self.learner.user)
        response = self.client.get(reverse('admissions:my-application'))
        self.assertContains(response, 'Grade 3')
        self.assertContains(response, 'Clinic card')
