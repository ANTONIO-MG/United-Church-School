"""Phase 3: the study-materials store — delivery choice, courier and fulfilment.

Flat rates (no API key): R120 door, R70 locker, free from R1,500. Live mode is
exercised with the Ship Logic HTTP calls mocked.
"""
from decimal import Decimal
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.communication.models import Notification
from apps.finance import models as finance
from apps.finance import services as finance_services

from . import courier, fulfilment
from .models import Address, Order, OrderItem, Product, ProductVariant, Shipment
from .tests import _onboarded

User = get_user_model()

FLAT = dict(COURIER_GUY_API_KEY='', SHOP_DELIVERY_DOOR_FEE='120', SHOP_DELIVERY_LOCKER_FEE='70',
            SHOP_FREE_DELIVERY_OVER='1500', VAT_REGISTERED=False, PAYMENTS_ENABLED=True)
ADDRESS = {'addr-recipient': 'Thandi Mokoena', 'addr-phone': '082 555 1234',
           'addr-street_address': '12 Kloof Road', 'addr-suburb': 'Croydon', 'addr-city': 'Cape Town',
           'addr-province': 'WC', 'addr-postal_code': '7130', 'addr-address_type': 'residential'}


def _response(payload, status=200):
    return mock.Mock(status_code=status, json=mock.Mock(return_value=payload), text='', headers={})


@override_settings(**FLAT)
class DeliveryTests(TestCase):
    def setUp(self):
        self.buyer = _onboarded(User.objects.create_user('buyer', 'buyer@example.com', 'pw12345!'))
        self.staff = User.objects.create_user('staff', 'staff@example.com', 'pw12345!', is_staff=True)
        self.hoodie = Product.objects.create(name='Hoodie', price=Decimal('650'), track_stock=True,
                                             fulfilment=Product.FULFIL_SHIPPED, weight_kg=Decimal('0.8'),
                                             length_cm=35, width_cm=30, height_cm=8)
        self.large = ProductVariant.objects.create(product=self.hoodie, name='L', stock=5)
        self.client.force_login(self.buyer)

    def _cart(self, qty=1):
        cart = Order.get_cart(self.buyer)
        OrderItem.objects.create(order=cart, product=self.hoodie, variant=self.large, quantity=qty)
        return cart

    def _choose_door(self):
        return self.client.post(reverse('finance:checkout'), {'action': 'delivery', 'method': 'door',
                                                              'address': 'new', **ADDRESS})

    def test_checkout_needs_a_delivery_choice(self):
        self._cart()
        page = self.client.get(reverse('finance:checkout'))
        self.assertContains(page, 'Choose delivery to continue')
        self.client.post(reverse('finance:checkout'))
        self.assertFalse(finance.Invoice.objects.exists())

    def test_door_delivery_adds_flat_fee_to_invoice_and_opens_shipment(self):
        cart = self._cart()
        self.assertRedirects(self._choose_door(), reverse('finance:checkout'), fetch_redirect_response=False)
        self.assertEqual(Address.objects.get(user=self.buyer).postal_code, '7130')
        self.assertContains(self.client.get(reverse('finance:checkout')), 'R770.00')

        self.client.post(reverse('finance:checkout'))
        invoice = finance.Invoice.objects.get(customer=self.buyer)
        self.assertEqual(invoice.total, Decimal('770.00'))
        self.assertTrue(invoice.items.filter(description='Delivery', unit_price=Decimal('120')).exists())
        cart.refresh_from_db()
        self.assertEqual(cart.delivery_method, 'door')
        self.assertEqual(cart.ship_to['city'], 'Cape Town')
        self.assertEqual(cart.shipment.status, Shipment.STATUS_AWAITING)
        self.assertEqual(cart.shipment.charged, Decimal('120.00'))

        finance_services.settle_payment(invoice, invoice.balance, gateway_ref='PF-D1')
        cart.shipment.refresh_from_db()
        self.assertEqual(cart.shipment.status, Shipment.STATUS_READY)

    def test_free_delivery_over_threshold(self):
        self._cart(qty=3)                       # R1,950
        self._choose_door()
        self.client.post(reverse('finance:checkout'))
        invoice = finance.Invoice.objects.get(customer=self.buyer)
        self.assertEqual(invoice.total, Decimal('1950.00'))

    def test_locker_delivery_flat(self):
        cart = self._cart()
        self.client.post(reverse('finance:checkout'), {'action': 'delivery', 'method': 'locker',
                                                       'locker_name': 'Pudo Clearwater Mall'})
        self.client.post(reverse('finance:checkout'))
        cart.refresh_from_db()
        self.assertEqual(cart.total, Decimal('720.00'))
        self.assertEqual(cart.shipment.locker_name, 'Pudo Clearwater Mall')

    def test_bad_postal_code_is_rejected(self):
        self._cart()
        response = self.client.post(reverse('finance:checkout'), {
            'action': 'delivery', 'method': 'door', 'address': 'new', **ADDRESS, 'addr-postal_code': '71'})
        self.assertContains(response, '4 digits')
        self.assertFalse(Address.objects.exists())

    def test_staff_dispatch_and_delivery_notify_buyer(self):
        cart = self._cart()
        self._choose_door()
        self.client.post(reverse('finance:checkout'))
        invoice = finance.Invoice.objects.get(customer=self.buyer)
        finance_services.settle_payment(invoice, invoice.balance, gateway_ref='PF-D2')
        shipment = Shipment.objects.get(order=cart)

        self.client.force_login(self.staff)
        self.assertContains(self.client.get(reverse('shop:fulfilment')), cart.order_no)
        self.assertContains(self.client.get(reverse('shop:packing-slip', args=[shipment.pk])), 'Kloof Road')
        self.client.post(reverse('shop:fulfilment-action', args=[shipment.pk]),
                         {'action': 'manual', 'tracking_reference': 'TCG123456'})
        shipment.refresh_from_db()
        self.assertEqual(shipment.status, Shipment.STATUS_BOOKED)
        self.assertTrue(Notification.objects.filter(recipient=self.buyer, verb='shipped').exists())

        self.client.post(reverse('shop:fulfilment-action', args=[shipment.pk]), {'action': 'delivered'})
        shipment.refresh_from_db()
        self.assertEqual(shipment.status, Shipment.STATUS_DELIVERED)
        self.assertTrue(Notification.objects.filter(recipient=self.buyer, verb='delivered').exists())

        self.client.force_login(self.buyer)
        self.assertContains(self.client.get(reverse('shop:order-detail', args=[cart.pk])), 'TCG123456')

    def test_students_cannot_open_fulfilment(self):
        self.assertNotEqual(self.client.get(reverse('shop:fulfilment')).status_code, 200)


