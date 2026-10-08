"""Admissions receivers: a paid registration invoice moves its application on."""
import logging

from django.dispatch import receiver

from apps.finance.dispatch import invoice_paid

logger = logging.getLogger('admissions')


@receiver(invoice_paid)
def advance_application_on_invoice_paid(sender, invoice, **kwargs):
    """Registration + levy + first month paid → the application goes to the
    office for review (or stays "documents outstanding")."""
    try:
        from .services import on_invoice_paid
        on_invoice_paid(invoice)
    except Exception:  # pragma: no cover - never break the payment webhook
        logger.exception('admissions: could not advance application for invoice %s',
                         getattr(invoice, 'public_id', '?'))
