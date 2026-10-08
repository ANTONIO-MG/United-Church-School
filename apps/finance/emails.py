"""Finance transactional e-mails — thin wrappers over the central branded
e-mail library in :mod:`apps.communication.emails` (one template folder for the
whole platform: ``communication/email/``). Best-effort; never raises."""

import logging

from django.conf import settings
from core.utils import absolute_url

logger = logging.getLogger('apps')


def send_invoice_email(invoice):
    """E-mail the customer a pay-link for an invoice."""
    try:
        from apps.communication import emails
        return emails.send_invoice_email(invoice, absolute_url(invoice.get_pay_url()))
    except Exception:  # pragma: no cover
        logger.exception('finance: invoice e-mail failed')
        return False


def send_receipt_email(invoice):
    """E-mail the customer a receipt once an invoice is fully paid."""
    try:
        from apps.communication import emails
        return emails.send_payment_made(invoice)
    except Exception:  # pragma: no cover
        logger.exception('finance: receipt e-mail failed')
        return False


def send_purchase_email(invoice):
    """E-mail an order-confirmation when a purchase invoice is created."""
    try:
        from apps.communication import emails
        return emails.send_purchase_email(invoice, absolute_url(invoice.get_pay_url()))
    except Exception:  # pragma: no cover
        logger.exception('finance: purchase e-mail failed')
        return False
