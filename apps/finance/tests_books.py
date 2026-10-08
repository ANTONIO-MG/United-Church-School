"""Phase 4: Wave-style invoices and estimates, reminders, statements, expenses."""
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from apps.communication.models import Notification

from . import documents, models, services

User = get_user_model()


def _onboarded(user):
    person = user.profile
    person.user_type, person.registered, person.profile_status = 'student', True, True
    person.save()
    return user


def _invoice(customer, amount='1000', **kw):
    invoice = models.Invoice.objects.create(customer=customer, status=models.Invoice.STATUS_SENT, **kw)
    models.InvoiceItem.objects.create(invoice=invoice, description='Module fee', unit_price=Decimal(amount))
    invoice.refresh_from_db()
    return invoice


@override_settings(VAT_REGISTERED=True, VAT_RATE='15')
class DocumentTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user('staff', 'staff@example.com', 'pw12345!', is_staff=True)
        self.student = _onboarded(User.objects.create_user('stu', 'stu@example.com', 'pw12345!',
                                                          first_name='Thandi', last_name='Mokoena'))

    def test_sequential_numbers_and_default_terms(self):
        year = timezone.localdate().year
        first, second = _invoice(self.student), _invoice(self.student)
        self.assertEqual(first.number, f'INV-{year}-0001')
        self.assertEqual(second.number, f'INV-{year}-0002')
        self.assertEqual((first.due_date - models.as_date(first.issue_date)).days, 7)
        estimate = models.Estimate.objects.create(customer=self.student)
        self.assertEqual(estimate.number, f'EST-{year}-0001')
        self.assertEqual((estimate.valid_until - models.as_date(estimate.issue_date)).days, 30)

    def test_editor_creates_invoice_with_discounted_lines(self):
        self.client.force_login(self.staff)
        response = self.client.post(reverse('finance:invoice-new'), {
            'customer': self.student.pk, 'issue_date': '2026-10-01', 'due_date': '2026-10-08',
            'summary': 'Semester 2', 'po_number': 'PO-9', 'notes': 'Thanks', 'footer': '',
            'lines-TOTAL_FORMS': '3', 'lines-INITIAL_FORMS': '0', 'lines-MIN_NUM_FORMS': '0', 'lines-MAX_NUM_FORMS': '1000',
            'lines-0-description': 'FREP module', 'lines-0-quantity': '2', 'lines-0-unit_price': '1500', 'lines-0-discount_percent': '10',
            'lines-1-description': 'Study pack', 'lines-1-quantity': '1', 'lines-1-unit_price': '450', 'lines-1-discount_percent': '0',
            'lines-2-description': '', 'lines-2-quantity': '1', 'lines-2-unit_price': '', 'lines-2-discount_percent': '0',
            'then': 'save'})
        invoice = models.Invoice.objects.get()
        self.assertRedirects(response, invoice.get_absolute_url(), fetch_redirect_response=False)
        self.assertEqual(invoice.status, models.Invoice.STATUS_DRAFT)
        self.assertEqual(invoice.items.count(), 2)              # the blank line was skipped
        self.assertEqual(invoice.total, Decimal('3150.00'))      # 3000 − 10% + 450
        self.assertEqual(invoice.discount_total, Decimal('300.00'))
        self.assertEqual(invoice.tax_amount, models.vat_portion(Decimal('3150'), 15))
        self.assertEqual(invoice.po_number, 'PO-9')

    def test_students_never_see_drafts(self):
        draft = _invoice(self.student)
        draft.status = models.Invoice.STATUS_DRAFT
        draft.save()
        self.client.force_login(self.student)
        self.assertEqual(self.client.get(reverse('finance:invoice-detail', args=[draft.pk])).status_code, 404)
        self.assertNotContains(self.client.get(reverse('finance:invoices') + '?tab=all'), draft.number)

    def test_send_duplicate_and_void(self):
        invoice = _invoice(self.student)
        self.client.force_login(self.staff)
        self.client.post(reverse('finance:invoice-action', args=[invoice.pk]), {'action': 'send'})
        invoice.refresh_from_db()
        self.assertIsNotNone(invoice.sent_at)
        self.assertEqual(len(mail.outbox), 1)

        self.client.post(reverse('finance:invoice-action', args=[invoice.pk]), {'action': 'duplicate'})
        copy = models.Invoice.objects.exclude(pk=invoice.pk).get()
        self.assertEqual((copy.status, copy.total), (models.Invoice.STATUS_DRAFT, invoice.total))

        services.settle_payment(invoice, Decimal('100'))
        self.client.post(reverse('finance:invoice-action', args=[invoice.pk]), {'action': 'void'})
        invoice.refresh_from_db()
        self.assertNotEqual(invoice.status, models.Invoice.STATUS_CANCELLED)   # has money against it
        self.client.post(reverse('finance:invoice-action', args=[copy.pk]), {'action': 'void'})
        copy.refresh_from_db()
        self.assertEqual(copy.status, models.Invoice.STATUS_CANCELLED)

    def test_reminder_stages_go_once_each(self):
        today = timezone.localdate()
        invoice = _invoice(self.student, due_date=today + timedelta(days=3))
        documents.run_reminders(today)
        documents.run_reminders(today)
        invoice.refresh_from_db()
        self.assertEqual(invoice.reminders_sent, ['before_3'])
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('due in 3 days', mail.outbox[0].subject)

        documents.run_reminders(today + timedelta(days=10))    # skipped "due" — only the latest stage
        invoice.refresh_from_db()
        self.assertEqual(invoice.reminders_sent, ['before_3', 'after_7'])
        self.assertIn('overdue', mail.outbox[-1].subject)

        services.settle_payment(invoice, invoice.balance)
        count = len(mail.outbox)
        documents.run_reminders(today + timedelta(days=20))
        self.assertEqual(len([m for m in mail.outbox[count:] if 'Reminder' in m.subject or 'overdue' in m.subject]), 0)

    def test_registration_invoices_are_not_reminded(self):
        from apps.learning.models import Institution, Module, ModuleEnrolment, Programme, ProgrammeModule
        invoice = _invoice(self.student, due_date=timezone.localdate())
        inst = Institution.objects.create(name='X', code='X')
        pm = ProgrammeModule.objects.create(programme=Programme.objects.create(institution=inst, name='P', code='P'),
                                            module=Module.objects.create(name='M', code='M'), name='M', code='M1')
        ModuleEnrolment.objects.create(person=self.student.profile, programme_module=pm, invoice_uid=invoice.public_id)
        documents.run_reminders()
        self.assertEqual(len(mail.outbox), 0)

    def test_estimate_accept_online_and_convert(self):
        estimate = models.Estimate.objects.create(customer=self.student, status=models.Estimate.STATUS_SENT,
                                                  summary='Group package')
        models.EstimateItem.objects.create(estimate=estimate, description='APC prep', quantity=3,
                                           unit_price=Decimal('2000'), discount_percent=5)
        estimate.recalc_total()
        self.assertEqual(estimate.total, Decimal('5700.00'))

        public = reverse('finance:estimate-public', args=[estimate.public_id])
        self.assertContains(self.client.get(public), 'APC prep')              # no login needed
        estimate.refresh_from_db()
        self.assertEqual(estimate.status, models.Estimate.STATUS_VIEWED)
        self.client.post(public, {'action': 'accept'})
        estimate.refresh_from_db()
        self.assertEqual(estimate.status, models.Estimate.STATUS_ACCEPTED)
        self.assertTrue(Notification.objects.filter(recipient=self.staff, verb='estimate accepted').exists())

        self.client.force_login(self.staff)
        self.client.post(reverse('finance:estimate-detail', args=[estimate.pk]), {'action': 'convert'})
        estimate.refresh_from_db()
        invoice = estimate.converted_invoice
        self.assertEqual((invoice.total, invoice.status), (Decimal('5700.00'), models.Invoice.STATUS_DRAFT))
        self.assertEqual(invoice.items.get().discount_amount, Decimal('300.00'))

    def test_statement_balances(self):
        old = _invoice(self.student, amount='1000')
        models.Invoice.objects.filter(pk=old.pk).update(issue_date=date(2026, 1, 10))
        services.settle_payment(old, Decimal('400'))
        models.InvoicePayment.objects.filter(invoice=old).update(paid_at=timezone.make_aware(timezone.datetime(2026, 1, 20)))
        new = _invoice(self.student, amount='500')
        models.Invoice.objects.filter(pk=new.pk).update(issue_date=date(2026, 3, 5))
        data = documents.statement(self.student, date(2026, 2, 1), date(2026, 12, 31))
        self.assertEqual(data['opening'], Decimal('600.00'))
        self.assertEqual(data['closing'], Decimal('1100.00'))

        self.client.force_login(self.student)
        self.assertContains(self.client.get(reverse('finance:statement')), 'Statement of account')
        other = User.objects.create_user('o', 'o@example.com', 'pw12345!')
        self.assertEqual(self.client.get(reverse('finance:statement-for', args=[other.pk])).status_code, 404)

    def test_pages_and_pdfs_render(self):
        invoice = _invoice(self.student)
        estimate = models.Estimate.objects.create(customer=self.student)
        models.EstimateItem.objects.create(estimate=estimate, description='X', unit_price=Decimal('10'))
        self.client.force_login(self.staff)
        for name, args in [('finance:invoices', []), ('finance:invoice-detail', [invoice.pk]),
                           ('finance:invoice-new', []), ('finance:invoice-edit', [invoice.pk]),
                           ('finance:estimates', []), ('finance:estimate-new', []),
                           ('finance:estimate-detail', [estimate.pk]), ('finance:statement-for', [self.student.pk]),
                           ('finance:expenses', []), ('finance:expense-add', []), ('finance:recurring', []),
                           ('finance:expense-setup', [])]:
            self.assertEqual(self.client.get(reverse(name, args=args)).status_code, 200, name)
        for url in [reverse('finance:estimate-pdf', args=[estimate.pk]),
                    reverse('finance:statement-for', args=[self.student.pk]) + '?format=pdf']:
            self.assertEqual(self.client.get(url)['Content-Type'], 'application/pdf', url)


