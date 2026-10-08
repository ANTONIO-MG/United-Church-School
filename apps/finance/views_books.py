"""Wave-style documents and the expense book.

* Invoice editor (new / edit), invoice actions (remind, duplicate, void).
* Estimates: list, editor, detail, PDF, public accept page, convert.
* Statements of account (HTML + PDF).
* Expenses, recurring profiles, vendors and categories.

Admin and staff only, except the public estimate page (tokenised, like the
invoice pay link) and a student's own statement.
"""
from datetime import date, timedelta
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.db.models import Q, Sum
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from core.errors import note
from core.roles import role_flags

from . import documents, forms, models

staff_required = user_passes_test(lambda u: u.is_active and u.is_staff)


def _is_staff(request):
    return role_flags(request)['is_admin_staff']


def _vat_number():
    from django.conf import settings
    return getattr(settings, 'VAT_NUMBER', '')


def _pdf(pdf, filename, inline=False):
    if not pdf:
        raise Http404('The PDF could not be generated.')
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'{"inline" if inline else "attachment"}; filename="{filename}"'
    return response


# ===========================================================================
# Shared editor for invoices and estimates
# ===========================================================================
def _editor(request, *, kind, instance, form_class, formset_class, template_title, prefill_customer=None):
    creating = instance.pk is None
    if request.method == 'POST':
        form = form_class(request.POST, instance=instance)
        lines = formset_class(request.POST, instance=instance, prefix='lines')
        if form.is_valid() and lines.is_valid():
            with transaction.atomic():
                document = form.save(commit=False)
                if creating:
                    document.created_by = request.user
                    document.status = 'draft'
                document.save()
                lines.instance = document
                lines.save()
                document.recalc_total()
            if request.POST.get('then') == 'send':
                return _send_document(request, document, kind)
            messages.success(request, f'{document.number} saved.')
            return redirect(document.get_absolute_url())
        messages.error(request, 'Please correct the highlighted fields.')
    else:
        initial = {'customer': prefill_customer} if prefill_customer else {}
        form = form_class(instance=instance, initial=initial)
        lines = formset_class(instance=instance, prefix='lines')

    from apps.shop.models import Product
    from django.conf import settings
    products = {str(p.pk): {'name': p.name, 'price': str(p.price), 'summary': p.summary}
                for p in Product.objects.filter(status='active')}
    return render(request, 'finance/document-editor.html', {
        'page_title': template_title, 'kind': kind, 'form': form, 'lines': lines, 'object': instance,
        'creating': creating, 'products_json': products,
        'vat_registered': getattr(settings, 'VAT_REGISTERED', False),
        'vat_rate': getattr(settings, 'VAT_RATE', 15),
    })


def _send_document(request, document, kind):
    from apps.communication import emails
    from core.utils import absolute_url
    if kind == 'invoice':
        documents.mark_sent(document)
        from . import emails as finance_emails
        sent = finance_emails.send_invoice_email(document)
    else:
        document.status = models.Estimate.STATUS_SENT if document.status == 'draft' else document.status
        document.sent_at = timezone.now()
        document.save(update_fields=['status', 'sent_at', 'updated_at'])
        sent = emails.send_estimate_email(document, absolute_url(document.get_public_url()))
    if sent:
        messages.success(request, f'{document.number} e-mailed to {document.customer.email}.')
    else:
        messages.warning(request, f'{document.number} is marked sent, but the e-mail did not go out '
                                  '(no address, or the mail server refused it).')
    return redirect(document.get_absolute_url())


# ===========================================================================
# Invoices
# ===========================================================================
@login_required
@staff_required
def invoice_new(request):
    customer = request.GET.get('customer')
    return _editor(request, kind='invoice', instance=models.Invoice(), form_class=forms.InvoiceEditForm,
                   formset_class=forms.InvoiceLineFormSet, template_title='New invoice',
                   prefill_customer=customer)


@login_required
@staff_required
def invoice_edit(request, pk):
    invoice = get_object_or_404(models.Invoice, pk=pk)
    if invoice.amount_paid:
        messages.info(request, 'This invoice has payments against it, so its lines are locked. '
                               'Duplicate it to raise a corrected one.')
        return redirect(invoice.get_absolute_url())
    return _editor(request, kind='invoice', instance=invoice, form_class=forms.InvoiceEditForm,
                   formset_class=forms.InvoiceLineFormSet, template_title=f'Edit {invoice.number}')


