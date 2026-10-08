"""Turning a cart into an order the buyer is billed for.

The shape of checkout is: price the cart once (:func:`apps.shop.pricing.price_cart`),
**freeze** that quote onto the order lines, and raise the invoice from the frozen
lines. The invoice, the PayFast amount and the receipt then all read the same
numbers, because there is only one set of them. Before this module the invoice
copied the undiscounted line prices, and a buyer who was shown 20% off paid 100%.

Nothing here talks to PayFast; the finance app takes the invoice from here.
"""
import logging

from django.db import transaction

from . import pricing
from .models import Order, Product

logger = logging.getLogger('apps')

#: Session key for the coupon code the buyer typed into the cart.
COUPON_SESSION_KEY = 'shop_coupon'


class CheckoutError(Exception):
    """The cart cannot be checked out as it stands; ``problems`` says why."""

    def __init__(self, problems):
        super().__init__('; '.join(problems))
        self.problems = problems


def coupon_code(request):
    return (request.session.get(COUPON_SESSION_KEY) or '').strip().upper()


def cart_problems(cart):
    """Reasons the cart cannot be bought right now, in words for the buyer."""
    problems = []
    for item in cart.items.select_related('product', 'variant'):
        product = item.product
        name = item.description
        if product.status != 'active':
            problems.append(f'“{name}” is no longer on sale — please remove it.')
            continue
        if product.fulfilment == Product.FULFIL_BOOKING:
            booking = _booking_of(item)
            if booking is None:
                problems.append(f'“{name}” needs a session time — remove it and book a slot.')
            elif booking.status != booking.STATUS_HELD:
                problems.append(f'The {booking.label} slot for “{name}” was released — '
                                'remove it and choose a time again.')
        cap = product.max_quantity
        if cap and item.quantity > cap:
            problems.append(f'Only {cap} of “{name}” can be bought at a time.')
        if product.track_stock:
            if item.variant_id:
                available = item.variant.stock if item.variant.is_active else 0
            else:
                available = product.stock
            if item.quantity > available:
                problems.append(
                    f'Only {available} of “{name}” left in stock.' if available
                    else f'“{name}” is out of stock.')
    return problems


def _booking_of(item):
    """The held session behind a 1-on-1 line, or ``None``."""
    from django.core.exceptions import ObjectDoesNotExist
    try:
        return item.booking
    except ObjectDoesNotExist:
        return None


def freeze_quote(cart, quote):
    """Write ``quote`` onto ``cart`` and its lines. Idempotent."""
    for line in quote['lines']:
        item = line['item']
        item.discount_amount = line['discount']
        item.discount_label = (line['label'] or '')[:160]
        item.save(update_fields=['discount_amount', 'discount_label', 'line_total'])
    cart.subtotal = quote['subtotal']
    cart.discount_total = quote['discount']
    cart.shipping_total = quote['shipping']
    cart.tax_total = quote['vat']
    cart.coupon = quote['coupon']
    cart.save(update_fields=['subtotal', 'discount_total', 'shipping_total', 'tax_total',
                             'coupon', 'updated_at'])
    cart.recalc_total()


def place_order(cart, *, user, coupon='', use_credit=False, delivery=None):
    """Price, freeze and invoice ``cart``. Returns the finance Invoice.

    Raises :class:`CheckoutError` when the cart has a problem the buyer must fix
    first (out of stock, item withdrawn). A cart that costs nothing — fully
    discounted, or all free items — is settled on the spot: there is nothing to
    send to PayFast.
    """
    from apps.finance import services as finance

    with transaction.atomic():
        cart = Order.objects.select_for_update().get(pk=cart.pk)
        if cart.checked_out:
            raise CheckoutError(['This order has already been placed.'])
        if not cart.items.exists():
            raise CheckoutError(['Your cart is empty.'])
        problems = cart_problems(cart)
        if problems:
            raise CheckoutError(problems)

        # A 1-on-1 slot is kept while payment is outstanding (an EFT takes a
        # day or two); if the cart hold already lapsed, the slot is re-checked.
        from . import booking as booking_service
        for item in cart.items.all():
            held = _booking_of(item)
            if held is not None:
                try:
                    booking_service.refresh_hold(held, hours=booking_service.CHECKOUT_HOLD_HOURS)
                except booking_service.BookingError as exc:
                    raise CheckoutError([str(exc)])

        needs_delivery = cart.items.filter(product__fulfilment=Product.FULFIL_SHIPPED).exists()
        if needs_delivery and not delivery:
            raise CheckoutError(['Choose how you would like your order delivered.'])

        quote = pricing.price_cart(cart, coupon,
                                   shipping=delivery['amount'] if needs_delivery else 0)
        freeze_quote(cart, quote)
        if needs_delivery:
            from . import delivery as delivery_service
            delivery_service.freeze(cart, delivery)
        invoice = finance.create_invoice_from_order(cart, created_by=user)
        cart.checked_out = True
        cart.save(update_fields=['checked_out', 'updated_at'])

    if invoice.total <= 0:
        finance.settle_free(invoice)
        invoice.refresh_from_db()
    elif use_credit:
        from .booking import apply_credit
        apply_credit(invoice, user)
        invoice.refresh_from_db()
    return invoice
