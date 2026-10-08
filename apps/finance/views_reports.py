"""Finance dashboards: My finances (students, parents) and the institution reports.

Reports are admin and staff only. Every report page takes the same period
picker and exports the table on screen as CSV (``?format=csv``).
"""
import csv
import json

from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required

from core.errors import note
from core.roles import role_flags

from . import reports

REPORTS = [
    ('profit-and-loss', 'Profit & loss', 'Income by stream against expenses, paid and invoiced side by side.', 'bi-bar-chart-line'),
    ('sales-by-item', 'Sales by item', 'Which products, services and fees earn the most — and the least.', 'bi-box-seam'),
    ('sales-by-customer', 'Sales by student', 'Top-paying students: invoiced, paid and still owed.', 'bi-people'),
    ('income-by-programme', 'Income by grade', 'Which grades bring the fee income in.', 'bi-mortarboard'),
    ('receivables', 'Receivables aging', 'Who owes what, and for how long.', 'bi-hourglass-split'),
    ('payments', 'Payments received', 'Every payment by date, method and reference.', 'bi-cash-stack'),
    ('expenses', 'Expenses by category', 'Where the money goes.', 'bi-wallet2'),
    ('cash-flow', 'Cash flow', 'Money in against money out, month by month.', 'bi-graph-up-arrow'),
]


def _staff(request):
    return role_flags(request)['is_admin_staff']


def _money(value):
    return f'{value:.2f}' if value is not None else ''


def _csv(filename, header, rows):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
    response.write('﻿')  # Excel opens UTF-8 correctly with a BOM
    writer = csv.writer(response)
    writer.writerow(header)
    writer.writerows(rows)
    return response


# ===========================================================================
# Students and parents
# ===========================================================================
@login_required
def my_finances(request):
    subject = request.user
    if role_flags(request).get('is_parent'):
        try:
            from core.scoping import viewing_child
            subject = viewing_child(request) or request.user
        except Exception:  # pragma: no cover
            pass
    data = reports.student_summary(subject)
    paid_so_far = data['spent']
    whole = paid_so_far + data['to_finish']
    chart = {'labels': [row['month'].strftime('%b %y') for row in data['series']],
             'paid': [float(row['paid']) for row in data['series']]}
    return render(request, 'finance/my-finances.html', {
        'page_title': 'My finances', 's': data, 'subject': subject,
        'viewing_child': subject.pk != request.user.pk,
        'progress': {'paid': int(paid_so_far * 100 / whole) if whole else 0,
                     'owed': int(data['owed'] * 100 / whole) if whole else 0},
        'chart_json': json.dumps(chart),
        'stream_max': max([row['amount'] for row in data['streams']] or [0]),
        'bookings': _bookings(subject), 'orders': _orders(subject),
    })


def _bookings(user):
    try:
        from apps.shop.models import Booking
        return (Booking.objects.filter(student=user, status=Booking.STATUS_CONFIRMED)
                .select_related('product', 'educator').order_by('start')[:5])
    except Exception:  # pragma: no cover
        return []


def _orders(user):
    try:
        from apps.shop.models import Order
        return (Order.objects.filter(buyer=user, checked_out=True, shipment__isnull=False)
                .select_related('shipment').order_by('-created_at')[:5])
    except Exception:  # pragma: no cover
        return []


# ===========================================================================
# Institution reports (admin / staff)
# ===========================================================================
@login_required
def reports_home(request):
    if not _staff(request):
        return redirect('finance:my-finances')
    period = reports.period_from(request.GET)
    data = reports.overview(period)
    chart = {
        'labels': [row['month'].strftime('%b %y') for row in data['series']],
        'paid': [float(row['paid']) for row in data['series']],
        'invoiced': [float(row['invoiced']) for row in data['series']],
        'expenses': [float(row['expenses']) for row in data['series']],
    }
    top_stream = max([r['paid'] for r in data['streams']] or [0])
    return render(request, 'finance/reports-home.html', {
        'page_title': 'Financial reports', 'd': data, 'period': period, 'reports': REPORTS,
        'PERIOD_CHOICES': reports.PERIOD_CHOICES, 'chart_json': json.dumps(chart), 'stream_max': top_stream,
        'aging_max': max([b['amount'] for b in data['aging']['buckets']] or [0]),
    })