@login_required
@staff_required
@require_POST
def invoice_action(request, pk):
    invoice = get_object_or_404(models.Invoice, pk=pk)
    action = request.POST.get('action')
    if action == 'remind':
        if documents.send_reminder(invoice):
            messages.success(request, f'Reminder e-mailed to {invoice.customer.email}.')
        else:
            messages.warning(request, 'The reminder could not be sent.')
    elif action == 'duplicate':
        copy = documents.duplicate_invoice(invoice, by=request.user)
        messages.success(request, f'{copy.number} created as a draft copy of {invoice.number}.')
        return redirect('finance:invoice-edit', pk=copy.pk)
    elif action == 'void':
        try:
            documents.void_invoice(invoice, by=request.user, reason=request.POST.get('reason', ''))
            messages.success(request, f'{invoice.number} voided.')
        except ValueError as exc:
            messages.error(request, str(exc))
    elif action == 'send':
        return _send_document(request, invoice, 'invoice')
    elif action == 'approve' and invoice.status == models.Invoice.STATUS_DRAFT:
        invoice.status = models.Invoice.STATUS_SENT
        invoice.save(update_fields=['status', 'updated_at'])
        messages.success(request, f'{invoice.number} approved — it is now payable.')
    return redirect(invoice.get_absolute_url())


# ===========================================================================
# Estimates
# ===========================================================================
@login_required
@staff_required
def estimates(request):
    status = request.GET.get('status', '')
    qs = models.Estimate.objects.select_related('customer')
    if status in dict(models.Estimate.STATUS_CHOICES):
        qs = qs.filter(status=status)
    search = request.GET.get('q', '')
    if search:
        qs = qs.filter(Q(number__icontains=search) | Q(customer__first_name__icontains=search)
                       | Q(customer__last_name__icontains=search) | Q(customer__email__icontains=search)
                       | Q(summary__icontains=search))
    documents.expire_estimates()
    open_qs = models.Estimate.objects.filter(status__in=['sent', 'viewed'])
    return render(request, 'finance/estimates.html', {
        'page_title': 'Estimates', 'estimates': qs[:300], 'status': status, 'search': search,
        'STATUS_CHOICES': models.Estimate.STATUS_CHOICES,
        'kpis': {
            'open_total': open_qs.aggregate(t=Sum('total'))['t'] or 0, 'open_count': open_qs.count(),
            'accepted': models.Estimate.objects.filter(status__in=['accepted', 'converted']).count(),
            'decided': models.Estimate.objects.filter(status__in=['accepted', 'converted', 'declined']).count(),
            'drafts': models.Estimate.objects.filter(status='draft').count(),
        },
    })


@login_required
@staff_required
def estimate_new(request):
    return _editor(request, kind='estimate', instance=models.Estimate(), form_class=forms.EstimateEditForm,
                   formset_class=forms.EstimateLineFormSet, template_title='New estimate',
                   prefill_customer=request.GET.get('customer'))


@login_required
@staff_required
def estimate_edit(request, pk):
    estimate = get_object_or_404(models.Estimate, pk=pk)
    if estimate.status == models.Estimate.STATUS_CONVERTED:
        messages.info(request, 'This estimate has already become an invoice.')
        return redirect(estimate.get_absolute_url())
    return _editor(request, kind='estimate', instance=estimate, form_class=forms.EstimateEditForm,
                   formset_class=forms.EstimateLineFormSet, template_title=f'Edit {estimate.number}')


@login_required
@staff_required
def estimate_detail(request, pk):
    estimate = get_object_or_404(models.Estimate.objects.select_related('customer', 'converted_invoice'), pk=pk)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'send':
            return _send_document(request, estimate, 'estimate')
        if action in ('accept', 'decline'):
            documents.respond_to_estimate(estimate, accepted=action == 'accept')
            messages.success(request, f'{estimate.number} marked {estimate.get_status_display().lower()}.')
        elif action == 'convert':
            invoice = documents.convert_estimate(estimate, by=request.user)
            messages.success(request, f'{invoice.number} created from {estimate.number}. Review it, then send.')
            return redirect(invoice.get_absolute_url())
        return redirect(estimate.get_absolute_url())
    return render(request, 'finance/estimate-detail.html', {
        'page_title': estimate.number, 'doc': estimate, 'estimate': estimate,
        'items': list(estimate.items.all()), 'public_url': estimate.get_public_url(),
        'vat_number': _vat_number(),
    })


@login_required
@staff_required
def estimate_pdf(request, pk):
    from . import pdf
    estimate = get_object_or_404(models.Estimate, pk=pk)
    return _pdf(pdf.render_estimate_pdf(estimate), f'Estimate-{estimate.number}.pdf')


