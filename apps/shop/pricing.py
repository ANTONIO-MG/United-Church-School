"""What a cart actually costs once discounts are applied.

One entry point, :func:`price_cart`, so the storefront, the cart page, checkout,
the invoice and the PayFast amount all quote the same number. Checkout freezes
this quote onto the order and the invoice (see :mod:`apps.shop.checkout`); it
used to copy the undiscounted line prices instead, so a buyer shown 20% off was
charged in full.

Rules — "best deal plus one coupon":

* Per line, the **best automatic saving** wins: the product's own discount % or
  the best live promotion covering it, whichever takes more off. They never
  compound.
* At most one **coupon** then applies on top, to what is left of each line it
  covers — otherwise a buyer can chain codes and pay nothing.
* A **percentage** coupon bites per line. A **fixed-amount** coupon is a cart
  saving: "R100 off" takes R100 off the order once, spread across the lines it
  covers — not R100 off every line.
* A minimum spend is judged on the cart subtotal, before any discount, and a
  discount that misses it is simply not a candidate. It does not knock out the
  others.
* Prices include VAT; ``vat`` is the VAT contained in the total.
"""
from decimal import ROUND_HALF_UP, Decimal

from django.conf import settings

from .models import Discount

CENT = Decimal('0.01')
ZERO = Decimal('0')


def _money(value):
    return Decimal(str(value or 0)).quantize(CENT, rounding=ROUND_HALF_UP)


def _pct_label(percent):
    percent = Decimal(str(percent)).normalize()
    return f'{percent:f}% off'


def _live_promotions():
    return [d for d in Discount.objects.filter(is_active=True, code__isnull=True)
            .prefetch_related('products') if d.is_live]


def find_coupon(code):
    """A live coupon for ``code``, or ``None``."""
    if not code:
        return None
    discount = (Discount.objects.filter(code=(code or '').strip().upper())
                .prefetch_related('products').first())
    return discount if discount and discount.is_live else None


def vat_in(amount):
    """VAT contained in a VAT-inclusive ``amount`` (0 when not VAT-registered)."""
    if not getattr(settings, 'VAT_REGISTERED', False):
        return ZERO
    rate = Decimal(str(getattr(settings, 'VAT_RATE', 15)))
    amount = Decimal(str(amount or 0))
    if amount <= 0 or rate <= 0:
        return ZERO
    return _money(amount * rate / (100 + rate))


def price_cart(order, coupon_code=None, *, shipping=ZERO):
    """Return a quote for ``order``.

    ``{'subtotal', 'discount', 'shipping', 'total', 'vat', 'lines', 'applied',
    'coupon', 'coupon_code', 'coupon_error'}``. ``lines`` carries the per-item
    breakdown (``item``, ``gross``, ``discount``, ``payable``, ``label``) so the
    cart shows what came off where, rather than one unexplained number.
    """
    items = list(order.items.select_related('product', 'product__category', 'variant'))
    subtotal = sum((_money(item.gross_total) for item in items), ZERO)
    coupon_code = (coupon_code or '').strip().upper()

    promotions = [p for p in _live_promotions() if not p.min_spend or subtotal >= p.min_spend]

    coupon, coupon_error = None, ''
    if coupon_code:
        coupon = find_coupon(coupon_code)
        if coupon is None:
            coupon_error = 'That code is not valid or has expired.'
        elif coupon.min_spend and subtotal < coupon.min_spend:
            coupon_error = f'Spend at least R{coupon.min_spend:,.2f} to use {coupon_code}.'
            coupon = None

    lines, applied = [], []
    for item in items:
        gross = _money(item.gross_total)
        product = item.product

        best, best_off, label = None, ZERO, ''
        if product.has_discount:
            best_off = gross - _money(product.sale_price_for(item.unit_price) * item.quantity)
            label = _pct_label(product.discount_percent)
        for promotion in promotions:
            if not promotion.covers(product):
                continue
            off = promotion.amount_for(gross)
            if off > best_off:
                best, best_off, label = promotion, off, promotion.name
        if best is not None and best not in applied:
            applied.append(best)
        lines.append({'item': item, 'gross': gross, 'discount': _money(best_off),
                      'label': label, 'payable': gross - _money(best_off)})

    if coupon is not None:
        covered = [line for line in lines if coupon.covers(line['item'].product) and line['payable'] > 0]
        if coupon.discount_type == Discount.TYPE_PERCENT:
            for line in covered:
                off = coupon.amount_for(line['payable'])
                _apply_coupon(line, off, coupon)
        else:
            _spread_fixed(covered, coupon)
        if any(line.get('coupon_off') for line in covered):
            applied.append(coupon)
        else:
            coupon_error = coupon_error or f'{coupon_code} does not apply to anything in your cart.'
            coupon = None

    discount = sum((line['discount'] for line in lines), ZERO)
    shipping = _money(shipping)
    total = subtotal - discount + shipping
    return {'subtotal': subtotal, 'discount': discount, 'shipping': shipping,
            'total': total, 'vat': vat_in(total), 'lines': lines, 'applied': applied,
            'coupon': coupon, 'coupon_code': coupon_code if coupon else '',
            'coupon_error': coupon_error}


def _apply_coupon(line, off, coupon):
    off = min(_money(off), line['payable'])
    if off <= 0:
        return
    line['coupon_off'] = off
    line['discount'] += off
    line['payable'] -= off
    line['label'] = f"{line['label']} + {coupon.code}" if line['label'] else coupon.code


def _spread_fixed(covered, coupon):
    """Take a fixed-amount coupon off the covered lines once, pro rata."""
    pool = sum((line['payable'] for line in covered), ZERO)
    if pool <= 0:
        return
    budget = min(_money(coupon.value), pool)
    remaining = budget
    for index, line in enumerate(covered):
        # The last line takes whatever rounding left over, so the lines add up
        # to the coupon exactly.
        if index == len(covered) - 1:
            off = remaining
        else:
            off = min(_money(budget * line['payable'] / pool), remaining)
        remaining -= off
        _apply_coupon(line, off, coupon)
