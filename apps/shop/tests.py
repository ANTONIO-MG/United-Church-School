"""Shop phase 1: one priced quote from cart to PayFast, and what a sale sets off.

The bug these guard against: the cart showed discounts, but checkout copied the
undiscounted line prices onto the invoice — so the buyer was charged in full —
and coupons were never counted as used.
"""
import shutil
import tempfile
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.communication.models import Notification
from apps.finance import models as finance
from apps.finance import services as finance_services

from . import checkout, pricing
from .models import Discount, DownloadLog, Order, OrderItem, Product, ProductFile, ProductVariant

User = get_user_model()
MEDIA = tempfile.mkdtemp()


def _onboarded(user):
    """A student who has finished registration, so onboarding lets them in."""
    person = user.profile
    person.user_type, person.registered, person.profile_status = 'student', True, True
    person.save()
    return user


def _free_door(user):
    """A delivery choice for carts with shipped items (free, so totals are goods only)."""
    from .models import Address
    address = Address.objects.create(user=user, recipient='Test Buyer', phone='0825551234',
                                     street_address='1 Main Rd', suburb='Yeoville', city='Johannesburg',
                                     province='GP', postal_code='2198')
    return {'method': 'door', 'address': address, 'locker_id': '', 'locker_name': '',
            'option': {'label': 'Courier to your door', 'service_level': ''}, 'amount': Decimal('0')}


def _cart(user, *lines):
    cart = Order.get_cart(user)
    for product, qty, variant in lines:
        OrderItem.objects.create(order=cart, product=product, quantity=qty, variant=variant)
    return cart


@override_settings(VAT_REGISTERED=False)
class PricingTests(TestCase):
    def setUp(self):
        self.buyer = User.objects.create_user('buyer', 'buyer@example.com', 'pw12345!')
        self.pack = Product.objects.create(name='FREP pack', price=Decimal('450'), discount_percent=20,
                                           fulfilment=Product.FULFIL_NONE)
        self.hoodie = Product.objects.create(name='Hoodie', price=Decimal('650'),
                                             fulfilment=Product.FULFIL_SHIPPED)

    def test_product_discount_percent_applies(self):
        quote = pricing.price_cart(_cart(self.buyer, (self.pack, 1, None)))
        self.assertEqual(quote['discount'], Decimal('90.00'))
        self.assertEqual(quote['total'], Decimal('360.00'))

    def test_best_automatic_saving_wins_and_does_not_compound(self):
        Discount.objects.create(name='Launch week', discount_type='percent', value=Decimal('30'))
        quote = pricing.price_cart(_cart(self.buyer, (self.pack, 1, None)))
        # 30% promotion beats the product's own 20%; they are not stacked.
        self.assertEqual(quote['discount'], Decimal('135.00'))
        self.assertEqual(quote['lines'][0]['label'], 'Launch week')

    def test_one_coupon_on_top_of_best_deal(self):
        Discount.objects.create(name='Ten off', code='TEN', discount_type='percent', value=Decimal('10'))
        quote = pricing.price_cart(_cart(self.buyer, (self.pack, 1, None)), 'ten')
        # 450 − 20% = 360, then 10% of 360 = 36 → 324.
        self.assertEqual(quote['total'], Decimal('324.00'))
        self.assertEqual(quote['coupon'].code, 'TEN')

    def test_fixed_coupon_is_taken_once_not_per_line(self):
        Discount.objects.create(name='R100 off', code='R100', discount_type='amount', value=Decimal('100'))
        cart = _cart(self.buyer, (self.pack, 1, None), (self.hoodie, 1, None))
        quote = pricing.price_cart(cart, 'R100')
        # 360 + 650 = 1010, less R100 once — not R100 on each line.
        self.assertEqual(quote['total'], Decimal('910.00'))
        coupon_off = sum(line.get('coupon_off', 0) for line in quote['lines'])
        self.assertEqual(coupon_off, Decimal('100.00'))

    def test_min_spend_miss_does_not_wipe_other_discounts(self):
        Discount.objects.create(name='Big spender', code='BIG', discount_type='percent',
                                value=Decimal('50'), min_spend=Decimal('5000'))
        quote = pricing.price_cart(_cart(self.buyer, (self.pack, 1, None)), 'BIG')
        self.assertIsNone(quote['coupon'])
        self.assertIn('5,000', quote['coupon_error'])
        self.assertEqual(quote['discount'], Decimal('90.00'))  # the product % survives

    @override_settings(VAT_REGISTERED=True, VAT_RATE='15')
    def test_vat_is_extracted_from_inclusive_total(self):
        quote = pricing.price_cart(_cart(self.buyer, (self.hoodie, 1, None)))
        self.assertEqual(quote['total'], Decimal('650.00'))
        self.assertEqual(quote['vat'], Decimal('84.78'))


