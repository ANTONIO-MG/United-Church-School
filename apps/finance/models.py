"""Data models for the finance app.

Invoicing & payment tracking that sits on top of the shop:

* :class:`Invoice` + :class:`InvoiceItem` — a bill issued to a user, optionally
  generated from a :class:`shop.Order` (the ``order`` FK is a string reference
  so finance does not import shop directly).
* :class:`InvoicePayment` — money received against an invoice; the invoice
  status is recomputed automatically (paid / partial / overdue) by
  :mod:`apps.finance.signals`.
"""

import uuid
from decimal import ROUND_HALF_UP, Decimal

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_date

from core import validators as v


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


def as_date(value):
    """``value`` (a date, datetime, ISO string or None) as a local date."""
    from datetime import date, datetime
    if isinstance(value, str):
        value = parse_date(value)
    if isinstance(value, datetime):
        return timezone.localdate(value) if timezone.is_aware(value) else value.date()
    if isinstance(value, date):
        return value
    return timezone.localdate()


def vat_defaults():
    """``(rate, inclusive)`` for a new invoice, from settings."""
    if getattr(settings, 'VAT_REGISTERED', False):
        return Decimal(str(getattr(settings, 'VAT_RATE', 15))), True
    return Decimal('0'), True


def vat_portion(amount, rate, *, inclusive=True):
    """The VAT in (inclusive) or on top of (exclusive) ``amount`` at ``rate`` %."""
    amount, rate = Decimal(str(amount or 0)), Decimal(str(rate or 0))
    if rate <= 0 or amount <= 0:
        return Decimal('0.00')
    vat = amount * rate / (100 + rate) if inclusive else amount * rate / 100
    return vat.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


class DocumentSequence(models.Model):
    """Per-year serial numbers for financial documents (INV-2026-0001).

    SARS expects every tax invoice to carry a unique serial number, and a book
    that counts up is one an accountant can audit for gaps. Taken under a row
    lock so two invoices raised at the same moment cannot share a number.
    """

    prefix = models.CharField(max_length=10)
    year = models.PositiveIntegerField()
    last = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['prefix', 'year'], name='uniq_sequence_per_year')]

    def __str__(self):
        return f'{self.prefix}-{self.year}: {self.last}'

    @classmethod
    def next_number(cls, prefix, year=None):
        from django.db import transaction
        year = year or timezone.localdate().year
        with transaction.atomic():
            row, _ = cls.objects.select_for_update().get_or_create(prefix=prefix, year=year)
            row.last += 1
            row.save(update_fields=['last'])
            return f'{prefix}-{year}-{row.last:04d}'


#: New invoices are due this many days after issue unless set otherwise.
DEFAULT_TERMS_DAYS = 7


