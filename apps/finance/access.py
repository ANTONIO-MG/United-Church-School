"""Granting module access, and the payment that justified it.

A student's modules unlock in exactly three ways, and every one of them leaves a
money trail:

1. **The 7-day trial** — free, automatic, expires on its own
   (:meth:`apps.learning.models.ModuleEnrolment.start_trial`).
2. **PayFast settles the invoice** — the gateway callback activates the modules
   and :func:`record_gateway_proof` files the proof automatically.
3. **A staff member grants access manually** — :func:`grant_access`, which is
   the only manual route, and which *requires* a payment to be recorded in the
   same call.

That third point is the whole reason this module exists. Granting access and
recording the money are one operation, not two, so there is no path that opens a
student's account without leaving a record of why. Both are staff-only: the views
in :mod:`apps.finance.views` are behind an admin/staff check, and nothing in the
student-facing UI reaches these functions.
"""
from datetime import date
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from . import models


def _person_of(invoice):
    return getattr(getattr(invoice, 'customer', None), 'profile', None)


@transaction.atomic
def grant_access(person, *, amount, months=1, modules=None, granted_by=None,
                 document=None, method='bank', reference='', paid_on=None, note='',
                 invoice=None, source=None):
    """Open ``person``'s modules for ``months``, recording the payment behind it.

    ``modules`` is an iterable of :class:`~apps.learning.models.ModuleEnrolment`;
    omit it and every locked or expired module the person has is granted. Pass
    ``document`` (an uploaded image or PDF) to file the deposit slip with it.

    Returns ``(proof, payment, [module_enrolments])``. ``payment`` is ``None``
    when there was no invoice to book the money against — the proof still records
    it, so the amount is never lost.
    """
    from apps.learning.models import ModuleEnrolment

    amount = Decimal(str(amount or 0))
    months = max(1, int(months or 1))
    if modules is None:
        modules = list(ModuleEnrolment.objects.filter(person=person).exclude(
            status=ModuleEnrolment.STATUS_ACTIVE))
    else:
        modules = list(modules)

    # The invoice to book against: the one named, else the person's most recent
    # unpaid one, so a manual EFT lands on the bill it was meant for.
    if invoice is None and person is not None:
        invoice = (models.Invoice.objects
                   .filter(customer=person.user)
                   .exclude(status=models.Invoice.STATUS_PAID)
                   .order_by('-created_at').first())

    payment = None
    if invoice is not None and amount > 0:
        payment = models.InvoicePayment.objects.create(
            invoice=invoice, amount=amount, method=method,
            gateway=models.InvoicePayment.GATEWAY_MANUAL,
            status=models.InvoicePayment.STATUS_COMPLETED,
            reference=reference, paid_at=timezone.now())
        invoice.refresh_status()

    proof = models.ProofOfPayment(
        person=person, invoice=invoice, payment=payment,
        source=source or (models.ProofOfPayment.SOURCE_UPLOAD if document
                          else models.ProofOfPayment.SOURCE_MANUAL),
        status=models.ProofOfPayment.STATUS_VERIFIED,
        amount=amount, paid_on=paid_on or date.today(), reference=reference, note=note,
        recorded_by=granted_by, verified_by=granted_by, verified_at=timezone.now(),
        granted_months=months)
    if document is not None:
        proof.original_name = getattr(document, 'name', '')[:255]
        proof.content_type = getattr(document, 'content_type', '')[:100]
        proof.document = document
    proof.save()

    for enrolment in modules:
        enrolment.activate(months=months)
    return proof, payment, modules


def record_gateway_proof(invoice, payment):
    """File the proof for a payment the gateway settled.

    Called from the PayFast fulfilment path. There is no document to attach —
    the gateway reference is the evidence — and no staff member to credit,
    because nobody keyed it in.
    """
    person = _person_of(invoice)
    if person is None:
        return None
    reference = (getattr(payment, 'gateway_ref', '') or getattr(payment, 'reference', '')
                 or str(invoice.public_id))
    proof, _ = models.ProofOfPayment.objects.get_or_create(
        person=person, payment=payment,
        defaults={
            'invoice': invoice,
            'source': models.ProofOfPayment.SOURCE_GATEWAY,
            'status': models.ProofOfPayment.STATUS_VERIFIED,
            'amount': getattr(payment, 'amount', 0) or 0,
            'paid_on': timezone.localdate(getattr(payment, 'paid_at', None) or timezone.now()),
            'reference': reference,
            'note': 'Settled online — recorded automatically by the payment gateway.',
            'verified_at': timezone.now(),
        })
    return proof


def payment_history(person):
    """Everything on record for this student, newest first — for their profile
    page and for the staff view of the account."""
    return (models.ProofOfPayment.objects
            .filter(person=person)
            .select_related('invoice', 'payment', 'recorded_by')
            .order_by('-paid_on', '-created_at'))


def access_state(person):
    """A one-glance summary of where this student stands.

    ``{'status': 'active'|'trial'|'locked'|'none', 'until': date|None,
    'days_left': int|None, 'modules': int, 'locked_modules': int}``.
    """
    from apps.learning.models import ModuleEnrolment

    enrolments = list(ModuleEnrolment.objects.filter(person=person))
    if not enrolments:
        return {'status': 'none', 'until': None, 'days_left': None,
                'modules': 0, 'locked_modules': 0}

    unlocked = [e for e in enrolments if e.is_unlocked]
    locked = [e for e in enrolments if not e.is_unlocked]
    active = [e for e in unlocked if e.status == ModuleEnrolment.STATUS_ACTIVE]
    trial = [e for e in unlocked if e.status == ModuleEnrolment.STATUS_TRIAL]

    if active:
        until = max((e.paid_until for e in active if e.paid_until), default=None)
        status = 'active'
    elif trial:
        ends = max((e.trial_ends_at for e in trial if e.trial_ends_at), default=None)
        until = timezone.localdate(ends) if ends else None
        status = 'trial'
    else:
        until, status = None, 'locked'

    days_left = (until - timezone.localdate()).days if until else None
    return {'status': status, 'until': until, 'days_left': days_left,
            'modules': len(enrolments), 'locked_modules': len(locked)}
