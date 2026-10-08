"""Views for the finance app.

Staff issue invoices (optionally generated from a shop order), add line items
and record payments. Regular users see their own invoices and outstanding
(due) payments.
"""

import uuid
from decimal import Decimal, InvalidOperation

from django.apps import apps
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.http import FileResponse, Http404, HttpResponse
from core.errors import note
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from core.branding import t
from core.roles import role_flags

from . import emails, forms, models, payfast, services

staff_required = user_passes_test(lambda u: u.is_active and u.is_staff)


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
            return redirect(obj.get_absolute_url() if hasattr(obj, 'get_absolute_url') else list_url)
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
# Lists
# ===========================================================================
@login_required
def invoices(request):
    """Wave's invoice list: what's owed on top, then Unpaid / Draft / Paid / All."""
    from datetime import timedelta

    from django.db.models import Sum
    from django.utils import timezone

    is_staff = role_flags(request)['is_admin_staff']
    base = models.Invoice.objects.select_related('customer').prefetch_related('payments')
    if not is_staff:
        base = base.filter(customer=request.user).exclude(status=models.Invoice.STATUS_DRAFT)
    today = timezone.localdate()
    open_qs = base.exclude(status__in=[models.Invoice.STATUS_PAID, models.Invoice.STATUS_CANCELLED,
                                       models.Invoice.STATUS_DRAFT])
    open_list = [inv for inv in open_qs if inv.balance > 0]
    overdue = [inv for inv in open_list if inv.due_date and inv.due_date < today]
    due_soon = [inv for inv in open_list if inv.due_date and today <= inv.due_date <= today + timedelta(days=30)]
    payments = models.InvoicePayment.objects.filter(status=models.InvoicePayment.STATUS_COMPLETED,
                                                    paid_at__date__gte=today.replace(day=1))
    if not is_staff:
        payments = payments.filter(invoice__customer=request.user)

    avg_days = None
    if is_staff:
        paid = (models.InvoicePayment.objects.filter(status=models.InvoicePayment.STATUS_COMPLETED,
                                                     paid_at__date__gte=today - timedelta(days=90))
                .select_related('invoice'))
        spans = [(p.paid_at.date() - p.invoice.issue_date).days for p in paid if p.invoice.issue_date]
        avg_days = round(sum(spans) / len(spans)) if spans else None

    tab = request.GET.get('tab') or ('unpaid' if open_list or not is_staff else 'all')
    if tab == 'unpaid':
        qs = open_qs
    elif tab == 'draft' and is_staff:
        qs = base.filter(status=models.Invoice.STATUS_DRAFT)
    elif tab == 'paid':
        qs = base.filter(status=models.Invoice.STATUS_PAID)
    else:
        tab, qs = 'all', base
    search = request.GET.get('q')
    if search and is_staff:
        qs = qs.filter(Q(number__icontains=search) | Q(customer__first_name__icontains=search)
                       | Q(customer__last_name__icontains=search) | Q(customer__email__icontains=search))
    rows = list(qs.order_by('-issue_date', '-id')[:300])
    if tab == 'unpaid':
        rows = [inv for inv in rows if inv.balance > 0]
    return render(request, 'finance/invoices.html', {
        'page_title': 'Invoices', 'invoices': rows, 'tab': tab, 'search': search or '',
        'is_staff': is_staff,
        'kpis': {'overdue': sum((i.balance for i in overdue), Decimal('0')), 'overdue_count': len(overdue),
                 'due_soon': sum((i.balance for i in due_soon), Decimal('0')),
                 'collected_month': payments.aggregate(t=Sum('amount'))['t'] or 0, 'avg_days': avg_days},
        'counts': {'unpaid': len(open_list), 'draft': base.filter(status=models.Invoice.STATUS_DRAFT).count(),
                   'paid': base.filter(status=models.Invoice.STATUS_PAID).count(), 'all': base.count()},
    })


@login_required
def due_payments(request):
    qs = (models.Invoice.objects.select_related('customer')
          .prefetch_related('payments')
          .exclude(status__in=[models.Invoice.STATUS_PAID, models.Invoice.STATUS_CANCELLED]))
    if not request.user.is_staff:
        qs = qs.filter(customer=request.user)
    # Only those with an outstanding balance.
    due = [inv for inv in qs if inv.balance > 0]
    return render(request, 'finance/due-payments.html', {
        'page_title': 'Due Payments', 'invoices': due,
    })


