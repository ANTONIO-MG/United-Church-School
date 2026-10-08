"""Data models for the shop app.

The shop lets staff list **products** and **services** (optionally tied to a
course or module — e.g. "tuition fee for Grade 5 Maths") and lets regular
users / parents purchase them and track payment + expiry:

* :class:`ProductCategory` / :class:`Product` — the catalogue.
* :class:`Order` + :class:`OrderItem` — a purchase (one buyer, one or more
  line items); :class:`OrderItem.expiry_date` is derived from a service's
  ``validity_days`` so subscriptions/term fees expire automatically.
* :class:`Payment` — money received against an order; the order flips to
  *paid* once the balance is cleared (see :mod:`apps.shop.signals`).
"""

import uuid
from datetime import timedelta
from decimal import ROUND_HALF_UP, Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from core import validators as v


STATUS_CHOICES = [
    ('active', 'Active'),
    ('inactive', 'Inactive'),
]


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# ---------------------------------------------------------------------------
# Catalogue
# ---------------------------------------------------------------------------
class ProductCategory(TimeStampedModel):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')

    class Meta:
        ordering = ['name']
        verbose_name = 'Product category'
        verbose_name_plural = 'Product categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:140]
        super().save(*args, **kwargs)


class Product(TimeStampedModel):
    KIND_PRODUCT = 'product'
    KIND_SERVICE = 'service'
    KIND_CHOICES = [
        (KIND_PRODUCT, 'Product'),
        (KIND_SERVICE, 'Service'),
    ]

    # What happens after payment. This, not ``kind``, is what the shop acts on:
    # a digital item unlocks its files, a booking confirms a 1-on-1 slot, a
    # shipped item goes to the courier, and a plain fee just settles.
    # ``kind`` is kept in step (booking → service, everything else → product)
    # because older pages and reports still group by it.
    FULFIL_DIGITAL = 'digital'
    FULFIL_BOOKING = 'booking'
    FULFIL_SHIPPED = 'shipped'
    FULFIL_NONE = 'none'
    FULFILMENT_CHOICES = [
        (FULFIL_DIGITAL, 'Digital download'),
        (FULFIL_BOOKING, '1-on-1 session'),
        (FULFIL_SHIPPED, 'Shipped item'),
        (FULFIL_NONE, 'Fee / other'),
    ]
    #: The storefront's three aisles, keyed by the fulfilment they hold.
    AISLES = {
        'resources': (FULFIL_DIGITAL, 'Learning resources'),
        'sessions': (FULFIL_BOOKING, '1-on-1 sessions'),
        'store': (FULFIL_SHIPPED, 'Study-materials store'),
    }

    category = models.ForeignKey(
        ProductCategory, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='products',
    )
    kind = models.CharField(max_length=10, choices=KIND_CHOICES, default=KIND_PRODUCT)
    fulfilment = models.CharField(max_length=10, choices=FULFILMENT_CHOICES,
                                  default=FULFIL_DIGITAL, db_index=True)
    name = models.CharField(max_length=200)
    sku = models.CharField('SKU', max_length=40, unique=True, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0,
                                help_text='Selling price in rand, VAT included where VAT applies.')
    discount_percent = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text='Percentage off the price, shown as a sale on the card. 0 = no discount.')
    image = models.ImageField(upload_to='shop/products/', blank=True, null=True,
                              validators=v.validate_image)
    stock = models.PositiveIntegerField(default=0, help_text='Units in stock (products only).')
    track_stock = models.BooleanField(
        default=False,
        help_text='Stop selling when stock (or a size\'s stock) reaches zero.')

    # --- 1-on-1 sessions (booking) ------------------------------------------
    # The rate itself lives per educator (EducatorRate); ``price`` is only the
    # "from" figure on the card. Everything here is staff-set.
    session_lengths = models.CharField(
        max_length=40, default='30,60,90,120',
        help_text='Minutes a student may book, comma-separated.')
    buffer_minutes = models.PositiveSmallIntegerField(
        default=15, help_text='Gap kept free either side of every session.')
    min_notice_hours = models.PositiveSmallIntegerField(
        default=24, help_text='How far ahead a session must be booked.')
    reschedule_cutoff_hours = models.PositiveSmallIntegerField(
        default=24, help_text='A student may move a session until this many hours before it.')
    booking_window_days = models.PositiveSmallIntegerField(
        default=28, help_text='How far into the future sessions can be booked.')

    # --- Parcel (shipped items) — what the courier quotes on -----------------
    weight_kg = models.DecimalField(max_digits=6, decimal_places=2, default=0,
                                    help_text='Packed weight of one unit, in kg.')
    length_cm = models.PositiveIntegerField(default=0)
    width_cm = models.PositiveIntegerField(default=0)
    height_cm = models.PositiveIntegerField(default=0)
    validity_days = models.PositiveIntegerField(
        null=True, blank=True,
        help_text='Days until a purchased service expires (services only).',
    )

    # --- Who the item is for ------------------------------------------------
    # The catalogue is one table but not one shop: a Grade 12 past-paper pack is
    # meaningless to a Grade 3 parent, while a school jersey is for everybody. Leaving
    # `institution` blank is what makes an item general; setting it scopes the
    # item to that institution, and `programme` narrows it further still.
    # Enforced in one place — see shop.scoping.visible_products.
    institution = models.ForeignKey(
        'learning.Institution', on_delete=models.CASCADE, null=True, blank=True,
        related_name='shop_products',
        help_text='Blank = a general item everyone can see (merchandise, open resources).',
    )
    programme = models.ForeignKey(
        'learning.Programme', on_delete=models.CASCADE, null=True, blank=True,
        related_name='shop_products',
        help_text='Narrows the item to one programme at that institution. Blank = all of them.',
    )
    # Optionally tie a purchasable item to a course / module — so a parent can
    # "pay the fee for a class" and the purchase links to that class, and so
    # myhub courses surface in the shop as buyable items. A tag for filtering,
    # not a gate: a candidate may buy material for a module they are not on.
    module = models.ForeignKey(
        'learning.ProgrammeModule', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='shop_products',
    )

    # --- Digital delivery ---------------------------------------------------
    # Most of what this shop sells is a file: a zip of past papers, a worksheet
    # PDF, a question-and-answer pack. Attaching it here is what turns a paid
    # order into a download — see shop.entitlements.
    digital_file = models.FileField(
        upload_to='shop/downloads/', blank=True, null=True,
        help_text='The zip or document the buyer downloads once the order is paid.',
        validators=v.validate_download,
    )

    @property
    def is_digital(self):
        """True when there is a file to deliver rather than something to post."""
        if self.digital_file:
            return True
        if self.pk is None:
            return False
        return self.files.exists()

    def deliverables(self):
        """Every file a buyer receives, as ``(label, fieldfile, file_id)``.

        ``file_id`` is ``None`` for the legacy single ``digital_file``, which is
        still honoured so nothing uploaded before multi-file support is lost.
        """
        out = []
        if self.digital_file:
            out.append((self.digital_file.name.rsplit('/', 1)[-1], self.digital_file, None))
        if self.pk is not None:
            for f in self.files.all():
                out.append((f.label, f.file, f.pk))
        return out

    # --- Storefront display fields (product-card look) ---
    LEVEL_CHOICES = [
        ('', '—'), ('beginner', 'Beginner'), ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'), ('all', 'All levels'),
    ]
    summary = models.CharField(max_length=300, blank=True, help_text='Short one-line tagline shown on the card.')
    educator = models.ForeignKey(
        'accounts.Person', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='taught_products', help_text='The instructor for this item.',
    )
    duration = models.CharField(max_length=60, blank=True, help_text='e.g. "12 weeks", "3 Months".')
    level = models.CharField(max_length=12, choices=LEVEL_CHOICES, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0,
                                 help_text='Average review rating (0–5), recomputed from reviews.')
    rating_count = models.PositiveIntegerField(default=0)
    students_count = models.PositiveIntegerField(default=0, help_text='Enrolled / sold count (display).')
    featured = models.BooleanField(default=False)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='+',
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def is_service(self):
        return self.kind == self.KIND_SERVICE

    @property
    def is_shipped(self):
        return self.fulfilment == self.FULFIL_SHIPPED

    @property
    def is_booking(self):
        return self.fulfilment == self.FULFIL_BOOKING

    @property
    def has_discount(self):
        return bool(self.discount_percent) and self.discount_percent > 0 and self.price > 0

    def sale_price_for(self, unit_price):
        """``unit_price`` less this product's own discount %, to the cent."""
        unit_price = Decimal(str(unit_price or 0))
        if not self.has_discount:
            return unit_price
        off = unit_price * Decimal(str(self.discount_percent)) / Decimal('100')
        return (unit_price - off).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    @property
    def sale_price(self):
        return self.sale_price_for(self.price)

    @property
    def lengths(self):
        """Bookable session lengths in minutes, sorted, never empty."""
        out = []
        for part in (self.session_lengths or '').split(','):
            try:
                value = int(part.strip())
            except ValueError:
                continue
            if 15 <= value <= 480 and value not in out:
                out.append(value)
        return sorted(out) or [60]

    @property
    def active_rates(self):
        if self.pk is None:
            return []
        return [rate for rate in self.educator_rates.all() if rate.is_active]

    @property
    def lowest_rate(self):
        rates = [rate.hourly_rate for rate in self.active_rates]
        return min(rates) if rates else self.price

    @property
    def active_variants(self):
        if self.pk is None:
            return []
        return [variant for variant in self.variants.all() if variant.is_active]

    @property
    def in_stock(self):
        """False only when stock is tracked and nothing is left to sell."""
        if not self.track_stock:
            return True
        variants = self.active_variants
        if variants:
            return any(variant.stock > 0 for variant in variants)
        return self.stock > 0

    @property
    def is_bookable(self):
        return self.is_booking and bool(self.active_rates)

    @property
    def max_quantity(self):
        """How many one buyer may put in a cart: one of a file, one of a slot."""
        if self.fulfilment in (self.FULFIL_DIGITAL, self.FULFIL_BOOKING):
            return 1
        return None

    @property
    def educator_name(self):
        if self.educator:
            return str(self.educator)
        return ''

    @property
    def star_range(self):
        """List for rendering star icons: 'full' / 'half' / 'empty' per star."""
        value = float(self.rating or 0)
        stars = []
        for position in range(1, 6):
            if value >= position:
                stars.append('full')
            elif value >= position - 0.5:
                stars.append('half')
            else:
                stars.append('empty')
        return stars

    def recompute_rating(self):
        """Recalculate the cached rating + count from this product's reviews."""
        aggregated = self.reviews.aggregate(avg=models.Avg('rating'), n=models.Count('id'))
        self.rating = round(aggregated['avg'] or 0, 2)
        self.rating_count = aggregated['n'] or 0
        self.save(update_fields=['rating', 'rating_count', 'updated_at'])

    def save(self, *args, **kwargs):
        if not self.sku:
            self.sku = f'SKU-{uuid.uuid4().hex[:8].upper()}'
        self.kind = self.KIND_SERVICE if self.fulfilment == self.FULFIL_BOOKING else self.KIND_PRODUCT
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('shop:product-detail', args=[self.pk])