def estimate_public(request, public_id):
    """The customer's view of an estimate, from the e-mailed link (no login)."""
    estimate = get_object_or_404(models.Estimate.objects.select_related('customer'), public_id=public_id)
    if request.method == 'POST' and request.POST.get('action') in ('accept', 'decline'):
        if estimate.is_expired:
            messages.error(request, 'This estimate has expired — ask us for an updated one.')
        else:
            documents.respond_to_estimate(estimate, accepted=request.POST['action'] == 'accept')
            messages.success(request, 'Thank you — we have your answer and will be in touch.'
                             if request.POST['action'] == 'accept' else 'Thanks for letting us know.')
        return redirect('finance:estimate-public', public_id=estimate.public_id)
    if not (request.user.is_authenticated and request.user.is_staff):
        documents.mark_viewed(estimate)
    return render(request, 'finance/estimate-public.html', {
        'page_title': f'Estimate {estimate.number}', 'doc': estimate, 'estimate': estimate,
        'items': list(estimate.items.all()), 'vat_number': _vat_number(),
    })


def estimate_public_pdf(request, public_id):
    from . import pdf
    estimate = get_object_or_404(models.Estimate, public_id=public_id)
    return _pdf(pdf.render_estimate_pdf(estimate), f'Estimate-{estimate.number}.pdf')


# ===========================================================================
# Statements
# ===========================================================================
def _parse(value, default):
    from django.utils.dateparse import parse_date
    return parse_date(value or '') or default


def _statement_subject(request, user_id):
    """Whose statement this request may see: staff anyone's, a parent their
    child's, everybody else their own."""
    User = get_user_model()
    if user_id is None:
        subject = request.user
        if role_flags(request).get('is_parent'):
            try:
                from core.scoping import viewing_child
                subject = viewing_child(request) or request.user
            except Exception:  # pragma: no cover
                pass
        return subject
    subject = get_object_or_404(User, pk=user_id)
    if subject.pk != request.user.pk and not _is_staff(request):
        note('FIN-2001', request, kind='statement')
        raise Http404
    return subject


@login_required
def statement(request, user_id=None):
    today = timezone.localdate()
    start = _parse(request.GET.get('from'), date(today.year, 1, 1))
    end = _parse(request.GET.get('to'), today)
    subject = _statement_subject(request, user_id)
    data = documents.statement(subject, start, end)
    if request.GET.get('format') == 'pdf':
        from . import pdf
        return _pdf(pdf.render_statement_pdf(data), f'Statement-{start:%Y%m%d}-{end:%Y%m%d}.pdf')
    return render(request, 'finance/statement.html', {
        'page_title': 'Statement of account', 's': data, 'subject': subject,
        'is_staff_view': _is_staff(request) and subject.pk != request.user.pk,
        'customers': get_user_model().objects.filter(invoices__isnull=False).distinct().order_by('first_name')
        if _is_staff(request) else [],
    })