# ===========================================================================
# Detail / receipt
# ===========================================================================
@login_required
def invoice_detail(request, pk):
    invoice = get_object_or_404(
        models.Invoice.objects.select_related('customer').prefetch_related('items', 'payments'),
        pk=pk,
    )
    if not (request.user.is_staff or invoice.customer_id == request.user.id):
        messages.error(request, t('messages.form_errors', 'You cannot view that invoice.'))
        return redirect('finance:invoices')
    if not request.user.is_staff and invoice.status == models.Invoice.STATUS_DRAFT:
        raise Http404

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'pay' and request.user.is_staff:
            amount = _to_decimal(request.POST.get('amount'), invoice.balance)
            if amount <= 0:
                amount = invoice.balance
            services.settle_payment(
                invoice, amount, gateway=models.InvoicePayment.GATEWAY_MANUAL,
                method=request.POST.get('method', 'online'),
                reference=request.POST.get('reference', ''),
            )
            messages.success(request, t('messages.saved', '{name} saved successfully.', name='Payment'))
            return redirect('finance:invoice-detail', pk=invoice.pk)
        if action == 'add_item' and request.user.is_staff:
            form = forms.InvoiceItemForm(request.POST)
            if form.is_valid():
                item = form.save(commit=False)
                item.invoice = invoice
                item.save()
                messages.success(request, t('messages.saved', '{name} saved successfully.', name='Item'))
            else:
                messages.error(request, t('messages.form_errors', 'Please correct the errors highlighted below.'))
            return redirect('finance:invoice-detail', pk=invoice.pk)

    return render(request, 'finance/invoice-detail.html', {
        'page_title': invoice.number, 'invoice': invoice, 'doc': invoice, 'kind': 'invoice',
        'items': list(invoice.items.all()),
        'payments': list(invoice.payments.all()),
        'payment_methods': models.InvoicePayment.METHOD_CHOICES,
        'vat_number': getattr(settings, 'VAT_NUMBER', ''),
        'is_staff': role_flags(request)['is_admin_staff'],
        'order': invoice.order,
        'estimate': getattr(invoice, 'from_estimate', None) if hasattr(invoice, 'from_estimate') else None,
    })


# ===========================================================================
# Staff CRUD
# ===========================================================================
@login_required
@staff_required
def add_invoice(request):
    return _save_form(request, forms.InvoiceForm, None, 'finance/invoice-form.html',
                      list_url='finance:invoices', page_title='Add Invoice')


@login_required
@staff_required
def edit_invoice(request, pk):
    invoice = get_object_or_404(models.Invoice, pk=pk)
    return _save_form(request, forms.InvoiceForm, invoice, 'finance/invoice-form.html',
                      list_url='finance:invoices', page_title='Edit Invoice')


@login_required
@staff_required
@require_POST
def delete_invoice(request, pk):
    return _delete(request, models.Invoice, pk, 'finance:invoices', 'Invoice')


@login_required
@staff_required
def generate_from_order(request, order_id):
    """Build a draft invoice from a shop order (line items copied across)."""
    try:
        Order = apps.get_model('shop', 'Order')
        order = get_object_or_404(Order, pk=order_id)
    except Exception:
        messages.error(request, t('messages.form_errors', 'That order could not be found.'))
        return redirect('finance:invoices')

    # Same copy as checkout, so any discount frozen on the order carries over.
    invoice = services.create_invoice_from_order(order, created_by=request.user,
                                                 status=models.Invoice.STATUS_DRAFT)
    messages.success(request, t('messages.created', '{name} created.', name='Invoice'))
    return redirect('finance:invoice-detail', pk=invoice.pk)