class ProductFile(TimeStampedModel):
    """One downloadable file of a digital product — a pack is often several."""

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='shop/downloads/',
                            validators=v.validate_download)
    title = models.CharField(max_length=200, blank=True,
                             help_text='Shown to the buyer. Blank = the file name.')
    original_name = models.CharField(max_length=255, blank=True)
    size = models.PositiveBigIntegerField(default=0)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.label

    @property
    def label(self):
        return self.title or self.original_name or self.file.name.rsplit('/', 1)[-1]

    @property
    def extension(self):
        return (self.original_name or self.file.name).rsplit('.', 1)[-1].lower()


class ProductImage(TimeStampedModel):
    """A gallery picture. The product's own ``image`` stays the cover."""

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='gallery')
    image = models.ImageField(upload_to='shop/gallery/', validators=v.validate_image)
    alt = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.alt or f'{self.product} image'


class ProductVariant(TimeStampedModel):
    """A size or colour of a shipped item — the hoodie in L, in navy.

    Stock lives here when the product has variants, because "we have hoodies"
    is not the same as "we have a large".
    """

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    name = models.CharField(max_length=60, help_text='e.g. "L", "Navy / XL".')
    sku = models.CharField('SKU', max_length=40, blank=True)
    price_adjustment = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        help_text='Added to the product price for this option (negative to reduce).')
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f'{self.product.name} — {self.name}'

    @property
    def unit_price(self):
        return (self.product.price or Decimal('0')) + (self.price_adjustment or Decimal('0'))