@override_settings(**dict(FLAT, COURIER_GUY_API_KEY='test-key',
                          COURIER_GUY_BASE_URL='https://courier.test/v2/'))
class LiveCourierTests(TestCase):
    RATES = {'rates': [
        {'rate': 139.5, 'service_level': {'code': 'ECO', 'name': 'Economy',
                                          'delivery_date_from': '2026-10-02T00:00', 'delivery_date_to': '2026-10-05T00:00'}},
        {'rate': 210.0, 'service_level': {'code': 'OVN', 'name': 'Overnight'}},
        {'rate': 69.0, 'service_level': {'code': 'D2LXS - ECO', 'name': 'Door to locker'}},
    ]}

    def setUp(self):
        self.buyer = _onboarded(User.objects.create_user('buyer', 'buyer@example.com', 'pw12345!'))
        self.hoodie = Product.objects.create(name='Hoodie', price=Decimal('650'), fulfilment=Product.FULFIL_SHIPPED,
                                             weight_kg=Decimal('0.8'))
        self.cart = Order.get_cart(self.buyer)
        OrderItem.objects.create(order=self.cart, product=self.hoodie, quantity=2)
        self.address = Address.objects.create(user=self.buyer, recipient='T', phone='0825551234',
                                              street_address='12 Kloof Rd', suburb='Croydon', city='Cape Town',
                                              province='WC', postal_code='7130')

    @mock.patch('requests.request')
    def test_live_quote_filters_by_method_and_sorts(self, request):
        request.return_value = _response(self.RATES)
        options = courier.quote(list(self.cart.items.all()), method='door', goods_total=Decimal('1300'),
                                address=self.address.snapshot())
        self.assertEqual([o.service_level for o in options], ['ECO', 'OVN'])
        self.assertEqual(options[0].amount, Decimal('139.50'))
        sent = request.call_args.kwargs['json']
        self.assertEqual(sent['delivery_address']['zone'], 'WC')
        self.assertEqual(sent['parcels'][0]['submitted_weight_kg'], 1.6)
        self.assertEqual(request.call_args.kwargs['headers']['Authorization'], 'Bearer test-key')

        lockers = courier.quote(list(self.cart.items.all()), method='locker', goods_total=Decimal('1300'),
                                locker='L123')
        self.assertEqual([o.service_level for o in lockers], ['D2LXS - ECO'])

    @mock.patch('requests.request')
    def test_book_and_track(self, request):
        self.cart.ship_to = self.address.snapshot()
        self.cart.save()
        shipment = Shipment.objects.create(order=self.cart, method='door', service_level='ECO',
                                           status=Shipment.STATUS_READY)
        request.return_value = _response({'id': 991, 'short_tracking_reference': 'ABC123', 'rate': 139.5})
        staff = User.objects.create_user('staff', 's@example.com', 'pw12345!', is_staff=True)
        fulfilment.book_courier(shipment, by=staff)
        shipment.refresh_from_db()
        self.assertEqual((shipment.status, shipment.tracking_reference, shipment.courier_cost),
                         (Shipment.STATUS_BOOKED, 'ABC123', Decimal('139.50')))
        self.assertEqual(request.call_args.kwargs['json']['service_level_code'], 'ECO')

        request.return_value = _response({'shipments': [{'status': 'delivered', 'tracking_events': [
            {'date': '2026-10-03T10:00:00+02:00', 'status': 'delivered', 'message': 'Delivered to recipient'}]}]})
        fulfilment.refresh_tracking()
        shipment.refresh_from_db()
        self.assertEqual(shipment.status, Shipment.STATUS_DELIVERED)
        self.assertEqual(shipment.events[-1]['message'], 'Delivered')

    @mock.patch('requests.request')
    def test_courier_outage_is_a_clear_error(self, request):
        request.return_value = _response({}, status=503)
        with self.assertRaises(courier.CourierError):
            courier.quote(list(self.cart.items.all()), method='door', goods_total=Decimal('1300'),
                          address=self.address.snapshot())
