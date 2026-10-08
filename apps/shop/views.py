"""Views for the shop.

Buyers (any logged-in user) browse the storefront, buy a product/service —
which creates an :class:`~apps.shop.models.Order` — and track payment + expiry
on their order pages. Staff manage the catalogue (products & categories) and
can record payments against any order.
"""

from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from core.branding import t
from core.errors import note

from . import forms, models

staff_required = user_passes_test(lambda u: u.is_active and u.is_staff)


# ===========================================================================
# Helpers (mirror apps.myhub.views)
# ===========================================================================
def _save_form(request, form_class, instance, template, *, list_url, page_title,
               extra_context=None):
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            obj = form.save(commit=False)
            if not obj.pk and hasattr(obj, 'created_by') and not obj.created_by_id:
                obj.created_by = request.user
            obj.save()
            form.save_m2m()
            messages.success(request, t('messages.saved', '{name} saved successfully.', name=page_title))
            return redirect(list_url)
        messages.error(request, t('messages.form_errors', 'Please correct the errors highlighted below.'))
    else:
        form = form_class(instance=instance)
    context = {'form': form, 'object': instance, 'page_title': page_title}
    if extra_context:
        context.update(extra_context)
    return render(request, template, context)


def _delete(request, model, pk, list_url, label):
    obj = get_object_or_404(model, pk=pk)
    obj.delete()
    messages.success(request, t('messages.deleted', '{name} deleted.', name=label))
    return redirect(list_url)


def _to_decimal(value, default=Decimal('0')):
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return default


# ===========================================================================
# Storefront (buyers)
# ===========================================================================
def _client_ip(request):
    forwarded = (request.META.get('HTTP_X_FORWARDED_FOR') or '').split(',')[0].strip()
    return forwarded or request.META.get('REMOTE_ADDR') or None


def _serve_download(request, product, fieldfile, file_obj=None):
    from django.http import FileResponse, Http404

    from .entitlements import can_download

    if not can_download(request.user, product):
        note('SHOP-2001', request, product=product.sku)
        raise Http404
    if not fieldfile:
        raise Http404
    models.DownloadLog.objects.create(user=request.user, product=product, file=file_obj,
                                      ip_address=_client_ip(request))
    filename = (getattr(file_obj, 'original_name', '') or fieldfile.name.rsplit('/', 1)[-1])
    return FileResponse(fieldfile.open('rb'), as_attachment=True, filename=filename)


@login_required
def download_product(request, pk):
    """Serve a purchased product's main file. Entitlement is checked here,
    never in a template — a download URL is guessable, so the check has to live
    on the request rather than on whether a button was rendered.
    """
    from django.http import Http404

    product = get_object_or_404(models.Product, pk=pk)
    if product.digital_file:
        return _serve_download(request, product, product.digital_file)
    first = product.files.first()
    if first is None:
        raise Http404
    return _serve_download(request, product, first.file, first)


@login_required
def download_file(request, pk, file_id):
    """Serve one file of a multi-file digital product."""
    product = get_object_or_404(models.Product, pk=pk)
    file_obj = get_object_or_404(models.ProductFile, pk=file_id, product=product)
    return _serve_download(request, product, file_obj.file, file_obj)


def _aisle_counts(products):
    from django.db.models import Count
    counts = dict(products.values_list('fulfilment').annotate(n=Count('id')).values_list('fulfilment', 'n'))
    return {key: counts.get(fulfilment, 0) for key, (fulfilment, _label) in models.Product.AISLES.items()}