@override_settings(VAT_REGISTERED=True, VAT_RATE='15', PAYMENTS_ENABLED=True, MEDIA_ROOT=MEDIA)
class CheckoutTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA, ignore_errors=True)

    def setUp(self):
        self.buyer = _onboarded(User.objects.create_user('buyer', 'buyer@example.com', 'pw12345!'))
        self.staff = User.objects.create_user('staff', 'staff@example.com', 'pw12345!', is_staff=True)
        self.bystander = _onboarded(User.objects.create_user('other', 'other@example.com', 'pw12345!'))
        self.pack = Product.objects.create(name='FREP pack', price=Decimal('450'), discount_percent=20)
        ProductFile.objects.create(product=self.pack, original_name='frep.pdf',
                                   file=SimpleUploadedFile('frep.pdf', b'%PDF-1.4 test'))
        self.hoodie = Product.objects.create(name='Hoodie', price=Decimal('650'), track_stock=True,
                                             fulfilment=Product.FULFIL_SHIPPED)
        self.large = ProductVariant.objects.create(product=self.hoodie, name='L', stock=3)
        self.coupon = Discount.objects.create(name='Ten off', code='TEN', discount_type='percent',
                                              value=Decimal('10'))
        self.client.force_login(self.buyer)

    def _checkout(self, coupon=''):
        cart = _cart(self.buyer, (self.pack, 1, None), (self.hoodie, 2, self.large))
        return cart, checkout.place_order(cart, user=self.buyer, coupon=coupon,
                                          delivery=_free_door(self.buyer))

    def test_invoice_matches_the_quote_the_buyer_saw(self):
        cart = _cart(self.buyer, (self.pack, 1, None), (self.hoodie, 2, self.large))
        quote = pricing.price_cart(cart, 'TEN')
        invoice = checkout.place_order(cart, user=self.buyer, coupon='TEN', delivery=_free_door(self.buyer))
        self.assertEqual(invoice.total, quote['total'])
        self.assertEqual(invoice.balance, quote['total'])
        self.assertEqual(invoice.discount_total, quote['discount'])
        # VAT-inclusive: the VAT is inside the total, not added to it.
        self.assertEqual(invoice.tax_rate, Decimal('15'))
        self.assertEqual(invoice.tax_amount, finance.vat_portion(invoice.total, 15))
        cart.refresh_from_db()
        self.assertTrue(cart.checked_out)
        self.assertEqual(cart.total, quote['total'])
        self.assertEqual(cart.coupon, self.coupon)

    def test_checkout_view_sends_the_discounted_amount_to_payfast(self):
        _cart(self.buyer, (self.pack, 1, None))
        response = self.client.post(reverse('finance:checkout'))
        invoice = finance.Invoice.objects.get(customer=self.buyer)
        self.assertRedirects(response, reverse('finance:pay', args=[invoice.public_id]),
                             fetch_redirect_response=False)
        self.assertEqual(invoice.total, Decimal('360.00'))

    def test_payment_runs_side_effects_once(self):
        cart, invoice = self._checkout('TEN')
        finance_services.settle_payment(invoice, invoice.balance, gateway_ref='PF-1')
        finance_services.settle_payment(invoice, Decimal('0'), gateway_ref='PF-1')  # ITN retry

        cart.refresh_from_db()
        self.large.refresh_from_db()
        self.coupon.refresh_from_db()
        self.assertEqual(cart.status, Order.STATUS_PAID)
        self.assertIsNotNone(cart.paid_processed_at)
        self.assertEqual(self.large.stock, 1)
        self.assertEqual(self.coupon.times_used, 1)

    def test_buyer_notified_about_their_purchase_only(self):
        cart, invoice = self._checkout()
        finance_services.settle_payment(invoice, invoice.balance, gateway_ref='PF-2')
        mine = Notification.objects.filter(recipient=self.buyer, verb='purchase')
        self.assertEqual(mine.count(), 1)
        self.assertIn(cart.order_no, mine.get().title)
        self.assertFalse(Notification.objects.filter(recipient=self.bystander).exists())
        self.assertTrue(Notification.objects.filter(recipient=self.staff, verb='sale').exists())

    def test_out_of_stock_blocks_checkout(self):
        cart = _cart(self.buyer, (self.hoodie, 5, self.large))
        with self.assertRaises(checkout.CheckoutError):
            checkout.place_order(cart, user=self.buyer, delivery=_free_door(self.buyer))

    def test_shipped_items_need_a_delivery_choice(self):
        cart = _cart(self.buyer, (self.hoodie, 1, self.large))
        with self.assertRaises(checkout.CheckoutError):
            checkout.place_order(cart, user=self.buyer)

    def test_free_order_settles_without_payfast(self):
        free = Product.objects.create(name='Free guide', price=0)
        ProductFile.objects.create(product=free, original_name='g.pdf',
                                   file=SimpleUploadedFile('g.pdf', b'%PDF-1.4'))
        cart = _cart(self.buyer, (free, 1, None))
        invoice = checkout.place_order(cart, user=self.buyer)
        self.assertEqual(invoice.status, finance.Invoice.STATUS_PAID)
        cart.refresh_from_db()
        self.assertEqual(cart.status, Order.STATUS_PAID)

    def test_downloads_are_gated_and_logged(self):
        file_obj = self.pack.files.get()
        url = reverse('shop:download-file', args=[self.pack.pk, file_obj.pk])
        self.assertEqual(self.client.get(url).status_code, 404)

        cart, invoice = self._checkout()
        finance_services.settle_payment(invoice, invoice.balance, gateway_ref='PF-3')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Consume through the client's wrapper; calling close() directly fires
        # request_finished and drops the test database connection.
        self.assertTrue(b''.join(response.streaming_content).startswith(b'%PDF'))
        self.assertEqual(DownloadLog.objects.filter(user=self.buyer, file=file_obj).count(), 1)

        self.client.force_login(self.bystander)
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_digital_items_are_capped_at_one(self):
        self.client.post(reverse('shop:add-to-cart', args=[self.pack.pk]), {'quantity': 4})
        self.client.post(reverse('shop:add-to-cart', args=[self.pack.pk]), {'quantity': 1})
        self.assertEqual(Order.get_cart(self.buyer).items.get().quantity, 1)

    def test_variant_required_for_sized_items(self):
        self.client.post(reverse('shop:add-to-cart', args=[self.hoodie.pk]))
        self.assertFalse(Order.get_cart(self.buyer).items.exists())
        self.client.post(reverse('shop:add-to-cart', args=[self.hoodie.pk]), {'variant': self.large.pk})
        self.assertEqual(Order.get_cart(self.buyer).items.get().variant, self.large)

    def test_coupon_applied_through_the_cart(self):
        _cart(self.buyer, (self.pack, 1, None))
        self.client.post(reverse('shop:apply-coupon'), {'code': 'ten'})
        response = self.client.get(reverse('shop:cart'))
        self.assertContains(response, 'R324.00')

    def test_pages_render(self):
        _cart(self.buyer, (self.pack, 1, None))
        for name, args in [('shop:storefront', []), ('shop:product-detail', [self.pack.pk]),
                           ('shop:product-detail', [self.hoodie.pk]), ('shop:cart', []),
                           ('finance:checkout', []), ('shop:my-orders', [])]:
            self.assertEqual(self.client.get(reverse(name, args=args)).status_code, 200, name)
        self.assertContains(self.client.get(reverse('shop:storefront') + '?aisle=store'), 'Hoodie')

    def test_invoice_and_receipt_pdfs(self):
        cart, invoice = self._checkout()
        self.assertEqual(self.client.get(reverse('finance:receipt-pdf', args=[invoice.pk])).status_code, 404)
        response = self.client.get(reverse('finance:invoice-pdf', args=[invoice.pk]))
        self.assertEqual(response['Content-Type'], 'application/pdf')
        finance_services.settle_payment(invoice, invoice.balance, gateway_ref='PF-4')
        response = self.client.get(reverse('finance:receipt-pdf', args=[invoice.pk]))
        self.assertEqual(response['Content-Type'], 'application/pdf')