class DownloadLog(models.Model):
    """Who downloaded which purchased file, and when — the audit trail that
    makes "unlimited downloads" safe to offer."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='shop_downloads')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='download_logs')
    file = models.ForeignKey(ProductFile, on_delete=models.SET_NULL, null=True, blank=True,
                             related_name='download_logs')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class ProductReview(TimeStampedModel):
    """A buyer's star rating + comment on a product/course."""

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='product_reviews')
    rating = models.PositiveSmallIntegerField(default=5, help_text='1–5 stars.')
    comment = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('product', 'user')

    def __str__(self):
        return f'{self.user} · {self.product} ({self.rating}★)'


# ---------------------------------------------------------------------------
# Orders & payments
# ---------------------------------------------------------------------------
class Order(TimeStampedModel):
    STATUS_PENDING = 'pending'
    STATUS_PAID = 'paid'
    STATUS_CANCELLED = 'cancelled'
    STATUS_REFUNDED = 'refunded'
    ORDER_STATUS = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_PAID, 'Paid'),
        (STATUS_CANCELLED, 'Cancelled'),
        (STATUS_REFUNDED, 'Refunded'),
    ]

    order_no = models.CharField(max_length=40, unique=True, blank=True)
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders',
    )
    status = models.CharField(max_length=10, choices=ORDER_STATUS, default=STATUS_PENDING)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    note = models.TextField(blank=True)
    # An order starts life as the buyer's **cart**. Checking out converts it into
    # an invoice (finance.Invoice) and flips this flag, so the next add-to-cart
    # starts a fresh basket.
    checked_out = models.BooleanField(default=False)

    # Snapshot of the priced quote, frozen at checkout (see shop.checkout). While
    # the order is still a cart these stay zero and the cart is priced live.
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0,
                                   help_text='Sum of lines before discounts.')
    discount_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_total = models.DecimalField(max_digits=12, decimal_places=2, default=0,
                                    help_text='VAT contained in the total (prices are VAT-inclusive).')
    coupon = models.ForeignKey('Discount', on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='orders')
    # Set once the paid-order side effects (stock, coupon count, notifications)
    # have run, so a second settlement callback cannot run them twice.
    paid_processed_at = models.DateTimeField(null=True, blank=True)

    # Delivery, frozen at checkout for orders with shipped items. ``ship_to`` is
    # a snapshot, not a link to the address book: editing a saved address later
    # must not move a parcel that is already on its way.
    DELIVERY_DOOR = 'door'
    DELIVERY_LOCKER = 'locker'
    DELIVERY_CHOICES = [(DELIVERY_DOOR, 'Door-to-door'), (DELIVERY_LOCKER, 'Pudo locker')]
    delivery_method = models.CharField(max_length=10, choices=DELIVERY_CHOICES, blank=True)
    ship_to = models.JSONField(default=dict, blank=True)
    delivery_label = models.CharField(max_length=160, blank=True,
                                      help_text='What the buyer chose, e.g. "Courier Guy Economy".')

    @property
    def needs_delivery(self):
        return any(item.product.is_shipped for item in self.items.all())

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.order_no

    def save(self, *args, **kwargs):
        if not self.order_no:
            self.order_no = f'ORD-{uuid.uuid4().hex[:10].upper()}'
        super().save(*args, **kwargs)

    @classmethod
    def get_cart(cls, user):
        """Return the user's active cart (an un-checked-out order), creating one."""
        cart = cls.objects.filter(buyer=user, checked_out=False).order_by('-created_at').first()
        if cart is None:
            cart = cls.objects.create(buyer=user)
        return cart

    @property
    def item_count(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def amount_paid(self):
        aggregated = self.payments.filter(status=Payment.STATUS_COMPLETED).aggregate(
            total=models.Sum('amount'))
        return aggregated['total'] or 0

    @property
    def balance(self):
        return (self.total or 0) - self.amount_paid

    @property
    def is_paid(self):
        return self.status == self.STATUS_PAID or (self.total > 0 and self.balance <= 0)

    def recalc_total(self):
        """Total payable: the (net) lines plus delivery."""
        aggregated = self.items.aggregate(total=models.Sum('line_total'))
        self.total = (aggregated['total'] or 0) + (self.shipping_total or 0)
        self.save(update_fields=['total', 'updated_at'])

    def get_absolute_url(self):
        return reverse('shop:order-detail', args=[self.pk])


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='order_items')
    variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT, null=True, blank=True,
                                related_name='order_items')
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    # Frozen at checkout from the priced quote; zero while the order is a cart.
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_label = models.CharField(max_length=160, blank=True)
    #: Net: ``unit_price × quantity − discount_amount``.
    line_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    expiry_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'{self.quantity} x {self.description}'

    @property
    def description(self):
        if self.variant_id:
            return f'{self.product.name} — {self.variant.name}'
        return self.product.name

    @property
    def gross_total(self):
        return (self.unit_price or 0) * (self.quantity or 0)

    @property
    def is_expired(self):
        return bool(self.expiry_date and self.expiry_date < timezone.now().date())

    def save(self, *args, **kwargs):
        if self.product_id:
            if not self.unit_price:
                self.unit_price = self.variant.unit_price if self.variant_id else self.product.price
            if not self.expiry_date and self.product.is_service and self.product.validity_days:
                self.expiry_date = timezone.now().date() + timedelta(days=self.product.validity_days)
        self.line_total = self.gross_total - (self.discount_amount or 0)
        super().save(*args, **kwargs)