@login_required
def storefront(request):
    from .scoping import visible_for_request

    # Scope first, filter second: the facets below can only ever narrow what the
    # viewer is already entitled to see, so a hand-typed ?institution= cannot
    # widen the catalogue (see shop.scoping).
    visible = visible_for_request(request, models.Product.objects.filter(status='active'))
    products = visible.select_related('category', 'module', 'educator', 'institution', 'programme')

    aisle = request.GET.get('aisle', '')
    category = request.GET.get('category')
    institution = request.GET.get('institution')
    programme = request.GET.get('programme')
    module = request.GET.get('module')
    scope = request.GET.get('scope')
    search = request.GET.get('q')
    sort = request.GET.get('sort', '')

    if aisle in models.Product.AISLES:
        products = products.filter(fulfilment=models.Product.AISLES[aisle][0])
    else:
        aisle = ''
    if category:
        products = products.filter(category_id=category)
    if institution:
        products = products.filter(institution_id=institution)
    if programme:
        products = products.filter(programme_id=programme)
    if module:
        products = products.filter(module_id=module)
    if scope == 'general':
        products = products.filter(institution__isnull=True)
    elif scope == 'mine':
        products = products.filter(institution__isnull=False)
    if search:
        products = products.filter(Q(name__icontains=search) | Q(summary__icontains=search)
                                   | Q(description__icontains=search))
    if request.GET.get('sale'):
        products = products.filter(discount_percent__gt=0)

    ordering = {'price': ('price', 'name'), '-price': ('-price', 'name'),
                'new': ('-created_at',), 'popular': ('-students_count', 'name')}
    products = products.order_by(*ordering.get(sort, ('-featured', 'name')))

    # Facet lists are built from what this viewer can see, so the dropdowns never
    # advertise an institution whose products they cannot open.
    from apps.learning.models import Institution, Programme, ProgrammeModule
    aisles = [(key, label, fulfilment) for key, (fulfilment, label) in models.Product.AISLES.items()]
    return render(request, 'shop/storefront.html', {
        'page_title': 'Shop',
        'products': products.prefetch_related('variants'),
        'aisles': aisles, 'aisle': aisle,
        'aisle_counts': _aisle_counts(visible),
        'total_count': visible.count(),
        'categories': models.ProductCategory.objects.filter(
            status='active', pk__in=visible.values('category_id')),
        'institutions': Institution.objects.filter(
            pk__in=visible.values('institution_id')).order_by('order', 'name'),
        'programmes': Programme.objects.filter(
            pk__in=visible.values('programme_id')).select_related('institution').order_by('institution__order', 'order'),
        'modules': ProgrammeModule.objects.filter(
            pk__in=visible.values('module_id')).order_by('code'),
        'search': search or '', 'scope': scope or '', 'sort': sort,
        'sel_category': category or '', 'sel_institution': institution or '',
        'sel_programme': programme or '', 'sel_module': module or '',
        'on_sale': bool(request.GET.get('sale')),
    })


@login_required
def product_detail(request, pk):
    from .entitlements import can_download
    from .scoping import visible_for_request

    product = get_object_or_404(
        models.Product.objects.select_related('educator', 'category', 'institution', 'programme', 'module')
              .prefetch_related('files', 'gallery', 'variants'), pk=pk)
    # A product outside the viewer's catalogue is not theirs to buy, even by URL.
    if not visible_for_request(request, models.Product.objects.filter(pk=pk)).exists() \
            and not request.user.is_staff:
        from django.http import Http404
        raise Http404
    review_form = forms.ProductReviewForm()

    if product.is_booking:
        picker = _booking_picker(request, product)
        if isinstance(picker, HttpResponse):
            return picker
    else:
        picker = None

    if request.method == 'POST':
        action = request.POST.get('action', 'buy')
        if action == 'review':
            existing = models.ProductReview.objects.filter(product=product, user=request.user).first()
            review_form = forms.ProductReviewForm(request.POST, instance=existing)
            if review_form.is_valid():
                review = review_form.save(commit=False)
                review.product = product
                review.user = request.user
                review.save()
                product.recompute_rating()
                messages.success(request, 'Thanks for your review!')
                return redirect('shop:product-detail', pk=product.pk)
            messages.error(request, t('messages.form_errors', 'Please correct the errors highlighted below.'))
        else:  # add to cart → proceed to cart/checkout
            return _add_to_cart(request, product)

    related = (models.Product.objects.filter(status='active', fulfilment=product.fulfilment)
               .exclude(pk=product.pk).select_related('educator'))
    if product.category_id:
        related = related.filter(category=product.category)
    related = visible_for_request(request, related)[:4]
    my_review = models.ProductReview.objects.filter(product=product, user=request.user).first()
    owned = product.is_digital and can_download(request.user, product) and not request.user.is_staff
    return render(request, 'shop/product-detail.html', {
        'page_title': product.name, 'product': product,
        'variants': product.active_variants,
        'files': product.deliverables() if product.is_digital else [],
        'gallery': list(product.gallery.all()),
        'reviews': product.reviews.select_related('user')[:20],
        'review_form': review_form, 'my_review': my_review, 'related': related,
        'owned': owned,
        'vat_registered': getattr(settings, 'VAT_REGISTERED', False),
        'picker': picker,
    })


