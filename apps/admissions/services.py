"""Admissions services — fees on enrolment, submission, decisions, parent invites.

The fee rules are the prospectus's (Fees 2026):

* **Registration** (new learners only, non-refundable), the **annual levy** and
  the **first month's school fees** are due on enrolment.
* Fees are paid monthly in advance thereafter, January to December.
* **Sibling discount**: 5% on school fees only (never levy or registration),
  from the second child at UCS onwards.

One invoice carries those lines and is linked to the learner's subject
enrolments, so paying it (PayFast, or the office marking an EFT / card payment)
unlocks every subject in the grade for the month — the same unlock path the
rest of the platform uses (``apps.learning.enrolment.activate_modules_for_invoice``).
"""
import logging
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from core import school

from .models import Application, Guardian

logger = logging.getLogger('admissions')


def application_for(person, *, create=True):
    """The learner's application (created as a draft on first use)."""
    if person is None:
        return None
    application = Application.objects.filter(person=person).first()
    if application is None and create:
        application = Application.objects.create(
            person=person, year=school.YEAR, gender=person.gender or '')
    return application


def fee_lines(programme, *, new_learner=True, siblings=0, month_label=None):
    """``[(description, amount, discount_percent)]`` due on enrolment in ``programme``."""
    if programme is None:
        return []
    grade = programme.display_name
    month_label = month_label or timezone.now().strftime('%B %Y')
    lines = []
    if new_learner and programme.registration_fee:
        lines.append((f'Registration fee — new learner, {grade} (non-refundable)',
                      Decimal(programme.registration_fee), Decimal('0')))
    if programme.annual_levy:
        lines.append((f'Annual levy {school.YEAR} — {grade}', Decimal(programme.annual_levy),
                      Decimal('0')))
    if programme.monthly_fee:
        discount = school.SIBLING_DISCOUNT_PCT if siblings else Decimal('0')
        label = f'School fees — {month_label}, {grade}'
        if discount:
            label += f' (sibling discount {discount:.0f}%)'
        lines.append((label, Decimal(programme.monthly_fee), discount))
    return lines


def fee_summary(programme, *, new_learner=True, siblings=0):
    """What the review step shows: the lines, the total due now and the year."""
    lines = fee_lines(programme, new_learner=new_learner, siblings=siblings)
    due = sum((amount - (amount * pct / 100) for _, amount, pct in lines), Decimal('0'))
    return {
        'lines': [{'label': label, 'amount': amount, 'discount_pct': pct,
                   'net': (amount - amount * pct / 100).quantize(Decimal('0.01'))}
                  for label, amount, pct in lines],
        'due_now': due.quantize(Decimal('0.01')),
        'monthly': Decimal(programme.monthly_fee or 0),
        'annual': programme.annual_fees,
        'annual_new': programme.annual_fees_new_learner,
        'registration': Decimal(programme.registration_fee or 0),
        'levy': Decimal(programme.annual_levy or 0),
    }


@transaction.atomic
def raise_enrolment_invoice(person, application, enrolments):
    """One invoice for registration + levy + first month, linked to every
    subject enrolment and the application. ``None`` when nothing is due."""
    from apps.finance.models import Invoice, InvoiceItem
    from apps.learning.models import ModuleEnrolment

    lines = fee_lines(application.programme, new_learner=application.is_new_learner,
                      siblings=application.siblings_at_ucs)
    if not lines:
        return None
    invoice = Invoice.objects.create(customer=person.user, created_by=person.user,
                                     status=Invoice.STATUS_SENT)
    invoice.summary = f'Enrolment at United Church School — {application.programme.display_name}'
    invoice.save(update_fields=['summary'])
    for label, amount, pct in lines:
        InvoiceItem.objects.create(invoice=invoice, description=label[:255], quantity=1,
                                   unit_price=amount, discount_percent=pct)
    invoice.recalc_total()
    invoice.refresh_status()
    ModuleEnrolment.objects.filter(pk__in=[e.pk for e in enrolments]).update(
        invoice_uid=invoice.public_id)
    application.invoice_uid = invoice.public_id
    application.save(update_fields=['invoice_uid', 'updated_at'])
    return invoice


