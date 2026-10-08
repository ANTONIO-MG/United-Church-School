"""Signal handlers for the shop app.

* Keep :attr:`Order.total` in sync with its line items.
* Flip an order to *paid* once completed payments cover its balance.
* Record create/update/delete of products and orders in the shared
  :class:`apps.accounts.models.ActivityLog` audit trail.

Connected in :meth:`apps.shop.apps.ShopConfig.ready`.
"""

import logging

from django.db.models.signals import post_delete, post_save, pre_delete
from django.dispatch import receiver
from apps.finance.dispatch import invoice_paid as finance_invoice_paid

from .models import Order, OrderItem, Payment, Product

logger = logging.getLogger('apps')


def _log(action, description):
    """Best-effort audit log entry (never breaks the request if it fails)."""
    try:
        from apps.accounts.models import ActivityLog
        ActivityLog.objects.create(action=action, description=description)
    except Exception:  # pragma: no cover - logging must never break saves
        logger.exception('shop: failed to write ActivityLog')


# ---------------------------------------------------------------------------
# Keep order totals in sync
# ---------------------------------------------------------------------------
@receiver(post_save, sender=OrderItem)
def recalc_on_item_save(sender, instance, **kwargs):
    instance.order.recalc_total()


@receiver(pre_delete, sender=OrderItem)
def release_booking_on_item_delete(sender, instance, **kwargs):
    """Taking a 1-on-1 out of the cart frees its slot straight away, rather
    than leaving it blocked until the hold runs out."""
    from .models import Booking
    Booking.objects.filter(order_item=instance, status=Booking.STATUS_HELD).update(
        status=Booking.STATUS_EXPIRED)


@receiver(post_delete, sender=OrderItem)
def recalc_on_item_delete(sender, instance, **kwargs):
    try:
        instance.order.recalc_total()
    except Order.DoesNotExist:  # order being cascade-deleted
        pass


# ---------------------------------------------------------------------------
# Flip the order to paid when the balance is cleared
# ---------------------------------------------------------------------------
@receiver(post_save, sender=Payment)
def settle_order_on_payment(sender, instance, **kwargs):
    order = instance.order
    if order.status == Order.STATUS_PENDING and order.total > 0 and order.balance <= 0:
        order.status = Order.STATUS_PAID
        order.save(update_fields=['status', 'updated_at'])
        _log('update', f'Order {order.order_no} marked paid')


# ---------------------------------------------------------------------------
# Audit logging
# ---------------------------------------------------------------------------
@receiver(post_save, sender=Product)
def log_product_save(sender, instance, created, **kwargs):
    _log('create' if created else 'update',
         f"Product {'created' if created else 'updated'}: {instance.name}")


@receiver(post_delete, sender=Product)
def log_product_delete(sender, instance, **kwargs):
    _log('delete', f'Product deleted: {instance.name}')


@receiver(post_save, sender=Order)
def log_order_save(sender, instance, created, **kwargs):
    if created:
        _log('create', f'Order created: {instance.order_no}')


@receiver(post_delete, sender=Order)
def log_order_delete(sender, instance, **kwargs):
    _log('delete', f'Order deleted: {instance.order_no}')


# ---------------------------------------------------------------------------
# Surface new Courses in the storefront automatically
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Deliver digital goods the moment the money lands
# ---------------------------------------------------------------------------
@receiver(finance_invoice_paid)
def email_downloads_on_payment(sender, invoice, **kwargs):
    """E-mail the buyer their files when the invoice behind their order is paid.

    Matters most for the EFT route: accounts ticks the invoice paid days after
    checkout, when the buyer is nowhere near the site. Paying by card hits the
    same path, so there is one delivery rule rather than two.

    finance.services already flipped the order to paid before firing this, so
    ``deliver_order`` sees the state it expects. Never raises — a mail problem
    must not undo a payment that really happened.
    """
    order = getattr(invoice, 'order', None)
    if order is None:
        return
    try:
        from .fulfilment import process_paid_order
        process_paid_order(order)
    except Exception:  # pragma: no cover
        logger.exception('shop: paid-order processing failed for %s', order.order_no)
    try:
        from .entitlements import deliver_order
        deliver_order(order)
    except Exception:  # pragma: no cover
        logger.exception('shop: download delivery failed for order %s', order.order_no)
