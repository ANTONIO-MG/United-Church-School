"""The numbers behind the finance dashboard and reports.

Every report is built here from the ledger rows (invoice lines, payments,
expenses), so the dashboard, the report pages and their CSV exports cannot
disagree. Two bases are kept side by side throughout, as asked for:

* **Paid** (cash basis) — money that actually arrived, on the day it arrived.
  A payment is spread over its invoice's lines in proportion to their amounts,
  so a part-payment of a mixed invoice is attributed fairly.
* **Invoiced** (accrual basis) — what was billed, on the invoice date.
  Drafts and voided invoices are never income.

Income is grouped into **streams** by what was sold (the shop product's
fulfilment); lines with no product are the module / tuition fees raised by
registration and bulk invoicing, and "Delivery" lines are delivery income.
"""
import calendar
from collections import OrderedDict, defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Sum
from django.utils import timezone

from . import models

ZERO = Decimal('0')

STREAMS = OrderedDict([
    ('fees', 'Module & tuition fees'),
    ('digital', 'Learning resources'),
    ('booking', '1-on-1 sessions'),
    ('shipped', 'Study-materials store'),
    ('delivery', 'Delivery charges'),
    ('other', 'Other income'),
])

LIVE_INVOICE_EXCLUDE = (models.Invoice.STATUS_DRAFT, models.Invoice.STATUS_CANCELLED)


# ---------------------------------------------------------------------------
# Periods
# ---------------------------------------------------------------------------
@dataclass
class Period:
    key: str
    label: str
    start: date
    end: date

    @property
    def days(self):
        return (self.end - self.start).days + 1

    def previous(self):
        length = timedelta(days=self.days)
        return Period('previous', 'Previous period', self.start - length, self.start - timedelta(days=1))


PERIOD_CHOICES = [('month', 'This month'), ('last_month', 'Last month'), ('quarter', 'This quarter'),
                  ('ytd', 'Year to date'), ('12m', 'Last 12 months'), ('last_year', 'Last year'),
                  ('custom', 'Custom')]


