"""Delivery quotes and shipments: The Courier Guy (Ship Logic v2), or flat rates.

Everything the shop needs from a courier goes through this module, so the rest
of the code never knows whether a live API is behind it:

* :func:`quote` — delivery options for a cart going to an address or a locker.
* :func:`lockers` — Pudo lockers near a place (live only).
* :func:`book` — create the courier shipment for a paid order.
* :func:`track` — refresh a shipment's status.
* :func:`label` — the waybill to print.

With ``COURIER_GUY_API_KEY`` unset the module quotes the configured flat rates
(door / locker, free over a threshold), and booking and tracking are done by
staff by hand. That is a complete, working mode — not an error state.

API reference: https://api-tcg.co.za (TCG's host for Ship Logic since May 2026;
Bearer key from the TCG portal). Service codes differ per account, so they are
read from the rates response rather than hard-coded.
"""
import logging
from dataclasses import dataclass
from datetime import timedelta
from decimal import ROUND_HALF_UP, Decimal

from django.conf import settings
from django.utils import timezone

logger = logging.getLogger('apps')

TIMEOUT = 20

#: Used when a product has no parcel dimensions yet — a padded A4 flyer.
DEFAULT_PARCEL = {'length': 35, 'width': 25, 'height': 5, 'weight': Decimal('0.5')}


class CourierError(Exception):
    """The courier could not do what was asked; the message is for staff/buyers."""


@dataclass
class Option:
    """One way to deliver: shown at checkout, frozen on the order."""
    method: str            # 'door' | 'locker'
    service_level: str     # courier code, '' for flat
    label: str
    amount: Decimal
    detail: str = ''       # e.g. "2–3 working days"

    def as_dict(self):
        return {'method': self.method, 'service_level': self.service_level, 'label': self.label,
                'amount': str(self.amount), 'detail': self.detail}


def is_live():
    return bool(getattr(settings, 'COURIER_GUY_API_KEY', ''))