class Payment(TimeStampedModel):
    STATUS_PENDING = 'pending'
    STATUS_COMPLETED = 'completed'
    STATUS_FAILED = 'failed'
    PAYMENT_STATUS = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_FAILED, 'Failed'),
    ]
    METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('bank', 'Bank Transfer'),
        ('online', 'Online'),
        ('cheque', 'Cheque'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, default='online')
    status = models.CharField(max_length=10, choices=PAYMENT_STATUS, default=STATUS_COMPLETED)
    reference = models.CharField(max_length=80, blank=True)
    paid_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='+',
    )

    class Meta:
        ordering = ['-paid_at']

    def __str__(self):
        return f'{self.amount} for {self.order}'


# ---------------------------------------------------------------------------
# Discounts (created by admin / staff only — see shop.views.staff_required)
# ---------------------------------------------------------------------------
class Discount(TimeStampedModel):
    """A price reduction, either automatic or unlocked by a code.

    Two shapes, one model, because they differ only in how they are triggered:

    * **Promotion** — no ``code``, so it applies on its own to everything in
      scope ("20% off all Grade 12 study packs this week").
    * **Coupon** — has a ``code`` the buyer types at checkout.

    Scope mirrors the catalogue's own: leave the targets blank and it applies to
    the whole cart; set them and it bites only on matching lines. Same rule as
    :mod:`apps.shop.scoping`, so "Grade 12 only" means the same thing in both.
    """

    TYPE_PERCENT = 'percent'
    TYPE_AMOUNT = 'amount'
    TYPE_CHOICES = [(TYPE_PERCENT, 'Percentage off'), (TYPE_AMOUNT, 'Fixed amount off')]

    name = models.CharField(max_length=120, help_text='Shown to the buyer, e.g. "Launch week – 20% off".')
    code = models.CharField(
        max_length=32, blank=True, unique=True, null=True,
        help_text='Leave blank for an automatic promotion; set it to require a coupon code.')
    discount_type = models.CharField(max_length=8, choices=TYPE_CHOICES, default=TYPE_PERCENT)
    value = models.DecimalField(max_digits=8, decimal_places=2,
                                help_text='Percent (0–100) or a rand amount, per discount_type.')

    # Scope — all blank means "the whole catalogue".
    institution = models.ForeignKey('learning.Institution', on_delete=models.CASCADE,
                                    null=True, blank=True, related_name='discounts')
    programme = models.ForeignKey('learning.Programme', on_delete=models.CASCADE,
                                  null=True, blank=True, related_name='discounts')
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE,
                                 null=True, blank=True, related_name='discounts')
    products = models.ManyToManyField(Product, blank=True, related_name='discounts',
                                      help_text='Specific items. Blank = anything else in scope.')

    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    max_uses = models.PositiveIntegerField(null=True, blank=True, help_text='Blank = unlimited.')
    times_used = models.PositiveIntegerField(default=0)
    min_spend = models.DecimalField(max_digits=12, decimal_places=2, default=0,
                                    help_text='Cart total the discount needs before it applies.')
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                   null=True, blank=True, related_name='+')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} ({self.code})' if self.code else self.name

    def save(self, *args, **kwargs):
        # unique=True on a blank string collides between promotions; NULL does not.
        if not self.code:
            self.code = None
        else:
            self.code = self.code.strip().upper()
        super().save(*args, **kwargs)

    @property
    def is_coupon(self):
        return bool(self.code)

    @property
    def is_live(self):
        """Active, inside its window, and not used up."""
        now = timezone.now()
        if not self.is_active:
            return False
        if self.starts_at and now < self.starts_at:
            return False
        if self.ends_at and now > self.ends_at:
            return False
        if self.max_uses is not None and self.times_used >= self.max_uses:
            return False
        return True

    def covers(self, product):
        """True when this discount applies to ``product``."""
        if self.products.exists():
            return self.products.filter(pk=product.pk).exists()
        if self.category_id and product.category_id != self.category_id:
            return False
        if self.institution_id and product.institution_id != self.institution_id:
            return False
        if self.programme_id and product.programme_id != self.programme_id:
            return False
        return True

    def amount_for(self, subtotal):
        """The rand value this discount takes off ``subtotal``, never below zero."""
        from decimal import Decimal
        if subtotal <= 0:
            return Decimal('0')
        if self.discount_type == self.TYPE_PERCENT:
            off = (subtotal * self.value) / Decimal('100')
        else:
            off = self.value
        return min(max(off, Decimal('0')), subtotal).quantize(Decimal('0.01'))