# ===========================================================================
# Cart checkout → invoice → PayFast
# ===========================================================================
@login_required
def checkout(request):
    """Review the priced cart, choose delivery, and place the order.

    The numbers come from the same quote the cart shows (shop.pricing), and
    placing the order freezes that quote — delivery included — onto the order
    and invoice (shop.checkout.place_order), so the amount sent to PayFast is
    the amount the buyer was shown.
    """
    from apps.shop import checkout as shop_checkout
    from apps.shop import courier
    from apps.shop import delivery as shop_delivery
    from apps.shop.forms import AddressForm
    from apps.shop.models import Address, CreditEntry
    from apps.shop.views import cart_context

    Order = apps.get_model('shop', 'Order')
    cart = Order.get_cart(request.user)
    if not cart.items.exists():
        messages.info(request, 'Your cart is empty.')
        return redirect('shop:storefront')

    context = cart_context(request, cart)
    quote = context['quote']
    goods_total = quote['subtotal'] - quote['discount']
    needs_delivery = context['has_shipped']
    address_form = AddressForm(initial={
        'recipient': request.user.get_full_name(),
        'phone': shop_delivery._buyer_phone(request.user)}, prefix='addr')
    lockers, locker_search = [], ''

    if request.method == 'POST' and request.POST.get('action') == 'delivery' and needs_delivery:
        method = request.POST.get('method')
        try:
            if method == Order.DELIVERY_DOOR:
                address = None
                if request.POST.get('address') and request.POST['address'] != 'new':
                    address = Address.objects.filter(pk=request.POST['address'], user=request.user).first()
                if address is None:
                    address_form = AddressForm(request.POST, prefix='addr')
                    if address_form.is_valid():
                        address = address_form.save(commit=False)
                        address.user = request.user
                        address.is_default = not Address.objects.filter(user=request.user).exists()
                        address.save()
                if address is not None:
                    shop_delivery.choose(request, cart, method=method, goods_total=goods_total, address=address)
                    return redirect('finance:checkout')
                messages.error(request, 'Please check the delivery address.')
            elif method == Order.DELIVERY_LOCKER:
                locker_id = (request.POST.get('locker_id') or '').strip()
                locker_name = (request.POST.get('locker_name') or '').strip()
                if courier.is_live() and locker_id:
                    locker_name = request.POST.get(f'locker_label_{locker_id}', locker_name)
                if not courier.is_live():
                    locker_id = locker_id or locker_name
                if not (locker_id or locker_name):
                    messages.error(request, 'Choose a Pudo locker.')
                else:
                    shop_delivery.choose(request, cart, method=method, goods_total=goods_total,
                                         locker_id=locker_id, locker_name=locker_name)
                    return redirect('finance:checkout')
        except courier.CourierError as exc:
            messages.error(request, str(exc))

    if request.GET.get('locker_search') and courier.is_live():
        locker_search = request.GET['locker_search'][:80]
        try:
            lockers = courier.lockers(locker_search)
        except courier.CourierError as exc:
            messages.error(request, str(exc))

    choice = shop_delivery.current(request, cart, goods_total) if needs_delivery else None
    if choice:
        from apps.shop import pricing
        quote = pricing.price_cart(cart, shop_checkout.coupon_code(request), shipping=choice['amount'])
        context.update({'quote': quote, 'lines': quote['lines']})

    if request.method == 'POST' and request.POST.get('action', 'place') == 'place':
        try:
            invoice = shop_checkout.place_order(
                cart, user=request.user, coupon=shop_checkout.coupon_code(request),
                use_credit=bool(request.POST.get('use_credit')), delivery=choice)
        except shop_checkout.CheckoutError as exc:
            for problem in exc.problems:
                messages.error(request, problem)
            return redirect('finance:checkout' if needs_delivery else 'shop:cart')
        request.session.pop(shop_checkout.COUPON_SESSION_KEY, None)
        shop_delivery.clear(request)
        if invoice.status == models.Invoice.STATUS_PAID:
            messages.success(request, 'Order placed and paid. Your items are ready.')
            return redirect('shop:order-detail', pk=cart.pk)
        emails.send_purchase_email(invoice)   # order confirmation (+ pay-link)
        return redirect('finance:pay', public_id=invoice.public_id)

    context.update({
        'page_title': 'Checkout',
        'payments_enabled': getattr(settings, 'PAYMENTS_ENABLED', True),
        'credit': CreditEntry.balance_for(request.user),
        'needs_delivery': needs_delivery, 'choice': choice,
        'addresses': Address.objects.filter(user=request.user),
        'address_form': address_form,
        'courier_live': courier.is_live(),
        'lockers': lockers, 'locker_search': locker_search,
        'flat_door': courier.flat_options(goods_total, ('door',))[0],
        'flat_locker': courier.flat_options(goods_total, ('locker',))[0],
        'free_over': courier.free_threshold(), 'goods_total': goods_total,
        'editing_delivery': bool(request.GET.get('change')) or (needs_delivery and not choice),
    })
    return render(request, 'finance/checkout.html', context)


