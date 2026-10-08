"""Term reporting views — mark sheets, report cards and the office overview.

Who sees what:

* **subject educator** (``ProgrammeModule.educators``) — the mark sheets of the
  subjects they teach, and nobody else's (anything else is a 404).
* **admin / staff** — every mark sheet, the term overview, and any learner's
  report card (drafts included, flagged as such).
* **learner** — their own report card, **published** results only.
* **parent** — their linked child's report card (``?student=``), published only.
"""
import csv
import datetime

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from core import school
from core.roles import role_flags
from core.scoping import viewing_child

from . import term_results as tr
from . import terms
from .models import TermResult


def _year_param(request, default=None):
    raw = (request.GET.get('year') or '').strip()
    if raw.isdigit() and 2000 <= int(raw) <= 2100:
        return int(raw)
    return default or terms.current_year_term()[0]


def _term_param(request, default=None):
    raw = (request.GET.get('term') or '').strip()
    if raw.isdigit() and int(raw) in terms.TERM_NUMBERS:
        return int(raw)
    return default


def _markable_modules(request):
    """Subjects this user may enter marks for."""
    from apps.learning.models import ProgrammeModule
    flags = role_flags(request)
    qs = ProgrammeModule.objects.select_related('programme', 'module')
    if flags['is_admin_staff']:
        return qs.filter(is_active=True)
    if flags['is_educator']:
        return qs.filter(educators__user=request.user).distinct()
    return qs.none()


def _module_for(request, pk):
    """The subject offering, if this user teaches it (or is admin/staff) — else 404."""
    module = _markable_modules(request).filter(pk=pk).first()
    if module is None:
        raise Http404
    return module


def _check_period(year, term):
    if term not in terms.TERM_NUMBERS or not 2000 <= year <= 2100:
        raise Http404


# ---------------------------------------------------------------------------
# Educator mark sheets
# ---------------------------------------------------------------------------
@login_required
def marks_index(request):
    flags = role_flags(request)
    if not (flags['is_admin_staff'] or flags['is_educator']):
        raise Http404
    year = _year_param(request)
    current_year, current_term = terms.current_year_term()
    modules = _markable_modules(request).order_by('programme__grade', 'programme__order', 'order', 'id')
    grade = (request.GET.get('grade') or '').strip()
    if grade.isdigit():
        modules = modules.filter(programme__grade=int(grade))
    modules = list(modules)
    status = tr.sheet_status(modules, year)
    from apps.learning.models import ModuleEnrolment
    from django.db.models import Count
    enrolled = dict(ModuleEnrolment.objects.filter(programme_module__in=modules)
                    .values('programme_module').annotate(n=Count('person', distinct=True))
                    .values_list('programme_module', 'n'))
    rows = []
    for module in modules:
        cells = []
        for term in terms.TERM_NUMBERS:
            counts = status.get((module.pk, term), {'draft': 0, 'published': 0})
            cells.append({'term': term, 'label': terms.term_label(term),
                          'exam': terms.exam_label(term) if tr.exam_applies(module, term) else '',
                          'draft': counts.get('draft', 0), 'published': counts.get('published', 0),
                          'is_current': year == current_year and term == current_term})
        rows.append({'module': module, 'enrolled': enrolled.get(module.pk, 0), 'cells': cells})
    return render(request, 'reports/marks-index.html', {
        'page_title': 'Mark sheets', 'rows': rows, 'year': year,
        'years': [current_year - 1, current_year, current_year + 1],
        'grade': grade, 'grades': school.GRADES, 'is_admin_staff': flags['is_admin_staff'],
        'term_numbers': terms.TERM_NUMBERS, 'term_labels': terms.TERM_LABELS,
    })


def _sheet_rows(module, year, term, results, posted=None):
    grade = tr.grade_of(module)
    show_exam = tr.exam_applies(module, term)
    rows = []
    for result in results:
        auto_exam = tr.compute_auto_exam(result.student, module, year, term) if show_exam else None
        sid = result.student_id
        rows.append({
            'result': result, 'student': result.student,
            'auto_exam': auto_exam,
            'sba_value': posted.get(f'sba_{sid}', '') if posted is not None else
            ('' if result.sba_pct is None else result.sba_pct),
            'exam_value': posted.get(f'exam_{sid}', '') if posted is not None else
            ('' if result.exam_pct is None else result.exam_pct),
            'comment_value': posted.get(f'comment_{sid}', '') if posted is not None else result.comment,
            'descriptor': tr.level_descriptor(result.level),
        })
    return rows, show_exam, school.sba_weight(grade, module.code)


