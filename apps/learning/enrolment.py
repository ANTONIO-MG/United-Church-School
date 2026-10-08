"""Registration & billing services for the school → grade → subject spine.

A learner registers in one :class:`Programme` (a grade) and its
:class:`ProgrammeModule` offerings (subjects). At United Church School fees are
charged **per grade, per month** (:attr:`Programme.monthly_fee`, plus the
registration fee and annual levy on enrolment — see
``apps.admissions.services``); a subject only carries its own
:attr:`ProgrammeModule.price_per_month` for an extra paid offering. A subject in
a fee-paying grade is created LOCKED and is unlocked by paying the invoice
raised for it (PayFast or EFT / the school office). Each paid month extends
access by a month; when it lapses, :func:`unlock_single_module` raises the next
month's school-fees invoice. All of it is idempotent so the wizard can be
replayed and the payment webhook can fire more than once.

Import cycle note: finance is imported lazily inside the functions (learning must
not import finance at module load), and the invoice is linked to each enrolment
by its ``public_id`` (:attr:`ModuleEnrolment.invoice_uid`), not an FK.
"""
from decimal import Decimal

from django.db import transaction

from apps.learning.models import ProgrammeModule
from .models import ModuleEnrolment, ProgrammeEnrolment


def _resolve_cohort(programme, cohort_id):
    """The Cohort an enrolment belongs to.

    A numeric ``cohort_id`` selects that intake. Anything else (the ``'year'``
    fallback the registration picker shows, or no choice at all) means the
    programme has no named intakes, so the **current academic year** stands in as
    its cohort — get-or-created here so every enrolment still belongs to a group
    (per-cohort chats/schedule/materials hang off it). Programmes that DO run
    named intakes are left unset rather than invented a year cohort."""
    from django.utils import timezone

    from .models import Cohort
    if cohort_id and str(cohort_id).isdigit():
        chosen = Cohort.objects.filter(pk=int(cohort_id), programme=programme).first()
        if chosen is not None:
            return chosen
    if programme.cohorts.filter(is_active=True).exists():
        return None
    year = timezone.now().year
    cohort, _ = Cohort.objects.get_or_create(
        programme=programme, code=str(year), defaults={'name': f'{year} intake'})
    return cohort


@transaction.atomic
def register_modules(person, programme, module_ids, cohort_id=None):
    """Create the :class:`ProgrammeEnrolment` and one LOCKED
    :class:`ModuleEnrolment` per selected module. Reuses existing rows so a
    repeated registration never duplicates. When ``cohort_id`` is a cohort of
    the programme, it is recorded on the ProgrammeEnrolment (the student's
    current intake). Returns the ModuleEnrolment rows."""
    prog_enrolment, _ = ProgrammeEnrolment.objects.get_or_create(
        person=person, programme=programme, defaults={'is_active': True})
    cohort = _resolve_cohort(programme, cohort_id)
    if cohort is not None and prog_enrolment.cohort_id != cohort.pk:
        prog_enrolment.cohort = cohort
        prog_enrolment.save(update_fields=['cohort', 'updated_at'])
    modules = list(ProgrammeModule.objects.filter(
        pk__in=module_ids, programme=programme, is_active=True))
    enrolments = []
    for module in modules:
        enrolment, _ = ModuleEnrolment.objects.get_or_create(
            person=person, programme_module=module,
            defaults={'price_at_enrolment': module.price_per_month or 0})
        enrolments.append(enrolment)
    return enrolments


def modules_total(enrolments):
    """Sum of the monthly prices of a set of ModuleEnrolments (Decimal)."""
    return sum((Decimal(str(e.price or 0)) for e in enrolments), Decimal('0'))


@transaction.atomic
def start_trial(enrolments):
    """Begin the 7-day free trial ("week one") on each still-locked module."""
    for enrolment in enrolments:
        if enrolment.status == ModuleEnrolment.STATUS_LOCKED:
            enrolment.start_trial()
    return enrolments