def pay(request, public_id):
    """Public, tokenised pay page — builds the PayFast redirect form. Works
    without logging in (the link is e-mailed to the customer)."""
    invoice = get_object_or_404(models.Invoice, public_id=public_id)
    if not (request.user.is_authenticated and request.user.is_staff):
        from .documents import mark_viewed
        mark_viewed(invoice)
    if invoice.balance <= 0:
        return render(request, 'finance/pay-done.html', {
            'page_title': 'Already paid', 'invoice': invoice, 'already': True,
        })

    # This deployment does not take online payments (settings.PAYMENTS_ENABLED).
    # Say so on the page: the invoice is still real and still owed, it simply
    # cannot be settled here. Falling through would build a PayFast form from a
    # gateway that was never configured, which fails at PayFast — after the
    # customer has committed to paying.
    if not getattr(settings, 'PAYMENTS_ENABLED', True):
        return render(request, 'finance/pay.html', {
            'page_title': f'Pay {invoice.number}',
            'invoice': invoice,
            'payments_disabled': True,
        })

    # Zero-config sandbox: no PayFast credentials → simulate locally so the
    # checkout flow is testable end to end (payfast_return settles the invoice).
    if payfast.simulate_in_sandbox():
        return render(request, 'finance/pay.html', {
            'page_title': f'Pay {invoice.number}',
            'invoice': invoice,
            'simulate': True,
            'return_url': reverse('finance:payfast-return') + f'?inv={invoice.public_id}',
            'sandbox': True,
        })

    checkout_data = payfast.build_checkout(invoice)
    return render(request, 'finance/pay.html', {
        'page_title': f'Pay {invoice.number}',
        'invoice': invoice,
        'simulate': False,
        'process_url': checkout_data['process_url'],
        'fields': checkout_data['fields'],
        'sandbox': payfast.is_sandbox(),
    })


# PayFast reports amounts to two decimals; allow a cent of rounding either way
# when comparing what was paid against what is owed.
_AMOUNT_TOLERANCE = Decimal('0.01')


@csrf_exempt
@require_POST
def payfast_notify(request):
    """PayFast ITN webhook (server-to-server). Validates and settles payment."""
    if not payfast.verify_itn(request.POST):
        return HttpResponse('INVALID', status=400)
    # ``public_id`` is a UUIDField — filtering it with a malformed value raises
    # rather than matching nothing, and this endpoint is unauthenticated.
    try:
        public_id = uuid.UUID((request.POST.get('m_payment_id') or '').strip())
    except (ValueError, TypeError):
        note('FIN-5001', request, reason='m_payment_id is not a UUID')
        return HttpResponse('OK')  # ack so PayFast stops retrying
    invoice = models.Invoice.objects.filter(public_id=public_id).first()
    if invoice is None:
        return HttpResponse('OK')  # ack so PayFast stops retrying
    # Verifying the notification is genuine is not the same as verifying it
    # covers the bill: PayFast confirms that *a* payment happened, not that it
    # was for this invoice's balance. Settle what was actually paid, and never
    # let a short payment close a larger invoice.
    amount = _to_decimal(request.POST.get('amount_gross'), Decimal('0'))
    if amount <= 0:
        note('FIN-5001', request, reason='amount_gross missing or unusable',
             invoice=invoice.number)
        return HttpResponse('OK')
    if amount + _AMOUNT_TOLERANCE < invoice.balance:
        # Under-payment. Record it — the money is real — but it leaves the
        # invoice partial rather than paid, which is what the balance says, and
        # somebody has to chase the difference.
        note('FIN-6003', request, invoice=invoice.number,
             paid=str(amount), balance=str(invoice.balance))
    services.settle_payment(
        invoice, min(amount, invoice.balance),
        gateway=models.InvoicePayment.GATEWAY_PAYFAST, method='payfast',
        gateway_ref=request.POST.get('pf_payment_id', ''), raw=request.POST.dict(),
        reference=request.POST.get('pf_payment_id', ''),
    )
    return HttpResponse('OK')


