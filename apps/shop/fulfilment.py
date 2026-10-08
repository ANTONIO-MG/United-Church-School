"""What happens to an order the moment it is paid.

:func:`process_paid_order` is the single place the side effects of a sale live:
the coupon is counted as used, stock comes down, the buyer is told — and only
the buyer, about only their purchase — and staff hear that a sale came in.

It runs off finance's ``invoice_paid`` signal, which both PayFast (ITN) and a
staff-recorded EFT payment fire, so the online and offline routes finish the
same way. ``Order.paid_processed_at`` makes it run once: PayFast retries its
ITN, and a sale must not be counted twice.
"""
import logging

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import F, Q
from django.urls import reverse
from django.utils import timezone

from .models import Discount, Order, Product, ProductVariant

logger = logging.getLogger('apps')


def staff_recipients():
    """Everyone who runs the shop: Django staff, and admin/staff profiles."""
    User = get_user_model()
    return (User.objects.filter(is_active=True)
            .filter(Q(is_staff=True) | Q(is_superuser=True)
                    | Q(profile__user_type__in=('admin', 'staff')))
            .distinct())


def process_paid_order(order):
    """Run the paid-order side effects for ``order`` once. Returns True if it ran."""
    with transaction.atomic():
        locked = Order.objects.select_for_update().get(pk=order.pk)
        if locked.paid_processed_at is not None:
            return False
        locked.paid_processed_at = timezone.now()
        locked.save(update_fields=['paid_processed_at', 'updated_at'])

        if locked.coupon_id:
            Discount.objects.filter(pk=locked.coupon_id).update(times_used=F('times_used') + 1)

        for item in locked.items.select_related('product', 'variant'):
            product = item.product
            Product.objects.filter(pk=product.pk).update(
                students_count=F('students_count') + item.quantity)
            if not product.track_stock:
                continue
            # Never below zero: an oversell is a staff problem to sort out, not
            # a negative number on the shelf.
            if item.variant_id:
                ProductVariant.objects.filter(pk=item.variant_id).update(
                    stock=_floor(F('stock') - item.quantity))
            else:
                Product.objects.filter(pk=product.pk).update(
                    stock=_floor(F('stock') - item.quantity))

    from .models import Shipment
    Shipment.objects.filter(order=locked, status=Shipment.STATUS_AWAITING).update(
        status=Shipment.STATUS_READY)

    from .checkout import _booking_of
    for item in locked.items.all():
        held = _booking_of(item)
        if held is not None:
            try:
                from .booking import settle_paid
                settle_paid(held)
            except Exception:  # pragma: no cover — the payment stands; staff can place it
                logger.exception('shop: could not confirm booking %s', held.pk)

    _notify(locked)
    return True


def _floor(expression):
    from django.db.models.functions import Greatest
    return Greatest(expression, 0)


def _notify(order):
    """Tell the buyer about their purchase, and staff that a sale came in."""
    try:
        from apps.communication.services import notify
    except Exception:  # pragma: no cover
        return

    url = reverse('shop:order-detail', args=[order.pk])
    items = list(order.items.select_related('product', 'variant'))
    names = ', '.join(item.description for item in items[:3])
    if len(items) > 3:
        names += f' and {len(items) - 3} more'

    has_files = any(item.product.is_digital for item in items)
    body = f'We received R{order.total:,.2f} for {names}.'
    if has_files:
        body += ' Your downloads are ready on the order page.'
    try:
        notify(order.buyer, title=f'Payment received — order {order.order_no}',
               body=body, verb='purchase', level='success', url=url)
    except Exception:  # pragma: no cover — a notification must never undo a sale
        logger.exception('shop: buyer notification failed for %s', order.order_no)

    buyer = order.buyer.get_full_name() or order.buyer.get_username()
    for person in staff_recipients().exclude(pk=order.buyer_id):
        try:
            notify(person, title=f'New sale — R{order.total:,.2f}',
                   body=f'{buyer} bought {names} ({order.order_no}).',
                   verb='sale', level='info', url=url, actor=order.buyer)
        except Exception:  # pragma: no cover
            logger.exception('shop: staff sale notification failed for %s', order.order_no)