def _parse_start(value):
    from django.utils.dateparse import parse_datetime
    from django.utils import timezone as tz
    moment = parse_datetime(value or '')
    if moment is None:
        return None
    return tz.make_aware(moment, tz.get_current_timezone()) if tz.is_naive(moment) else moment


def _booking_picker(request, product):
    """State for the 1-on-1 picker, or a redirect once a slot is held/moved.

    Everything is in the query string (educator, length, week), so the picker is
    a plain GET page that works without JavaScript and every view of it is a
    shareable link. ``?reschedule=<id>`` reuses it to move a confirmed booking.
    """
    from datetime import timedelta

    from django.utils import timezone as tz

    from . import booking as booking_service

    moving = None
    if request.GET.get('reschedule') or request.POST.get('reschedule'):
        moving = get_object_or_404(models.Booking.objects.select_related('educator__user', 'product'),
                                   pk=request.GET.get('reschedule') or request.POST.get('reschedule'),
                                   product=product)
        if not (moving.student_id == request.user.id or booking_service._is_staff(request.user)):
            raise Http404

    rates = [r for r in product.educator_rates.select_related('educator__user') if r.is_active]
    if moving:
        rates = [r for r in rates if r.educator_id == moving.educator_id]
    rate = next((r for r in rates if str(r.pk) == request.GET.get('educator', request.POST.get('rate'))),
                rates[0] if rates else None)
    try:
        minutes = int(request.GET.get('minutes') or request.POST.get('minutes') or 0)
    except ValueError:
        minutes = 0
    if moving:
        minutes = moving.minutes
    if minutes not in product.lengths:
        minutes = 60 if 60 in product.lengths else product.lengths[0]

    if request.method == 'POST' and request.POST.get('action') in ('book', 'reschedule') and rate:
        start = _parse_start(request.POST.get('start'))
        if start is None:
            messages.error(request, 'Please pick a time.')
        else:
            try:
                if moving:
                    booking_service.reschedule(moving, start=start, by=request.user)
                    messages.success(request, f'Moved to {moving.label}.')
                    return redirect('shop:my-bookings')
                held = booking_service.hold_slot(user=request.user, rate=rate, start=start,
                                                 minutes=minutes, note=request.POST.get('note', ''))
                messages.success(request, f'{held.label} is held for you for '
                                          f'{booking_service.HOLD_MINUTES} minutes — check out to confirm it.')
                return redirect('shop:cart')
            except booking_service.BookingError as exc:
                messages.error(request, str(exc))

    today = tz.localdate()
    try:
        offset = max(0, min(int(request.GET.get('week', 0)), 8))
    except ValueError:
        offset = 0
    start_day = today + timedelta(days=7 * offset)
    days = []
    if rate:
        days = booking_service.week_of_slots(rate, minutes, start_day, days=7,
                                             exclude_booking=moving)
    chosen_day = request.GET.get('day')
    selected = next((d for d in days if d['day'].isoformat() == chosen_day), None) \
        or next((d for d in days if d['slots']), days[0] if days else None)
    return {
        'rates': rates, 'rate': rate, 'minutes': minutes, 'lengths': product.lengths,
        'days': days, 'selected': selected, 'week': offset,
        'price': rate.price_for(minutes) if rate else None,
        'moving': moving,
        'can_prev': offset > 0,
        'can_next': (offset + 1) * 7 < product.booking_window_days,
    }


