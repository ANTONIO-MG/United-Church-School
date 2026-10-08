"""Raising an invoice — the page staff use most, and the one with no coverage.

Two defects lived here:

* ``due_date`` was assigned straight from ``request.POST``. Django does not
  coerce on assignment, so the model kept a ``str``; adding the first line item
  fired the InvoiceItem post-save signal → ``refresh_status()`` →
  ``is_overdue`` → ``str < date`` → ``TypeError``. A due date is the point of an
  invoice, so this was the ordinary path, not an edge case.
* the "whole course" audience referenced a name that no longer existed after
  ``Course`` was retired for the Institution → Programme → ProgrammeModule
  spine, so choosing it raised ``NameError``. It is now "everyone on a module".
"""

import datetime
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from apps.accounts.models import Person
from apps.learning.models import (Institution, Module, Programme, ProgrammeModule,
                                  ModuleEnrolment)

from . import models

User = get_user_model()


class CreateInvoiceViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.staff = User.objects.create_user(
            username='staff', email='staff@example.com', password='pw12345!', is_staff=True)
        cls.buyer = User.objects.create_user(
            username='buyer', email='buyer@example.com', password='pw12345!')

    def setUp(self):
        self.client = Client()
        self.client.force_login(self.staff)

    def _post(self, **overrides):
        data = {
            'audience': 'user',
            'users': [str(self.buyer.pk)],
            'due_date': '2026-09-01',
            'notes': 'Term 3 fees',
        }
        data.update(overrides)
        return self.client.post('/finance/manage/create/', data)

    # --- F-06: the due-date crash --------------------------------------------

    def test_invoice_with_a_due_date_is_created(self):
        response = self._post()
        self.assertEqual(response.status_code, 302)
        invoice = models.Invoice.objects.get(customer=self.buyer)
        self.assertEqual(invoice.due_date, datetime.date(2026, 9, 1))

    def test_due_date_is_stored_as_a_date_not_a_string(self):
        """``is_overdue`` compares against a date; a str there raises TypeError."""
        self._post()
        invoice = models.Invoice.objects.get(customer=self.buyer)
        self.assertIsInstance(invoice.due_date, datetime.date)
        self.assertIsInstance(invoice.is_overdue, bool)  # would raise if str

    def test_adding_a_line_item_to_a_dated_invoice_does_not_raise(self):
        """The exact 500: the InvoiceItem signal calls refresh_status()."""
        self._post()
        invoice = models.Invoice.objects.get(customer=self.buyer)
        models.InvoiceItem.objects.create(
            invoice=invoice, description='Module', quantity=1, unit_price=Decimal('5000.00'))
        invoice.refresh_from_db()
        self.assertEqual(invoice.total, Decimal('5000.00'))

    def test_a_malformed_due_date_is_a_field_error_not_a_silent_none(self):
        response = self._post(due_date='2026-13-45')
        self.assertEqual(response.status_code, 200)  # re-rendered, not redirected
        self.assertFalse(models.Invoice.objects.filter(customer=self.buyer).exists())
        self.assertIn('due_date', response.context['form'].errors)

    def test_no_due_date_is_allowed(self):
        response = self._post(due_date='')
        self.assertEqual(response.status_code, 302)
        # A blank due date takes the default payment terms rather than none.
        invoice = models.Invoice.objects.get(customer=self.buyer)
        self.assertEqual((invoice.due_date - models.as_date(invoice.issue_date)).days,
                         models.DEFAULT_TERMS_DAYS)

    def test_no_recipients_creates_nothing(self):
        response = self._post(users=[])
        self.assertEqual(response.status_code, 200)
        self.assertFalse(models.Invoice.objects.filter(created_by=self.staff).exists())


class CreateInvoiceByModuleTests(TestCase):
    """The bulk audience — previously a NameError for every submission."""

    @classmethod
    def setUpTestData(cls):
        cls.staff = User.objects.create_user(
            username='staff2', email='staff2@example.com', password='pw12345!', is_staff=True)
        institution = Institution.objects.create(name='United Church School', code='UCS')
        programme = Programme.objects.create(institution=institution, name='Grade 10', code='GR10')
        module = Module.objects.create(name='Auditing', code='AUD')
        cls.pm = ProgrammeModule.objects.create(
            programme=programme, module=module, name='Auditing', code='AUD-1', is_active=True)

        cls.enrolled = []
        for i in range(2):
            user = User.objects.create_user(
                username=f'learner{i}', email=f'learner{i}@example.com', password='pw12345!')
            person, _ = Person.objects.update_or_create(user=user, defaults={'user_type': 'student'})
            ModuleEnrolment.objects.create(person=person, programme_module=cls.pm)
            cls.enrolled.append(user)

        cls.outsider = User.objects.create_user(
            username='outsider', email='outsider@example.com', password='pw12345!')
        Person.objects.update_or_create(user=cls.outsider, defaults={'user_type': 'student'})

    def setUp(self):
        self.client = Client()
        self.client.force_login(self.staff)

    def test_one_invoice_is_created_per_enrolled_person(self):
        response = self.client.post('/finance/manage/create/', {
            'audience': 'module', 'programme_module': str(self.pm.pk),
            'due_date': '2026-09-01', 'notes': '',
        })
        self.assertEqual(response.status_code, 302)
        billed = set(models.Invoice.objects.filter(created_by=self.staff)
                     .values_list('customer_id', flat=True))
        self.assertEqual(billed, {u.pk for u in self.enrolled})
        self.assertNotIn(self.outsider.pk, billed)

    def test_module_audience_without_a_module_is_a_field_error(self):
        response = self.client.post('/finance/manage/create/', {
            'audience': 'module', 'programme_module': '', 'notes': '',
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('programme_module', response.context['form'].errors)
        self.assertFalse(models.Invoice.objects.filter(created_by=self.staff).exists())


class IsOverdueCoercionTests(TestCase):
    """``is_overdue`` must survive a string, whoever assigned it."""

    def test_string_due_date_does_not_raise(self):
        user = User.objects.create_user(
            username='c1', email='c1@example.com', password='pw12345!')
        invoice = models.Invoice.objects.create(
            customer=user, status=models.Invoice.STATUS_SENT, due_date='2020-01-01')
        invoice.due_date = '2020-01-01'  # as an unvalidated view would leave it
        self.assertIs(invoice.is_overdue, True)

    def test_unparseable_string_is_simply_not_overdue(self):
        user = User.objects.create_user(
            username='c2', email='c2@example.com', password='pw12345!')
        invoice = models.Invoice(customer=user, status=models.Invoice.STATUS_SENT)
        invoice.due_date = 'not a date'
        self.assertIs(invoice.is_overdue, False)