@login_required
def report(request, slug):
    if not _staff(request):
        note('FIN-2001', request, kind=f'report:{slug}')
        raise Http404
    meta = next((r for r in REPORTS if r[0] == slug), None)
    if meta is None:
        raise Http404
    period = reports.period_from(request.GET)
    start, end = period.start, period.end
    as_csv = request.GET.get('format') == 'csv'
    context = {'page_title': meta[1], 'slug': slug, 'meta': meta, 'period': period, 'reports': REPORTS,
               'PERIOD_CHOICES': reports.PERIOD_CHOICES}
    stamp = f'{slug}-{start:%Y%m%d}-{end:%Y%m%d}'

    if slug == 'profit-and-loss':
        pnl = reports.profit_and_loss(start, end)
        if as_csv:
            rows = [['Income', r['label'], _money(r['paid']), _money(r['invoiced'])] for r in pnl['income']]
            rows.append(['Income', 'Total income', _money(pnl['total_paid']), _money(pnl['total_invoiced'])])
            if pnl['vat_registered']:
                rows.append(['Income', 'Less VAT', _money(-pnl['vat_paid']), _money(-pnl['vat_invoiced'])])
            for g in pnl['groups']:
                rows += [[g['label'], line['label'], _money(-line['amount']), _money(-line['amount'])] for line in g['lines']]
            rows.append(['', 'Net profit', _money(pnl['net_paid']), _money(pnl['net_invoiced'])])
            return _csv(stamp, ['Section', 'Line', 'Paid (cash)', 'Invoiced (accrual)'], rows)
        context['pnl'] = pnl

    elif slug == 'sales-by-item':
        rows = reports.sales_by_item(start, end)
        if as_csv:
            return _csv(stamp, ['Item', 'Stream', 'Units', 'Gross', 'Discount', 'Invoiced', 'Paid'],
                        [[r['label'], r['stream'], r['units'], _money(r['gross']), _money(r['discount']),
                          _money(r['invoiced']), _money(r['paid'])] for r in rows])
        context.update(rows=rows, top=max([r['paid'] for r in rows] or [0]))

    elif slug == 'sales-by-customer':
        rows = reports.sales_by_customer(start, end)
        if as_csv:
            return _csv(stamp, ['Student', 'E-mail', 'Invoices', 'Invoiced', 'Paid', 'Outstanding', 'Last payment'],
                        [[r['name'], r['email'], r['invoice_count'], _money(r['invoiced']), _money(r['paid']),
                          _money(r['outstanding']), r['last_paid'] or ''] for r in rows])
        context['rows'] = rows

    elif slug == 'income-by-programme':
        rows = reports.income_by_programme(start, end)
        if as_csv:
            return _csv(stamp, ['Institution', 'Programme', 'Students', 'Invoiced', 'Paid'],
                        [[r['institution'], r['programme'], r['students'], _money(r['invoiced']), _money(r['paid'])]
                         for r in rows])
        context.update(rows=rows, top=max([r['paid'] for r in rows] or [0]))

    elif slug == 'receivables':
        aging = reports.receivables_aging()
        if as_csv:
            keys = [k for k, _ in reports.AGING_BUCKETS]
            return _csv(f'receivables-{end:%Y%m%d}', ['Student'] + [l for _, l in reports.AGING_BUCKETS] + ['Total'],
                        [[r['name']] + [_money(r[k]) for k in keys] + [_money(r['total'])] for r in aging['customers']])
        context.update(aging=aging, bucket_keys=[k for k, _ in reports.AGING_BUCKETS])

    elif slug == 'payments':
        data = reports.payments_received(start, end)
        if as_csv:
            return _csv(stamp, ['Date', 'Invoice', 'Student', 'Method', 'Reference', 'Amount'],
                        [[p.paid_at.date(), p.invoice.number, p.invoice.customer.get_full_name() or p.invoice.customer.email,
                          p.get_method_display(), p.gateway_ref or p.reference, _money(p.amount)] for p in data['payments']])
        context['data'] = data

    elif slug == 'expenses':
        data = reports.expenses_by_category(start, end)
        if as_csv:
            return _csv(stamp, ['Date', 'Category', 'Vendor', 'Description', 'Reference', 'Paid through', 'VAT', 'Amount'],
                        [[e.date, e.category.name, e.vendor.name if e.vendor else '', e.description, e.reference,
                          e.get_paid_through_display(), _money(e.vat_amount), _money(e.amount)] for e in data['expenses']])
        context.update(data=data, top=max([r['total'] for r in data['rows']] or [0]))

    elif slug == 'cash-flow':
        series = reports.monthly_series(start, end)
        if as_csv:
            return _csv(stamp, ['Month', 'Money in', 'Money out', 'Net', 'Running total'],
                        [[r['month'].strftime('%Y-%m'), _money(r['paid']), _money(r['expenses']), _money(r['net']),
                          _money(r['running'])] for r in series])
        context.update(series=series, chart_json=json.dumps({
            'labels': [r['month'].strftime('%b %y') for r in series],
            'paid': [float(r['paid']) for r in series], 'expenses': [float(r['expenses']) for r in series],
            'running': [float(r['running']) for r in series]}))

    return render(request, 'finance/report.html', context)