# ===========================================================================
# Cart
# ===========================================================================
def _add_to_cart(request, product, quantity=1):
    """Add (or increment) a product in the buyer's active cart."""
    if product.status != 'active':
        messages.error(request, 'That item is no longer on sale.')
        return redirect('shop:storefront')
    if product.is_booking:
        # Booking a 1-on-1 means choosing an educator and a time first; the
        # booking picker adds the line to the cart once a slot is held.
        messages.info(request, 'Choose an educator and a time to book this session.')
        return redirect('shop:product-detail', pk=product.pk)

    try:
        quantity = max(1, int(request.POST.get('quantity', quantity)))
    except (TypeError, ValueError):
        quantity = 1

    variant = None
    if product.active_variants:
        variant = models.ProductVariant.objects.filter(
            pk=request.POST.get('variant') or 0, product=product, is_active=True).first()
        if variant is None:
            messages.error(request, 'Please choose a size / option first.')
            return redirect('shop:product-detail', pk=product.pk)

    cart = models.Order.get_cart(request.user)
    item = cart.items.filter(product=product, variant=variant).first()
    wanted = quantity + (item.quantity if item else 0)
    cap = product.max_quantity
    if cap:
        wanted = min(wanted, cap)
    if product.track_stock:
        available = variant.stock if variant else product.stock
        if available <= 0:
            messages.error(request, f'“{product.name}” is out of stock.')
            return redirect('shop:product-detail', pk=product.pk)
        if wanted > available:
            wanted = available
            messages.warning(request, f'Only {available} left — your cart has been set to {available}.')

    if item:
        if item.quantity == wanted and cap:
            messages.info(request, f'“{product.name}” is already in your cart.')
            return redirect('shop:cart')
        item.quantity = wanted
        item.save()
    else:
        models.OrderItem.objects.create(order=cart, product=product, variant=variant, quantity=wanted)
    cart.recalc_total()
    messages.success(request, f'Added “{product.name}” to your cart.')
    return redirect('shop:cart')


@login_required
@require_POST
def add_to_cart(request, pk):
    product = get_object_or_404(models.Product, pk=pk, status='active')
    return _add_to_cart(request, product)


def cart_context(request, cart):
    """The quote and everything the cart / checkout pages show beside it."""
    from . import checkout, pricing

    quote = pricing.price_cart(cart, checkout.coupon_code(request))
    return {
        'cart': cart, 'quote': quote, 'lines': quote['lines'],
        'problems': checkout.cart_problems(cart),
        'has_shipped': any(line['item'].product.is_shipped for line in quote['lines']),
        'typed_coupon': checkout.coupon_code(request),
    }


@login_required
def cart(request):
    cart = models.Order.get_cart(request.user)
    context = cart_context(request, cart)
    context['page_title'] = 'My cart'
    return render(request, 'shop/cart.html', context)


def _back_to(request, default='shop:cart'):
    """Where to return after a cart action — only ever a path on this site."""
    from django.utils.http import url_has_allowed_host_and_scheme
    target = request.POST.get('next') or ''
    if target and url_has_allowed_host_and_scheme(target, allowed_hosts={request.get_host()},
                                                  require_https=request.is_secure()):
        return redirect(target)
    return redirect(default)


@login_required
@require_POST
def apply_coupon(request):
    from . import checkout, pricing

    if request.POST.get('action') == 'remove':
        request.session.pop(checkout.COUPON_SESSION_KEY, None)
        messages.info(request, 'Coupon removed.')
        return _back_to(request)

    code = (request.POST.get('code') or '').strip().upper()
    if not code:
        return _back_to(request)
    quote = pricing.price_cart(models.Order.get_cart(request.user), code)
    if quote['coupon']:
        request.session[checkout.COUPON_SESSION_KEY] = code
        messages.success(request, f'{code} applied — you save R{quote["discount"]:,.2f}.')
    else:
        request.session.pop(checkout.COUPON_SESSION_KEY, None)
        messages.error(request, quote['coupon_error'] or 'That code is not valid.')
    return _back_to(request)


@login_required
@require_POST
def update_cart_item(request, item_id):
    cart = models.Order.get_cart(request.user)
    item = get_object_or_404(models.OrderItem.objects.select_related('product', 'variant'),
                             pk=item_id, order=cart)
    action = request.POST.get('action')
    if action == 'remove':
        item.delete()
    else:
        try:
            quantity = max(1, int(request.POST.get('quantity', item.quantity)))
        except (TypeError, ValueError):
            quantity = item.quantity
        if item.product.max_quantity:
            quantity = min(quantity, item.product.max_quantity)
        if item.product.track_stock:
            available = item.variant.stock if item.variant_id else item.product.stock
            if quantity > available:
                quantity = max(1, available)
                messages.warning(request, f'Only {available} of “{item.description}” left.')
        item.quantity = quantity
        item.save()
    cart.recalc_total()
    return redirect('shop:cart')