@transaction.atomic
def invoice_for_modules(person, enrolments, *, send_to_student=False):
    """Raise ONE finance invoice with a line per (separately priced) subject and
    link it to each of those ModuleEnrolments so payment unlocks exactly them.

    Returns the invoice, or ``None`` when nothing is chargeable (all free). When
    ``send_to_student`` is true the invoice PDF is e-mailed to the student (the
    EFT / pay-later path); the invoice also appears in the admin invoice list as
    an unpaid **sent** invoice for staff to see.
    """
    from apps.finance.models import Invoice, InvoiceItem

    priced = [e for e in enrolments if (e.price or 0) > 0]
    if not priced:
        return None

    invoice = Invoice.objects.create(
        customer=person.user, created_by=person.user, status=Invoice.STATUS_SENT)
    for enrolment in priced:
        module = enrolment.programme_module
        InvoiceItem.objects.create(
            invoice=invoice,
            description=f'{module.display_name} ({module.code}) — per month'[:255],
            quantity=1, unit_price=Decimal(str(enrolment.price or 0)),
        )
    invoice.recalc_total()
    invoice.refresh_status()
    ModuleEnrolment.objects.filter(pk__in=[e.pk for e in priced]).update(
        invoice_uid=invoice.public_id)

    if send_to_student:
        try:
            from apps.finance.emails import send_invoice_email
            send_invoice_email(invoice)
        except Exception as exc:  # e-mail is best-effort; the invoice still stands
            from core.errors import report
            report('MAIL-5001', exc=exc, context={'invoice': str(invoice.public_id), 'kind': 'module-invoice'})
    return invoice


@transaction.atomic
def activate_modules_for_invoice(invoice):
    """Unlock every module an invoice was raised for — called from the
    ``invoice_paid`` signal when the invoice settles (PayFast or a manual mark).
    Idempotent: activating an already-active module just extends it."""
    if invoice.fee_months:              # school fees: the grade, for the months paid
        from .fees import apply_paid_invoice
        return apply_paid_invoice(invoice)
    rows = list(ModuleEnrolment.objects.filter(invoice_uid=invoice.public_id))
    for enrolment in rows:
        enrolment.activate(months=1)
    return rows


def _open_invoice(public_id):
    from apps.finance.models import Invoice
    if not public_id:
        return None
    return (Invoice.objects.filter(public_id=public_id)
            .exclude(status=Invoice.STATUS_PAID)
            .exclude(status=Invoice.STATUS_CANCELLED).first())


def school_fees_invoice(person, programme, *, months=1, month=None):
    """The next unpaid month(s) of school fees for ``person`` in ``programme``
    (a grade) — one invoice covering every subject in the grade. Delegates to
    :func:`apps.learning.fees.raise_fees_invoice`; ``None`` when the grade
    charges no monthly fee."""
    from .fees import raise_fees_invoice
    first = month.date().replace(day=1) if hasattr(month, 'date') else month
    return raise_fees_invoice(person, programme, months=months, first=first)


@transaction.atomic
def unlock_single_module(person, programme_module):
    """Ensure a locked subject has an enrolment + an invoice to pay, used by the
    "click a locked subject → get an invoice" flow. Reuses the existing unpaid
    invoice if one is already linked (re-clicking never duplicates). In a
    fee-paying grade that invoice is the month's school fees, covering every
    subject in the grade (:func:`school_fees_invoice`).
    Returns (enrolment, invoice); invoice is ``None`` for a free subject."""
    ProgrammeEnrolment.objects.get_or_create(
        person=person, programme=programme_module.programme, defaults={'is_active': True})
    enrolment, _ = ModuleEnrolment.objects.get_or_create(
        person=person, programme_module=programme_module,
        defaults={'price_at_enrolment': programme_module.price_per_month or 0})

    invoice = _open_invoice(enrolment.invoice_uid)
    if invoice is None and not programme_module.price_per_month:
        invoice = school_fees_invoice(person, programme_module.programme)
    if invoice is None:
        invoice = invoice_for_modules(person, [enrolment])
    return enrolment, invoice