# ---------------------------------------------------------------------------
# 1-on-1 sessions: rates, working hours, bookings, account credit
# ---------------------------------------------------------------------------
class EducatorRate(TimeStampedModel):
    """What one educator charges per hour for one 1-on-1 service. Staff-set."""

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='educator_rates')
    educator = models.ForeignKey('accounts.Person', on_delete=models.CASCADE,
                                 related_name='session_rates')
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2,
                                      validators=[MinValueValidator(0)])
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['hourly_rate', 'id']
        constraints = [models.UniqueConstraint(fields=['product', 'educator'],
                                               name='uniq_rate_per_educator_per_service')]

    def __str__(self):
        return f'{self.educator} · {self.product} · R{self.hourly_rate}/h'

    def price_for(self, minutes):
        return (Decimal(str(self.hourly_rate)) * Decimal(minutes) / Decimal(60)).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP)


class EducatorAvailability(models.Model):
    """A weekly window in which an educator takes 1-on-1s (e.g. Tue 14:00–19:00)."""

    WEEKDAYS = [(0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'), (3, 'Thursday'),
                (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')]

    educator = models.ForeignKey('accounts.Person', on_delete=models.CASCADE,
                                 related_name='availability')
    weekday = models.PositiveSmallIntegerField(choices=WEEKDAYS)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        ordering = ['educator', 'weekday', 'start_time']
        verbose_name_plural = 'Educator availability'

    def __str__(self):
        return f'{self.educator} · {self.get_weekday_display()} {self.start_time:%H:%M}–{self.end_time:%H:%M}'


class EducatorTimeOff(models.Model):
    """A stretch an educator is away — leave, exam invigilation, a conference."""

    educator = models.ForeignKey('accounts.Person', on_delete=models.CASCADE, related_name='time_off')
    start = models.DateTimeField()
    end = models.DateTimeField()
    reason = models.CharField(max_length=160, blank=True)

    class Meta:
        ordering = ['start']
        verbose_name_plural = 'Educator time off'

    def __str__(self):
        return f'{self.educator} away {self.start:%d %b} – {self.end:%d %b}'


class Booking(TimeStampedModel):
    """One 1-on-1 session a student has chosen.

    Life: **held** (in a cart, the slot kept for them for a few minutes) →
    **confirmed** (paid; the live session exists) → **completed**, or
    **cancelled**. A hold that runs out is **expired** and frees the slot.
    """

    STATUS_HELD = 'held'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_EXPIRED = 'expired'
    STATUS_CHOICES = [
        (STATUS_HELD, 'Held — awaiting payment'),
        (STATUS_CONFIRMED, 'Confirmed'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELLED, 'Cancelled'),
        (STATUS_EXPIRED, 'Expired'),
    ]
    #: Statuses that occupy the educator's time.
    BLOCKING = (STATUS_HELD, STATUS_CONFIRMED)

    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='bookings')
    educator = models.ForeignKey('accounts.Person', on_delete=models.PROTECT,
                                 related_name='bookings_taught')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name='session_bookings')
    start = models.DateTimeField(db_index=True)
    end = models.DateTimeField()
    minutes = models.PositiveSmallIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_HELD,
                              db_index=True)
    hold_expires_at = models.DateTimeField(null=True, blank=True)
    order_item = models.OneToOneField(OrderItem, on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name='booking')
    meeting = models.ForeignKey('communication.MeetingRoom', on_delete=models.SET_NULL,
                                null=True, blank=True, related_name='bookings')
    reschedule_count = models.PositiveSmallIntegerField(default=0)
    note = models.TextField(blank=True, help_text='What the student would like to cover.')
    cancelled_reason = models.CharField(max_length=255, blank=True)
    cancelled_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                     null=True, blank=True, related_name='+')

    class Meta:
        ordering = ['start']
        indexes = [models.Index(fields=['educator', 'start'])]

    def __str__(self):
        return f'{self.student} with {self.educator} · {self.start:%d %b %H:%M}'

    @property
    def label(self):
        local = timezone.localtime(self.start)
        return f'{local:%a %-d %b, %H:%M}–{timezone.localtime(self.end):%H:%M}'

    @property
    def is_upcoming(self):
        return self.status == self.STATUS_CONFIRMED and self.start > timezone.now()

    def can_reschedule(self, now=None):
        now = now or timezone.now()
        cutoff = self.start - timedelta(hours=self.product.reschedule_cutoff_hours)
        return self.status == self.STATUS_CONFIRMED and now < cutoff