def _invoice_from_query(request):
    """The invoice named by ``?inv=<uuid>``, or ``None``.

    ``public_id`` is a UUIDField, so filtering it with a missing or malformed
    value raises rather than matching nothing — which turned a bookmarked return
    URL into a 500 instead of a "payment not found" page.
    """
    raw = (request.GET.get('inv') or '').strip()
    if not raw:
        return None
    try:
        return models.Invoice.objects.filter(public_id=uuid.UUID(raw)).first()
    except (ValueError, TypeError):
        return None


def payfast_return(request):
    """Buyer is redirected here after paying. In sandbox we settle the invoice
    here too (the ITN can't reach localhost); in production the ITN is
    authoritative and this just shows the status."""
    invoice = _invoice_from_query(request)
    # ``simulate_in_sandbox()``, not ``is_sandbox()``: settling on a bare GET is
    # only safe in the zero-credential development case, which that helper also
    # gates on DEBUG. Keying it on the sandbox flag alone meant a production
    # build that still had PAYFAST_SANDBOX=true handed out free enrolments to
    # anyone who opened their own return URL.
    if invoice and payfast.simulate_in_sandbox() and invoice.balance > 0:
        services.settle_payment(
            invoice, invoice.balance, gateway=models.InvoicePayment.GATEWAY_PAYFAST,
            method='payfast', gateway_ref=f'SANDBOX-{invoice.public_id}',
            reference='sandbox', raw={'sandbox': True},
        )
        invoice.refresh_from_db()
    # After a completed payment, signed-in users get the "payment completed"
    # hand-off screen, which holds the outcome for a few seconds and then
    # forwards to the dashboard — rather than the dashboard appearing at once
    # with the confirmation reduced to a toast.
    # (Anonymous pay-link payers — an e-mailed invoice link — still get the
    # confirmation page, since they have no dashboard to land on.)
    if request.user.is_authenticated:
        return redirect(reverse('accounts:register-complete') + '?mode=paid')
    return render(request, 'finance/pay-done.html', {
        'page_title': 'Payment complete', 'invoice': invoice, 'already': False,
    })


def payfast_cancel(request):
    invoice = _invoice_from_query(request)
    return render(request, 'finance/pay-cancel.html', {
        'page_title': 'Payment cancelled', 'invoice': invoice,
    })


# ===========================================================================
# Payment history
# ===========================================================================
@login_required
def payment_history(request):
    flags = role_flags(request)
    payments = models.InvoicePayment.objects.select_related('invoice', 'invoice__customer')
    upcoming = (models.Invoice.objects.select_related('customer')
                .exclude(status__in=[models.Invoice.STATUS_PAID, models.Invoice.STATUS_CANCELLED]))
    if not flags['is_admin_staff']:
        payments = payments.filter(invoice__customer=request.user)
        upcoming = upcoming.filter(customer=request.user)

    status = request.GET.get('status')
    if status in dict(models.InvoicePayment.STATUS_CHOICES):
        payments = payments.filter(status=status)
    gateway = request.GET.get('gateway')
    if gateway in dict(models.InvoicePayment.GATEWAY_CHOICES):
        payments = payments.filter(gateway=gateway)

    due = [inv for inv in upcoming if inv.balance > 0]
    return render(request, 'finance/payment-history.html', {
        'page_title': 'Payment History',
        'payments': payments[:300],
        'upcoming': due,
        'status': status or '', 'gateway': gateway or '',
        'STATUS_CHOICES': models.InvoicePayment.STATUS_CHOICES,
        'GATEWAY_CHOICES': models.InvoicePayment.GATEWAY_CHOICES,
    })


def _pdf_response(pdf, filename):
    if not pdf:
        raise Http404('The PDF could not be generated.')
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@login_required
def invoice_pdf(request, pk):
    """Download the invoice as the same PDF that is e-mailed."""
    from . import pdf
    invoice = get_object_or_404(models.Invoice.objects.prefetch_related('items'), pk=pk)
    if not (_staff_only(request) or invoice.customer_id == request.user.id):
        note('FIN-2001', request, kind='invoice-pdf')
        raise Http404
    return _pdf_response(pdf.render_invoice_pdf(invoice), f'Invoice-{invoice.number}.pdf')


