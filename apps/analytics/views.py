"""Analytics dashboard — admin/staff only.

Whole-school analytics belong to the office: students and parents never see
them, and educators get their own subjects' results on the marks and
teaching pages instead. Every view is gated on ``role_flags`` (admin/staff). Phase 1 ships the executive dashboard +
an Excel export; richer drill-downs and charts follow.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render

from core.errors import note
from core.roles import role_flags

from . import services


def _gate(request):
    flags = role_flags(request)
    return flags['is_admin_staff']


@login_required
def dashboard(request):
    if not _gate(request):
        note('ANLT-2001', request)
        messages.error(request, 'Analytics is available to the school office only.')
        return redirect('myhub:index')
    return render(request, 'analytics/dashboard.html', {
        'page_title': 'Analytics', 'data': services.institution_dashboard(),
    })


@login_required
def export_subjects(request):
    """Download module-performance as an Excel file (openpyxl)."""
    if not _gate(request):
        return redirect('myhub:index')
    rows = services.module_performance(limit=1000)
    headers = ['module', 'avg_mark', 'students', 'pass_rate']
    filename, content = services.export_rows_xlsx(rows, headers, 'module-performance.xlsx')
    if content is None:
        note('RPRT-7001', request, package='openpyxl')
        messages.error(request, 'Excel export needs the openpyxl package installed.')
        return redirect('analytics:dashboard')
    resp = HttpResponse(
        content,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    resp['Content-Disposition'] = f'attachment; filename="{filename}"'
    return resp