class Invoice(TimeStampedModel):
    STATUS_DRAFT = 'draft'
    STATUS_SENT = 'sent'
    STATUS_PARTIAL = 'partial'
    STATUS_PAID = 'paid'
    STATUS_OVERDUE = 'overdue'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_SENT, 'Sent'),
        (STATUS_PARTIAL, 'Partial'),
        (STATUS_PAID, 'Paid'),
        (STATUS_OVERDUE, 'Overdue'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    number = models.CharField(max_length=40, unique=True, blank=True)
    # Non-guessable token used for the emailed "pay this invoice" link, so a
    # recipient can pay without first logging in.
    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='invoices',
    )
    # String reference: shop is wired separately; finance must not import it.
    order = models.ForeignKey(
        'shop.Order', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='invoices',
    )

    issue_date = models.DateField(default=timezone.now)
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_DRAFT)

    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_total = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
        help_text='Sum of the line discounts, for display. Lines are already net of it.')
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    # VAT. A rate of 0 is the old behaviour — ``tax_amount`` is whatever staff
    # typed and is added on top — so invoices raised before VAT registration
    # keep the totals they were issued with. New invoices take the rate from
    # settings (see :func:`vat_defaults`) at creation and keep it, because a
    # tax invoice must not change if the rate later does.
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0,
                                   help_text='VAT rate in percent. 0 = no VAT.')
    tax_inclusive = models.BooleanField(
        default=True, help_text='Line prices already include VAT (the VAT is extracted, not added).')

    notes = models.TextField(blank=True, help_text='Notes / terms printed on the invoice.')
    summary = models.CharField(max_length=200, blank=True,
                               help_text='One line under the title, e.g. "Semester 2 tuition".')
    po_number = models.CharField('P.O. / reference', max_length=60, blank=True)
    footer = models.CharField(max_length=255, blank=True, help_text='Small print at the bottom.')
    viewed_at = models.DateTimeField(null=True, blank=True,
                                     help_text='First time the customer opened the pay link.')
    sent_at = models.DateTimeField(null=True, blank=True)
    last_reminder_at = models.DateTimeField(null=True, blank=True)
    reminders_sent = models.JSONField(default=list, blank=True,
                                      help_text='Automatic reminder stages already sent.')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='+',
    )

    class Meta:
        ordering = ['-issue_date', '-id']

    def __str__(self):
        return self.number

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = DocumentSequence.next_number('INV')
        if self._state.adding and not self.due_date:
            from datetime import timedelta
            self.due_date = as_date(self.issue_date) + timedelta(days=DEFAULT_TERMS_DAYS)
        if self._state.adding and not self.tax_rate:
            rate, inclusive = vat_defaults()
            self.tax_rate, self.tax_inclusive = rate, inclusive
        super().save(*args, **kwargs)

    @property
    def is_tax_invoice(self):
        """A VAT invoice — titled "Tax invoice" and carrying the VAT number."""
        return bool(self.tax_rate) and self.tax_rate > 0

    @property
    def bill_to_name(self):
        """The customer as they should be addressed on the invoice."""
        user = self.customer
        return (user.get_full_name() or '').strip() or user.get_username()

    @property
    def payment_reference(self):
        """What the payer must type in the EFT reference field.

        An EFT arrives on the bank statement as an amount and one free-text
        string. Without the payer's name *and* the invoice number in it, matching
        a deposit back to a student is manual detective work — so the invoice
        tells them exactly what to use, e.g. ``Thandi Mokoena INV-4F2A1B``.
        """
        return f'{self.bill_to_name} {self.number}'.strip()

    @property
    def amount_paid(self):
        aggregated = self.payments.filter(
            status=InvoicePayment.STATUS_COMPLETED).aggregate(total=models.Sum('amount'))
        return aggregated['total'] or 0

    def get_pay_url(self):
        """The tokenised public pay-link (works without logging in)."""
        return reverse('finance:pay', args=[self.public_id])

    @property
    def balance(self):
        return (self.total or 0) - self.amount_paid

    @property
    def is_overdue(self):
        # Django does not coerce on assignment, so an unvalidated
        # ``invoice.due_date = request.POST['due_date']`` leaves a str here and
        # ``str < date`` raises — which turned "create an invoice with a due
        # date" into a 500 by way of the InvoiceItem post-save signal. Views
        # validate now (forms.InvoiceCreateForm); this makes the property safe
        # whatever assigned to it.
        due = self.due_date
        if isinstance(due, str):
            due = parse_date(due)
        return bool(
            due and due < timezone.now().date()
            and self.status not in (self.STATUS_PAID, self.STATUS_CANCELLED)
        )

    def recalc_total(self):
        aggregated = self.items.aggregate(total=models.Sum('amount'),
                                          discount=models.Sum('discount_amount'))
        self.subtotal = aggregated['total'] or Decimal('0')
        self.discount_total = aggregated['discount'] or Decimal('0')
        if self.tax_rate:
            self.tax_amount = vat_portion(self.subtotal, self.tax_rate, inclusive=self.tax_inclusive)
            self.total = self.subtotal if self.tax_inclusive else self.subtotal + self.tax_amount
        else:
            self.total = self.subtotal + (self.tax_amount or 0)
        self.save(update_fields=['subtotal', 'discount_total', 'tax_amount', 'total', 'updated_at'])

    @property
    def total_excl_tax(self):
        return (self.total or 0) - (self.tax_amount or 0)

    def refresh_status(self):
        """Move the invoice between partial / paid / overdue based on payments
        and the due date. Draft / cancelled invoices are left untouched."""
        if self.status == self.STATUS_CANCELLED:
            return
        new_status = self.status
        if self.total > 0 and self.balance <= 0:
            new_status = self.STATUS_PAID
        elif self.amount_paid > 0:
            new_status = self.STATUS_PARTIAL
        elif self.is_overdue:
            new_status = self.STATUS_OVERDUE
        if new_status != self.status:
            self.status = new_status
            self.save(update_fields=['status', 'updated_at'])

    def get_absolute_url(self):
        return reverse('finance:invoice-detail', args=[self.pk])

    @property
    def gross_subtotal(self):
        return (self.subtotal or 0) + (self.discount_total or 0)

    @property
    def days_overdue(self):
        if not self.due_date or self.status in (self.STATUS_PAID, self.STATUS_CANCELLED):
            return 0
        return max((timezone.localdate() - self.due_date).days, 0)

    @property
    def stage(self):
        """Where the invoice is in Wave's Create → Send → Get paid rail."""
        if self.status == self.STATUS_PAID:
            return 3
        if self.status == self.STATUS_DRAFT:
            return 1
        return 2


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    # Optional source: pick a shop product (which may itself represent a course
    # or module — see Phase B) and the line auto-fills its description + price.
    product = models.ForeignKey(
        'shop.Product', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='invoice_items',
    )
    description = models.CharField(max_length=255, blank=True)
    detail = models.CharField(max_length=255, blank=True,
                              help_text='Second line under the description, e.g. "20% off".')
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    #: Net: ``unit_price × quantity − discount_amount``.
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return self.description or (str(self.product) if self.product_id else 'Item')

    @property
    def gross_amount(self):
        return (self.unit_price or 0) * (self.quantity or 0)

    def save(self, *args, **kwargs):
        # Auto-populate from the chosen product when fields are left blank.
        if self.product_id:
            if not self.description:
                self.description = self.product.name[:255]
            if not self.unit_price:
                self.unit_price = self.product.price or 0
        gross = Decimal(str(self.gross_amount))
        if self.discount_percent and not self.discount_amount:
            self.discount_amount = (gross * Decimal(str(self.discount_percent)) / 100).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP)
        self.discount_amount = min(Decimal(str(self.discount_amount or 0)), gross)
        self.amount = gross - self.discount_amount
        super().save(*args, **kwargs)


