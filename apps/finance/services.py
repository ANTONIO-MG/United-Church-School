"""Finance service layer: turn a shop cart into an invoice, and settle payments.

Kept separate from the views so the checkout flow and the PayFast callbacks
(ITN + return) share one idempotent settle path.
"""

import logging

from django.utils import timezone

from . import models

logger = logging.getLogger('apps')


def create_invoice_from_order(order, *, created_by=None, status=None):
    """Create a finance Invoice from a shop Order (cart), copying line items
    and linking each item back to its product. Returns the Invoice."""
    invoice = models.Invoice.objects.create(
        customer=order.buyer,
        order=order,
        created_by=created_by or order.buyer,
        status=status or models.Invoice.STATUS_SENT,
    )
    # Lines are copied as checkout froze them (shop.checkout.freeze_quote):
    # the gross price, and the discount beside it, so the invoice shows the
    # saving rather than silently charging the undiscounted price.
    for order_item in order.items.select_related('product', 'variant').all():
        models.InvoiceItem.objects.create(
            invoice=invoice,
            product=order_item.product,
            description=order_item.description[:255],
            detail=(order_item.discount_label or '')[:255],
            quantity=order_item.quantity,
            unit_price=order_item.unit_price,
            discount_amount=order_item.discount_amount or 0,
        )
    if getattr(order, 'shipping_total', 0):
        models.InvoiceItem.objects.create(
            invoice=invoice, description='Delivery', quantity=1,
            unit_price=order.shipping_total)
    invoice.recalc_total()
    return invoice


def settle_free(invoice):
    """Close an invoice that costs nothing — a fully-discounted or free order.

    There is no money to collect, so no payment row is written and nothing goes
    to PayFast; the invoice is simply marked paid and the usual paid-invoice
    side effects run (order settled, downloads unlocked, receipt sent).
    """
    if invoice.total > 0 or invoice.status == models.Invoice.STATUS_PAID:
        return False
    invoice.status = models.Invoice.STATUS_PAID
    invoice.save(update_fields=['status', 'updated_at'])
    _on_invoice_paid(invoice)
    return True


def settle_payment(invoice, amount, *, gateway=models.InvoicePayment.GATEWAY_MANUAL,
                   method='online', gateway_ref='', raw=None, reference=''):
    """Record a COMPLETED payment against ``invoice`` (idempotent on
    ``gateway_ref`` for gateway callbacks). Refreshes status and, when the
    invoice becomes fully paid, e-mails a receipt and settles the linked order.
    Returns the InvoicePayment (existing one if already recorded)."""
    if gateway_ref:
        existing = invoice.payments.filter(gateway_ref=gateway_ref).first()
        if existing:
            return existing

    was_paid = invoice.status == models.Invoice.STATUS_PAID
    payment = models.InvoicePayment.objects.create(
        invoice=invoice, amount=amount, method=method, gateway=gateway,
        status=models.InvoicePayment.STATUS_COMPLETED, gateway_ref=gateway_ref,
        reference=reference, raw=raw or {}, paid_at=timezone.now(),
    )
    invoice.refresh_status()
    invoice.refresh_from_db()

    # Every payment leaves a proof, whoever made it. A gateway payment has no
    # document to upload — the gateway reference is the evidence — but it lands
    # in the same payment history as an uploaded deposit slip, so a student's
    # record is one list rather than "the online ones" and "the other ones".
    try:
        from . import access
        access.record_gateway_proof(invoice, payment)
    except Exception:  # pragma: no cover - a proof must never break settlement
        logger.exception('finance: could not record proof of payment for %s', invoice.number)

    if invoice.status == models.Invoice.STATUS_PAID and not was_paid:
        _on_invoice_paid(invoice)
    return payment


def _on_invoice_paid(invoice):
    """Side effects when an invoice flips to fully paid: receipt e-mail + mark
    the originating cart/order paid."""
    try:
        from . import emails
        emails.send_receipt_email(invoice)
    except Exception:  # pragma: no cover
        logger.exception('finance: receipt e-mail failed for %s', invoice.number)
    try:
        order = invoice.order
        if order is not None:
            from apps.shop.models import Order
            order.status = Order.STATUS_PAID
            order.checked_out = True
            order.save(update_fields=['status', 'checked_out', 'updated_at'])
    except Exception:  # pragma: no cover
        logger.exception('finance: could not settle order for %s', invoice.number)
    # Let other apps react (e.g. accounts enrols the student for a registration
    # invoice). Receivers must never break settlement, so failures are logged.
    try:
        from .dispatch import invoice_paid
        invoice_paid.send(sender=models.Invoice, invoice=invoice)
    except Exception:  # pragma: no cover
        logger.exception('finance: invoice_paid receivers failed for %s', invoice.number)