@login_required
def my_orders(request):
    orders = (models.Order.objects.filter(checked_out=True)
              .select_related('buyer').prefetch_related('items__product', 'invoices'))
    if not request.user.is_staff:
        orders = orders.filter(buyer=request.user)
    status = request.GET.get('status')
    if status in dict(models.Order.ORDER_STATUS):
        orders = orders.filter(status=status)
    return render(request, 'shop/orders.html', {
        'page_title': 'My orders' if not request.user.is_staff else 'All orders',
        'orders': orders, 'status': status or '',
        'ORDER_STATUS': models.Order.ORDER_STATUS,
    })


@login_required
def order_detail(request, pk):
    order = get_object_or_404(
        models.Order.objects.select_related('buyer', 'coupon')
              .prefetch_related('items__product__files', 'items__variant', 'payments', 'invoices'),
        pk=pk,
    )
    if not (request.user.is_staff or order.buyer_id == request.user.id):
        messages.error(request, 'You cannot view that order.')
        return redirect('shop:my-orders')

    invoice = order.invoices.order_by('-created_at').first()
    if request.method == 'POST' and request.POST.get('action') == 'pay' and request.user.is_staff:
        # Staff record money against the order's invoice, so the finance record,
        # the receipt and the paid-order side effects all follow the one path.
        if invoice is None:
            messages.error(request, 'This order has no invoice to record a payment against.')
            return redirect('shop:order-detail', pk=order.pk)
        from apps.finance import services as finance
        amount = _to_decimal(request.POST.get('amount'), invoice.balance)
        if amount <= 0:
            amount = invoice.balance
        finance.settle_payment(invoice, min(amount, invoice.balance),
                               method=request.POST.get('method', 'bank'),
                               reference=request.POST.get('reference', ''))
        messages.success(request, 'Payment recorded.')
        return redirect('shop:order-detail', pk=order.pk)

    from apps.finance.models import InvoicePayment
    return render(request, 'shop/order-detail.html', {
        'page_title': order.order_no, 'order': order, 'invoice': invoice,
        'items': order.items.select_related('product', 'variant'),
        'payment_methods': InvoicePayment.METHOD_CHOICES,
        'is_paid': order.status == models.Order.STATUS_PAID,
        'shipment': getattr(order, 'shipment', None) if hasattr(order, 'shipment') else None,
    })


# ===========================================================================
# 1-on-1 bookings
# ===========================================================================
@login_required
def my_bookings(request):
    """Students see their sessions; educators the ones they teach; staff all."""
    from django.utils import timezone as tz

    from . import booking as booking_service

    is_staff = booking_service._is_staff(request.user)
    person = getattr(request.user, 'profile', None)
    qs = models.Booking.objects.select_related('product', 'educator__user', 'student', 'meeting') \
        .exclude(status=models.Booking.STATUS_EXPIRED)
    view = request.GET.get('view', '')
    if is_staff and view == 'all':
        pass
    elif person is not None and qs.filter(educator=person).exists() and view != 'mine':
        qs = qs.filter(educator=person)
        view = 'teaching'
    else:
        qs = qs.filter(student=request.user)
        view = 'mine'
    now = tz.now()
    upcoming = qs.filter(end__gte=now).exclude(status=models.Booking.STATUS_CANCELLED).order_by('start')
    past = qs.exclude(pk__in=upcoming.values('pk')).order_by('-start')[:50]
    return render(request, 'shop/bookings.html', {
        'page_title': '1-on-1 sessions', 'upcoming': upcoming, 'past': past,
        'view': view, 'is_staff': is_staff,
        'is_educator': person is not None and models.Booking.objects.filter(educator=person).exists(),
        'credit': models.CreditEntry.balance_for(request.user),
    })