class InvoicePayment(TimeStampedModel):
    STATUS_PENDING = 'pending'
    STATUS_COMPLETED = 'completed'
    STATUS_FAILED = 'failed'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_FAILED, 'Failed'),
    ]
    METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('bank', 'Bank Transfer'),
        ('online', 'Online'),
        ('payfast', 'PayFast'),
        ('cheque', 'Cheque'),
        ('credit', 'Account credit'),
    ]
    GATEWAY_MANUAL = 'manual'
    GATEWAY_PAYFAST = 'payfast'
    GATEWAY_CHOICES = [(GATEWAY_MANUAL, 'Manual'), (GATEWAY_PAYFAST, 'PayFast')]

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, default='online')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_COMPLETED, db_index=True)
    gateway = models.CharField(max_length=10, choices=GATEWAY_CHOICES, default=GATEWAY_MANUAL)
    reference = models.CharField(max_length=120, blank=True)
    gateway_ref = models.CharField(max_length=120, blank=True, help_text='Gateway payment id (e.g. PayFast pf_payment_id).')
    raw = models.JSONField(default=dict, blank=True, help_text='Raw gateway callback payload.')
    paid_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-paid_at']

    def __str__(self):
        return f'{self.amount} on {self.invoice}'


class ProofOfPayment(TimeStampedModel):
    """Evidence that a student paid — every payment, however it arrived.

    Three things produce one of these, and all three land in the same place so a
    student's payment history is one list rather than three:

    * **gateway** — PayFast settled an invoice. Recorded automatically by
      :func:`apps.finance.services.record_gateway_proof`; there is no document
      to upload because the gateway *is* the evidence, so ``gateway_ref`` carries
      the PayFast payment id.
    * **upload** — a student paid by EFT and sent through a deposit slip. A staff
      member uploads it here; it can be a photograph or a PDF.
    * **manual** — staff recorded a payment they can vouch for with no document
      attached (cash in the room, a bank statement they are looking at).

    Only administrators and staff may create these — see
    :func:`apps.finance.access.record_payment_and_grant_access`, which is the one
    way a manual payment is captured and access is granted, precisely so that
    granting access and recording the money that justified it cannot drift apart.
    """

    SOURCE_UPLOAD = 'upload'
    SOURCE_GATEWAY = 'gateway'
    SOURCE_MANUAL = 'manual'
    SOURCE_CHOICES = [
        (SOURCE_UPLOAD, 'Document uploaded by staff'),
        (SOURCE_GATEWAY, 'Settled by the payment gateway'),
        (SOURCE_MANUAL, 'Recorded by staff, no document'),
    ]

    STATUS_PENDING = 'pending'
    STATUS_VERIFIED = 'verified'
    STATUS_REJECTED = 'rejected'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Awaiting verification'),
        (STATUS_VERIFIED, 'Verified'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    person = models.ForeignKey('accounts.Person', on_delete=models.CASCADE,
                               related_name='payment_proofs')
    invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='proofs')
    payment = models.ForeignKey(InvoicePayment, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='proofs',
                                help_text='The money record this proof supports.')

    # A photograph of a deposit slip or a bank-generated PDF — both are normal.
    document = models.FileField(upload_to='payment_proofs/%Y/%m/', blank=True,
                                validators=v.validate_attachment,
                                help_text='Image or PDF of the deposit slip / bank confirmation.')
    original_name = models.CharField(max_length=255, blank=True)
    content_type = models.CharField(max_length=100, blank=True)

    source = models.CharField(max_length=10, choices=SOURCE_CHOICES, default=SOURCE_UPLOAD,
                              db_index=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_VERIFIED,
                              db_index=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    paid_on = models.DateField(null=True, blank=True, help_text='Date on the deposit slip.')
    reference = models.CharField(max_length=120, blank=True,
                                 help_text='Bank reference, or the gateway payment id.')
    note = models.TextField(blank=True, help_text='Anything staff need to remember about it.')

    # Who captured it, and who stood behind it. Both are staff; on a gateway
    # payment neither is set because nobody keyed it in.
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                    null=True, blank=True, related_name='payment_proofs_recorded')
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                    null=True, blank=True, related_name='payment_proofs_verified')
    verified_at = models.DateTimeField(null=True, blank=True)
    # How much access this proof bought, when it was captured as part of a grant.
    granted_months = models.PositiveSmallIntegerField(
        default=0, help_text='Months of module access granted off the back of this payment.')

    class Meta:
        ordering = ['-paid_on', '-created_at']
        verbose_name = 'Proof of payment'
        verbose_name_plural = 'Proofs of payment'
        indexes = [models.Index(fields=['person', '-created_at'])]

    def __str__(self):
        return f'{self.person} · R{self.amount} · {self.get_source_display()}'

    @property
    def is_image(self):
        name = (self.original_name or self.document.name or '').lower()
        return name.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.heic'))

    @property
    def is_pdf(self):
        return (self.original_name or self.document.name or '').lower().endswith('.pdf')