class CreditEntry(models.Model):
    """Account credit: one line of a student's ledger.

    Positive when credit is granted (a session staff or the educator cancelled),
    negative when it is spent at checkout. The balance is the sum — a ledger
    rather than a stored number, so every rand can be traced to its reason.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='credit_entries')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reason = models.CharField(max_length=255)
    booking = models.ForeignKey(Booking, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='credit_entries')
    invoice = models.ForeignKey('finance.Invoice', on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='credit_entries')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                   null=True, blank=True, related_name='+')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Credit entries'

    def __str__(self):
        return f'{self.user} {self.amount:+} · {self.reason}'

    @classmethod
    def balance_for(cls, user):
        total = cls.objects.filter(user=user).aggregate(total=models.Sum('amount'))['total']
        return max(total or Decimal('0'), Decimal('0'))


# ---------------------------------------------------------------------------
# Delivery: address book and shipments
# ---------------------------------------------------------------------------
PROVINCES = [
    ('GP', 'Gauteng'), ('WC', 'Western Cape'), ('KZN', 'KwaZulu-Natal'), ('EC', 'Eastern Cape'),
    ('FS', 'Free State'), ('LP', 'Limpopo'), ('MP', 'Mpumalanga'), ('NW', 'North West'),
    ('NC', 'Northern Cape'),
]


class Address(TimeStampedModel):
    """A delivery address in a buyer's address book."""

    TYPE_CHOICES = [('residential', 'Home'), ('business', 'Work / business')]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='addresses')
    recipient = models.CharField('Recipient name', max_length=120)
    phone = models.CharField('Mobile number', max_length=30,
                             help_text='The courier SMSes delivery updates to this number.')
    street_address = models.CharField(max_length=200, help_text='Street number and name.')
    complex = models.CharField('Unit / complex / building', max_length=120, blank=True)
    suburb = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    province = models.CharField(max_length=3, choices=PROVINCES)
    postal_code = models.CharField(max_length=4)
    address_type = models.CharField(max_length=12, choices=TYPE_CHOICES, default='residential')
    company = models.CharField(max_length=120, blank=True)
    is_default = models.BooleanField(default=False)

    class Meta:
        ordering = ['-is_default', '-updated_at']
        verbose_name_plural = 'Addresses'

    def __str__(self):
        return f'{self.recipient}, {self.street_address}, {self.suburb}, {self.city} {self.postal_code}'

    @property
    def one_line(self):
        parts = [self.complex, self.street_address, self.suburb, self.city, self.postal_code]
        return ', '.join(p for p in parts if p)

    def snapshot(self):
        return {'recipient': self.recipient, 'phone': self.phone, 'street_address': self.street_address,
                'complex': self.complex, 'suburb': self.suburb, 'city': self.city,
                'province': self.province, 'postal_code': self.postal_code,
                'address_type': self.address_type, 'company': self.company}