@login_required
@require_POST
def cancel_booking(request, pk):
    from . import booking as booking_service
    booking = get_object_or_404(models.Booking, pk=pk)
    try:
        booking_service.cancel(booking, by=request.user, reason=request.POST.get('reason', ''))
        messages.success(request, 'Session cancelled. The student has been notified'
                         + (' and credited.' if booking.price else '.'))
    except booking_service.BookingError as exc:
        messages.error(request, str(exc))
    return redirect(f"{reverse('shop:my-bookings')}?view={request.POST.get('view', '')}")


@login_required
@staff_required
def educators(request):
    """Every educator who runs 1-on-1s, their services, rates and weekly hours."""
    people = forms.educator_choices().prefetch_related('availability', 'session_rates__product')
    return render(request, 'shop/educators.html', {
        'page_title': 'Educators & availability', 'people': people,
        'WEEKDAYS': models.EducatorAvailability.WEEKDAYS,
    })


@login_required
@staff_required
def educator_hours(request, person_id):
    person = get_object_or_404(forms.educator_choices(), pk=person_id)
    hours, away = forms.availability_formsets(person, request.POST or None)
    if request.method == 'POST':
        if hours.is_valid() and away.is_valid():
            hours.save()
            away.save()
            messages.success(request, f'Hours saved for {person}.')
            return redirect('shop:educators')
        messages.error(request, t('messages.form_errors', 'Please correct the errors highlighted below.'))
    return render(request, 'shop/educator-hours.html', {
        'page_title': f'Hours · {person}', 'person': person, 'hours': hours, 'away': away,
        'upcoming': models.Booking.objects.filter(educator=person, status=models.Booking.STATUS_CONFIRMED)
                          .select_related('student', 'product').order_by('start')[:10],
    })


# ===========================================================================
# Fulfilment (staff): pack, book the courier, track
# ===========================================================================
@login_required
@staff_required
def fulfilment(request):
    from . import courier

    status = request.GET.get('status') or models.Shipment.STATUS_READY
    shipments = (models.Shipment.objects.select_related('order__buyer')
                 .prefetch_related('order__items__product', 'order__items__variant'))
    counts = {value: shipments.filter(status=value).count() for value, _ in models.Shipment.STATUS_CHOICES}
    return render(request, 'shop/fulfilment.html', {
        'page_title': 'Fulfilment', 'status': status,
        'shipments': shipments.filter(status=status).order_by('created_at' if status == 'ready' else '-updated_at')[:200],
        'STATUS_CHOICES': [c for c in models.Shipment.STATUS_CHOICES if c[0] != models.Shipment.STATUS_AWAITING],
        'counts': counts, 'courier_live': courier.is_live(),
    })


@login_required
@staff_required
@require_POST
def fulfilment_action(request, pk):
    from . import courier, fulfilment as service

    shipment = get_object_or_404(models.Shipment.objects.select_related('order__buyer'), pk=pk)
    action = request.POST.get('action')
    try:
        if action == 'book':
            service.book_courier(shipment, by=request.user)
            messages.success(request, f'Courier booked for {shipment.order.order_no} · {shipment.tracking_reference}.')
        elif action == 'manual':
            reference = (request.POST.get('tracking_reference') or '').strip()
            if not reference:
                messages.error(request, 'Enter the tracking / waybill number.')
            else:
                service.record_manual_dispatch(shipment, by=request.user, tracking_reference=reference,
                                               courier_name=request.POST.get('courier_name', ''))
                messages.success(request, f'{shipment.order.order_no} marked as shipped. The buyer has been told.')
        elif action == 'delivered':
            service.mark_delivered(shipment, by=request.user)
            messages.success(request, f'{shipment.order.order_no} marked as delivered.')
        elif action == 'collected':
            # Parcel handed over at the counter / to a runner: treat as delivered.
            service.mark_delivered(shipment, by=request.user)
            messages.success(request, f'{shipment.order.order_no} handed over.')
    except courier.CourierError as exc:
        messages.error(request, str(exc))
    return redirect(f"{reverse('shop:fulfilment')}?status={request.POST.get('back', shipment.status)}")


