"""School fees: per grade, per calendar month, paid in advance."""
from datetime import date
from decimal import Decimal
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.finance import services as finance_services
from apps.finance.models import Invoice
from apps.learning import fees
from apps.learning.models import ModuleEnrolment, Programme
from core import academic_spine


def learner(email, grade=4):
    user = get_user_model().objects.create_user(username=email, email=email, password='x-Pass-1234')
    person = user.profile
    person.user_type, person.registered, person.profile_status = 'student', True, True
    person.save()
    programme = Programme.objects.get(institution__code='UCS', grade=grade)
    academic_spine.enrol_student(person, programme, activate=False)
    return person, programme


def on(day):
    """Freeze 'today' for the fees module and the enrolment model."""
    from django.utils import timezone as tz
    aware = tz.make_aware(tz.datetime(day.year, day.month, day.day, 9, 0))
    return mock.patch('django.utils.timezone.now', return_value=aware)


@override_settings(FEES_GRACE_DAYS=7, EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class SchoolFeesTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        academic_spine.seed(verbose=False, calendar=False)

    def pay(self, invoice):
        finance_services.settle_payment(invoice, invoice.balance, method='eft')

    def test_paying_three_months_opens_every_subject_to_the_end_of_the_third_month(self):
        person, grade4 = learner('a@example.com')
        with on(date(2026, 2, 10)):
            invoice = fees.raise_fees_invoice(person, grade4, months=3)
            self.assertEqual(invoice.total, Decimal('3750.00'))            # 3 × R1 250
            self.assertEqual((invoice.fee_start, invoice.fee_months), (date(2026, 2, 1), 3))
            self.pay(invoice)
            rows = ModuleEnrolment.objects.filter(person=person)
            self.assertTrue(rows.exists())
            self.assertEqual({r.paid_until for r in rows}, {date(2026, 4, 30)})
            self.assertTrue(all(r.is_unlocked for r in rows))

    def test_an_unpaid_month_locks_only_after_the_grace_period(self):
        person, grade4 = learner('b@example.com')
        with on(date(2026, 2, 3)):
            self.pay(fees.raise_fees_invoice(person, grade4, months=1))      # February
        row = ModuleEnrolment.objects.filter(person=person).first()
        with on(date(2026, 3, 5)):
            self.assertTrue(row.is_unlocked)                                  # inside the grace
            self.assertFalse(fees.fee_status(person)['locked'])
        with on(date(2026, 3, 9)):
            row.refresh_from_db()
            self.assertFalse(row.is_unlocked)                                 # March unpaid
            status = fees.fee_status(person)
            self.assertTrue(status['locked'])
            self.assertEqual(status['first_unpaid'], date(2026, 3, 1))

    def test_months_follow_on_from_what_is_already_paid(self):
        person, grade4 = learner('c@example.com')
        with on(date(2026, 1, 5)):
            self.pay(fees.raise_fees_invoice(person, grade4, months=2))      # Jan – Feb
            second = fees.raise_fees_invoice(person, grade4, months=1)
            self.assertEqual(second.fee_start, date(2026, 3, 1))
            self.pay(second)
        self.assertEqual(fees.paid_until(person, grade4), date(2026, 3, 31))

    def test_the_full_year_paid_in_january_earns_five_percent(self):
        person, grade7 = learner('d@example.com', grade=7)
        with on(date(2026, 1, 20)):
            options = {o['months']: o for o in fees.fee_options(grade7, date(2026, 1, 1))}
            self.assertEqual(options[12]['gross'], Decimal('21600.00'))
            self.assertEqual(options[12]['amount'], Decimal('20520.00'))
            self.assertEqual(options[1]['amount'], Decimal('1800.00'))
        with on(date(2026, 2, 2)):
            later = fees.fee_options(grade7, date(2026, 2, 1))
            self.assertEqual(later[-1]['months'], 11)
            self.assertEqual(later[-1]['amount'], Decimal('19800.00'))       # no discount

    def test_the_monthly_run_invoices_once(self):
        person, grade4 = learner('e@example.com')
        with on(date(2026, 3, 1)):
            self.assertIn('1 school-fees', fees.run_monthly_billing())
            self.assertIn('0 school-fees', fees.run_monthly_billing())
            invoice = Invoice.objects.get(customer=person.user, fee_months=1)
            self.assertEqual(invoice.fee_start, date(2026, 3, 1))
            self.pay(invoice)
            self.assertIn('0 school-fees', fees.run_monthly_billing())

    def test_the_family_fees_page_and_a_locked_subject_redirect(self):
        person, grade4 = learner('f@example.com')
        self.client.force_login(person.user)
        response = self.client.get(reverse('finance:school-fees'))
        self.assertContains(response, 'R 1,250.00')
        self.assertContains(response, 'Rest of the year')
        subject = grade4.modules.first()
        response = self.client.get(reverse('learning:module-unlock', args=[subject.pk]))
        self.assertRedirects(response, reverse('finance:school-fees'), fetch_redirect_response=False)
        response = self.client.post(reverse('finance:school-fees'), {'months': 2, 'action': 'eft'})
        self.assertEqual(Invoice.objects.get(customer=person.user).fee_months, 2)