# ---------------------------------------------------------------------------
# Estimates (quotes)
# ---------------------------------------------------------------------------
class Estimate(TimeStampedModel):
    """A quote: what something will cost, before anyone owes anything.

    Laid out like the invoice (same PDF family). Accepted estimates convert to a
    draft invoice in one step, carrying every line across.
    """

    STATUS_DRAFT = 'draft'
    STATUS_SENT = 'sent'
    STATUS_VIEWED = 'viewed'
    STATUS_ACCEPTED = 'accepted'
    STATUS_DECLINED = 'declined'
    STATUS_EXPIRED = 'expired'
    STATUS_CONVERTED = 'converted'
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'), (STATUS_SENT, 'Sent'), (STATUS_VIEWED, 'Viewed'),
        (STATUS_ACCEPTED, 'Accepted'), (STATUS_DECLINED, 'Declined'),
        (STATUS_EXPIRED, 'Expired'), (STATUS_CONVERTED, 'Converted to invoice'),
    ]
    VALID_DAYS = 30

    number = models.CharField(max_length=40, unique=True, blank=True)
    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='estimates')
    issue_date = models.DateField(default=timezone.now)
    valid_until = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_DRAFT, db_index=True)
    summary = models.CharField(max_length=200, blank=True)
    po_number = models.CharField('P.O. / reference', max_length=60, blank=True)
    notes = models.TextField(blank=True)
    footer = models.CharField(max_length=255, blank=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tax_inclusive = models.BooleanField(default=True)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    sent_at = models.DateTimeField(null=True, blank=True)
    viewed_at = models.DateTimeField(null=True, blank=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    converted_invoice = models.OneToOneField(Invoice, on_delete=models.SET_NULL, null=True, blank=True,
                                             related_name='from_estimate')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                                   blank=True, related_name='+')

    class Meta:
        ordering = ['-issue_date', '-id']

    def __str__(self):
        return self.number

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = DocumentSequence.next_number('EST')
        if self._state.adding:
            from datetime import timedelta
            if not self.valid_until:
                self.valid_until = as_date(self.issue_date) + timedelta(days=self.VALID_DAYS)
            if not self.tax_rate:
                self.tax_rate, self.tax_inclusive = vat_defaults()
        super().save(*args, **kwargs)

    def recalc_total(self):
        aggregated = self.items.aggregate(total=models.Sum('amount'), discount=models.Sum('discount_amount'))
        self.subtotal = aggregated['total'] or Decimal('0')
        self.discount_total = aggregated['discount'] or Decimal('0')
        self.tax_amount = vat_portion(self.subtotal, self.tax_rate, inclusive=self.tax_inclusive)
        self.total = self.subtotal if (self.tax_inclusive or not self.tax_rate) else self.subtotal + self.tax_amount
        self.save(update_fields=['subtotal', 'discount_total', 'tax_amount', 'total', 'updated_at'])

    @property
    def gross_subtotal(self):
        return (self.subtotal or 0) + (self.discount_total or 0)

    @property
    def is_tax_invoice(self):
        return bool(self.tax_rate) and self.tax_rate > 0

    @property
    def is_expired(self):
        return bool(self.valid_until and self.valid_until < timezone.localdate()
                    and self.status in (self.STATUS_DRAFT, self.STATUS_SENT, self.STATUS_VIEWED))

    @property
    def bill_to_name(self):
        return (self.customer.get_full_name() or '').strip() or self.customer.get_username()

    def get_absolute_url(self):
        return reverse('finance:estimate-detail', args=[self.pk])

    def get_public_url(self):
        return reverse('finance:estimate-public', args=[self.public_id])


class EstimateItem(models.Model):
    estimate = models.ForeignKey(Estimate, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('shop.Product', on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='estimate_items')
    description = models.CharField(max_length=255, blank=True)
    detail = models.CharField(max_length=255, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return self.description

    @property
    def gross_amount(self):
        return (self.unit_price or 0) * (self.quantity or 0)

    def save(self, *args, **kwargs):
        if self.product_id:
            if not self.description:
                self.description = self.product.name[:255]
            if not self.unit_price:
                self.unit_price = self.product.price or 0
        gross = Decimal(str(self.gross_amount))
        if self.discount_percent:
            self.discount_amount = (gross * Decimal(str(self.discount_percent)) / 100).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP)
        self.discount_amount = min(Decimal(str(self.discount_amount or 0)), gross)
        self.amount = gross - self.discount_amount
        super().save(*args, **kwargs)


# ---------------------------------------------------------------------------
# Expenses
# ---------------------------------------------------------------------------
class ExpenseCategory(models.Model):
    """An expense account ("Software & subscriptions"), grouped for the P&L."""

    GROUP_COST_OF_SALES = 'cost_of_sales'
    GROUP_OPERATING = 'operating'
    GROUP_PAYROLL = 'payroll'
    GROUP_OTHER = 'other'
    GROUP_CHOICES = [
        (GROUP_COST_OF_SALES, 'Cost of sales'), (GROUP_PAYROLL, 'Staff & educators'),
        (GROUP_OPERATING, 'Operating expenses'), (GROUP_OTHER, 'Other expenses'),
    ]

    name = models.CharField(max_length=120, unique=True)
    code = models.CharField(max_length=20, blank=True, help_text='Account code for your accountant, optional.')
    group = models.CharField(max_length=20, choices=GROUP_CHOICES, default=GROUP_OPERATING)
    description = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['group', 'name']
        verbose_name_plural = 'Expense categories'

    def __str__(self):
        return self.name


class Vendor(TimeStampedModel):
    """Who got paid — a supplier, landlord, contractor or educator."""

    name = models.CharField(max_length=160, unique=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    vat_number = models.CharField(max_length=30, blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


PAID_THROUGH_CHOICES = [
    ('bank', 'Business bank account'), ('card', 'Business card'), ('cash', 'Petty cash'),
    ('payfast', 'PayFast balance'), ('debit_order', 'Debit order'), ('owner', 'Paid personally (to reimburse)'),
]
EXPENSE_VAT_CHOICES = [('inclusive', 'Amount includes VAT'), ('none', 'No VAT')]


class Expense(TimeStampedModel):
    """Money going out, with the fields an accountant asks for."""

    STATUS_PAID = 'paid'
    STATUS_UNPAID = 'unpaid'
    STATUS_CHOICES = [(STATUS_PAID, 'Paid'), (STATUS_UNPAID, 'Unpaid (bill to pay)')]

    date = models.DateField(default=timezone.localdate, db_index=True)
    category = models.ForeignKey(ExpenseCategory, on_delete=models.PROTECT, related_name='expenses')
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True, related_name='expenses')
    description = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=12, decimal_places=2, help_text='Total paid, in rand.')
    vat_treatment = models.CharField('VAT', max_length=10, choices=EXPENSE_VAT_CHOICES, default='inclusive')
    vat_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    paid_through = models.CharField(max_length=15, choices=PAID_THROUGH_CHOICES, default='bank')
    reference = models.CharField('Reference #', max_length=80, blank=True)
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default=STATUS_PAID)
    due_date = models.DateField(null=True, blank=True, help_text='For unpaid bills.')
    receipt = models.FileField(upload_to='expenses/%Y/%m/', blank=True, validators=v.validate_attachment)
    notes = models.TextField(blank=True)
    institution = models.ForeignKey('learning.Institution', on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='expenses', help_text='Cost centre. Blank = the whole business.')
    recurring = models.ForeignKey('RecurringExpense', on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='expenses')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                                   blank=True, related_name='+')

    class Meta:
        ordering = ['-date', '-id']

    def __str__(self):
        return f'{self.date} · {self.description} · R{self.amount}'

    @property
    def amount_excl_vat(self):
        return (self.amount or 0) - (self.vat_amount or 0)

    def save(self, *args, **kwargs):
        if self.vat_treatment == 'inclusive' and getattr(settings, 'VAT_REGISTERED', False):
            self.vat_amount = vat_portion(self.amount, getattr(settings, 'VAT_RATE', 15), inclusive=True)
        elif self.vat_treatment == 'none':
            self.vat_amount = Decimal('0')
        super().save(*args, **kwargs)