class Shipment(TimeStampedModel):
    """Getting one order's parcel to the buyer.

    Created at checkout (``awaiting_payment``), ready to pack once paid
    (``ready``), ``booked`` when a courier waybill exists, then ``in_transit`` /
    ``delivered`` as tracking reports. With no courier API configured staff
    record the tracking number themselves (``carrier = manual``).
    """

    STATUS_AWAITING = 'awaiting_payment'
    STATUS_READY = 'ready'
    STATUS_BOOKED = 'booked'
    STATUS_IN_TRANSIT = 'in_transit'
    STATUS_DELIVERED = 'delivered'
    STATUS_FAILED = 'failed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (STATUS_AWAITING, 'Awaiting payment'),
        (STATUS_READY, 'Ready to pack'),
        (STATUS_BOOKED, 'Courier booked'),
        (STATUS_IN_TRANSIT, 'On its way'),
        (STATUS_DELIVERED, 'Delivered'),
        (STATUS_FAILED, 'Delivery problem'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]
    CARRIER_COURIER_GUY = 'courier_guy'
    CARRIER_MANUAL = 'manual'
    CARRIER_CHOICES = [(CARRIER_COURIER_GUY, 'The Courier Guy'), (CARRIER_MANUAL, 'Other / manual')]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='shipment')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_AWAITING, db_index=True)
    method = models.CharField(max_length=10, choices=Order.DELIVERY_CHOICES)
    carrier = models.CharField(max_length=20, choices=CARRIER_CHOICES, default=CARRIER_COURIER_GUY)
    service_level = models.CharField(max_length=40, blank=True, help_text='Courier service code, e.g. ECO.')
    locker_code = models.CharField(max_length=60, blank=True)
    locker_name = models.CharField(max_length=200, blank=True)
    charged = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                  help_text='What the buyer paid for delivery.')
    courier_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                       help_text='What the courier charged us (from the booking).')
    tracking_reference = models.CharField(max_length=80, blank=True, db_index=True)
    courier_shipment_id = models.CharField(max_length=80, blank=True)
    courier_name = models.CharField(max_length=80, blank=True, help_text='For manual shipments.')
    tracking_url = models.URLField(blank=True)
    events = models.JSONField(default=list, blank=True, help_text='Tracking history, newest last.')
    booked_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    last_tracked_at = models.DateTimeField(null=True, blank=True)
    booked_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                  null=True, blank=True, related_name='+')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.order.order_no} · {self.get_status_display()}'

    @property
    def is_open(self):
        return self.status in (self.STATUS_READY, self.STATUS_BOOKED, self.STATUS_IN_TRANSIT)

    def log(self, status, message, when=None):
        self.events = list(self.events or []) + [{
            'at': (when or timezone.now()).isoformat(), 'status': status, 'message': message}]