@login_required
def mark_sheet(request, pk, year, term):
    _check_period(year, term)
    module = _module_for(request, pk)
    results = tr.refresh_term(module, year, term)
    show_exam = tr.exam_applies(module, term)
    posted = None

    if request.method == 'POST':
        action = request.POST.get('action', 'save')
        errors, changes = [], []
        for result in results:
            sid = result.student_id
            name = result.student.get_full_name() or result.student.get_username()
            try:
                sba = tr.parse_pct(request.POST.get(f'sba_{sid}'))
                exam = tr.parse_pct(request.POST.get(f'exam_{sid}')) if show_exam else None
            except ValueError as exc:
                errors.append(f'{name}: {exc}')
                continue
            if show_exam and exam is None:
                auto_exam = tr.compute_auto_exam(result.student, module, year, term)
                if auto_exam is not None:
                    exam = tr._dec(auto_exam)       # blank = accept the online exam paper
            comment = (request.POST.get(f'comment_{sid}') or '').strip()[:2000]
            changes.append((result, sba, exam, comment))
        if errors:
            for error in errors[:10]:
                messages.error(request, error)
            posted = request.POST
        else:
            newly_published = []
            skipped = 0
            for result, sba, exam, comment in changes:
                result.sba_pct, result.exam_pct, result.comment = sba, exam, comment
                result.entered_by = request.user
                result.recompute()
                if action == 'publish':
                    if result.term_pct is None:
                        skipped += 1
                    else:
                        was = result.status
                        tr.publish(result, by=request.user)
                        if was != TermResult.STATUS_PUBLISHED:
                            newly_published.append(result)
                elif action == 'unpublish':
                    result.status = TermResult.STATUS_DRAFT
                    result.published_at = None
                result.save()
            label = f'{module.display_name} · {terms.term_label(term)} {year}'
            if action == 'publish':
                tr.notify_published(newly_published, actor=request.user)
                messages.success(request, f'{label}: {len(newly_published)} result(s) published; '
                                          'learners and parents have been notified.')
                if skipped:
                    messages.warning(request, f'{skipped} learner(s) have no mark yet and were not published.')
            elif action == 'unpublish':
                messages.info(request, f'{label}: results withdrawn to draft — families no longer see them.')
            else:
                messages.success(request, f'{label}: mark sheet saved as draft.')
            return redirect('reports:mark-sheet', pk=module.pk, year=year, term=term)

    rows, show_exam, weight = _sheet_rows(module, year, term, results, posted)
    published = sum(1 for r in results if r.status == TermResult.STATUS_PUBLISHED)
    start, end = terms.term_dates(year, term)
    return render(request, 'reports/mark-sheet.html', {
        'page_title': f'Mark sheet · {module.display_name}',
        'module': module, 'year': year, 'term': term,
        'term_label': terms.term_label(term), 'exam_label': terms.exam_label(term),
        'term_start': start, 'term_end': end,
        'rows': rows, 'show_exam': show_exam, 'sba_weight': weight, 'exam_weight': 100 - weight,
        'published_count': published, 'draft_count': len(results) - published,
        'term_numbers': terms.TERM_NUMBERS,
        'level_bands': [(7, 80), (6, 70), (5, 60), (4, 50), (3, 40), (2, 30), (1, 0)],
    })


@login_required
def mark_sheet_csv(request, pk, year, term):
    _check_period(year, term)
    module = _module_for(request, pk)
    results = tr.refresh_term(module, year, term)
    show_exam = tr.exam_applies(module, term)
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    filename = f'{module.programme.code}-{module.code}-{year}-T{term}.csv'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    writer = csv.writer(response)
    header = ['Learner', 'Email', 'Auto %', 'SBA %']
    if show_exam:
        header.append(f'{terms.exam_label(term)} %')
    header += ['Term mark %', 'Level', 'Descriptor', 'Comment', 'Status']
    writer.writerow(header)
    for r in results:
        row = [r.student.get_full_name() or r.student.get_username(), r.student.email,
               '' if r.auto_pct is None else r.auto_pct, '' if r.sba_pct is None else r.sba_pct]
        if show_exam:
            row.append('' if r.exam_pct is None else r.exam_pct)
        row += ['' if r.term_pct is None else r.term_pct, r.level or '',
                tr.level_descriptor(r.level), r.comment, r.get_status_display()]
        writer.writerow(row)
    return response