@override_settings(VAT_REGISTERED=True, VAT_RATE='15')
class ExpenseTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user('staff', 'staff@example.com', 'pw12345!', is_staff=True)
        self.category = models.ExpenseCategory.objects.get(name='Software & subscriptions')

    def test_vat_is_extracted(self):
        expense = models.Expense.objects.create(category=self.category, description='M365', amount=Decimal('2340'))
        self.assertEqual(expense.vat_amount, Decimal('305.22'))

    def test_recording_with_repeat_creates_a_profile_that_catches_up(self):
        self.client.force_login(self.staff)
        start = timezone.localdate().replace(day=1) - timedelta(days=70)
        start = start.replace(day=31) if start.month in (1, 3, 5, 7, 8, 10, 12) else start.replace(day=28)
        self.client.post(reverse('finance:expense-add'), {
            'date': start.isoformat(), 'category': self.category.pk, 'description': 'Microsoft 365',
            'new_vendor': 'Microsoft', 'amount': '2340', 'vat_treatment': 'inclusive', 'paid_through': 'debit_order',
            'status': 'paid', 'repeat': '1:monthly'})
        first = models.Expense.objects.get()
        profile = first.recurring
        self.assertEqual(first.vendor.name, 'Microsoft')
        documents.run_recurring_expenses()
        dates = list(models.Expense.objects.order_by('date').values_list('date', flat=True))
        self.assertGreaterEqual(len(dates), 3)
        # Anchored to the start day: 31st → last day of shorter months.
        for later in dates[1:]:
            self.assertTrue(later.day == start.day or (later + timedelta(days=1)).day == 1)
        profile.refresh_from_db()
        self.assertGreater(profile.next_date, timezone.localdate())
        before = models.Expense.objects.count()
        documents.run_recurring_expenses()
        self.assertEqual(models.Expense.objects.count(), before)

    def test_end_date_stops_profile(self):
        today = timezone.localdate()
        profile = models.RecurringExpense.objects.create(
            name='Rent', category=self.category, description='Rent', amount=Decimal('8000'),
            start_date=today - timedelta(weeks=5), end_date=today - timedelta(weeks=3), frequency='weekly')
        documents.run_recurring_expenses()
        profile.refresh_from_db()
        self.assertEqual(models.Expense.objects.filter(recurring=profile).count(), 3)
        self.assertFalse(profile.is_active)