@login_required
def receipt_pdf(request, pk):
    """Download the receipt PDF for a (part-)paid invoice."""
    from . import pdf
    invoice = get_object_or_404(models.Invoice.objects.prefetch_related('items', 'payments'), pk=pk)
    if not (_staff_only(request) or invoice.customer_id == request.user.id):
        note('FIN-2001', request, kind='receipt-pdf')
        raise Http404
    if not invoice.amount_paid and invoice.status != models.Invoice.STATUS_PAID:
        raise Http404
    return _pdf_response(pdf.render_receipt_pdf(invoice), f'Receipt-{invoice.number}.pdf')


@login_required
def receipt(request, pk):
    invoice = get_object_or_404(models.Invoice.objects.prefetch_related('items', 'payments'), pk=pk)
    if not (request.user.is_staff or invoice.customer_id == request.user.id):
        note('FIN-2001', request, kind='receipt')
        messages.error(request, 'You cannot view that receipt.')
        return redirect('finance:invoices')
    return render(request, 'finance/receipt.html', {'page_title': f'Receipt · {invoice.number}', 'invoice': invoice})


# ===========================================================================
# Staff: create & send invoices (to a user or a whole course)
# ===========================================================================
@login_required
@staff_required
@require_POST
def send_invoice(request, pk):
    """E-mail the customer the pay-link and mark the invoice as sent."""
    invoice = get_object_or_404(models.Invoice, pk=pk)
    if invoice.status == models.Invoice.STATUS_DRAFT:
        invoice.status = models.Invoice.STATUS_SENT
        invoice.save(update_fields=['status', 'updated_at'])
    sent = emails.send_invoice_email(invoice)
    if sent:
        messages.success(request, f'Pay-link e-mailed to {invoice.customer.email}.')
    else:
        messages.warning(request, 'Could not e-mail the invoice (no address or mail error).')
    return redirect('finance:invoice-detail', pk=invoice.pk)


@login_required
@staff_required
def create_invoice(request):
    """Create an invoice from scratch and assign it to individual users, or
    bulk-create one per person enrolled in a module.

    Everything except the recipient list goes through
    :class:`~apps.finance.forms.InvoiceCreateForm` so that ``due_date`` is a
    real ``date`` before it reaches the model — assigning the raw POST string
    made the first line item a 500.
    """
    User = get_user_model()

    if request.method == 'POST':
        form = forms.InvoiceCreateForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            recipients = _resolve_recipients(request, data['audience'],
                                             data.get('programme_module'))
            if not recipients:
                messages.error(request,
                               'No recipients resolved — pick a user, or a subject with enrolments.')
            else:
                product = data.get('product')
                created = 0
                for user in recipients:
                    invoice = models.Invoice.objects.create(
                        customer=user, created_by=request.user,
                        status=models.Invoice.STATUS_SENT,
                        due_date=data.get('due_date'), notes=data.get('notes', ''),
                    )
                    if product:
                        models.InvoiceItem.objects.create(invoice=invoice, product=product)
                        invoice.recalc_total()
                    if data.get('email_now'):
                        emails.send_invoice_email(invoice)
                    created += 1
                messages.success(
                    request, f'Created {created} invoice(s)'
                             + (' and e-mailed pay-links.' if data.get('email_now') else '.'))
                return redirect('finance:invoices')
        else:
            messages.error(request, 'Please correct the highlighted fields.')
    else:
        form = forms.InvoiceCreateForm()

    return render(request, 'finance/invoice-create.html', {
        'page_title': 'Create Invoice',
        'form': form,
        'users': User.objects.filter(is_active=True).order_by('username'),
    })


def _resolve_recipients(request, audience, programme_module=None):
    """The User objects an invoice run should create invoices for.

    ``module`` replaces the old ``course`` audience: ``Course`` was retired in
    favour of the Institution → Programme → ProgrammeModule spine, and this
    branch was left referencing a name that no longer existed — so choosing it
    raised ``NameError`` rather than invoicing anybody.
    """
    User = get_user_model()
    if audience == forms.InvoiceCreateForm.AUDIENCE_USER:
        ids = request.POST.getlist('users')
        return list(User.objects.filter(pk__in=ids, is_active=True))
    if audience == forms.InvoiceCreateForm.AUDIENCE_MODULE and programme_module is not None:
        user_ids = (programme_module.enrolments
                    .exclude(person__user__isnull=True)
                    .values_list('person__user_id', flat=True))
        return list(User.objects.filter(pk__in=set(user_ids), is_active=True))
    return []


# ===========================================================================
# Proof of payment + manual access granting  (admin / staff only)
# ===========================================================================
def _staff_only(request):
    """True when this user may record payments and grant access."""
    return role_flags(request)['is_admin_staff']