# ===========================================================================
# Expenses
# ===========================================================================
def _expense_period(request):
    today = timezone.localdate()
    period = request.GET.get('period', 'month')
    if period == 'last_month':
        end = today.replace(day=1) - timedelta(days=1)
        start = end.replace(day=1)
    elif period == 'quarter':
        q_month = 3 * ((today.month - 1) // 3) + 1
        start, end = today.replace(month=q_month, day=1), today
    elif period == 'year':
        start, end = today.replace(month=1, day=1), today
    elif period == 'custom':
        start = _parse(request.GET.get('from'), today.replace(day=1))
        end = _parse(request.GET.get('to'), today)
    else:
        period, start, end = 'month', today.replace(day=1), today
    return period, start, end


@login_required
@staff_required
def expenses(request):
    period, start, end = _expense_period(request)
    qs = (models.Expense.objects.filter(date__gte=start, date__lte=end)
          .select_related('category', 'vendor', 'institution', 'recurring'))
    category = request.GET.get('category')
    if category:
        qs = qs.filter(category_id=category)
    search = request.GET.get('q', '')
    if search:
        qs = qs.filter(Q(description__icontains=search) | Q(vendor__name__icontains=search)
                       | Q(reference__icontains=search))
    total = qs.aggregate(t=Sum('amount'))['t'] or Decimal('0')
    by_category = list(qs.values('category__name').annotate(t=Sum('amount')).order_by('-t'))
    top = by_category[0]['t'] if by_category else 0
    for row in by_category:
        row['pct'] = int(row['t'] * 100 / top) if top else 0
    recurring = models.RecurringExpense.objects.filter(is_active=True)
    return render(request, 'finance/expenses.html', {
        'page_title': 'Expenses', 'expenses': qs[:500], 'period': period, 'start': start, 'end': end,
        'total': total, 'vat': qs.aggregate(t=Sum('vat_amount'))['t'] or 0,
        'unpaid': models.Expense.objects.filter(status=models.Expense.STATUS_UNPAID).aggregate(t=Sum('amount'))['t'] or 0,
        'monthly_recurring': sum((r.monthly_equivalent for r in recurring), Decimal('0')),
        'recurring_count': recurring.count(),
        'by_category': by_category, 'categories': models.ExpenseCategory.objects.filter(is_active=True),
        'sel_category': category or '', 'search': search,
    })


@login_required
@staff_required
def expense_form(request, pk=None):
    expense = get_object_or_404(models.Expense, pk=pk) if pk else None
    form = forms.ExpenseForm(request.POST or None, request.FILES or None, instance=expense)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            item = form.save(commit=False)
            if not item.pk:
                item.created_by = request.user
            item.save()
            repeat = form.cleaned_data.get('repeat') if 'repeat' in form.cleaned_data else ''
            if repeat:
                every, frequency = repeat.split(':')
                profile = models.RecurringExpense.objects.create(
                    name=item.description[:120], category=item.category, vendor=item.vendor,
                    description=item.description, amount=item.amount, vat_treatment=item.vat_treatment,
                    paid_through=item.paid_through, institution=item.institution, notes=item.notes,
                    every=int(every), frequency=frequency, start_date=item.date,
                    end_date=form.cleaned_data.get('repeat_until'), created_by=request.user)
                profile.next_date = profile.advance(item.date)
                profile.save(update_fields=['next_date'])
                item.recurring = profile
                item.save(update_fields=['recurring'])
        messages.success(request, f'Expense saved{" and set to repeat" if item.recurring_id and not pk else ""}.')
        if request.POST.get('then') == 'another':
            return redirect('finance:expense-add')
        return redirect('finance:expenses')
    if request.method == 'POST':
        messages.error(request, 'Please correct the highlighted fields.')
    return render(request, 'finance/expense-form.html', {
        'page_title': 'Edit expense' if expense else 'Record an expense', 'form': form, 'object': expense,
    })


@login_required
@staff_required
@require_POST
def expense_delete(request, pk):
    expense = get_object_or_404(models.Expense, pk=pk)
    expense.delete()
    messages.success(request, 'Expense deleted.')
    return redirect('finance:expenses')


@login_required
@staff_required
def expense_receipt(request, pk):
    from django.http import FileResponse
    expense = get_object_or_404(models.Expense, pk=pk)
    if not expense.receipt:
        raise Http404
    return FileResponse(expense.receipt.open('rb'), filename=expense.receipt.name.rsplit('/', 1)[-1])


@login_required
@staff_required
def recurring(request):
    if request.method == 'POST':
        profile = get_object_or_404(models.RecurringExpense, pk=request.POST.get('pk'))
        if request.POST.get('action') == 'toggle':
            profile.is_active = not profile.is_active
            if profile.is_active and profile.next_date and profile.next_date < timezone.localdate():
                profile.next_date = timezone.localdate()
            profile.save(update_fields=['is_active', 'next_date', 'updated_at'])
            messages.success(request, f'“{profile.name}” {"resumed" if profile.is_active else "paused"}.')
        return redirect('finance:recurring')
    profiles = models.RecurringExpense.objects.select_related('category', 'vendor')
    return render(request, 'finance/recurring.html', {
        'page_title': 'Recurring expenses', 'profiles': profiles,
        'monthly': sum((p.monthly_equivalent for p in profiles if p.is_active), Decimal('0')),
    })


@login_required
@staff_required
def recurring_form(request, pk):
    profile = get_object_or_404(models.RecurringExpense, pk=pk)
    form = forms.RecurringExpenseForm(request.POST or None, instance=profile)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'“{profile.name}” saved.')
        return redirect('finance:recurring')
    return render(request, 'finance/expense-form.html', {
        'page_title': f'Recurring · {profile.name}', 'form': form, 'object': profile, 'is_recurring': True,
        'history': profile.expenses.order_by('-date')[:12],
    })


@login_required
@staff_required
def expense_setup(request):
    """Vendors and expense categories on one page."""
    vendor_form = forms.VendorForm(prefix='v')
    category_form = forms.ExpenseCategoryForm(prefix='c')
    if request.method == 'POST':
        if request.POST.get('which') == 'vendor':
            vendor_form = forms.VendorForm(request.POST, prefix='v')
            if vendor_form.is_valid():
                vendor_form.save()
                messages.success(request, 'Vendor added.')
                return redirect('finance:expense-setup')
        else:
            category_form = forms.ExpenseCategoryForm(request.POST, prefix='c')
            if category_form.is_valid():
                category_form.save()
                messages.success(request, 'Category added.')
                return redirect('finance:expense-setup')
        messages.error(request, 'Please correct the highlighted fields.')
    return render(request, 'finance/expense-setup.html', {
        'page_title': 'Vendors & categories', 'vendor_form': vendor_form, 'category_form': category_form,
        'vendors': models.Vendor.objects.annotate(spent=Sum('expenses__amount')),
        'categories': models.ExpenseCategory.objects.annotate(spent=Sum('expenses__amount')),
    })