def _money(value):
    return Decimal(str(value or 0)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def free_threshold():
    return _money(getattr(settings, 'SHOP_FREE_DELIVERY_OVER', 0))


def qualifies_for_free(goods_total):
    threshold = free_threshold()
    return threshold > 0 and _money(goods_total) >= threshold


# ---------------------------------------------------------------------------
# Parcels
# ---------------------------------------------------------------------------
def parcels_for(items):
    """One parcel for the shipped lines of an order: widest footprint, stacked height."""
    length = width = height = 0
    weight = Decimal('0')
    for item in items:
        product = item.product
        if not product.is_shipped:
            continue
        qty = item.quantity or 1
        length = max(length, product.length_cm or DEFAULT_PARCEL['length'])
        width = max(width, product.width_cm or DEFAULT_PARCEL['width'])
        height += (product.height_cm or DEFAULT_PARCEL['height']) * qty
        weight += Decimal(str(product.weight_kg or DEFAULT_PARCEL['weight'])) * qty
    if not weight:
        return []
    return [{'submitted_length_cm': length, 'submitted_width_cm': width,
             'submitted_height_cm': max(height, 1), 'submitted_weight_kg': float(weight),
             'parcel_description': 'United Church School supplies'}]


def _address_payload(snapshot):
    return {
        'type': snapshot.get('address_type') or 'residential',
        'company': snapshot.get('company', ''),
        'street_address': ' '.join(p for p in [snapshot.get('complex', ''), snapshot.get('street_address', '')] if p),
        'local_area': snapshot.get('suburb', ''),
        'suburb': snapshot.get('suburb', ''),
        'city': snapshot.get('city', ''),
        'zone': snapshot.get('province', ''),
        'country': 'ZA',
        'code': snapshot.get('postal_code', ''),
    }


def _collection():
    c = dict(getattr(settings, 'SHOP_COLLECTION', {}) or {})
    return {'type': 'business', 'company': c.get('company', ''), 'street_address': c.get('street_address', ''),
            'local_area': c.get('suburb', ''), 'suburb': c.get('suburb', ''), 'city': c.get('city', ''),
            'zone': c.get('zone', ''), 'country': 'ZA', 'code': c.get('code', '')}


# ---------------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------------
def _request(method, path, *, json=None, params=None):
    import requests

    url = settings.COURIER_GUY_BASE_URL.rstrip('/') + '/' + path.lstrip('/')
    try:
        response = requests.request(method, url, json=json, params=params, timeout=TIMEOUT,
                                    headers={'Authorization': f'Bearer {settings.COURIER_GUY_API_KEY}',
                                             'Content-Type': 'application/json'})
    except requests.RequestException as exc:
        logger.warning('courier: %s %s failed: %s', method, path, exc)
        raise CourierError('The courier could not be reached. Please try again shortly.') from exc
    if response.status_code >= 400:
        logger.warning('courier: %s %s → %s %s', method, path, response.status_code, response.text[:300])
        raise CourierError(f'The courier rejected the request ({response.status_code}).')
    try:
        return response.json()
    except ValueError:
        return {'raw': response.content, 'content_type': response.headers.get('Content-Type', '')}


# ---------------------------------------------------------------------------
# Quotes
# ---------------------------------------------------------------------------
def flat_options(goods_total, methods=('door', 'locker')):
    free = qualifies_for_free(goods_total)
    fees = {'door': _money(settings.SHOP_DELIVERY_DOOR_FEE),
            'locker': _money(settings.SHOP_DELIVERY_LOCKER_FEE)}
    labels = {'door': 'Courier to your door', 'locker': 'Courier to a Pudo locker'}
    return [Option(method=m, service_level='', label=labels[m],
                   amount=Decimal('0.00') if free else fees[m],
                   detail='Usually 2–4 working days after dispatch' + (' · free delivery' if free else ''))
            for m in methods]


def quote(items, *, method, goods_total, address=None, locker=None):
    """Delivery options for ``items`` by ``method`` ('door' / 'locker').

    Live: Ship Logic rates for the actual parcel and destination, cheapest
    first. Flat: the configured fee. Either way the free-delivery threshold
    applies, so the buyer's rule does not change with the mode.
    """
    if not is_live():
        return flat_options(goods_total, methods=(method,))

    parcels = parcels_for(items)
    if not parcels:
        return []
    today = timezone.localdate()
    payload = {'collection_address': _collection(), 'parcels': parcels,
               'collection_min_date': today.isoformat(),
               'delivery_min_date': (today + timedelta(days=1)).isoformat(),
               'opt_in_rates': [], 'opt_in_time_based_rates': []}
    if method == 'locker':
        if not locker:
            raise CourierError('Choose a locker first.')
        payload['delivery_pickup_point_id'] = locker
        payload['delivery_pickup_point_provider'] = 'tcg-locker'
    else:
        payload['delivery_address'] = _address_payload(address or {})
        payload['declared_value'] = float(goods_total)

    data = _request('POST', 'rates', json=payload)
    free = qualifies_for_free(goods_total)
    options = []
    for rate in data.get('rates') or []:
        level = rate.get('service_level') or {}
        code = level.get('code', '')
        is_locker = code.upper().startswith(('D2L', 'D2K', 'D2P'))
        if (method == 'locker') != is_locker:
            continue
        window = ''
        if level.get('delivery_date_from'):
            window = f"Arrives {level['delivery_date_from'][:10]}"
            if level.get('delivery_date_to') and level['delivery_date_to'][:10] != level['delivery_date_from'][:10]:
                window += f" – {level['delivery_date_to'][:10]}"
        options.append(Option(method=method, service_level=code,
                              label=f"The Courier Guy · {level.get('name') or code}",
                              amount=Decimal('0.00') if free else _money(rate.get('rate')),
                              detail=window + (' · free delivery' if free else '')))
    options.sort(key=lambda o: o.amount)
    return options


def lockers(search):
    """Pudo lockers near ``search`` (a suburb or city), nearest first. Live only."""
    if not is_live() or not (search or '').strip():
        return []
    data = _request('GET', 'pickup-points', params={'order_closest': 'true', 'search': search.strip()})
    out = []
    for point in (data.get('pickup_points') or [])[:25]:
        address = point.get('address') or {}
        out.append({'id': str(point.get('pickup_point_id', '')),
                    'name': address.get('company') or point.get('name') or 'Pudo locker',
                    'address': address.get('entered_address') or '',
                    'provider': point.get('pickup_point_provider', 'tcg-locker')})
    return [p for p in out if p['id']]


# ---------------------------------------------------------------------------
# Shipments
# ---------------------------------------------------------------------------
def book(shipment):
    """Create the courier shipment for a paid order. Returns the shipment."""
    if not is_live():
        raise CourierError('No courier API key is configured — enter the tracking number by hand.')
    order = shipment.order
    snapshot = order.ship_to or {}
    collection = getattr(settings, 'SHOP_COLLECTION', {}) or {}
    payload = {
        'collection_address': _collection(),
        'collection_contact': {'name': collection.get('contact', ''), 'mobile_number': collection.get('phone', ''),
                               'email': collection.get('email', '')},
        'delivery_contact': {'name': snapshot.get('recipient', ''), 'mobile_number': snapshot.get('phone', ''),
                             'email': order.buyer.email},
        'parcels': parcels_for(order.items.select_related('product')),
        'service_level_code': shipment.service_level,
        'customer_reference': order.order_no,
        'special_instructions_delivery': snapshot.get('instructions', ''),
    }
    if shipment.method == 'locker':
        payload['delivery_pickup_point_id'] = shipment.locker_code
        payload['delivery_pickup_point_provider'] = 'tcg-locker'
    else:
        payload['delivery_address'] = _address_payload(snapshot)
    if not shipment.service_level:
        raise CourierError('This order has no courier service level — requote it first.')

    data = _request('POST', 'shipments', json=payload)
    shipment.courier_shipment_id = str(data.get('id', ''))
    shipment.tracking_reference = (data.get('short_tracking_reference')
                                   or data.get('custom_tracking_reference') or '')
    shipment.courier_cost = _money(data.get('rate')) if data.get('rate') is not None else None
    shipment.carrier = shipment.CARRIER_COURIER_GUY
    return shipment


def track(shipment):
    """Latest status for a booked shipment: ``(status, events)`` in our terms."""
    if not is_live() or not shipment.tracking_reference:
        return None
    data = _request('GET', 'shipments', params={'tracking_reference': shipment.tracking_reference})
    rows = data.get('shipments') or []
    if not rows:
        return None
    row = rows[0]
    raw = (row.get('status') or '').lower()
    if raw in ('delivered',):
        status = shipment.STATUS_DELIVERED
    elif raw in ('cancelled',):
        status = shipment.STATUS_CANCELLED
    elif raw in ('failed-delivery', 'failed-collection', 'exception', 'returned-to-sender'):
        status = shipment.STATUS_FAILED
    elif raw in ('submitted', 'collection-assigned', 'collection-unassigned', 'at-hub', 'awaiting-collection'):
        status = shipment.STATUS_BOOKED
    else:
        status = shipment.STATUS_IN_TRANSIT
    events = [{'at': e.get('date', ''), 'status': e.get('status', ''), 'message': e.get('message', '') or e.get('status', '')}
              for e in (row.get('tracking_events') or [])]
    return status, events


def label(shipment):
    """The waybill: ``('url', url)`` or ``('pdf', bytes)``."""
    if not is_live() or not shipment.courier_shipment_id:
        raise CourierError('There is no courier waybill for this shipment.')
    data = _request('GET', 'shipments/label', params={'id': shipment.courier_shipment_id})
    if isinstance(data, dict) and data.get('url'):
        return 'url', data['url']
    if isinstance(data, dict) and data.get('raw'):
        return 'pdf', data['raw']
    raise CourierError('The courier did not return a waybill.')


def tracking_url(reference):
    template = getattr(settings, 'COURIER_TRACKING_URL', '') or ''
    return template.replace('{ref}', reference) if reference and template else ''