# ---------------------------------------------------------------------------
# Report cards
# ---------------------------------------------------------------------------
def _report_target(request):
    """``(learner, published_only, pickable students or None)`` for this user."""
    flags = role_flags(request)
    User = get_user_model()
    if flags['is_admin_staff']:
        students = User.objects.filter(profile__user_type='student', is_active=True).order_by(
            'first_name', 'last_name')
        sid = (request.GET.get('student') or '').strip()
        target = get_object_or_404(students, pk=sid) if sid.isdigit() else None
        return target, False, students
    if flags['is_parent']:
        from core.scoping import children_of
        child = viewing_child(request)
        if child is None:
            raise Http404
        return child, True, children_of(request.user).order_by('first_name', 'last_name')
    if flags['is_educator']:
        return None, True, None
    return request.user, True, None


def _term_attendance(user, year, term):
    """Days present / absent / late for the term from the daily register."""
    person = getattr(user, 'profile', None)
    if person is None:
        return None
    try:
        from apps.attendance.services import learner_summary
    except ImportError:  # pragma: no cover - attendance app not installed
        return None
    start, end = terms.term_dates(year, term)
    summary = learner_summary(person, start=start, end=end)
    return summary if summary.get('total') else None


def report_card_context(request):
    target, published_only, students = _report_target(request)
    year = _year_param(request)
    ctx = {'target': target, 'students': students, 'published_only': published_only,
           'year': year, 'term_numbers': terms.TERM_NUMBERS, 'term_labels': terms.TERM_LABELS}
    if target is None:
        return ctx
    enrolment = tr.programme_for(target, year)
    summary = tr.year_summary(target, year, published_only=published_only)
    visible_terms = sorted({t for s in summary['subjects'] for t, r in s['terms'].items() if r})
    default_term = visible_terms[-1] if visible_terms else terms.current_year_term()[1]
    term = _term_param(request, default_term)
    rows = []
    for subject in summary['subjects']:
        result = subject['terms'].get(term)
        if result is None and term != 4:
            continue
        rows.append({**subject, 'result': result,
                     'term_list': [subject['terms'].get(t) for t in terms.TERM_NUMBERS],
                     'descriptor_term': tr.level_descriptor(result.level) if result else '',
                     'show_exam': tr.exam_applies(subject['module'], term)})
    from core.branding import strings
    years = sorted(set(TermResult.objects.filter(student=target).values_list('year', flat=True))
                   | {terms.current_year_term()[0]}, reverse=True)
    promotion = summary['promotion'] if term == 4 else None
    ctx.update({
        'brand': strings().get('brand', {}),
        'learner_name': target.get_full_name() or target.get_username(),
        'programme': summary['programme'] or (enrolment.programme if enrolment else None),
        'grade': summary['grade'],
        'class_name': (enrolment.cohort.name or enrolment.cohort.code) if enrolment and enrolment.cohort else '',
        'term': term, 'term_label': terms.term_label(term), 'exam_label': terms.exam_label(term),
        'rows': rows, 'has_results': any(r['result'] for r in rows),
        'is_final': term == 4, 'summary': summary, 'promotion': promotion,
        'years': years, 'visible_terms': visible_terms,
        'outcome_label': {'promote': 'Meets the requirements for promotion',
                          'complete': 'Meets the requirements for the National Senior Certificate',
                          'retain': 'Does not yet meet the promotion requirements'}.get(
                              (promotion or {}).get('outcome'), ''),
        'scale': [(int(b['letter']), b['min'], b['label']) for b in tr.DEFAULT_GRADE_SCALE],
        # The National Protocol for Assessment: a term report shows days absent.
        'attendance': _term_attendance(target, year, term),
        'today': datetime.date.today(),
    })
    return ctx


