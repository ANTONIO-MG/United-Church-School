"""Bulk learner import / export pages for the school office.

* ``bulk_import`` — ``/admissions/import/``: download the template, upload a
  filled-in sheet, see the dry-run preview (every row with its errors and
  warnings), then confirm the import. The uploaded file is held in a private
  temporary folder between the preview and the confirmation, keyed by a token
  kept in the session.
* ``bulk_template`` — a freshly generated template (always matches the
  current column format).
* ``bulk_export`` — ``/admissions/export/``: filter by year and grade and
  download the learners in the same format.

Admin and staff only; everyone else gets a 404, like the rest of the office.
"""
import tempfile
import uuid
from pathlib import Path

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render

from core import school
from core.roles import role_flags

from . import bulk
from .models import Application

XLSX = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
MAX_UPLOAD = 10 * 1024 * 1024
SESSION_KEY = 'admissions_bulk_import'
UPLOAD_DIR = Path(tempfile.gettempdir()) / 'ucs-learner-import'


def _require_office(request):
    if not (role_flags(request).get('is_admin_staff', False) or request.user.is_superuser):
        raise Http404


def _upload_path(token):
    return UPLOAD_DIR / f'{uuid.UUID(str(token))}.xlsx'


def _options(data):
    return {'create_parent_accounts': bool(data.get('create_parent_accounts')),
            'send_invites': bool(data.get('send_invites'))}


def _xlsx_response(data, filename):
    response = HttpResponse(data, content_type=XLSX)
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@login_required
def bulk_template(request):
    _require_office(request)
    return _xlsx_response(bulk.template_bytes(), 'UCS-learner-import-template.xlsx')


@login_required
def bulk_import(request):
    _require_office(request)
    pending = request.session.get(SESSION_KEY) or {}
    report, options = None, _options(pending.get('options', {}))

    if request.method == 'POST':
        action = request.POST.get('action', 'preview')
        if action == 'cancel':
            _discard(request)
            return redirect('admissions:bulk-import')

        if action == 'import':
            token = pending.get('token')
            path = _upload_path(token) if token else None
            if not path or not path.exists():
                messages.error(request, 'The uploaded file has expired — please upload it again.')
                return redirect('admissions:bulk-import')
            options = _options(request.POST)
            report = bulk.import_workbook(path.read_bytes(), dry_run=False, user=request.user,
                                          **options)
            _discard(request)
            if report.fatal:
                messages.error(request, report.fatal)
            else:
                messages.success(request, f'Import complete: {report.summary()}')
            return render(request, 'admissions/import.html', _context(report, options, done=True,
                                                                      filename=pending.get('name')))

        # preview (dry run)
        upload = request.FILES.get('file')
        options = _options(request.POST)
        if upload is None:
            messages.error(request, 'Choose the filled-in .xlsx file to upload.')
        elif not upload.name.lower().endswith('.xlsx'):
            messages.error(request, 'The file must be an Excel workbook (.xlsx).')
        elif upload.size > MAX_UPLOAD:
            messages.error(request, 'The file is larger than 10 MB.')
        else:
            data = upload.read()
            report = bulk.import_workbook(data, dry_run=True, user=request.user, **options)
            _discard(request)
            if not report.fatal:
                token = uuid.uuid4()
                UPLOAD_DIR.mkdir(parents=True, exist_ok=True, mode=0o700)
                _upload_path(token).write_bytes(data)
                request.session[SESSION_KEY] = {'token': str(token), 'name': upload.name,
                                                'options': options}
            return render(request, 'admissions/import.html',
                          _context(report, options, filename=upload.name))

    return render(request, 'admissions/import.html', _context(None, options))


def _discard(request):
    pending = request.session.pop(SESSION_KEY, None) or {}
    token = pending.get('token')
    if token:
        try:
            _upload_path(token).unlink(missing_ok=True)
        except (OSError, ValueError):
            pass


def _context(report, options, *, done=False, filename=''):
    return {
        'page_title': 'Import learners',
        'report': report, 'options': options, 'done': done, 'filename': filename,
        'rows': report.rows if report else [],
        'columns': bulk.COLUMNS, 'sections': bulk.SECTIONS,
        'static_template': 'documents/UCS-learner-import-template.xlsx',
        'generated_domain': bulk.GENERATED_EMAIL_DOMAIN,
    }


@login_required
def bulk_export(request):
    _require_office(request)
    years = sorted(set(Application.objects.values_list('year', flat=True)) | {school.YEAR},
                   reverse=True)
    year = request.GET.get('year') or ''
    grade = request.GET.get('grade') or ''
    year = int(year) if year.isdigit() else school.YEAR
    grade = int(grade) if grade.isdigit() and int(grade) in school.GRADES else None
    if request.GET.get('download'):
        data = bulk.export_workbook(year=year, grade=grade)
        name = f'UCS-learners-{year}' + (f'-grade-{grade}' if grade else '') + '.xlsx'
        return _xlsx_response(data, name)
    applications = Application.objects.filter(year=year)
    if grade:
        applications = applications.filter(programme__grade=grade)
    count = applications.count()
    return render(request, 'admissions/export.html', {
        'page_title': 'Export learners', 'years': years, 'grades': school.GRADES,
        'filters': {'year': year, 'grade': grade}, 'count': count,
    })