@login_required
def grant_access(request):
    """Record a payment and open a student's modules — the manual route.

    This is the only way access is granted by hand, and it will not grant
    anything without recording the payment that justified it: the two are one
    form, one submit, one audit trail. Staff may attach the student's deposit
    slip (image or PDF); it is filed against them and appears in their payment
    history alongside anything PayFast settled.
    """
    if not _staff_only(request):
        note('FIN-2001', request, kind='grant-access')
        messages.error(request, 'Only administrators and staff can record payments '
                                'and grant access.')
        return redirect('finance:invoices')

    from apps.learning.models import ModuleEnrolment

    from . import access as access_service

    form = forms.GrantAccessForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        data = form.cleaned_data
        person = data['student']
        proof, payment, modules = access_service.grant_access(
            person,
            amount=data['amount'], months=data['months'], granted_by=request.user,
            document=data.get('document'), method=data['method'],
            reference=data.get('reference') or '', paid_on=data.get('paid_on'),
            note=data.get('note') or '')
        messages.success(
            request,
            f'Recorded R{proof.amount} for {person} and opened {len(modules)} module'
            f'{"s" if len(modules) != 1 else ""} for {proof.granted_months} month'
            f'{"s" if proof.granted_months != 1 else ""}.'
            + (' The proof of payment is on their record.' if proof.document else ''))
        return redirect('finance:student-payments', person_id=person.pk)
    if request.method == 'POST':
        messages.error(request, 'Please correct the errors highlighted below.')

    # A locked student is the reason someone opens this page, so show them first.
    locked = (ModuleEnrolment.objects
              .exclude(status=ModuleEnrolment.STATUS_ACTIVE)
              .select_related('person__user', 'programme_module__programme__institution')
              .order_by('person_id'))
    return render(request, 'finance/grant-access.html', {
        'page_title': 'Record payment & grant access', 'form': form,
        'locked': [e for e in locked if not e.is_unlocked][:100],
    })


@login_required
def student_payments(request, person_id):
    """One student's payment history and access state.

    Staff see anybody's; a student may only open their own, which is also where
    they land from their profile.
    """
    from apps.accounts.models import Person

    from . import access as access_service

    person = get_object_or_404(Person.objects.select_related('user'), pk=person_id)
    if not (_staff_only(request) or person.user_id == request.user.id):
        note('FIN-2001', request, kind='student-payments')
        messages.error(request, 'That is not your payment history.')
        return redirect('finance:invoices')

    return render(request, 'finance/student-payments.html', {
        'page_title': f'Payments · {person}',
        'person': person,
        'proofs': access_service.payment_history(person),
        'state': access_service.access_state(person),
        'invoices': models.Invoice.objects.filter(customer=person.user).order_by('-created_at')[:20],
        'can_manage': _staff_only(request),
    })


@login_required
def proof_document(request, pk):
    """Serve a stored proof of payment. Staff, or the student it belongs to."""
    proof = get_object_or_404(models.ProofOfPayment.objects.select_related('person__user'), pk=pk)
    if not (_staff_only(request) or proof.person.user_id == request.user.id):
        note('FIN-2001', request, kind='proof-document')
        raise Http404
    if not proof.document:
        raise Http404
    return FileResponse(proof.document.open('rb'),
                        filename=proof.original_name or proof.document.name.rsplit('/', 1)[-1])


# ===========================================================================
# Invoice register + money overview (admin / staff)
# ===========================================================================
def _register_queryset(request):
    """Every invoice, narrowed by the register's filters.

    Institution / programme filters reach the invoice through the *buyer's*
    enrolment rather than through the line items, because that is the question
    being asked — "what do the Grade 10 parents owe us?", not "which lines mention Grade 10".
    Module filters do go through the lines, since a module is a property of what
    was bought.
    """
    qs = (models.Invoice.objects
          .select_related('customer', 'order')
          .prefetch_related('items__product', 'payments'))

    status = request.GET.get('status')
    institution = request.GET.get('institution')
    programme = request.GET.get('programme')
    module = request.GET.get('module')
    search = request.GET.get('q')

    if status in dict(models.Invoice.STATUS_CHOICES):
        qs = qs.filter(status=status)
    if institution:
        qs = qs.filter(customer__profile__programme_enrolments__programme__institution_id=institution)
    if programme:
        qs = qs.filter(customer__profile__programme_enrolments__programme_id=programme)
    if module:
        qs = qs.filter(items__product__module_id=module)
    if search:
        qs = qs.filter(Q(number__icontains=search)
                       | Q(customer__first_name__icontains=search)
                       | Q(customer__last_name__icontains=search)
                       | Q(customer__email__icontains=search))
    return qs.distinct()


