"""The buyer's delivery choice, between the cart and a placed order.

At checkout a buyer with shipped items picks **door** (an address from their
address book, or a new one) or **locker** (a Pudo locker). The choice lives in
the session until the order is placed, and is re-priced every time it is shown:
flat rates cost nothing to recompute, and the free-delivery threshold depends on
the cart total, which a coupon can change. A live Courier Guy quote is kept with
a fingerprint of the cart and re-requested only when the cart changes.

:func:`freeze` writes the choice onto the order (a snapshot of the address,
never a link to the address book) and opens its :class:`Shipment`.
"""
import hashlib
from decimal import Decimal

from . import courier
from .models import Address, Order, Shipment

SESSION_KEY = 'shop_delivery'


def cart_fingerprint(cart):
    parts = [f'{i.product_id}:{i.variant_id}:{i.quantity}' for i in cart.items.order_by('pk')]
    return hashlib.sha1('|'.join(parts).encode()).hexdigest()


def shipped_items(cart):
    return [i for i in cart.items.select_related('product') if i.product.is_shipped]


def stored(request):
    return dict(request.session.get(SESSION_KEY) or {})


def clear(request):
    request.session.pop(SESSION_KEY, None)


def choose(request, cart, *, method, goods_total, address=None, locker_id='', locker_name=''):
    """Price and remember a delivery choice. Raises CourierError."""
    items = shipped_items(cart)
    snapshot = address.snapshot() if address is not None else {}
    options = courier.quote(items, method=method, goods_total=goods_total,
                            address=snapshot, locker=locker_id)
    if not options:
        raise courier.CourierError('No delivery option is available for that destination.')
    option = options[0]
    request.session[SESSION_KEY] = {
        'method': method, 'address_id': address.pk if address is not None else None,
        'locker_id': locker_id, 'locker_name': locker_name,
        'option': option.as_dict(), 'fingerprint': cart_fingerprint(cart),
        'goods_total': str(goods_total),
    }
    return option


def current(request, cart, goods_total):
    """The priced choice for this cart, or ``None`` if one must be made (again)."""
    choice = stored(request)
    if not choice or not shipped_items(cart):
        return None
    address = None
    if choice.get('method') == Order.DELIVERY_DOOR:
        address = Address.objects.filter(pk=choice.get('address_id'), user=request.user).first()
        if address is None:
            return None
    elif not choice.get('locker_id') and not choice.get('locker_name'):
        return None

    option = choice.get('option') or {}
    if not courier.is_live():
        fresh = courier.flat_options(goods_total, methods=(choice['method'],))[0]
        option = fresh.as_dict()
    elif choice.get('fingerprint') != cart_fingerprint(cart) or choice.get('goods_total') != str(goods_total):
        try:
            option = choose(request, cart, method=choice['method'], goods_total=goods_total,
                            address=address, locker_id=choice.get('locker_id', ''),
                            locker_name=choice.get('locker_name', '')).as_dict()
        except courier.CourierError:
            return None
    return {'method': choice['method'], 'address': address,
            'locker_id': choice.get('locker_id', ''), 'locker_name': choice.get('locker_name', ''),
            'option': option, 'amount': Decimal(option.get('amount') or '0')}


def freeze(order, choice):
    """Record ``choice`` on ``order`` and open its shipment."""
    if choice['method'] == Order.DELIVERY_DOOR:
        order.ship_to = choice['address'].snapshot()
    else:
        order.ship_to = {'recipient': order.buyer.get_full_name() or order.buyer.get_username(),
                         'phone': _buyer_phone(order.buyer),
                         'locker_id': choice['locker_id'], 'locker_name': choice['locker_name']}
    order.delivery_method = choice['method']
    order.delivery_label = (choice['option'].get('label') or '')[:160]
    order.save(update_fields=['ship_to', 'delivery_method', 'delivery_label', 'updated_at'])
    Shipment.objects.update_or_create(order=order, defaults={
        'method': choice['method'], 'service_level': choice['option'].get('service_level', ''),
        'locker_code': choice.get('locker_id', ''), 'locker_name': choice.get('locker_name', ''),
        'charged': choice['amount'], 'status': Shipment.STATUS_AWAITING,
        'carrier': Shipment.CARRIER_COURIER_GUY if courier.is_live() else Shipment.CARRIER_MANUAL,
    })


def _buyer_phone(user):
    contact = getattr(getattr(user, 'profile', None), 'contact', None)
    return (getattr(contact, 'primary_phone', '') or getattr(getattr(user, 'profile', None), 'phone', '') or '').strip()
