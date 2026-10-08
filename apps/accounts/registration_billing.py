"""Getting the enrolment invoice to the family — e-mail, and WhatsApp.

A family that does not pay by card at the end of the online application pays
by EFT or at the school office, so the invoice (registration, levy and the
first month's school fees) has to reach them somewhere they will look:

* **E-mail** — the invoice with its PDF attached, via
  :func:`apps.finance.emails.send_invoice_email`.
* **WhatsApp** — the same PDF, to the number given on the contact step of
  registration (``PersonContact.primary_phone``, normalised to ``+27 82…``).

Neither is allowed to break registration. If e-mail is down, or WhatsApp is not
configured, the application still stands and the invoice is still in the
account under Finance — the family is simply told which channel did not go
through. The WhatsApp transport lives in :mod:`core.whatsapp` and is dormant
until configured.
"""
import datetime
import logging

from django.utils import timezone

from core import whatsapp
from core.branding import BRAND
from core.utils import absolute_url

logger = logging.getLogger(__name__)

#: How long the free week lasts. Mirrors ModuleEnrolment.TRIAL_DAYS.
TRIAL_DAYS = 7


def whatsapp_enabled():
    """True when WhatsApp is configured on this installation."""
    return whatsapp.enabled()


def send_invoice_whatsapp(invoice, person):
    """Send the invoice PDF to the number on the student's contact record.

    Returns ``(sent: bool, reason: str)``. ``reason`` explains a ``False`` so the
    caller can tell the student something specific ("no number on file") instead
    of a shrug.
    """
    if not whatsapp.enabled():
        return False, 'WhatsApp is not configured on this installation'

    number = whatsapp.number_for(person)
    if not number:
        return False, 'no usable WhatsApp number on the contact details'

    try:
        from apps.finance.pdf import render_invoice_pdf
        pdf_bytes = render_invoice_pdf(invoice)
        if hasattr(pdf_bytes, 'read'):
            pdf_bytes = pdf_bytes.read()
    except Exception:                              # pragma: no cover
        logger.exception('finance: could not render invoice %s as PDF', invoice.number)
        return False, 'the invoice PDF could not be produced'

    return whatsapp.send_document(
        number, pdf_bytes, f'{invoice.number}.pdf',
        caption=(f'Your {BRAND.get("name") or "United Church School"} invoice {invoice.number} — '
                 f'R{invoice.total:,.2f}. The application is pending until payment is received: '
                 "pay at Standard Bank using the learner's name and grade as the reference, and "
                 f'e-mail the deposit slip to {BRAND.get("support_email") or "uchs@unitedcs.co.za"}.'))


def send_invoice_email(invoice):
    """The invoice by e-mail. Returns ``(sent, reason)`` like its sibling."""
    try:
        from apps.finance import emails
        emails.send_invoice_email(invoice)
        return True, ''
    except Exception:                              # pragma: no cover - SMTP
        logger.exception('finance: invoice %s e-mail failed', invoice.number)
        return False, 'the e-mail could not be sent'


def _module_labels(enrolments):
    """Readable subject names from a list of ModuleEnrolment rows."""
    labels = []
    for e in enrolments or []:
        offering = getattr(e, 'programme_module', None)
        if offering is None:
            continue
        labels.append(getattr(offering, 'display_name', None) or str(offering))
    return labels


def send_registration_summary(person, invoice, enrolments, *, paid, programme=None,
                              trial_ends=None):
    """The welcome + summary e-mail, with the right PDF attached.

    ``paid`` picks both the document and the wording: a proof of payment when the
    card has cleared, the invoice itself when they will pay by EFT or at the
    school office. A PDF that fails to render is simply not attached — the e-mail
    still goes, because a missing attachment is worth far less than a missing
    welcome.

    Returns ``True`` if the e-mail went out. Never raises.
    """
    try:
        from apps.communication import emails
        from apps.finance import pdf as finance_pdf

        if paid:
            content = finance_pdf.render_receipt_pdf(invoice)
            filename, label = f'proof-of-payment-{invoice.number}.pdf', 'proof of payment'
        else:
            content = finance_pdf.render_invoice_pdf(invoice)
            filename, label = f'invoice-{invoice.number}.pdf', 'invoice'

        attachments = [(filename, content, 'application/pdf')] if content else []
        if not content:
            logger.warning('registration: %s PDF unavailable for %s — sending summary without it',
                           label, invoice.number)

        institution = getattr(getattr(programme, 'institution', None), 'name', '')
        return emails.send_registration_summary_email(
            person,
            institution=institution,
            programme=getattr(programme, 'display_name', None) or (str(programme) if programme else ''),
            modules=_module_labels(enrolments),
            total=invoice.total, currency='R',
            paid=paid, trial_ends=trial_ends,
            login_url=absolute_url('/myhub/'),
            attachments=attachments, attachment_label=label,
        )
    except Exception:                              # pragma: no cover
        logger.exception('registration: summary e-mail failed for invoice %s',
                         getattr(invoice, 'number', '?'))
        return False


def send_invoice_everywhere(invoice, person):
    """E-mail *and* WhatsApp the invoice; report what got through.

    Returns ``{'sent': [...], 'failed': [...], 'trial_ends': date}``. Never
    raises: a delivery problem is something to tell the student about, not a
    reason to fail a registration that has already happened.
    """
    sent, failed = [], []

    ok, _reason = send_invoice_email(invoice)
    (sent if ok else failed).append('e-mail')

    ok, reason = send_invoice_whatsapp(invoice, person)
    if ok:
        sent.append('WhatsApp')
    elif 'not configured' not in reason:
        # An installation without WhatsApp set up is not a failure to report to
        # a student — they never expected it. Anything else is.
        failed.append('WhatsApp')

    return {
        'sent': sent,
        'failed': failed,
        'trial_ends': (timezone.now() + datetime.timedelta(days=TRIAL_DAYS)).date(),
    }
