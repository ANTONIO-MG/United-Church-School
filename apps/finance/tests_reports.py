"""Phase 5: finance dashboards and reports.

The two bases must stay honest: "paid" is money that arrived (spread over the
invoice's lines), "invoiced" is what was billed on the invoice date.
"""
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from apps.shop.models import Product

from . import models, reports, services

User = get_user_model()


def _onboarded(user):
    person = user.profile
    person.user_type, person.registered, person.profile_status = 'student', True, True
    person.save()
    return user


@override_settings(VAT_REGISTERED=False)
class ReportTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user('staff', 'staff@example.com', 'pw12345!', is_staff=True)
        self.a = _onboarded(User.objects.create_user('a', 'a@example.com', 'pw12345!', first_name='Ayanda'))
        self.b = _onboarded(User.objects.create_user('b', 'b@example.com', 'pw12345!', first_name='Bongi'))
        self.pack = Product.objects.create(name='FREP pack', price=Decimal('400'), fulfilment='digital')
        self.hoodie = Product.objects.create(name='Hoodie', price=Decimal('600'), fulfilment='shipped')
        self.today = timezone.localdate()
        self.start = self.today.replace(day=1)

        self.mixed = models.Invoice.objects.create(customer=self.a, status='sent')
        models.InvoiceItem.objects.create(invoice=self.mixed, product=self.pack, unit_price=Decimal('400'))
        models.InvoiceItem.objects.create(invoice=self.mixed, product=self.hoodie, unit_price=Decimal('600'))
        models.InvoiceItem.objects.create(invoice=self.mixed, description='Module fee — FREP', unit_price=Decimal('1000'))
        self.mixed.refresh_from_db()
        services.settle_payment(self.mixed, Decimal('1000'))              # half paid

        self.fee = models.Invoice.objects.create(customer=self.b, status='sent')
        models.InvoiceItem.objects.create(invoice=self.fee, description='Module fee', unit_price=Decimal('3000'))
        self.fee.refresh_from_db()
        services.settle_payment(self.fee, Decimal('3000'))

        draft = models.Invoice.objects.create(customer=self.b, status='draft')
        models.InvoiceItem.objects.create(invoice=draft, description='Never sent', unit_price=Decimal('9999'))

        cat = models.ExpenseCategory.objects.get(name='Printing & study materials')
        models.Expense.objects.create(category=cat, description='Print run', amount=Decimal('500'))
        rent = models.ExpenseCategory.objects.get(name='Rent & utilities')
        models.Expense.objects.create(category=rent, description='Rent', amount=Decimal('1500'))

    def test_streams_paid_vs_invoiced(self):
        rows = {r['key']: r for r in reports.income_by_stream(self.start, self.today)}
        self.assertEqual(rows['fees']['invoiced'], Decimal('4000'))
        self.assertEqual(rows['digital']['invoiced'], Decimal('400'))
        # R1,000 paid on a R2,000 invoice is spread 20% / 30% / 50% over its lines.
        self.assertEqual(rows['digital']['paid'], Decimal('200.00'))
        self.assertEqual(rows['shipped']['paid'], Decimal('300.00'))
        self.assertEqual(rows['fees']['paid'], Decimal('3500.00'))
        self.assertNotIn(Decimal('9999'), [r['invoiced'] for r in rows.values()])   # drafts are not income

    def test_profit_and_loss_has_both_bases(self):
        pnl = reports.profit_and_loss(self.start, self.today)
        self.assertEqual(pnl['total_paid'], Decimal('4000.00'))
        self.assertEqual(pnl['total_invoiced'], Decimal('5000'))
        self.assertEqual(pnl['cost_of_sales'], Decimal('500'))
        self.assertEqual(pnl['net_paid'], Decimal('2000.00'))
        self.assertEqual(pnl['net_invoiced'], Decimal('3000'))

    @override_settings(VAT_REGISTERED=True, VAT_RATE='15')
    def test_profit_is_ex_vat_when_registered(self):
        pnl = reports.profit_and_loss(self.start, self.today)
        self.assertEqual(pnl['revenue_invoiced'], Decimal('5000') - models.vat_portion(Decimal('5000'), 15))

    def test_top_customers_and_items(self):
        customers = reports.sales_by_customer(self.start, self.today)
        self.assertEqual(customers[0]['user'], self.b)
        self.assertEqual(customers[1]['outstanding'], Decimal('1000.00'))
        items = reports.sales_by_item(self.start, self.today)
        self.assertEqual(items[0]['label'], 'Module fee')

    def test_aging_buckets(self):
        models.Invoice.objects.filter(pk=self.mixed.pk).update(due_date=self.today - timedelta(days=45))
        aging = reports.receivables_aging(self.today)
        buckets = {b['key']: b['amount'] for b in aging['buckets']}
        self.assertEqual(buckets['31_60'], Decimal('1000.00'))
        self.assertEqual(aging['total'], Decimal('1000.00'))

    def test_cash_flow_running_total(self):
        series = reports.monthly_series(self.start, self.today)
        self.assertEqual(series[-1]['paid'], Decimal('4000.00'))
        self.assertEqual(series[-1]['running'], Decimal('2000.00'))

    def test_reports_are_staff_only_and_export_csv(self):
        self.client.force_login(self.a)
        self.assertEqual(self.client.get(reverse('finance:report', args=['profit-and-loss'])).status_code, 404)
        self.assertRedirects(self.client.get(reverse('finance:reports')), reverse('finance:my-finances'),
                             fetch_redirect_response=False)
        self.client.force_login(self.staff)
        self.assertEqual(self.client.get(reverse('finance:reports')).status_code, 200)
        for slug, *_ in __import__('apps.finance.views_reports', fromlist=['REPORTS']).REPORTS:
            url = reverse('finance:report', args=[slug])
            self.assertEqual(self.client.get(url + '?period=12m').status_code, 200, slug)
            response = self.client.get(url + '?period=12m&format=csv')
            self.assertEqual(response['Content-Type'], 'text/csv; charset=utf-8', slug)
        csv_text = self.client.get(reverse('finance:report', args=['profit-and-loss']) + '?format=csv').content.decode('utf-8-sig')
        self.assertIn('Paid (cash),Invoiced (accrual)', csv_text)

    def test_student_dashboard_is_their_own(self):
        self.client.force_login(self.a)
        page = self.client.get(reverse('finance:my-finances'))
        self.assertContains(page, 'R1,000.00 to pay')
        self.assertNotContains(page, 'Bongi')


