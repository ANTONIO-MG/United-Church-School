"""A parent applies for another child from their own account.

The parent starts an application (a learner account + ParentLink + draft are
made for the child at once), walks the same five-step wizard "acting for" the
child, and pays by EFT. They may only ever act for their own linked children,
and the learner's own self-application keeps working as before.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.accounts.models import Invitation, ParentLink, Person
from apps.admissions.models import Application
from apps.admissions.tests import grade
from apps.finance.models import Invoice
from apps.learning.models import ModuleEnrolment
from core import academic_spine

User = get_user_model()


def make(email, kind, first, last='Mokoena'):
    user = User.objects.create_user(username=email, email=email, password='x-Pass-1234')
    p = user.profile
    p.user_type, p.registered, p.profile_status = kind, True, True
    p.first_name, p.last_name = first, last
    p.save()
    return p


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class ParentAppliesForAChildTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        academic_spine.seed(verbose=False, calendar=False)

    def setUp(self):
        self.parent = make('lerato@example.com', 'parent', 'Lerato')
        self.first = make('thandi@example.com', 'student', 'Thandi')
        ParentLink.objects.create(parent=self.parent.user, student=self.first.user,
                                  relationship='Mother')
        self.client.force_login(self.parent.user)

    # -- the steps --------------------------------------------------------
    def start(self, **extra):
        data = {'first_name': 'Sipho', 'last_name': 'Mokoena', 'relationship': 'Mother',
                'year': '2026', 'email': ''}
        data.update(extra)
        return self.client.post(reverse('accounts:parent-apply'), data)

    def step1(self):
        return self.client.post(reverse('accounts:register'), {
            'basics-first_name': 'Sipho', 'basics-last_name': 'Mokoena',
            'basics-gender': 'male', 'basics-date_of_birth': '2010-05-06',
            'contact-phone_country': 'ZA', 'contact-primary_phone': '082 555 0000',
            'contact-city': 'Johannesburg',
            'consent-privacy_policy_accepted': 'on', 'consent-data_processing_accepted': 'on',
        })

    def step2(self):
        g = grade(10)
        by_code = {m.code: m.pk for m in g.modules.all()}
        return self.client.post(reverse('accounts:register-course'), {
            'programme_id': g.pk, 'is_new_learner': 'yes', 'cohort_id': 'year',
            f'choice_{g.pk}_fal': by_code['ZUL-FAL'], f'choice_{g.pk}_maths': by_code['MATH'],
            'module_ids': [by_code[c] for c in ('PHYS-SCI', 'LIFE-SCI', 'ACC')]})

    def step3(self):
        return self.client.post(reverse('accounts:register-family'), {
            'learner-highest_grade_passed': 'Grade 9', 'learner-is_south_african': 'True',
            'learner-id_document_type': 'sa_id', 'learner-id_number': '1005065800085',
            'learner-physical_address': '12 Raleigh Street, Yeoville',
            'learner-home_language': 'isiZulu', 'learner-previous_school': 'Yeoville Primary',
            'general-has_father': 'True', 'general-has_mother': 'True', 'general-lives_with': 'Mother',
            'general-fee_payer': 'mother', 'general-fee_payer_can_afford': 'True',
            'general-siblings_at_ucs': '0', 'general-smsweb_number': '082 555 0000',
            'mother-title': 'Mrs', 'mother-full_name': 'Lerato Mokoena',
            'mother-cell_phone': '082 555 0000', 'mother-email': 'lerato@example.com',
            'emergency-emergency_name': 'Sipho Dube', 'emergency-emergency_relationship': 'Uncle',
            'emergency-emergency_cell_phone': '083 000 1111',
        })

    def step4(self):
        return self.client.post(reverse('accounts:register-medical'), {
            'medical-has_medical_condition': 'False',
            'medical-medical_expenses_name': 'Lerato Mokoena',
            'medical-medical_expenses_phone': '082 555 0000'})

    def step5(self, action='eft'):
        data = {f'decl-{name}': 'on' for name in (
            'accept_terms', 'accept_indemnity', 'accept_learner_code', 'accept_parent_code',
            'accept_prospectus', 'accept_fees', 'accept_popia', 'acknowledge_documents',
            'media_consent', 'extramural_participation', 'confirm_signature')}
        data.update({'decl-signed_by': 'Lerato Mokoena', 'decl-signed_relationship': 'Mother',
                     'action': action})
        return self.client.post(reverse('accounts:register-review'), data)

    def child(self):
        return Person.objects.get(first_name='Sipho', user_type='student')

    # -- the tests -------------------------------------------------------
    def test_the_dashboard_offers_apply_for_a_child(self):
        response = self.client.get(reverse('myhub:index'))
        self.assertContains(response, reverse('accounts:parent-apply'))
        self.assertContains(self.client.get(reverse('accounts:parent-apply')), 'Apply for a child')

    def test_starting_makes_a_linked_learner_with_a_generated_login_and_a_draft(self):
        self.assertRedirects(self.start(), reverse('accounts:register'),
                             fetch_redirect_response=False)
        child = self.child()
        self.assertTrue(child.user.email.endswith('@learners.ucs.local'))
        self.assertFalse(child.user.has_usable_password())
        self.assertFalse(child.registered)
        self.assertTrue(ParentLink.objects.filter(parent=self.parent.user, student=child.user,
                                                  relationship='Mother').exists())
        self.assertEqual(Application.objects.get(person=child).status, Application.STATUS_DRAFT)
        self.assertEqual(self.client.session['applying_for'], child.user.pk)
        # Starting again with the same name resumes the draft, no duplicate.
        self.start()
        self.assertEqual(Person.objects.filter(first_name='Sipho').count(), 1)

    def test_a_parent_applies_for_a_second_child_end_to_end(self):
        self.start()
        child = self.child()
        self.assertRedirects(self.step1(), reverse('accounts:register-course'),
                             fetch_redirect_response=False)
        self.assertRedirects(self.step2(), reverse('accounts:register-family'),
                             fetch_redirect_response=False)
        # Step 3 starts with the parent pre-filled as the mother.
        response = self.client.get(reverse('accounts:register-family'))
        self.assertContains(response, 'value="Lerato Mokoena"')
        self.assertContains(response, 'You are applying for')
        self.assertRedirects(self.step3(), reverse('accounts:register-medical'),
                             fetch_redirect_response=False)
        self.assertRedirects(self.step4(), reverse('accounts:register-review'),
                             fetch_redirect_response=False)
        self.assertContains(self.client.get(reverse('accounts:register-review')),
                            'value="Lerato Mokoena"')
        response = self.step5()
        self.assertRedirects(response, reverse('accounts:register-complete') + '?mode=eft',
                             fetch_redirect_response=False)

        child.refresh_from_db()
        self.assertTrue(child.registered)
        application = Application.objects.get(person=child)
        self.assertIn(application.status, (Application.STATUS_SUBMITTED,
                                           Application.STATUS_DOCUMENTS))
        self.assertEqual(application.signed_by, 'Lerato Mokoena')
        invoice = Invoice.objects.get(public_id=application.invoice_uid)
        self.assertEqual(invoice.customer, child.user)
        self.assertEqual(invoice.total, Decimal('4550.00'))
        self.assertEqual(ModuleEnrolment.objects.filter(person=child).count(), 7)
        # The parent's own account is untouched.
        self.parent.refresh_from_db()
        self.assertFalse(Application.objects.filter(person=self.parent).exists())
        self.assertEqual(self.parent.user_type, 'parent')
        # Already linked, so no invitation to her own account; she got the pay link.
        self.assertFalse(Invitation.objects.filter(email='lerato@example.com').exists())
        self.assertTrue(any('lerato@example.com' in m.to and invoice.number in m.subject
                            for m in mail.outbox))
        # Acting is over; the new child is the one being viewed.
        session = self.client.session
        self.assertNotIn('applying_for', session)
        self.assertEqual(session['viewing_child'], child.user.pk)

        # The dashboard shows both children, and offers the learner's login.
        response = self.client.get(reverse('myhub:index'))
        self.assertContains(response, 'Thandi')
        self.assertContains(response, 'Sipho')
        self.assertEqual(len(response.context['cards']), 2)
        login_url = reverse('accounts:parent-apply-login', args=[child.user.pk])
        self.assertContains(response, login_url)
        self.assertContains(self.client.get(reverse('accounts:register-complete') + '?mode=eft'),
                            login_url)

        # A generated login: the parent sets the password; the child can sign in.
        self.assertContains(self.client.get(login_url), child.user.email)
        self.client.post(login_url, {'password1': 'Zebra-Lamp-2049', 'password2': 'Zebra-Lamp-2049'})
        child.user.refresh_from_db()
        self.assertTrue(child.user.check_password('Zebra-Lamp-2049'))
        # Once set, the page will not overwrite it.
        self.client.post(login_url, {'password1': 'Other-Pass-9999', 'password2': 'Other-Pass-9999'})
        child.user.refresh_from_db()
        self.assertTrue(child.user.check_password('Zebra-Lamp-2049'))

    def test_a_child_with_their_own_email_is_sent_a_set_password_link(self):
        self.start(email='sipho@example.com')
        child = self.child()
        self.assertEqual(child.user.email, 'sipho@example.com')
        mail.outbox.clear()
        self.client.post(reverse('accounts:parent-apply-login', args=[child.user.pk]))
        self.assertTrue(any('sipho@example.com' in m.to for m in mail.outbox))

    def test_an_email_already_in_use_is_refused(self):
        response = self.start(email='thandi@example.com')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Person.objects.filter(first_name='Sipho').exists())

    def test_continue_resumes_the_wizard_for_the_child(self):
        self.start()
        child = self.child()
        self.client.post(reverse('accounts:parent-apply-stop'))
        self.assertNotIn('applying_for', self.client.session)
        self.assertContains(self.client.get(reverse('myhub:index')), 'Continue application')
        self.client.get(reverse('accounts:parent-apply-continue', args=[child.user.pk]))
        self.assertEqual(self.client.session['applying_for'], child.user.pk)

    def test_a_parent_cannot_act_for_someone_elses_child(self):
        stranger = make('stranger@example.com', 'student', 'Bongani', 'Dlamini')
        stranger.registered = False
        stranger.save()
        response = self.client.get(reverse('accounts:parent-apply-continue', args=[stranger.user.pk]))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.client.get(
            reverse('accounts:parent-apply-login', args=[stranger.user.pk])).status_code, 404)
        # Tampering with the session is ignored: the wizard does not touch the stranger.
        session = self.client.session
        session['applying_for'] = stranger.user.pk
        session.save()
        self.step1()
        stranger.refresh_from_db()
        self.assertEqual(stranger.first_name, 'Bongani')
        self.assertNotIn('applying_for', self.client.session)
        self.assertFalse(Application.objects.filter(person=stranger).exists())

    def test_only_parents_start_an_application_for_a_child(self):
        self.client.force_login(self.first.user)
        self.start()
        self.assertFalse(Person.objects.filter(first_name='Sipho').exists())
