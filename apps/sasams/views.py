"""SA-SAMS export pages — admin / staff only (everyone else gets a 404).

* ``/sasams/``                  — year / term / grade, data quality, downloads.
* ``/sasams/download/``         — the XLSX workbook (``?format=csv`` → ZIP of CSVs).
* ``/sasams/learner-numbers/``  — fill in admission and LURITS numbers for a grade.
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import urlencode

from core.roles import role_flags

from apps.reports.terms import current_year_term

from . import exports

MAX_NUMBER_LENGTH = 20


def _require_office(request):
    if not (role_flags(request).get('is_admin_staff') or request.user.is_superuser):
        raise Http404


def _int(value, default=None, lo=None, hi=None):
    try:
        number = int(str(value).strip())
    except (TypeError, ValueError):
        return default
    if (lo is not None and number < lo) or (hi is not None and number > hi):
        return default
    return number


def _params(request):
    source = request.POST if request.method == 'POST' else request.GET
    year, term = current_year_term()
    return {
        'year': _int(source.get('year'), year, 2000, 2100),
        'term': _int(source.get('term'), term, 1, 4),
        'grade': _int(source.get('grade'), None, 1, 12),
        'drafts': source.get('drafts') in ('1', 'on', 'true', 'yes'),
    }


def _years(year):
    return list(range(year + 1, year - 6, -1))


@login_required
def index(request):
    _require_office(request)
    params = _params(request)
    records = exports.collect(params['year'], params['grade'])
    issues = exports.data_quality(records)
    errors = sum(1 for i in issues if i['Severity'] == exports.ERROR)
    learners_with_issues = len({i['person_id'] for i in issues if i['Severity'] == exports.ERROR})
    query = {'year': params['year'], 'term': params['term']}
    if params['grade']:
        query['grade'] = params['grade']
    if params['drafts']:
        query['drafts'] = 1
    return render(request, 'sasams/index.html', {
        'page_title': 'SA-SAMS export',
        **params,
        'years': _years(params['year']),
        'terms': [1, 2, 3, 4],
        'grades': exports.grades(),
        'emis': exports._emis(),
        'learner_count': len(records),
        'issues': issues[:500],
        'issues_total': len(issues),
        'errors': errors,
        'warnings': len(issues) - errors,
        'learners_with_issues': learners_with_issues,
        'clean_learners': len(records) - learners_with_issues,
        'summary': exports.quality_summary(issues),
        'xlsx_url': f"{reverse('sasams:download')}?{urlencode(query)}",
        'csv_url': f"{reverse('sasams:download')}?{urlencode({**query, 'format': 'csv'})}",
        'numbers_url': f"{reverse('sasams:learner-numbers')}?"
                       f"{urlencode({'year': params['year'], 'grade': params['grade'] or ''})}",
    })


@login_required
def download(request):
    _require_office(request)
    p = _params(request)
    stem = exports.file_stem(p['year'], p['term'], p['grade'])
    if request.GET.get('format') == 'csv':
        body = exports.csv_zip_bytes(p['year'], p['term'], p['grade'], p['drafts'])
        response = HttpResponse(body, content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="{stem}_csv.zip"'
        return response
    body = exports.workbook_bytes(p['year'], p['term'], p['grade'], p['drafts'])
    response = HttpResponse(
        body, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{stem}.xlsx"'
    return response


def save_numbers(records, data):
    """Apply ``admission_<pk>`` / ``lurits_<pk>`` fields from ``data`` to the
    learners in ``records``. Returns ``(saved, errors)``; a value already used by
    another learner is refused."""
    from apps.accounts.models import Person
    saved, errors = 0, []
    for record in records:
        person = record.person
        changed = []
        for attr, prefix, label in (('admission_number', 'admission', 'Admission number'),
                                    ('lurits_number', 'lurits', 'LURITS number')):
            key = f'{prefix}_{person.pk}'
            if key not in data:
                continue
            value = ' '.join((data.get(key) or '').split())
            if value == (getattr(person, attr) or ''):
                continue
            name = f'{person.first_name} {person.last_name}'.strip() or f'Learner {person.pk}'
            if len(value) > MAX_NUMBER_LENGTH:
                errors.append(f'{name}: {label} is longer than {MAX_NUMBER_LENGTH} characters.')
                continue
            if attr == 'lurits_number' and value and not value.isdigit():
                errors.append(f'{name}: LURITS number "{value}" must be digits only.')
                continue
            if value and Person.objects.filter(**{f'{attr}__iexact': value}).exclude(pk=person.pk).exists():
                errors.append(f'{name}: {label} "{value}" is already used by another learner.')
                continue
            setattr(person, attr, value)
            changed.append(attr)
        if changed:
            person.save(update_fields=changed)
            saved += 1
    return saved, errors


@login_required
def learner_numbers(request):
    _require_office(request)
    params = _params(request)
    grades = exports.grades()
    if params['grade'] is None and grades:
        params['grade'] = grades[0].grade
    records = exports.collect(params['year'], params['grade']) if params['grade'] else []
    if request.method == 'POST':
        saved, errors = save_numbers(records, request.POST)
        for error in errors:
            messages.error(request, error)
        if saved:
            messages.success(request, f'Saved numbers for {saved} learner{"s" if saved != 1 else ""}.')
        elif not errors:
            messages.info(request, 'Nothing changed.')
        return redirect(f"{reverse('sasams:learner-numbers')}?"
                        f"{urlencode({'year': params['year'], 'grade': params['grade']})}")
    rows = [{'record': r, 'id_number': exports._id_number(r) if r.application else ''} for r in records]
    return render(request, 'sasams/learner-numbers.html', {
        'page_title': 'Admission & LURITS numbers',
        **params,
        'years': _years(params['year']),
        'grades': grades,
        'rows': rows,
        'missing_admission': sum(1 for r in records if not r.person.admission_number),
        'missing_lurits': sum(1 for r in records if not r.person.lurits_number),
        'max_length': MAX_NUMBER_LENGTH,
    })