class ForecastTests(TestCase):
    def test_remaining_months_to_cohort_end(self):
        from apps.learning.models import (Cohort, Institution, Module, ModuleEnrolment, Programme,
                                          ProgrammeEnrolment, ProgrammeModule)
        user = _onboarded(User.objects.create_user('s', 's@example.com', 'pw12345!'))
        inst = Institution.objects.create(name='United Church School', code='UCS')
        programme = Programme.objects.create(institution=inst, name='Grade 10', code='GR10')
        today = timezone.localdate()
        cohort = Cohort.objects.create(programme=programme, code='P26', end_date=reports.add_months(today, 6))
        ProgrammeEnrolment.objects.create(person=user.profile, programme=programme, cohort=cohort)
        pm = ProgrammeModule.objects.create(programme=programme, module=Module.objects.create(name='FREP', code='FREP'),
                                            name='FREP', code='FREP1', price_per_month=Decimal('800'))
        ModuleEnrolment.objects.create(person=user.profile, programme_module=pm, status='active',
                                       paid_until=reports.add_months(today, 2), price_at_enrolment=Decimal('800'))
        forecast = reports.study_forecast(user, today)
        self.assertEqual(forecast['lines'][0]['months'], 4)
        self.assertEqual(forecast['total'], Decimal('3200'))