class RecurringExpense(TimeStampedModel):
    """A cost that repeats — rent, licences, a retainer — and books itself."""

    FREQ_WEEKLY = 'weekly'
    FREQ_MONTHLY = 'monthly'
    FREQ_YEARLY = 'yearly'
    FREQ_CHOICES = [(FREQ_WEEKLY, 'Week(s)'), (FREQ_MONTHLY, 'Month(s)'), (FREQ_YEARLY, 'Year(s)')]

    name = models.CharField('Profile name', max_length=120)
    category = models.ForeignKey(ExpenseCategory, on_delete=models.PROTECT, related_name='recurring')
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True, related_name='recurring')
    description = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    vat_treatment = models.CharField('VAT', max_length=10, choices=EXPENSE_VAT_CHOICES, default='inclusive')
    paid_through = models.CharField(max_length=15, choices=PAID_THROUGH_CHOICES, default='debit_order')
    institution = models.ForeignKey('learning.Institution', on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='recurring_expenses')
    notes = models.TextField(blank=True)
    every = models.PositiveSmallIntegerField('Repeat every', default=1)
    frequency = models.CharField(max_length=8, choices=FREQ_CHOICES, default=FREQ_MONTHLY)
    start_date = models.DateField(default=timezone.localdate)
    end_date = models.DateField(null=True, blank=True, help_text='Blank = never ends.')
    next_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                                   blank=True, related_name='+')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.next_date:
            self.next_date = self.start_date
        super().save(*args, **kwargs)

    def advance(self, day):
        """The date after ``day`` in this profile's rhythm."""
        from datetime import timedelta
        if self.frequency == self.FREQ_WEEKLY:
            return day + timedelta(weeks=self.every)
        months = self.every * (12 if self.frequency == self.FREQ_YEARLY else 1)
        month = day.month - 1 + months
        year = day.year + month // 12
        month = month % 12 + 1
        import calendar
        # Keep the anchor day (31st → last day of a shorter month).
        anchor = self.start_date.day
        return day.replace(year=year, month=month, day=min(anchor, calendar.monthrange(year, month)[1]))

    @property
    def monthly_equivalent(self):
        amount = Decimal(str(self.amount or 0))
        if self.frequency == self.FREQ_WEEKLY:
            return (amount * Decimal('52') / Decimal('12') / self.every).quantize(Decimal('0.01'))
        if self.frequency == self.FREQ_YEARLY:
            return (amount / Decimal('12') / self.every).quantize(Decimal('0.01'))
        return (amount / self.every).quantize(Decimal('0.01'))