def submit(application):
    """Mark the application submitted (or documents-outstanding)."""
    application.submitted_at = application.submitted_at or timezone.now()
    if application.status == Application.STATUS_DRAFT:
        application.status = (Application.STATUS_DOCUMENTS if application.missing_documents()
                               else Application.STATUS_SUBMITTED)
    application.save(update_fields=['submitted_at', 'status', 'updated_at'])
    return application


def refresh_status(application, *, paid=None):
    """Move an open application along as documents and payment arrive.

    The pack: "the application is pending until payment is received". Once
    paid and documented it goes to the office for review."""
    if application.status not in (Application.STATUS_SUBMITTED, Application.STATUS_DOCUMENTS,
                                  Application.STATUS_REVIEW):
        return application
    if paid is None:
        paid = invoice_is_paid(application)
    if application.missing_documents():
        new = Application.STATUS_DOCUMENTS
    elif paid or not application.invoice_uid:
        new = Application.STATUS_REVIEW
    else:
        new = Application.STATUS_SUBMITTED
    if new != application.status:
        application.status = new
        application.save(update_fields=['status', 'updated_at'])
    return application


def invoice_is_paid(application):
    if not application.invoice_uid:
        return False
    from apps.finance.models import Invoice
    invoice = Invoice.objects.filter(public_id=application.invoice_uid).first()
    return bool(invoice and invoice.status == Invoice.STATUS_PAID)


def on_invoice_paid(invoice):
    """``invoice_paid`` receiver body: advance the application the invoice belongs to."""
    application = Application.objects.filter(invoice_uid=invoice.public_id).first()
    if application is not None:
        refresh_status(application, paid=True)


@transaction.atomic
def decide(application, user, status, note=''):
    """Admit or decline (or withdraw) an application."""
    from apps.learning.models import ProgrammeEnrolment

    application.status = status
    application.decided_by = user
    application.decided_at = timezone.now()
    if note:
        application.decision_note = note
    application.save()
    if application.programme_id:
        ProgrammeEnrolment.objects.filter(
            person=application.person, programme=application.programme).update(
            is_active=status == Application.STATUS_ADMITTED)
    return application


def invite_guardians(application, invited_by=None):
    """Invite each parent with an e-mail address to a parent account linked to
    the learner (max two, ``ParentLink.MAX_PER_STUDENT``). Idempotent."""
    from apps.accounts import emails
    from apps.accounts.models import Invitation, ParentLink

    person = application.person
    sent = []
    for guardian in application.guardians.exclude(email=''):
        if guardian.invite_sent_at:
            continue
        if person.user_id and not ParentLink.can_add_parent(person.user):
            break
        if person.user_id and guardian.email.lower() == (person.user.email or '').lower():
            continue                      # the parent IS the account holder
        invite = Invitation.objects.create(role=Invitation.ROLE_PARENT, email=guardian.email,
                                           student=person, invited_by=invited_by)
        try:
            emails.send_invite(invite)
        except Exception:  # pragma: no cover - e-mail is best-effort
            logger.exception('admissions: parent invite e-mail failed')
        guardian.invite_sent_at = timezone.now()
        guardian.save(update_fields=['invite_sent_at', 'updated_at'])
        sent.append(guardian.email)
    return sent


def save_guardians(application, guardian_forms):
    """Persist the filled-in parent forms (each bound to
    :func:`guardian_instance`); delete a role that was cleared."""
    for form in guardian_forms:
        if form.is_blank:
            if form.instance.pk:
                form.instance.delete()
            continue
        guardian = form.save(commit=False)
        guardian.application = application
        guardian.role = form.role
        guardian.save()


def guardian_instance(application, role):
    return application.guardians.filter(role=role).first() or Guardian(application=application,
                                                                         role=role)
