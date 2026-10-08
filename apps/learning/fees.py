"""School fees — billed per GRADE, per calendar month, paid in advance.

United Church School charges a learner's grade, not their subjects: every
subject in the grade opens when the month's school fees are paid, and locks
when a month goes unpaid (after the ``FEES_GRACE_DAYS`` grace period). A family
may pay any number of months ahead — "pay for the 1st month, or more" — up to
December of the school year.

* :func:`fee_status` — how far a learner's fees are paid and what is owing.
* :func:`fee_options` — the "pay N months" choices with their amounts.
* :func:`raise_fees_invoice` — one invoice for N months (reuses an open one).
* :func:`apply_paid_invoice` — the ``invoice_paid`` hook: unlock the grade's
  subjects for exactly the months the invoice covers.
* :func:`run_monthly_billing` — the scheduler job: on the 1st, invoice every
  learner whose month is not yet paid.

An invoice records what it pays for on itself (``fee_programme``,
``fee_start``, ``fee_months``), so the unlock never depends on line text.
"""
import logging
from datetime import date, timedelta
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from core import school

logger = logging.getLogger('apps.learning.fees')


# --------------------------------------------------------------------------
# Where a learner stands
# --------------------------------------------------------------------------
def _today():
    return timezone.localdate()


def current_programme(person):
    """The learner's active fee-paying grade (newest enrolment), or ``None``."""
    from .models import ProgrammeEnrolment
    row = (ProgrammeEnrolment.objects.filter(person=person, is_active=True)
           .select_related('programme', 'cohort').order_by('-created_at').first())
    return row.programme if row else None


def _enrolments(person, programme):
    from .models import ModuleEnrolment
    return ModuleEnrolment.objects.filter(person=person, programme_module__programme=programme)


def paid_until(person, programme):
    """The last day the grade's fees are paid to (``None`` = nothing paid).
    The grade is only as paid as its least-paid subject."""
    dates = [row.paid_until for row in _enrolments(person, programme)
             if row.status == row.STATUS_ACTIVE and row.paid_until]
    return min(dates) if dates else None


def next_unpaid_month(person, programme, today=None):
    """The first calendar month (as its 1st day) not yet paid."""
    today = today or _today()
    until = paid_until(person, programme)
    if until and until >= today:
        return school.add_months(school.month_start(until), 1)
    return school.month_start(today)


def months_left_in_year(first):
    """Months from ``first`` to December of its year, inclusive."""
    return 12 - first.month + 1


def open_fees_invoice(person, programme):
    """An unpaid school-fees invoice already raised for this learner and grade."""
    from apps.finance.models import Invoice
    return (Invoice.objects.filter(customer=person.user, fee_programme=programme, fee_months__gt=0)
            .exclude(status__in=[Invoice.STATUS_PAID, Invoice.STATUS_CANCELLED])
            .order_by('-created_at').first())


def fee_status(person, programme=None, today=None):
    """Everything the fees page and the lock screen need."""
    today = today or _today()
    programme = programme or current_programme(person)
    if programme is None:
        return None
    until = paid_until(person, programme)
    grace = school.FEES_GRACE_DAYS
    try:
        from django.conf import settings
        grace = getattr(settings, 'FEES_GRACE_DAYS', grace)
    except Exception:  # pragma: no cover
        pass
    first_unpaid = next_unpaid_month(person, programme, today)
    current_paid = bool(until and until >= today)
    return {
        'programme': programme,
        'monthly': Decimal(programme.monthly_fee or 0),
        'paid_until': until,
        'current_month_paid': current_paid,
        'locked': bool(programme.monthly_fee) and not (
            until and (until + timedelta(days=grace)) >= today),
        'first_unpaid': first_unpaid,
        'months_owing': 0 if current_paid else (
            (today.year - first_unpaid.year) * 12 + today.month - first_unpaid.month + 1),
        'open_invoice': open_fees_invoice(person, programme),
        'grace_days': grace,
        'options': fee_options(programme, first_unpaid, today=today, person=person),
    }


# --------------------------------------------------------------------------
# What a family can choose to pay
# --------------------------------------------------------------------------
def _sibling_discount(person):
    latest = person.applications.order_by('-year').first() if person is not None else None
    return school.SIBLING_DISCOUNT_PCT if (latest and latest.siblings_at_ucs) else Decimal('0')


def _prepay_discount(first, months, today):
    """5% for the FULL school year paid on or before 31 January."""
    full_year = first.month == 1 and months >= school.FEE_MONTHS_PER_YEAR
    in_time = today <= date(first.year, 1, 31)
    return school.ANNUAL_PREPAY_DISCOUNT_PCT if (full_year and in_time) else Decimal('0')


def fee_lines(programme, first, months, *, person=None, today=None):
    """``[(description, unit_price, discount_pct, quantity)]`` for N months."""
    today = today or _today()
    monthly = Decimal(programme.monthly_fee or 0)
    if not monthly or months < 1:
        return []
    discount = max(_sibling_discount(person), _prepay_discount(first, months, today))
    label = f'School fees — {school.months_label(first, months)}, {programme.display_name}'
    if discount:
        reason = ('full year paid by 31 January' if _prepay_discount(first, months, today)
                  else 'sibling discount')
        label += f' ({reason}: {discount:.0f}%)'
    return [(label, monthly, discount, months)]