@login_required
@staff_required
def invoice_register(request):
    """Who bought what, for how much, and whether they have paid."""
    from apps.learning.models import Institution, Programme, ProgrammeModule

    invoices = _register_queryset(request).order_by('-issue_date', '-id')
    rows, billed, collected = [], Decimal('0'), Decimal('0')
    for invoice in invoices[:500]:
        paid = Decimal(str(invoice.amount_paid or 0))
        billed += Decimal(str(invoice.total or 0))
        collected += paid
        rows.append({'invoice': invoice, 'paid': paid,
                     'items': list(invoice.items.all())})

    return render(request, 'finance/invoice-register.html', {
        'page_title': 'Invoice register', 'rows': rows,
        'billed': billed, 'collected': collected, 'outstanding': billed - collected,
        'institutions': Institution.objects.filter(is_active=True).order_by('order'),
        'programmes': Programme.objects.filter(is_active=True).select_related('institution'),
        'modules': ProgrammeModule.objects.order_by('code'),
        'STATUS_CHOICES': models.Invoice.STATUS_CHOICES,
        'sel': {k: request.GET.get(k, '') for k in
                ('status', 'institution', 'programme', 'module', 'q')},
    })


@login_required
def money_overview(request):
    """Fees and shop income, at whatever scope the viewer is entitled to.

    Staff see the whole book — billed, collected, outstanding, what sold most,
    and what month-end looks like if everything already invoiced is settled.
    A student sees only their own spend and what is still owed; a parent sees
    their child's. The audience is resolved once, at the top, so the numbers
    below cannot leak across it.
    """
    from django.db.models import Count, Sum
    from apps.shop.models import Order, OrderItem

    is_staff = request.user.is_staff or request.user.is_superuser

    subject = request.user
    if not is_staff:
        from core.roles import role_flags
        if role_flags(request).get('is_parent'):
            try:
                from core.scoping import viewing_child
                subject = viewing_child(request) or request.user
            except Exception:      # pragma: no cover
                subject = request.user

    invoices = models.Invoice.objects.all() if is_staff else \
        models.Invoice.objects.filter(customer=subject)
    invoices = invoices.exclude(status=models.Invoice.STATUS_CANCELLED)

    billed = invoices.aggregate(total=Sum('total'))['total'] or Decimal('0')
    collected = Decimal('0')
    for invoice in invoices.prefetch_related('payments'):
        collected += Decimal(str(invoice.amount_paid or 0))
    outstanding = billed - collected

    # "Estimated month-end" is everything invoiced and not yet cancelled — i.e.
    # what lands if every invoice already sent is settled. Labelled as an
    # estimate because that is exactly what it is.
    context = {
        'page_title': 'Financial overview' if is_staff else 'My spending',
        'is_staff': is_staff, 'subject': subject,
        'billed': billed, 'collected': collected, 'outstanding': outstanding,
        'estimated_month_end': billed,
        'invoices': invoices.order_by('-issue_date')[:25],
    }

    items = OrderItem.objects.filter(order__status=Order.STATUS_PAID)
    if not is_staff:
        items = items.filter(order__buyer=subject)
    context['top_products'] = (items.values('product__name')
                               .annotate(units=Sum('quantity'), revenue=Sum('line_total'))
                               .order_by('-units')[:10])

    if is_staff:
        context['by_institution'] = (
            items.values('product__institution__code')
                 .annotate(units=Sum('quantity'), revenue=Sum('line_total'))
                 .order_by('-revenue')[:10])
        context['unpaid_count'] = invoices.exclude(status=models.Invoice.STATUS_PAID).count()
    else:
        # What they may still need to pay for: their own unsettled invoices.
        context['upcoming'] = invoices.exclude(status=models.Invoice.STATUS_PAID)\
                                      .order_by('due_date', 'issue_date')[:10]
    return render(request, 'finance/money-overview.html', context)
