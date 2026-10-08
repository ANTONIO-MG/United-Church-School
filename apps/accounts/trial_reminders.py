"""The nudge that goes out a day before a student's free week runs out.

A student who takes the seven-day pass has the whole platform open while their
registration invoice sits unpaid. If the week ends with the invoice still open,
their modules lock — so one reminder goes out roughly 24 hours before that
happens, with the invoice attached and a pay link.

It is deliberately narrow. A reminder is sent only when *all* of these hold:

* the enrolment is still on the trial (not already paid, not already expired);
* the trial ends inside the next 24 hours;
* the invoice behind it still has a balance — a student whose invoice was
  settled, or written off/marked paid by an admin, is never chased;
* nothing has been sent for that invoice already.

The "already sent" mark is the invoice's own ``reminder_sent_at`` if the finance
model has one, and otherwise a Notification row keyed to the invoice — so the
job is safe to run on every tick of the scheduler and still e-mails once.
"""

import datetime
import logging

from django.utils import timezone

from core.utils import absolute_url

logger = logging.getLogger(__name__)

#: How close to the end of the trial the reminder goes out.
REMIND_WITHIN = datetime.timedelta(hours=24)

#: Marker text on the Notification row that records a sent reminder.
_MARK_VERB = 'trial-ending-reminder'


def _already_reminded(user, invoice):
    """True when this invoice has already had its one reminder."""
    from apps.communication.models import Notification
    return Notification.objects.filter(
        recipient=user, verb=_MARK_VERB, url__contains=str(invoice.public_id)).exists()


def _mark_reminded(user, invoice):
    from apps.communication.models import Notification
    Notification.objects.create(
        recipient=user, verb=_MARK_VERB,
        title='Free week ending — invoice reminder sent',
        body=f'Reminder e-mail sent for invoice {invoice.number}.',
        url=invoice.get_pay_url(),
        level='warning',
    )


def due_enrolments(now=None):
    """Trial enrolments whose week ends within the next 24 hours.

    Grouped by invoice, because a student registers several modules at once on
    one invoice and must get one e-mail, not one per module.
    """
    from apps.learning.models import ModuleEnrolment

    now = now or timezone.now()
    rows = (ModuleEnrolment.objects
            .filter(status=ModuleEnrolment.STATUS_TRIAL,
                    trial_ends_at__gt=now,
                    trial_ends_at__lte=now + REMIND_WITHIN,
                    invoice_uid__isnull=False)
            .select_related('person__user', 'programme_module'))

    grouped = {}
    for row in rows:
        grouped.setdefault(row.invoice_uid, []).append(row)
    return grouped


def send_trial_reminders(now=None):
    """Send the reminders due right now. Returns a short summary string.

    Wired into the scheduler as the ``trial-ending-reminders`` job.
    """
    from apps.communication import emails
    from apps.finance.models import Invoice
    from apps.finance.pdf import render_invoice_pdf

    now = now or timezone.now()
    sent = skipped = 0

    for invoice_uid, enrolments in due_enrolments(now).items():
        invoice = Invoice.objects.filter(public_id=invoice_uid).first()
        if invoice is None:
            continue

        # Paid, or marked paid / written off by admin or staff — leave them be.
        if invoice.balance <= 0 or invoice.status == Invoice.STATUS_PAID:
            skipped += 1
            continue

        person = enrolments[0].person
        user = getattr(person, 'user', None)
        if user is None or not getattr(user, 'email', ''):
            skipped += 1
            continue

        if _already_reminded(user, invoice):
            skipped += 1
            continue

        pdf = render_invoice_pdf(invoice)
        attachments = [(f'invoice-{invoice.number}.pdf', pdf, 'application/pdf')] if pdf else []

        ends_at = min(e.trial_ends_at for e in enrolments)
        ok = emails.send_trial_expiry_reminder(
            person, invoice,
            days_left=1, trial_ends=ends_at,
            pay_url=absolute_url(invoice.get_pay_url()),
            modules=[e.programme_module.display_name for e in enrolments],
            attachments=attachments,
        )
        if ok:
            _mark_reminded(user, invoice)
            sent += 1
        else:
            logger.warning('trial reminder: e-mail failed for invoice %s', invoice.number)

    return f'{sent} reminder(s) sent, {skipped} skipped'