def fee_options(programme, first, *, today=None, person=None):
    """The "pay N months" choices from ``first`` to December."""
    today = today or _today()
    if not programme.monthly_fee:
        return []
    remaining = months_left_in_year(first)
    choices = sorted({1, 2, 3, 6, remaining} & set(range(1, remaining + 1)))
    options = []
    for months in choices:
        lines = fee_lines(programme, first, months, person=person, today=today)
        gross = sum((unit * qty for _label, unit, _pct, qty in lines), Decimal('0'))
        net = sum((unit * qty * (100 - pct) / 100 for _label, unit, pct, qty in lines), Decimal('0'))
        last = school.add_months(first, months - 1)
        options.append({
            'months': months, 'gross': gross.quantize(Decimal('0.01')),
            'amount': net.quantize(Decimal('0.01')), 'saving': (gross - net).quantize(Decimal('0.01')),
            'label': school.months_label(first, months),
            'until': school.month_end(last),
            'rest_of_year': months == remaining,
        })
    return options


# --------------------------------------------------------------------------
# Invoicing and unlocking
# --------------------------------------------------------------------------
def tag_fees(invoice, programme, first, months):
    """Record on the invoice which grade and months it pays for."""
    invoice.fee_programme = programme
    invoice.fee_start = first
    invoice.fee_months = months
    invoice.save(update_fields=['fee_programme', 'fee_start', 'fee_months', 'updated_at'])
    return invoice


@transaction.atomic
def raise_fees_invoice(person, programme, months=1, first=None, *, reuse=True, today=None):
    """One invoice for ``months`` of school fees from ``first`` (default: the
    first unpaid month). An open fees invoice for the same months is reused."""
    from apps.finance.models import Invoice, InvoiceItem
    from .models import ModuleEnrolment

    today = today or _today()
    if not programme.monthly_fee:
        return None
    first = school.month_start(first or next_unpaid_month(person, programme, today))
    months = max(1, min(int(months or 1), months_left_in_year(first)))
    if reuse:
        existing = open_fees_invoice(person, programme)
        if existing is not None and existing.fee_start == first and existing.fee_months == months:
            return existing
        if existing is not None and existing.fee_start == first and not existing.payments.exists():
            existing.status = Invoice.STATUS_CANCELLED          # superseded by a new choice
            existing.save(update_fields=['status', 'updated_at'])
    invoice = Invoice.objects.create(customer=person.user, created_by=person.user,
                                     status=Invoice.STATUS_SENT, due_date=first)
    invoice.summary = f'School fees — {programme.display_name}'
    invoice.save(update_fields=['summary'])
    for label, unit, pct, qty in fee_lines(programme, first, months, person=person, today=today):
        InvoiceItem.objects.create(invoice=invoice, description=label[:255], quantity=qty,
                                   unit_price=unit, discount_percent=pct)
    invoice.recalc_total()
    invoice.refresh_status()
    tag_fees(invoice, programme, first, months)
    ModuleEnrolment.objects.filter(person=person, programme_module__programme=programme).update(
        invoice_uid=invoice.public_id)
    return invoice


def _person_for_invoice(invoice):
    return getattr(invoice.customer, 'profile', None)


@transaction.atomic
def apply_paid_invoice(invoice):
    """Unlock every subject in the invoice's grade for the months it covers.
    Idempotent: re-applying never shortens or double-counts access."""
    if not invoice.fee_months or not invoice.fee_programme_id:
        return []
    person = _person_for_invoice(invoice)
    if person is None:
        return []
    rows = list(_enrolments(person, invoice.fee_programme))
    for row in rows:
        row.activate(months=invoice.fee_months, start=invoice.fee_start)
    return rows


def sync_paid_fees(person, programme):
    """Re-apply every paid fees invoice for this grade — used when a learner is
    enrolled after paying (e.g. a returning learner who paid January early)."""
    from apps.finance.models import Invoice
    applied = 0
    for invoice in Invoice.objects.filter(customer=person.user, fee_programme=programme,
                                          fee_months__gt=0, status=Invoice.STATUS_PAID):
        applied += bool(apply_paid_invoice(invoice))
    return applied


# --------------------------------------------------------------------------
# The monthly run
# --------------------------------------------------------------------------
def run_monthly_billing(today=None, send=True):
    """Invoice the current month for every learner whose grade charges fees,
    whose month is not yet paid and who has no open fees invoice. Runs every
    few hours; does nothing twice."""
    from .models import ProgrammeEnrolment

    today = today or _today()
    month = school.month_start(today)
    raised = 0
    rows = (ProgrammeEnrolment.objects.filter(is_active=True, programme__monthly_fee__gt=0,
                                              person__user__is_active=True)
            .select_related('person__user', 'programme'))
    for row in rows:
        person, programme = row.person, row.programme
        if not _enrolments(person, programme).exists():
            continue
        until = paid_until(person, programme)
        if until and until >= school.month_end(month):
            continue
        if open_fees_invoice(person, programme) is not None:
            continue
        invoice = raise_fees_invoice(person, programme, months=1, first=month, today=today)
        if invoice is None:
            continue
        raised += 1
        if send:
            try:
                from apps.finance.emails import send_invoice_email
                send_invoice_email(invoice)
            except Exception:  # pragma: no cover - best effort
                logger.exception('fees: could not e-mail invoice %s', invoice.number)
    return f'{raised} school-fees invoice(s) raised for {month:%B %Y}'