@login_required
def report_card(request):
    flags = role_flags(request)
    if flags['is_educator'] and not flags['is_admin_staff']:
        return redirect('reports:marks')
    ctx = report_card_context(request)
    ctx['page_title'] = 'Report card'
    return render(request, 'reports/report-card.html', ctx)


@login_required
def report_card_pdf(request):
    flags = role_flags(request)
    if flags['is_educator'] and not flags['is_admin_staff']:
        raise Http404
    ctx = report_card_context(request)
    if ctx.get('target') is None:
        raise Http404
    if ctx.get('promotion'):
        # The PDF's built-in Helvetica has no '≥' glyph.
        ctx['promotion'] = dict(ctx['promotion'], checks=[
            (label.replace('≥', '>='), met, detail) for label, met, detail in ctx['promotion']['checks']])
    import io
    from django.template.loader import render_to_string
    try:
        from xhtml2pdf import pisa

        from apps.finance.pdf import _link_callback
        html = render_to_string('reports/report-card-pdf.html', ctx, request=request)
        buf = io.BytesIO()
        result = pisa.CreatePDF(html, dest=buf, link_callback=_link_callback)
        if result.err:
            raise RuntimeError('xhtml2pdf reported errors')
    except Exception:
        import logging
        logging.getLogger('apps').exception('reports: report card PDF failed')
        messages.error(request, 'The PDF could not be produced just now — use Print instead.')
        return redirect(reverse('reports:report-card') + '?' + request.GET.urlencode())
    response = HttpResponse(buf.getvalue(), content_type='application/pdf')
    name = ctx['learner_name'].replace(' ', '-')
    response['Content-Disposition'] = f'attachment; filename="Report-{name}-{ctx["year"]}-T{ctx["term"]}.pdf"'
    return response


# ---------------------------------------------------------------------------
# Office overview
# ---------------------------------------------------------------------------
@login_required
def term_overview(request):
    flags = role_flags(request)
    if not flags['is_admin_staff']:
        raise Http404
    from django.db.models import Count

    from apps.learning.models import ModuleEnrolment, ProgrammeModule
    year = _year_param(request)
    current_year, current_term = terms.current_year_term()
    modules = list(ProgrammeModule.objects.filter(is_active=True)
                   .select_related('programme', 'module')
                   .prefetch_related('educators')
                   .order_by('programme__grade', 'programme__order', 'order', 'id'))
    status = tr.sheet_status(modules, year)
    enrolled = dict(ModuleEnrolment.objects.filter(programme_module__in=modules)
                    .values('programme_module').annotate(n=Count('person', distinct=True))
                    .values_list('programme_module', 'n'))
    grades, totals = {}, {t: {'published': 0, 'draft': 0, 'missing': 0} for t in terms.TERM_NUMBERS}
    for module in modules:
        n = enrolled.get(module.pk, 0)
        cells = []
        for term in terms.TERM_NUMBERS:
            counts = status.get((module.pk, term), {})
            pub, draft = counts.get('published', 0), counts.get('draft', 0)
            missing = max(0, n - pub - draft)
            state = ('none' if n == 0 else 'done' if pub >= n else
                     'partial' if pub or draft else 'outstanding')
            cells.append({'term': term, 'published': pub, 'draft': draft, 'missing': missing,
                          'state': state})
            totals[term]['published'] += pub
            totals[term]['draft'] += draft
            totals[term]['missing'] += missing
        key = module.programme.grade or 0
        grades.setdefault(key, {'programme': module.programme, 'rows': []})['rows'].append({
            'module': module, 'enrolled': n, 'cells': cells,
            'educators': ', '.join(p.user.get_full_name() or p.user.email
                                   for p in module.educators.all() if getattr(p, 'user', None)),
        })
    return render(request, 'reports/term-overview.html', {
        'page_title': 'Term reports', 'year': year,
        'years': [current_year - 1, current_year, current_year + 1],
        'grades': [grades[k] for k in sorted(grades)],
        'totals': [dict(term=t, label=terms.term_label(t), **totals[t]) for t in terms.TERM_NUMBERS],
        'current_term': current_term if year == current_year else None,
        'term_numbers': terms.TERM_NUMBERS, 'term_labels': terms.TERM_LABELS,
    })