def period_from(request_get, default='ytd'):
    from django.utils.dateparse import parse_date
    today = timezone.localdate()
    key = request_get.get('period') or default
    if key == 'month':
        start, end = today.replace(day=1), today
    elif key == 'last_month':
        end = today.replace(day=1) - timedelta(days=1)
        start = end.replace(day=1)
    elif key == 'quarter':
        start, end = today.replace(month=3 * ((today.month - 1) // 3) + 1, day=1), today
    elif key == '12m':
        start, end = add_months(today.replace(day=1), -11), today
    elif key == 'last_year':
        start, end = date(today.year - 1, 1, 1), date(today.year - 1, 12, 31)
    elif key == 'custom':
        start = parse_date(request_get.get('from') or '') or today.replace(month=1, day=1)
        end = parse_date(request_get.get('to') or '') or today
        if end < start:
            start, end = end, start
    else:
        key, start, end = 'ytd', today.replace(month=1, day=1), today
    return Period(key, dict(PERIOD_CHOICES).get(key, 'Custom'), start, end)


def add_months(day, months):
    month = day.month - 1 + months
    year = day.year + month // 12
    month = month % 12 + 1
    return day.replace(year=year, month=month, day=min(day.day, calendar.monthrange(year, month)[1]))


def months_between(start, end):
    """First days of each month from ``start`` to ``end`` inclusive."""
    cursor, out = start.replace(day=1), []
    while cursor <= end:
        out.append(cursor)
        cursor = add_months(cursor, 1)
    return out


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------
def stream_of(item):
    product = item.product
    if product is not None:
        return {'digital': 'digital', 'booking': 'booking', 'shipped': 'shipped'}.get(product.fulfilment, 'other')
    if (item.description or '').strip().lower() == 'delivery':
        return 'delivery'
    return 'fees'


def item_label(item):
    if item.product_id:
        return item.product.name
    return (item.description or 'Other').strip()[:120]


# ---------------------------------------------------------------------------
# Ledger rows
# ---------------------------------------------------------------------------
def invoiced_lines(start, end, customer=None):
    """Accrual: invoice lines dated in the period (by invoice date)."""
    qs = (models.InvoiceItem.objects
          .filter(invoice__issue_date__gte=start, invoice__issue_date__lte=end)
          .exclude(invoice__status__in=LIVE_INVOICE_EXCLUDE)
          .select_related('invoice__customer', 'product'))
    if customer is not None:
        qs = qs.filter(invoice__customer=customer)
    return qs


def paid_lines(start, end, customer=None):
    """Cash: each payment in the period spread across its invoice's lines.

    Yields ``(item, amount, paid_on, payment)``. A payment on an invoice with
    no lines (hand-made, total only) is attributed to fees.
    """
    payments = (models.InvoicePayment.objects
                .filter(status=models.InvoicePayment.STATUS_COMPLETED,
                        paid_at__date__gte=start, paid_at__date__lte=end)
                .exclude(invoice__status=models.Invoice.STATUS_CANCELLED)
                .select_related('invoice__customer')
                .prefetch_related('invoice__items__product'))
    if customer is not None:
        payments = payments.filter(invoice__customer=customer)
    for payment in payments:
        items = list(payment.invoice.items.all())
        base = sum((Decimal(str(i.amount or 0)) for i in items), ZERO)
        paid_on = timezone.localdate(payment.paid_at)
        if base <= 0:
            yield None, Decimal(str(payment.amount)), paid_on, payment
            continue
        remaining = Decimal(str(payment.amount))
        for index, item in enumerate(items):
            if index == len(items) - 1:
                share = remaining          # the last line takes the rounding, so shares sum exactly
            else:
                share = (Decimal(str(payment.amount)) * Decimal(str(item.amount or 0)) / base).quantize(Decimal('0.01'))
                remaining -= share
            yield item, share, paid_on, payment


def expenses_in(start, end):
    return (models.Expense.objects.filter(date__gte=start, date__lte=end)
            .select_related('category', 'vendor', 'institution'))


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------
def income_by_stream(start, end, customer=None):
    rows = OrderedDict((key, {'key': key, 'label': label, 'paid': ZERO, 'invoiced': ZERO})
                       for key, label in STREAMS.items())
    for item in invoiced_lines(start, end, customer):
        rows[stream_of(item)]['invoiced'] += Decimal(str(item.amount or 0))
    for item, amount, _day, _payment in paid_lines(start, end, customer):
        rows[stream_of(item) if item else 'fees']['paid'] += amount
    return [r for r in rows.values() if r['paid'] or r['invoiced']]


def profit_and_loss(start, end):
    income = income_by_stream(start, end)
    total_paid = sum((r['paid'] for r in income), ZERO)
    total_invoiced = sum((r['invoiced'] for r in income), ZERO)

    groups = OrderedDict((key, {'key': key, 'label': label, 'lines': [], 'total': ZERO})
                         for key, label in models.ExpenseCategory.GROUP_CHOICES)
    by_category = (expenses_in(start, end).values('category__name', 'category__group')
                   .annotate(total=Sum('amount'), vat=Sum('vat_amount')).order_by('-total'))
    vat_registered = _vat_registered()
    for row in by_category:
        # A VAT vendor reclaims input VAT, so the cost to the business is ex-VAT.
        cost = row['total'] - (row['vat'] or ZERO) if vat_registered else row['total']
        group = groups[row['category__group'] or 'other']
        group['lines'].append({'label': row['category__name'], 'amount': cost})
        group['total'] += cost
    cost_of_sales = groups['cost_of_sales']['total']
    operating = sum((g['total'] for k, g in groups.items() if k != 'cost_of_sales'), ZERO)

    # Income is VAT-inclusive; profit is reported ex-VAT when registered.
    output_vat_paid = _vat_in(total_paid) if vat_registered else ZERO
    output_vat_invoiced = _vat_in(total_invoiced) if vat_registered else ZERO
    net_paid = total_paid - output_vat_paid
    net_invoiced = total_invoiced - output_vat_invoiced
    return {
        'income': income, 'total_paid': total_paid, 'total_invoiced': total_invoiced,
        'vat_paid': output_vat_paid, 'vat_invoiced': output_vat_invoiced,
        'revenue_paid': net_paid, 'revenue_invoiced': net_invoiced,
        'groups': [g for g in groups.values() if g['lines']],
        'cost_of_sales': cost_of_sales, 'operating': operating,
        'gross_paid': net_paid - cost_of_sales, 'gross_invoiced': net_invoiced - cost_of_sales,
        'net_paid': net_paid - cost_of_sales - operating,
        'net_invoiced': net_invoiced - cost_of_sales - operating,
        'expenses_total': cost_of_sales + operating, 'vat_registered': vat_registered,
    }


def sales_by_item(start, end):
    rows = defaultdict(lambda: {'label': '', 'stream': '', 'units': 0, 'gross': ZERO, 'discount': ZERO,
                                'invoiced': ZERO, 'paid': ZERO})
    for item in invoiced_lines(start, end):
        key = f'p{item.product_id}' if item.product_id else f'd:{item_label(item).lower()}'
        row = rows[key]
        row['label'], row['stream'] = item_label(item), STREAMS[stream_of(item)]
        row['units'] += item.quantity or 0
        row['gross'] += Decimal(str(item.gross_amount))
        row['discount'] += Decimal(str(item.discount_amount or 0))
        row['invoiced'] += Decimal(str(item.amount or 0))
    for item, amount, _day, _payment in paid_lines(start, end):
        if item is None:
            continue
        key = f'p{item.product_id}' if item.product_id else f'd:{item_label(item).lower()}'
        rows[key]['label'] = rows[key]['label'] or item_label(item)
        rows[key]['stream'] = rows[key]['stream'] or STREAMS[stream_of(item)]
        rows[key]['paid'] += amount
    return sorted(rows.values(), key=lambda r: (r['paid'], r['invoiced']), reverse=True)


def sales_by_customer(start, end):
    rows = {}
    for item in invoiced_lines(start, end):
        customer = item.invoice.customer
        row = rows.setdefault(customer.pk, _customer_row(customer))
        row['invoiced'] += Decimal(str(item.amount or 0))
        row['invoices'].add(item.invoice_id)
    for item, amount, day, payment in paid_lines(start, end):
        customer = payment.invoice.customer
        row = rows.setdefault(customer.pk, _customer_row(customer))
        row['paid'] += amount
        row['last_paid'] = max(row['last_paid'] or day, day)
    outstanding = _outstanding_by_customer()
    for pk, row in rows.items():
        row['outstanding'] = outstanding.get(pk, ZERO)
        row['invoice_count'] = len(row.pop('invoices'))
    return sorted(rows.values(), key=lambda r: (r['paid'], r['invoiced']), reverse=True)


def _customer_row(user):
    return {'user': user, 'name': user.get_full_name() or user.email or user.get_username(),
            'email': user.email, 'invoiced': ZERO, 'paid': ZERO, 'invoices': set(), 'last_paid': None}


def _open_invoices():
    return (models.Invoice.objects.exclude(status__in=LIVE_INVOICE_EXCLUDE + (models.Invoice.STATUS_PAID,))
            .filter(total__gt=0).select_related('customer').prefetch_related('payments'))


def _outstanding_by_customer():
    out = defaultdict(lambda: ZERO)
    for invoice in _open_invoices():
        if invoice.balance > 0:
            out[invoice.customer_id] += invoice.balance
    return out


def income_by_programme(start, end):
    """Income attributed to the institution and programme the buyer is enrolled on.

    A student on two programmes is attributed to the one they enrolled on
    first; people with no programme (parents, corporates) are "Not enrolled".
    """
    from apps.learning.models import ProgrammeEnrolment

    home = {}
    for enrolment in (ProgrammeEnrolment.objects.select_related('programme__institution', 'person')
                      .order_by('created_at')):
        home.setdefault(enrolment.person.user_id, enrolment.programme)

    rows = {}

    def row_for(user_id):
        programme = home.get(user_id)
        key = programme.pk if programme else None
        if key not in rows:
            rows[key] = {'programme': str(programme) if programme else 'Not enrolled in a grade',
                         'institution': programme.institution.name if programme else '—',
                         'invoiced': ZERO, 'paid': ZERO, 'students': set()}
        return rows[key]

    for item in invoiced_lines(start, end):
        row = row_for(item.invoice.customer_id)
        row['invoiced'] += Decimal(str(item.amount or 0))
        row['students'].add(item.invoice.customer_id)
    for _item, amount, _day, payment in paid_lines(start, end):
        row = row_for(payment.invoice.customer_id)
        row['paid'] += amount
        row['students'].add(payment.invoice.customer_id)
    for row in rows.values():
        row['students'] = len(row['students'])
    return sorted(rows.values(), key=lambda r: r['paid'], reverse=True)


AGING_BUCKETS = [('current', 'Not yet due'), ('1_30', '1–30 days'), ('31_60', '31–60 days'),
                 ('61_90', '61–90 days'), ('90_plus', 'Over 90 days')]


def receivables_aging(today=None):
    today = today or timezone.localdate()
    buckets = OrderedDict((k, ZERO) for k, _ in AGING_BUCKETS)
    customers = {}
    for invoice in _open_invoices():
        balance = invoice.balance
        if balance <= 0:
            continue
        days = (today - invoice.due_date).days if invoice.due_date else 0
        key = ('current' if days <= 0 else '1_30' if days <= 30 else '31_60' if days <= 60
               else '61_90' if days <= 90 else '90_plus')
        buckets[key] += balance
        row = customers.setdefault(invoice.customer_id, {
            'user': invoice.customer, 'name': invoice.customer.get_full_name() or invoice.customer.email,
            **{k: ZERO for k, _ in AGING_BUCKETS}, 'total': ZERO, 'invoices': []})
        row[key] += balance
        row['total'] += balance
        row['invoices'].append(invoice)
    return {'buckets': [{'key': k, 'label': label, 'amount': buckets[k]} for k, label in AGING_BUCKETS],
            'total': sum(buckets.values(), ZERO),
            'customers': sorted(customers.values(), key=lambda r: r['total'], reverse=True)}


def payments_received(start, end):
    qs = (models.InvoicePayment.objects
          .filter(status=models.InvoicePayment.STATUS_COMPLETED, paid_at__date__gte=start, paid_at__date__lte=end)
          .exclude(invoice__status=models.Invoice.STATUS_CANCELLED)
          .select_related('invoice__customer').order_by('-paid_at'))
    by_method = qs.values('method').annotate(total=Sum('amount')).order_by('-total')
    labels = dict(models.InvoicePayment.METHOD_CHOICES)
    return {'payments': qs, 'total': qs.aggregate(t=Sum('amount'))['t'] or ZERO,
            'by_method': [{'label': labels.get(r['method'], r['method']), 'total': r['total']} for r in by_method]}


def expenses_by_category(start, end):
    qs = expenses_in(start, end)
    rows = list(qs.values('category__name', 'category__group').annotate(total=Sum('amount'), vat=Sum('vat_amount'))
                .order_by('-total'))
    groups = dict(models.ExpenseCategory.GROUP_CHOICES)
    for row in rows:
        row['group'] = groups.get(row['category__group'], '')
    return {'rows': rows, 'total': qs.aggregate(t=Sum('amount'))['t'] or ZERO, 'expenses': qs.order_by('-date')}


def monthly_series(start, end):
    """Per month: paid income, invoiced income, expenses — for the charts and cash flow."""
    months = months_between(start, end)
    series = OrderedDict((m, {'month': m, 'paid': ZERO, 'invoiced': ZERO, 'expenses': ZERO}) for m in months)
    for item in invoiced_lines(start, end):
        key = models.as_date(item.invoice.issue_date).replace(day=1)
        if key in series:
            series[key]['invoiced'] += Decimal(str(item.amount or 0))
    for _item, amount, day, _payment in paid_lines(start, end):
        key = day.replace(day=1)
        if key in series:
            series[key]['paid'] += amount
    for row in expenses_in(start, end).values('date', 'amount'):
        key = row['date'].replace(day=1)
        if key in series:
            series[key]['expenses'] += row['amount']
    running = ZERO
    for row in series.values():
        row['net'] = row['paid'] - row['expenses']
        running += row['net']
        row['running'] = running
    return list(series.values())


def overview(period):
    """Everything the finance dashboard shows, for ``period`` and the one before."""
    previous = period.previous()
    pnl, before = profit_and_loss(period.start, period.end), profit_and_loss(previous.start, previous.end)
    chart_start = add_months(period.end.replace(day=1), -11)
    items = sales_by_item(period.start, period.end)
    return {
        'period': period, 'pnl': pnl, 'previous': before,
        'change': {
            'paid': _change(pnl['total_paid'], before['total_paid']),
            'invoiced': _change(pnl['total_invoiced'], before['total_invoiced']),
            'expenses': _change(pnl['expenses_total'], before['expenses_total']),
            'net': _change(pnl['net_paid'], before['net_paid']),
        },
        'aging': receivables_aging(),
        'series': monthly_series(chart_start, period.end),
        'streams': pnl['income'],
        'top_items': items[:8], 'bottom_items': [r for r in reversed(items) if r['invoiced'] or r['paid']][:5],
        'top_customers': sales_by_customer(period.start, period.end)[:8],
        'programmes': income_by_programme(period.start, period.end)[:8],
        'expense_categories': expenses_by_category(period.start, period.end)['rows'][:8],
    }


def _change(now, before):
    if not before:
        return None
    return int(round((now - before) * 100 / abs(before)))


def _vat_registered():
    from django.conf import settings
    return bool(getattr(settings, 'VAT_REGISTERED', False))


def _vat_in(amount):
    from django.conf import settings
    return models.vat_portion(amount, getattr(settings, 'VAT_RATE', 15), inclusive=True)


# ---------------------------------------------------------------------------
# A student's own finances
# ---------------------------------------------------------------------------
TYPICAL_PROGRAMME_MONTHS = 12


def student_summary(user):
    """What a student (or their parent) sees on My finances."""
    today = timezone.localdate()
    invoices = (models.Invoice.objects.filter(customer=user).exclude(status__in=LIVE_INVOICE_EXCLUDE)
                .prefetch_related('payments', 'items__product').order_by('-issue_date', '-id'))
    spent = (models.InvoicePayment.objects.filter(invoice__customer=user, status=models.InvoicePayment.STATUS_COMPLETED)
             .exclude(invoice__status=models.Invoice.STATUS_CANCELLED).aggregate(t=Sum('amount'))['t'] or ZERO)
    open_invoices = [i for i in invoices if i.status != models.Invoice.STATUS_PAID and i.balance > 0]
    owed = sum((i.balance for i in open_invoices), ZERO)
    next_due = min(open_invoices, key=lambda i: i.due_date or date.max) if open_invoices else None

    first = (models.InvoicePayment.objects.filter(invoice__customer=user, status=models.InvoicePayment.STATUS_COMPLETED)
             .order_by('paid_at').values_list('paid_at', flat=True).first())
    since = timezone.localdate(first) if first else today
    streams = income_by_stream(since, today, customer=user)
    series = [{'month': m, 'paid': ZERO} for m in months_between(add_months(today.replace(day=1), -11), today)]
    by_month = {row['month']: row for row in series}
    for _item, amount, day, _payment in paid_lines(add_months(today.replace(day=1), -11), today, customer=user):
        key = day.replace(day=1)
        if key in by_month:
            by_month[key]['paid'] += amount

    forecast = study_forecast(user, today)
    return {
        'spent': spent, 'owed': owed, 'since': since, 'next_due': next_due,
        'invoices': invoices[:50], 'open_invoices': open_invoices,
        'streams': [{'label': r['label'], 'amount': r['paid']} for r in streams if r['paid']],
        'series': series, 'forecast': forecast,
        'to_finish': forecast['total'] + owed,
        'payments': (models.InvoicePayment.objects.filter(invoice__customer=user,
                                                          status=models.InvoicePayment.STATUS_COMPLETED)
                     .select_related('invoice').order_by('-paid_at')[:20]),
    }


def study_forecast(user, today=None):
    """Monthly module fees from each active module's paid-up date to the end of studies.

    The end is the cohort's end date for that programme; with no cohort end
    date, :data:`TYPICAL_PROGRAMME_MONTHS` from when the student enrolled. A
    locked module whose first month is already on an unpaid invoice is not
    counted twice — that month is in "owed".
    """
    from apps.learning.models import ModuleEnrolment, ProgrammeEnrolment

    today = today or timezone.localdate()
    person = getattr(user, 'profile', None)
    if person is None:
        return {'lines': [], 'total': ZERO, 'until': None}
    ends = {}
    for enrolment in ProgrammeEnrolment.objects.filter(person=person, is_active=True).select_related('cohort'):
        end = enrolment.cohort.end_date if enrolment.cohort and enrolment.cohort.end_date else None
        if end is None:
            end = add_months(timezone.localdate(enrolment.created_at), TYPICAL_PROGRAMME_MONTHS)
        ends[enrolment.programme_id] = end

    lines, total, latest = [], ZERO, None
    for enrolment in (ModuleEnrolment.objects.filter(person=person)
                      .exclude(status=ModuleEnrolment.STATUS_EXPIRED)
                      .select_related('programme_module__programme')):
        module = enrolment.programme_module
        end = ends.get(module.programme_id)
        price = Decimal(str(enrolment.price or 0))
        if end is None or end <= today or price <= 0:
            continue
        paid_to = enrolment.paid_until if enrolment.paid_until and enrolment.paid_until > today else today
        months = max(0, (end.year - paid_to.year) * 12 + (end.month - paid_to.month) + (1 if end.day > paid_to.day else 0))
        if enrolment.status == ModuleEnrolment.STATUS_LOCKED and enrolment.invoice_uid and months:
            months -= 1
        if not months:
            continue
        cost = price * months
        total += cost
        latest = max(latest or end, end)
        lines.append({'module': module.name or module.code, 'code': module.code, 'months': months,
                      'monthly': price, 'cost': cost, 'until': end})
    return {'lines': lines, 'total': total, 'until': latest}