@override_settings(MEDIA_ROOT=MEDIA)
class ProductEditorTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user('staff', 'staff@example.com', 'pw12345!', is_staff=True)
        self.client.force_login(self.staff)

    def _post(self, **extra):
        data = {'fulfilment': 'digital', 'name': 'Audit pack', 'price': '300', 'discount_percent': '10',
                'status': 'active', 'weight_kg': '0', 'length_cm': '0', 'width_cm': '0',
                'height_cm': '0', 'stock': '0',
                'variants-TOTAL_FORMS': '0', 'variants-INITIAL_FORMS': '0',
                'variants-MIN_NUM_FORMS': '0', 'variants-MAX_NUM_FORMS': '1000',
                'rates-TOTAL_FORMS': '0', 'rates-INITIAL_FORMS': '0',
                'rates-MIN_NUM_FORMS': '0', 'rates-MAX_NUM_FORMS': '1000'}
        data.update(extra)
        return self.client.post(reverse('shop:add-product'), data)

    def test_digital_product_needs_a_file(self):
        self._post()
        self.assertFalse(Product.objects.exists())

    def test_digital_product_with_several_files(self):
        files = [SimpleUploadedFile('a.pdf', b'%PDF-1.4 a'), SimpleUploadedFile('b.zip', b'PK\x03\x04')]
        response = self._post(new_files=files)
        self.assertRedirects(response, reverse('shop:all-products'), fetch_redirect_response=False)
        product = Product.objects.get()
        self.assertEqual(product.files.count(), 2)
        self.assertEqual(product.sale_price, Decimal('270.00'))

    def test_rejects_executable(self):
        self._post(new_files=[SimpleUploadedFile('evil.exe', b'MZ')])
        self.assertFalse(Product.objects.exists())

    def test_shipped_product_with_sizes(self):
        response = self._post(**{
            'fulfilment': 'shipped', 'name': 'Hoodie', 'track_stock': 'on',
            'variants-TOTAL_FORMS': '2',
            'variants-0-name': 'M', 'variants-0-stock': '4', 'variants-0-price_adjustment': '0', 'variants-0-is_active': 'on',
            'variants-1-name': 'XL', 'variants-1-stock': '0', 'variants-1-price_adjustment': '50', 'variants-1-is_active': 'on',
        })
        self.assertEqual(response.status_code, 302)
        product = Product.objects.get()
        self.assertEqual(product.kind, Product.KIND_PRODUCT)
        self.assertEqual(sorted(product.variants.values_list('name', flat=True)), ['M', 'XL'])
        self.assertTrue(product.in_stock)

    def test_booking_service_with_educator_rates(self):
        educator = User.objects.create_user('edu', 'edu@example.com', 'pw12345!').profile
        educator.user_type = 'educator'
        educator.save()
        response = self._post(**{
            'fulfilment': 'booking', 'name': 'Tax consult', 'lengths': ['30', '60'],
            'buffer_minutes': '10', 'rates-TOTAL_FORMS': '1',
            'rates-0-educator': educator.pk, 'rates-0-hourly_rate': '500', 'rates-0-is_active': 'on',
        })
        self.assertEqual(response.status_code, 302)
        product = Product.objects.get()
        self.assertEqual(product.kind, Product.KIND_SERVICE)
        self.assertEqual(product.lengths, [30, 60])
        self.assertEqual(product.buffer_minutes, 10)
        self.assertEqual(product.lowest_rate, Decimal('500.00'))

    def test_editor_pages_render(self):
        self.assertEqual(self.client.get(reverse('shop:add-product')).status_code, 200)
        self.assertEqual(self.client.get(reverse('shop:all-products')).status_code, 200)