# ---------------------------------------------------------------------------
# Shipping a paid order
# ---------------------------------------------------------------------------
def book_courier(shipment, *, by):
    """Book the courier for a packed order (live API). Raises CourierError."""
    from . import courier
    from .models import Shipment

    courier.book(shipment)
    shipment.status = Shipment.STATUS_BOOKED
    shipment.booked_at = timezone.now()
    shipment.booked_by = by
    shipment.tracking_url = courier.tracking_url(shipment.tracking_reference)
    shipment.log('booked', f'Courier booked · waybill {shipment.tracking_reference}')
    shipment.save()
    _notify_shipped(shipment)
    return shipment


def record_manual_dispatch(shipment, *, by, tracking_reference, courier_name=''):
    """Staff booked the parcel themselves (no API key, or another courier)."""
    from . import courier
    from .models import Shipment

    shipment.carrier = Shipment.CARRIER_MANUAL if courier_name else shipment.carrier
    shipment.courier_name = courier_name[:80]
    shipment.tracking_reference = tracking_reference.strip()[:80]
    shipment.tracking_url = courier.tracking_url(shipment.tracking_reference) if not courier_name else ''
    shipment.status = Shipment.STATUS_BOOKED
    shipment.booked_at = timezone.now()
    shipment.booked_by = by
    shipment.log('booked', f'Dispatched with {courier_name or "The Courier Guy"} · {shipment.tracking_reference}')
    shipment.save()
    _notify_shipped(shipment)
    return shipment


def mark_delivered(shipment, *, by=None, when=None):
    from .models import Shipment

    if shipment.status == Shipment.STATUS_DELIVERED:
        return shipment
    shipment.status = Shipment.STATUS_DELIVERED
    shipment.delivered_at = when or timezone.now()
    shipment.log('delivered', 'Delivered' + (f' (marked by {by})' if by else ''))
    shipment.save()
    try:
        from apps.communication.services import notify
        notify(shipment.order.buyer, title=f'Delivered — order {shipment.order.order_no}',
               body='Your parcel has been delivered. Enjoy, and good luck with your studies!',
               verb='delivered', level='success', url=reverse('shop:order-detail', args=[shipment.order_id]))
    except Exception:  # pragma: no cover
        logger.exception('shop: delivered notification failed for %s', shipment.pk)
    return shipment


def _notify_shipped(shipment):
    try:
        from apps.communication.services import notify
        where = ('your locker' if shipment.method == 'locker' else 'your door')
        body = f'Your parcel is on its way to {where}.'
        if shipment.tracking_reference:
            body += f' Tracking number: {shipment.tracking_reference}.'
        notify(shipment.order.buyer, title=f'Shipped — order {shipment.order.order_no}', body=body,
               verb='shipped', level='info', url=reverse('shop:order-detail', args=[shipment.order_id]),
               email=True)
    except Exception:  # pragma: no cover
        logger.exception('shop: shipped notification failed for %s', shipment.pk)


def refresh_tracking():
    """Scheduler entry point: pull courier status for parcels on their way."""
    from . import courier
    from .models import Shipment

    if not courier.is_live():
        return 'courier API not configured'
    updated = 0
    for shipment in (Shipment.objects.filter(status__in=(Shipment.STATUS_BOOKED, Shipment.STATUS_IN_TRANSIT),
                                             carrier=Shipment.CARRIER_COURIER_GUY)
                     .exclude(tracking_reference='').select_related('order__buyer')[:200]):
        try:
            result = courier.track(shipment)
        except courier.CourierError:
            continue
        shipment.last_tracked_at = timezone.now()
        if result is None:
            shipment.save(update_fields=['last_tracked_at', 'updated_at'])
            continue
        status, events = result
        if events:
            shipment.events = events
        if status == Shipment.STATUS_DELIVERED:
            shipment.save()
            mark_delivered(shipment)
        else:
            shipment.status = status
            shipment.save()
        updated += 1
    return f'{updated} shipment(s) tracked'