@login_required
@staff_required
def waybill(request, pk):
    from . import courier

    shipment = get_object_or_404(models.Shipment, pk=pk)
    try:
        kind, value = courier.label(shipment)
    except courier.CourierError as exc:
        messages.error(request, str(exc))
        return redirect('shop:fulfilment')
    if kind == 'url':
        return redirect(value)
    response = HttpResponse(value, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="waybill-{shipment.order.order_no}.pdf"'
    return response


@login_required
@staff_required
def packing_slip(request, pk):
    shipment = get_object_or_404(models.Shipment.objects.select_related('order__buyer'), pk=pk)
    return render(request, 'shop/packing-slip.html', {
        'shipment': shipment, 'order': shipment.order,
        'items': shipment.order.items.select_related('product', 'variant').filter(product__fulfilment=models.Product.FULFIL_SHIPPED),
    })


# ===========================================================================
# Catalogue management (staff)
# ===========================================================================
@login_required
@staff_required
def all_products(request):
    from django.db.models import Sum

    products = (models.Product.objects.select_related('category', 'institution')
                .prefetch_related('variants', 'files'))
    fulfilment = request.GET.get('type')
    if fulfilment in dict(models.Product.FULFILMENT_CHOICES):
        products = products.filter(fulfilment=fulfilment)
    status = request.GET.get('status')
    if status in dict(models.STATUS_CHOICES):
        products = products.filter(status=status)
    search = request.GET.get('q')
    if search:
        products = products.filter(Q(name__icontains=search) | Q(sku__icontains=search))
    sold = dict(models.OrderItem.objects.filter(order__status=models.Order.STATUS_PAID)
                .values_list('product_id').annotate(n=Sum('line_total')).values_list('product_id', 'n'))
    rows = [{'product': p, 'revenue': sold.get(p.pk) or 0} for p in products.order_by('-created_at')]
    return render(request, 'shop/all-products.html', {
        'page_title': 'Products & services', 'rows': rows,
        'FULFILMENT_CHOICES': models.Product.FULFILMENT_CHOICES,
        'sel': {'type': fulfilment or '', 'status': status or '', 'q': search or ''},
        'counts': {
            'all': models.Product.objects.count(),
            'active': models.Product.objects.filter(status='active').count(),
            'on_sale': models.Product.objects.filter(discount_percent__gt=0, status='active').count(),
            'low_stock': sum(1 for p in models.Product.objects.filter(track_stock=True)
                                                        .prefetch_related('variants')
                             if not p.in_stock),
        },
    })


def _product_editor(request, product):
    """Add or edit a product: the model fields, its files, gallery and sizes."""
    creating = product is None
    instance = product or models.Product(fulfilment=request.GET.get('type') or models.Product.FULFIL_DIGITAL)
    if request.method == 'POST':
        form = forms.ProductForm(request.POST, request.FILES, instance=instance)
        variants = forms.ProductVariantFormSet(request.POST, instance=instance, prefix='variants')
        rates = forms.EducatorRateFormSet(request.POST, instance=instance, prefix='rates')
        if form.is_valid() and variants.is_valid() and rates.is_valid():
            from django.db import transaction
            with transaction.atomic():
                obj = form.save(commit=False)
                if creating:
                    obj.created_by = request.user
                obj.save()
                form.save_m2m()
                variants.instance = obj
                variants.save()
                rates.instance = obj
                rates.save()
                next_order = obj.files.count()
                for index, upload in enumerate(form.cleaned_data.get('new_files') or []):
                    models.ProductFile.objects.create(
                        product=obj, file=upload, original_name=upload.name[:255],
                        size=upload.size or 0, order=next_order + index)
                next_order = obj.gallery.count()
                for index, upload in enumerate(form.cleaned_data.get('new_images') or []):
                    models.ProductImage.objects.create(product=obj, image=upload,
                                                       alt=obj.name[:200], order=next_order + index)
                remove_files = request.POST.getlist('remove_file')
                if remove_files:
                    obj.files.filter(pk__in=remove_files).delete()
                remove_images = request.POST.getlist('remove_image')
                if remove_images:
                    obj.gallery.filter(pk__in=remove_images).delete()
                if request.POST.get('remove_legacy_file') and obj.digital_file:
                    obj.digital_file = None
                    obj.save(update_fields=['digital_file'])
            messages.success(request, f'“{obj.name}” {"added to" if creating else "saved in"} the shop.')
            if request.POST.get('then') == 'another':
                return redirect(f"{reverse('shop:add-product')}?type={obj.fulfilment}")
            return redirect('shop:all-products')
        messages.error(request, t('messages.form_errors', 'Please correct the errors highlighted below.'))
    else:
        form = forms.ProductForm(instance=instance)
        variants = forms.ProductVariantFormSet(instance=instance, prefix='variants')
        rates = forms.EducatorRateFormSet(instance=instance, prefix='rates')

    return render(request, 'shop/product-form.html', {
        'page_title': 'Add to the shop' if creating else f'Edit · {instance.name}',
        'form': form, 'variants': variants, 'rates': rates, 'object': product,
        'existing_files': list(instance.files.all()) if instance.pk else [],
        'existing_images': list(instance.gallery.all()) if instance.pk else [],
        'fulfilment_help': {
            models.Product.FULFIL_DIGITAL: ('bi-file-earmark-arrow-down', 'PDFs, spreadsheets or a ZIP — unlocked the moment it is paid.'),
            models.Product.FULFIL_BOOKING: ('bi-person-video3', 'A 1-on-1 on Teams, priced per hour per educator.'),
            models.Product.FULFIL_SHIPPED: ('bi-box-seam', 'Hoodies, printed packs, merch — delivered by courier.'),
            models.Product.FULFIL_NONE: ('bi-receipt', 'A fee or anything else that needs no delivery.'),
        },
        'vat_registered': getattr(settings, 'VAT_REGISTERED', False),
        'vat_rate': getattr(settings, 'VAT_RATE', 15),
    })


@login_required
@staff_required
def add_product(request):
    return _product_editor(request, None)


@login_required
@staff_required
def edit_product(request, pk):
    return _product_editor(request, get_object_or_404(models.Product, pk=pk))


@login_required
@staff_required
@require_POST
def delete_product(request, pk):
    product = get_object_or_404(models.Product, pk=pk)
    if product.order_items.exists():
        # Sold items are part of invoices and orders; deleting would break
        # them, so a sold product is withdrawn instead.
        product.status = 'inactive'
        product.save(update_fields=['status', 'updated_at'])
        messages.info(request, f'“{product.name}” has sales, so it was hidden from the shop instead of deleted.')
        return redirect('shop:all-products')
    return _delete(request, models.Product, pk, 'shop:all-products', 'Product')


@login_required
@staff_required
def categories(request):
    if request.method == 'POST':
        form = forms.ProductCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, t('messages.saved', '{name} saved successfully.', name='Category'))
            return redirect('shop:categories')
        messages.error(request, t('messages.form_errors', 'Please correct the errors highlighted below.'))
    else:
        form = forms.ProductCategoryForm()
    return render(request, 'shop/categories.html', {
        'page_title': 'Product Categories',
        'categories': models.ProductCategory.objects.all(), 'form': form,
    })


@login_required
@staff_required
@require_POST
def delete_category(request, pk):
    return _delete(request, models.ProductCategory, pk, 'shop:categories', 'Category')


# ===========================================================================
# Discounts & promotions (admin / staff only)
# ===========================================================================
@login_required
@staff_required
def discounts(request):
    """List every discount. Loading the catalogue is a staff job, and so is
    deciding what it sells for."""
    return render(request, 'shop/discounts.html', {
        'page_title': 'Discounts & promotions',
        'discounts': models.Discount.objects.select_related(
            'institution', 'programme', 'category').prefetch_related('products'),
    })


@login_required
@staff_required
def add_discount(request):
    return _save_form(request, forms.DiscountForm, None, 'shop/discount-form.html',
                      list_url='shop:discounts', page_title='New discount')


@login_required
@staff_required
def edit_discount(request, pk):
    return _save_form(request, forms.DiscountForm,
                      get_object_or_404(models.Discount, pk=pk), 'shop/discount-form.html',
                      list_url='shop:discounts', page_title='Edit discount')


@login_required
@staff_required
@require_POST
def delete_discount(request, pk):
    return _delete(request, models.Discount, pk, 'shop:discounts', 'Discount')
