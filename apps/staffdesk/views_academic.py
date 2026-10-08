"""/staff/ — the academic pages: grades & certificates, at-risk students,
content imports and the AI reports archive.

Everything here used to need Django admin or a shell. The pages are thin: the
real work stays in the services that already own it —
:mod:`apps.reports.services` for marks and certificates,
:func:`apps.analytics.services.compute_risk` for risk, the ``learning``
management commands for imports and
:func:`apps.communication.services.notify` for telling people — so a change
made here behaves exactly as the same change made anywhere else.

Admin and staff only (:func:`~apps.staffdesk.access.staff_required`); every
state change is a POST.
"""

import io
import json
import logging
import threading
import sys
import traceback
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.management import CommandError, call_command
from django.core.paginator import Paginator
from django.core.serializers.json import DjangoJSONEncoder
from django.db import connections, transaction
from django.db.models import Avg, Count, F, Max, Q
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.ai_assistant.models import AiInsight, AiReport
from apps.analytics.models import ReportSnapshot, RiskFlag
from apps.learning.models import ModuleEnrolment, Programme, ProgrammeModule
from apps.reports import services as report_services
from apps.reports.models import Certificate, Grade, ModuleWeighting
from core.utils import display_name

from . import forms_academic as forms
from .access import staff_required
from .models import ImportRun, RiskTriage

logger = logging.getLogger('apps')
User = get_user_model()

PAGE_SIZE = 50


def _page(request, qs, size=PAGE_SIZE):
    return Paginator(qs, size).get_page(request.GET.get('page'))


def _query_without_page(request, *also):
    """The current filters as a query string, minus ``page`` (and ``also``) —
    for pager and tab links that must keep every other filter."""
    params = request.GET.copy()
    for key in ('page',) + also:
        params.pop(key, None)
    return params.urlencode()


def _offerings():
    return (ProgrammeModule.objects.filter(is_active=True)
            .select_related('programme__institution').order_by('programme__code', 'code'))


def _int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _next(request, fallback):
    """Return to the page the action came from, if it is one of ours."""
    target = request.POST.get('next') or ''
    if target.startswith('/staff/'):
        return redirect(target)
    return redirect(fallback)


# ===========================================================================
# Grades
# ===========================================================================
@staff_required
def grades(request):
    """Every computed grade, filterable by programme, module and student."""
    qs = Grade.objects.select_related('student', 'module__programme__institution', 'overridden_by')

    programme_id = _int(request.GET.get('programme'))
    module_id = _int(request.GET.get('module'))
    student_id = _int(request.GET.get('student'))
    search = (request.GET.get('q') or '').strip()
    tab = request.GET.get('tab') or 'all'

    if programme_id:
        qs = qs.filter(module__programme_id=programme_id)
    if module_id:
        qs = qs.filter(module_id=module_id)
    if student_id:
        qs = qs.filter(student_id=student_id)
    if search:
        qs = qs.filter(Q(student__first_name__icontains=search) | Q(student__last_name__icontains=search)
                       | Q(student__email__icontains=search))

    stats = qs.aggregate(n=Count('id'), passed=Count('id', filter=Q(passed=True)),
                         overridden=Count('id', filter=Q(override_pct__isnull=False)),
                         avg=Avg('final_pct'))
    counts = {'all': stats['n'], 'passed': stats['passed'], 'failed': stats['n'] - stats['passed'],
              'overridden': stats['overridden']}
    if tab == 'passed':
        qs = qs.filter(passed=True)
    elif tab == 'failed':
        qs = qs.filter(passed=False)
    elif tab == 'overridden':
        qs = qs.filter(override_pct__isnull=False)
    else:
        tab = 'all'

    modules = _offerings()
    if programme_id:
        modules = modules.filter(programme_id=programme_id)

    return render(request, 'staffdesk/academic/grades.html', {
        'page_title': 'Grades',
        'page': _page(request, qs.order_by('module__programme__code', 'module__code', '-final_pct')),
        'query': _query_without_page(request),
        'filter_query': _query_without_page(request, 'tab'),
        'tab': tab, 'counts': counts,
        'pass_rate': round(stats['passed'] / stats['n'] * 100) if stats['n'] else None,
        'average': stats['avg'],
        'programmes': Programme.objects.filter(is_active=True).select_related('institution').order_by('code'),
        'modules': modules,
        'programme_id': programme_id, 'module_id': module_id, 'student_id': student_id,
        'student': User.objects.filter(pk=student_id).first() if student_id else None,
        'search': search,
        'selected_module': ProgrammeModule.objects.filter(pk=module_id).first() if module_id else None,
    })


@staff_required
def grade_detail(request, pk):
    grade = get_object_or_404(
        Grade.objects.select_related('student', 'module__programme__institution', 'overridden_by'), pk=pk)
    weighting = ModuleWeighting.objects.filter(module_id=grade.module_id).first()
    certificate = Certificate.objects.filter(student=grade.student, module_id=grade.module_id,
                                             kind='module').first()
    initial = {'value': grade.override_pct if grade.is_overridden else grade.final_pct,
               'reason': grade.override_reason}
    return render(request, 'staffdesk/academic/grade-detail.html', {
        'page_title': f'Grade · {display_name(grade.student)}',
        'grade': grade, 'weighting': weighting, 'certificate': certificate,
        'form': forms.GradeOverrideForm(initial=initial),
        'components': sorted((grade.components or {}).items()),
    })


@staff_required
@require_POST
def grade_recompute(request, pk):
    grade = get_object_or_404(Grade.objects.select_related('student', 'module'), pk=pk)
    if grade.module_id is None:
        messages.error(request, 'This mark is not attached to a subject, so there is nothing to recompute.')
        return redirect('staffdesk:grade-detail', pk=pk)
    report_services.compute_grade(grade.student, grade.module)
    report_services.rank_module(grade.module)
    messages.success(request, 'Grade recomputed from the latest marks.')
    return _next(request, reverse('staffdesk:grade-detail', args=[pk]))


@staff_required
@require_POST
def grade_override(request, pk):
    grade = get_object_or_404(Grade.objects.select_related('student', 'module'), pk=pk)
    form = forms.GradeOverrideForm(request.POST)
    if not form.is_valid():
        for errors in form.errors.values():
            messages.error(request, errors[0])
        return redirect('staffdesk:grade-detail', pk=pk)
    grade = report_services.override_grade(grade, value=form.cleaned_data['value'],
                                           reason=form.cleaned_data['reason'], by=request.user)
    messages.success(request, f'Final mark set to {grade.final_pct}% ({grade.letter}). '
                              f'The computed mark ({grade.computed_pct}%) is kept alongside.')
    return redirect('staffdesk:grade-detail', pk=pk)


@staff_required
@require_POST
def grade_override_clear(request, pk):
    grade = get_object_or_404(Grade.objects.select_related('student', 'module'), pk=pk)
    grade = report_services.clear_override(grade)
    messages.success(request, f'Override cleared — the final mark is the computed {grade.final_pct}% again.')
    return redirect('staffdesk:grade-detail', pk=pk)


@staff_required
@require_POST
def grades_recompute_module(request):
    """Recompute every enrolled (or already graded) student in one module."""
    module = get_object_or_404(ProgrammeModule, pk=_int(request.POST.get('module')))
    users = set(ModuleEnrolment.objects.filter(programme_module=module)
                .values_list('person__user_id', flat=True))
    users |= set(Grade.objects.filter(module=module).values_list('student_id', flat=True))
    users.discard(None)
    for student in User.objects.filter(pk__in=users):
        report_services.compute_grade(student, module)
    report_services.rank_module(module)
    messages.success(request, f'Recomputed {len(users)} grade{"s" if len(users) != 1 else ""} '
                              f'for {module.reference}.')
    return _next(request, f"{reverse('staffdesk:grades')}?module={module.pk}")


# ---------------------------------------------------------------------------
# Module weightings
# ---------------------------------------------------------------------------
@staff_required
def weightings(request):
    programme_id = _int(request.GET.get('programme'))
    qs = _offerings().select_related('weighting').annotate(n_grades=Count('grades'))
    if programme_id:
        qs = qs.filter(programme_id=programme_id)
    return render(request, 'staffdesk/academic/weightings.html', {
        'page_title': 'Module weightings',
        'page': _page(request, qs),
        'query': _query_without_page(request),
        'programmes': Programme.objects.filter(is_active=True).select_related('institution').order_by('code'),
        'programme_id': programme_id,
    })


@staff_required
def weighting_edit(request, module_id):
    module = get_object_or_404(_offerings(), pk=module_id)
    instance = ModuleWeighting.objects.filter(module=module).first() or ModuleWeighting(module=module)
    if request.method == 'POST':
        form = forms.ModuleWeightingForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            if request.POST.get('recompute'):
                graded = User.objects.filter(grades__module=module).distinct()
                for student in graded:
                    report_services.compute_grade(student, module)
                report_services.rank_module(module)
                messages.success(request, f'Weighting saved and {graded.count()} grade(s) recomputed.')
            else:
                messages.success(request, 'Weighting saved. Grades pick it up the next time they are computed.')
            return redirect('staffdesk:weightings')
    else:
        form = forms.ModuleWeightingForm(instance=instance)
    return render(request, 'staffdesk/academic/weighting-form.html', {
        'page_title': f'Weighting · {module.reference}',
        'module': module, 'form': form, 'is_new': instance.pk is None,
        'n_grades': Grade.objects.filter(module=module).count(),
        'default_scale': forms.pretty_json(report_services.models.DEFAULT_GRADE_SCALE),
    })


# ===========================================================================
# Certificates
# ===========================================================================
@staff_required
def certificates(request):
    qs = Certificate.objects.select_related('student', 'module__programme__institution', 'revoked_by')
    search = (request.GET.get('q') or '').strip()
    kind = request.GET.get('kind') or ''
    tab = request.GET.get('tab') or 'valid'
    if search:
        qs = qs.filter(Q(number__icontains=search) | Q(title__icontains=search)
                       | Q(student__first_name__icontains=search) | Q(student__last_name__icontains=search)
                       | Q(student__email__icontains=search))
    if kind in dict(Certificate.KIND_CHOICES):
        qs = qs.filter(kind=kind)
    counts = qs.aggregate(all=Count('id'), revoked=Count('id', filter=Q(revoked_at__isnull=False)))
    counts['valid'] = counts['all'] - counts['revoked']
    if tab == 'revoked':
        qs = qs.filter(revoked_at__isnull=False)
    elif tab == 'all':
        pass
    else:
        tab = 'valid'
        qs = qs.filter(revoked_at__isnull=True)
    month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    return render(request, 'staffdesk/academic/certificates.html', {
        'page_title': 'Certificates',
        'page': _page(request, qs.order_by('-issued_at')),
        'query': _query_without_page(request),
        'filter_query': _query_without_page(request, 'tab'),
        'tab': tab, 'counts': counts, 'search': search, 'kind': kind,
        'kinds': Certificate.KIND_CHOICES,
        'issued_month': Certificate.objects.filter(issued_at__gte=month_start).count(),
    })


def _programme_mark(student, programme):
    """Average final mark across the student's graded modules on ``programme``."""
    avg = Grade.objects.filter(student=student, module__programme=programme).aggregate(a=Avg('final_pct'))['a']
    return float(avg or 0)


@staff_required
def certificate_issue(request):
    initial = {}
    for name in ('student', 'module', 'programme', 'kind'):
        if request.GET.get(name):
            initial[name] = request.GET[name]
    form = forms.CertificateIssueForm(request.POST or None, initial=initial)
    if request.method == 'POST' and form.is_valid():
        d = form.cleaned_data
        student = d['student']
        if d['kind'] == 'module':
            module = d['module']
            existing = Certificate.objects.filter(student=student, module=module, kind='module').first()
            if existing:
                messages.warning(request, f'{display_name(student)} already holds {existing.number} for '
                                          f'{module.reference}. Regenerate it instead to refresh the mark.')
                return redirect(f"{reverse('staffdesk:certificates')}?q={existing.number}&tab=all")
            mark = d['final_mark']
            if mark is None:
                grade = Grade.objects.filter(student=student, module=module).first()
                mark = grade.final_pct if grade else 0
            cert = report_services.issue_certificate(
                student, module=module, kind='module',
                title=d['title'] or f'Subject Completion — {module}', final_mark=mark)
        else:
            programme = d['programme']
            # issue_certificate is idempotent per student + module + kind, and a
            # programme certificate has no module — so a student can hold one.
            existing = Certificate.objects.filter(student=student, module=None, kind='programme').first()
            if existing:
                messages.warning(request, f'{display_name(student)} already holds a grade certificate '
                                          f'({existing.number} — {existing.title}).')
                return redirect(f"{reverse('staffdesk:certificates')}?q={existing.number}&tab=all")
            mark = d['final_mark'] if d['final_mark'] is not None else _programme_mark(student, programme)
            cert = report_services.issue_certificate(
                student, module=None, kind='programme',
                title=d['title'] or f'Grade Completion — {programme.display_name}', final_mark=mark)
        messages.success(request, f'Certificate {cert.number} issued to {display_name(student)}.')
        return redirect(f"{reverse('staffdesk:certificates')}?q={cert.number}")
    return render(request, 'staffdesk/academic/certificate-issue.html', {
        'page_title': 'Issue a certificate', 'form': form,
    })


@staff_required
@require_POST
def certificate_revoke(request, pk):
    cert = get_object_or_404(Certificate, pk=pk)
    reason = (request.POST.get('reason') or '').strip()
    if not reason:
        messages.error(request, 'Say why the certificate is being revoked.')
    else:
        report_services.revoke_certificate(cert, reason=reason, by=request.user)
        messages.success(request, f'{cert.number} revoked. The verification page now says so.')
    return _next(request, 'staffdesk:certificates')


@staff_required
@require_POST
def certificate_reinstate(request, pk):
    cert = get_object_or_404(Certificate, pk=pk)
    report_services.reinstate_certificate(cert)
    messages.success(request, f'{cert.number} reinstated.')
    return _next(request, 'staffdesk:certificates')


@staff_required
@require_POST
def certificate_regenerate(request, pk):
    """Refresh the mark from the current grade and drop the cached PDF.

    The number and verification link are kept — a reprint, not a new award —
    and the next download renders the PDF afresh
    (:func:`apps.reports.certificates.ensure_pdf`).
    """
    cert = get_object_or_404(Certificate.objects.select_related('module'), pk=pk)
    fields = []
    if cert.module_id:
        grade = Grade.objects.filter(student_id=cert.student_id, module_id=cert.module_id).first()
        if grade and grade.final_pct != cert.final_mark:
            cert.final_mark = grade.final_pct
            fields.append('final_mark')
    if cert.pdf:
        cert.pdf.delete(save=False)
        cert.pdf = None
        fields.append('pdf')
    if fields:
        cert.save(update_fields=fields)
    messages.success(request, f'{cert.number} regenerated — the next download is freshly rendered.')
    return _next(request, 'staffdesk:certificates')


# ===========================================================================
# At-risk students
# ===========================================================================
#: Scores at or above this open (or refresh) a flag on a risk scan.
RISK_THRESHOLD = 30


def severity_of(score):
    """(label, chip variant) for a 0–100 risk score."""
    if score >= 70:
        return 'High', 'danger'
    if score >= 40:
        return 'Medium', 'warning'
    return 'Low', 'primary'


def _with_triage_state(qs):
    """Annotate when each flag was last acknowledged / reopened.

    A flag counts as acknowledged when it was acknowledged after it was last
    reopened, so reopening puts it back in the open queue.
    """
    return qs.annotate(
        last_ack=Max('triage__at', filter=Q(triage__action=RiskTriage.ACTION_ACK)),
        last_reopen=Max('triage__at', filter=Q(triage__action=RiskTriage.ACTION_REOPEN)),
        n_notes=Count('triage', filter=Q(triage__action=RiskTriage.ACTION_NOTE)),
    )


def _is_acknowledged(flag):
    return bool(flag.last_ack and (not flag.last_reopen or flag.last_ack > flag.last_reopen))


ACKED = Q(last_ack__isnull=False) & (Q(last_reopen__isnull=True) | Q(last_ack__gt=F('last_reopen')))


def scan_risk():
    """Score every active student with :func:`compute_risk` and open or refresh
    their flag. Returns ``(opened, refreshed)``.

    One open, module-less flag per student: a rescan updates its score and
    reasons rather than stacking duplicates. Flags are never closed here —
    resolving is a person's call.
    """
    from apps.analytics.services import compute_risk

    opened = refreshed = 0
    students = User.objects.filter(profile__user_type='student', is_active=True)
    for student in students.iterator():
        score, reasons = compute_risk(student)
        if score < RISK_THRESHOLD:
            continue
        flag = RiskFlag.objects.filter(student=student, module=None, resolved=False).first()
        if flag:
            if flag.score != score or flag.reasons != reasons:
                flag.score, flag.reasons = score, reasons
                flag.save(update_fields=['score', 'reasons'])
                refreshed += 1
        else:
            RiskFlag.objects.create(student=student, score=score, reasons=reasons)
            opened += 1
    return opened, refreshed


@staff_required
def at_risk(request):
    base = _with_triage_state(RiskFlag.objects.select_related('student', 'module__programme__institution'))
    module_id = _int(request.GET.get('module'))
    search = (request.GET.get('q') or '').strip()
    level = request.GET.get('severity') or ''
    if module_id:
        base = base.filter(module_id=module_id)
    if search:
        base = base.filter(Q(student__first_name__icontains=search) | Q(student__last_name__icontains=search)
                           | Q(student__email__icontains=search))
    if level == 'high':
        base = base.filter(score__gte=70)
    elif level == 'medium':
        base = base.filter(score__gte=40, score__lt=70)
    elif level == 'low':
        base = base.filter(score__lt=40)

    unresolved = base.filter(resolved=False)
    queues = {
        'open': unresolved.exclude(ACKED),
        'acknowledged': unresolved.filter(ACKED),
        'resolved': base.filter(resolved=True),
        'all': base,
    }
    tab = request.GET.get('tab') if request.GET.get('tab') in queues else 'open'
    counts = {name: q.count() for name, q in queues.items()}

    page = _page(request, queues[tab].order_by('resolved', '-score', '-created_at'))
    for flag in page:
        flag.severity, flag.severity_variant = severity_of(flag.score)
        flag.acknowledged = _is_acknowledged(flag)

    month_ago = timezone.now() - timedelta(days=30)
    return render(request, 'staffdesk/academic/at-risk.html', {
        'page_title': 'At-risk students',
        'page': page, 'query': _query_without_page(request),
        'filter_query': _query_without_page(request, 'tab'),
        'tab': tab, 'counts': counts,
        'kpis': {
            'high': RiskFlag.objects.filter(resolved=False, score__gte=70).count(),
            'open': RiskFlag.objects.filter(resolved=False).count(),
            'resolved_30d': RiskTriage.objects.filter(action=RiskTriage.ACTION_RESOLVE,
                                                      at__gte=month_ago).values('flag').distinct().count(),
        },
        'modules': _offerings(), 'module_id': module_id, 'search': search, 'severity': level,
        'threshold': RISK_THRESHOLD,
    })


@staff_required
@require_POST
def at_risk_scan(request):
    opened, refreshed = scan_risk()
    messages.success(request, f'Risk scan finished: {opened} new flag{"s" if opened != 1 else ""}, '
                              f'{refreshed} refreshed.')
    return redirect('staffdesk:at-risk')


def _educators_for(flag):
    """Who teaches this student: the flag's module, else every module they are on."""
    if flag.module_id:
        modules = ProgrammeModule.objects.filter(pk=flag.module_id)
    else:
        modules = ProgrammeModule.objects.filter(
            enrolments__person__user=flag.student,
            enrolments__status__in=[ModuleEnrolment.STATUS_ACTIVE, ModuleEnrolment.STATUS_TRIAL])
    return (User.objects.filter(profile__taught_modules__in=modules, is_active=True)
            .distinct().order_by('first_name', 'last_name'))


def _default_messages(flag):
    student = display_name(flag.student)
    reasons = '; '.join(flag.reasons or []) or 'recent activity'
    where = f' in {flag.module.reference}' if flag.module_id else ''
    return {
        'student': {'title': 'Checking in on your progress',
                    'body': f'Hi {student}, we noticed you might be falling behind{where}. '
                            'If anything is getting in the way, reply or book a session — we are here to help.'},
        'educator': {'title': f'{student} may need support',
                     'body': f'{student} has been flagged as at risk{where} ({reasons}). '
                             'Could you check in with them?'},
    }


@staff_required
def at_risk_detail(request, pk):
    flag = get_object_or_404(
        _with_triage_state(RiskFlag.objects.select_related('student', 'module__programme__institution')), pk=pk)
    flag.severity, flag.severity_variant = severity_of(flag.score)
    acknowledged = _is_acknowledged(flag)
    defaults = _default_messages(flag)
    return render(request, 'staffdesk/academic/at-risk-detail.html', {
        'page_title': f'At risk · {display_name(flag.student)}',
        'flag': flag, 'acknowledged': acknowledged,
        'log': flag.triage.select_related('by'),
        'grades': Grade.objects.filter(student=flag.student).select_related('module__programme__institution'),
        'educators': _educators_for(flag),
        'student_form': forms.NotifyForm(initial=defaults['student'], prefix='student'),
        'educator_form': forms.NotifyForm(initial=defaults['educator'], prefix='educator'),
        'compose_url': f"{reverse('communication:announcement-compose')}?user={flag.student_id}",
        'other_flags': RiskFlag.objects.filter(student=flag.student).exclude(pk=flag.pk).order_by('-created_at')[:10],
    })


@staff_required
@require_POST
def at_risk_triage(request, pk):
    flag = get_object_or_404(RiskFlag, pk=pk)
    form = forms.TriageForm(request.POST)
    if not form.is_valid():
        for errors in form.errors.values():
            messages.error(request, errors[0])
        return _next(request, reverse('staffdesk:at-risk-detail', args=[pk]))
    action, note = form.cleaned_data['action'], form.cleaned_data['note'].strip()
    if action == RiskTriage.ACTION_RESOLVE:
        flag.resolved = True
        flag.save(update_fields=['resolved'])
    elif action == RiskTriage.ACTION_REOPEN:
        flag.resolved = False
        flag.save(update_fields=['resolved'])
    RiskTriage.objects.create(flag=flag, action=action, note=note, by=request.user)
    messages.success(request, {
        'ack': 'Acknowledged.', 'resolve': 'Marked resolved.', 'reopen': 'Reopened.', 'note': 'Note added.',
    }[action])
    return _next(request, reverse('staffdesk:at-risk-detail', args=[pk]))


@staff_required
@require_POST
def at_risk_notify(request, pk, who):
    from apps.communication.services import notify

    flag = get_object_or_404(RiskFlag.objects.select_related('student', 'module'), pk=pk)
    if who not in ('student', 'educator'):
        raise Http404
    defaults = _default_messages(flag)[who]
    form = forms.NotifyForm(request.POST, prefix=who)
    title, body = ((form.cleaned_data['title'], form.cleaned_data['body']) if form.is_valid()
                   else (defaults['title'], defaults['body']))

    if who == 'student':
        notify(flag.student, title=title, body=body, url=reverse('reports:my-progress'),
               category='grades', email=True, actor=request.user)
        recipients = [flag.student]
        action = RiskTriage.ACTION_NOTIFY_STUDENT
    else:
        recipients = list(_educators_for(flag))
        if not recipients:
            messages.error(request, 'No educator teaches this student, so there was nobody to tell.')
            return _next(request, reverse('staffdesk:at-risk-detail', args=[pk]))
        url = f"{reverse('reports:my-progress')}?student={flag.student_id}"
        for educator in recipients:
            notify(educator, title=title, body=body, url=url, category=None, email=True, actor=request.user)
        action = RiskTriage.ACTION_NOTIFY_EDUCATOR

    names = ', '.join(display_name(u) for u in recipients)
    RiskTriage.objects.create(flag=flag, action=action, note=f'{title} → {names}', by=request.user)
    messages.success(request, f'Notified {names}.')
    return _next(request, reverse('staffdesk:at-risk-detail', args=[pk]))


# ---------------------------------------------------------------------------
# Report snapshots
# ---------------------------------------------------------------------------
@staff_required
def snapshots(request):
    qs = ReportSnapshot.objects.all()
    period = request.GET.get('period') or ''
    if period in dict(ReportSnapshot.PERIOD_CHOICES):
        qs = qs.filter(period=period)
    return render(request, 'staffdesk/academic/snapshots.html', {
        'page_title': 'Report snapshots',
        'page': _page(request, qs), 'query': _query_without_page(request),
        'period': period, 'periods': ReportSnapshot.PERIOD_CHOICES,
    })


@staff_required
@require_POST
def snapshot_take(request):
    """Freeze today's institution dashboard into a snapshot."""
    from apps.analytics.services import institution_dashboard

    period = request.POST.get('period')
    if period not in dict(ReportSnapshot.PERIOD_CHOICES):
        period = 'monthly'
    # Round-trip through JSON so Decimals and dates store cleanly in the JSONField.
    data = json.loads(json.dumps(institution_dashboard(), cls=DjangoJSONEncoder))
    snap = ReportSnapshot.objects.create(scope='institution', period=period, data=data)
    messages.success(request, 'Snapshot saved.')
    return redirect('staffdesk:snapshot-detail', pk=snap.pk)


@staff_required
def snapshot_detail(request, pk):
    snap = get_object_or_404(ReportSnapshot, pk=pk)
    data = snap.data if isinstance(snap.data, dict) else {}
    # The headline numbers, when the snapshot is an institution dashboard; the
    # raw JSON is always shown underneath for anything else.
    students = data.get('students') if isinstance(data.get('students'), dict) else {}
    tiles = [(label, value) for label, value in [
        ('Students', students.get('total')), ('Active', students.get('active')),
        ('Logged in this week', students.get('logged_week')),
        ('Modules', data.get('total_modules')), ('Lessons', data.get('total_lessons')),
        ('Certificates issued', data.get('certificates_issued')),
    ] if value is not None]
    modules = data.get('modules') if isinstance(data.get('modules'), list) else []
    return render(request, 'staffdesk/academic/snapshot-detail.html', {
        'page_title': f'Snapshot · {snap}',
        'snap': snap, 'tiles': tiles,
        'module_rows': [m for m in modules if isinstance(m, dict)],
        'raw': forms.pretty_json(snap.data),
    })


# ===========================================================================
# Content imports
# ===========================================================================
#: Tests switch this off to run commands inline, inside the test transaction.
RUN_IN_THREAD = True
#: An active run older than this was cut off (a restart, a killed worker).
STALE_AFTER = timedelta(hours=6)
MAX_OUTPUT = 200_000


def _execute(run_id):
    """Run one :class:`ImportRun` to completion, capturing everything it prints."""
    run = ImportRun.objects.get(pk=run_id)
    run.status = ImportRun.STATUS_RUNNING
    run.save(update_fields=['status'])
    buf = io.StringIO()
    status = ImportRun.STATUS_OK
    try:
        call_command(run.command, *run.args, stdout=buf, stderr=buf)
    except CommandError as exc:
        buf.write(f'\nError: {exc}\n')
        status = ImportRun.STATUS_FAILED
    except BaseException:  # noqa: BLE001 — SystemExit from argparse included
        buf.write('\n' + traceback.format_exc())
        status = ImportRun.STATUS_FAILED
        logger.exception('staffdesk: import run %s failed', run_id)
        from core.errors import report
        report('DESK-9003', sys.exc_info()[1], context={'run': run_id, 'command': run.command})
    output = buf.getvalue()
    if len(output) > MAX_OUTPUT:
        output = output[:MAX_OUTPUT] + '\n… output truncated …'
    ImportRun.objects.filter(pk=run_id).update(status=status, output=output, finished_at=timezone.now())


def _execute_in_thread(run_id):
    try:
        _execute(run_id)
    finally:
        connections.close_all()


def start_run(command, argv, user):
    run = ImportRun.objects.create(command=command, args=argv, started_by=user)
    if RUN_IN_THREAD:
        transaction.on_commit(lambda: threading.Thread(
            target=_execute_in_thread, args=(run.pk,), daemon=True, name=f'import-run-{run.pk}').start())
    else:
        _execute(run.pk)
    return run


def _mark_stale_runs():
    cutoff = timezone.now() - STALE_AFTER
    ImportRun.objects.filter(status__in=[ImportRun.STATUS_QUEUED, ImportRun.STATUS_RUNNING],
                             started_at__lt=cutoff).update(
        status=ImportRun.STATUS_FAILED, finished_at=timezone.now())


@staff_required
def imports(request):
    _mark_stale_runs()
    cards = []
    for name, (form_class, title, blurb, icon) in forms.IMPORT_COMMANDS.items():
        cards.append({'name': name, 'title': title, 'blurb': blurb, 'icon': icon,
                      'form': form_class(prefix=name),
                      'active': ImportRun.objects.filter(command=name, status__in=[
                          ImportRun.STATUS_QUEUED, ImportRun.STATUS_RUNNING]).first()})
    return render(request, 'staffdesk/academic/imports.html', {
        'page_title': 'Content imports',
        'cards': cards,
        'runs': ImportRun.objects.select_related('started_by')[:30],
        'seed_packs': forms.seed_pack_names(),
        'source_roots': [forms._relative(r) for r in forms.source_roots()],
    })


@staff_required
@require_POST
def import_run(request, command):
    if command not in forms.IMPORT_COMMANDS:
        raise Http404
    form = forms.IMPORT_COMMANDS[command][0](request.POST, prefix=command)
    if not form.is_valid():
        for field, errors in form.errors.items():
            messages.error(request, f'{field}: {errors[0]}' if field != '__all__' else errors[0])
        return redirect('staffdesk:imports')
    if ImportRun.objects.filter(command=command, status__in=[ImportRun.STATUS_QUEUED,
                                                             ImportRun.STATUS_RUNNING]).exists():
        messages.warning(request, f'{command} is already running — wait for it to finish.')
        return redirect('staffdesk:imports')
    run = start_run(command, form.argv(), request.user)
    messages.success(request, f'{command} started.')
    return redirect('staffdesk:import-run-detail', pk=run.pk)


@staff_required
def import_run_detail(request, pk):
    run = get_object_or_404(ImportRun.objects.select_related('started_by'), pk=pk)
    return render(request, 'staffdesk/academic/import-run.html', {
        'page_title': f'Run · {run.command}', 'run': run,
    })


@staff_required
def import_run_status(request, pk):
    run = get_object_or_404(ImportRun, pk=pk)
    return JsonResponse({'status': run.status, 'label': run.get_status_display(),
                         'active': run.is_active, 'output': run.output})


# ===========================================================================
# AI reports & insights
# ===========================================================================
@staff_required
def ai_reports(request):
    qs = AiReport.objects.select_related('module__programme__institution', 'student', 'created_by')
    kind = request.GET.get('kind') or ''
    status = request.GET.get('status') or ''
    module_id = _int(request.GET.get('module'))
    search = (request.GET.get('q') or '').strip()
    if kind in dict(AiReport.KIND_CHOICES):
        qs = qs.filter(kind=kind)
    if status in dict(AiReport.STATUS_CHOICES):
        qs = qs.filter(status=status)
    if module_id:
        qs = qs.filter(module_id=module_id)
    if search:
        qs = qs.filter(Q(title__icontains=search) | Q(content__icontains=search))
    return render(request, 'staffdesk/academic/ai-reports.html', {
        'page_title': 'AI reports',
        'page': _page(request, qs), 'query': _query_without_page(request),
        'kinds': AiReport.KIND_CHOICES, 'statuses': AiReport.STATUS_CHOICES,
        'kind': kind, 'status': status, 'module_id': module_id, 'search': search,
        'modules': _offerings(),
        'counts': {'reports': AiReport.objects.count(),
                   'insights': AiInsight.objects.filter(status=AiInsight.STATUS_NEW).count()},
        'section': 'reports',
    })


@staff_required
def ai_report_detail(request, pk):
    report = get_object_or_404(
        AiReport.objects.select_related('module__programme__institution', 'student', 'created_by'), pk=pk)
    return render(request, 'staffdesk/academic/ai-report-detail.html', {
        'page_title': report.title, 'report': report,
        'data': forms.pretty_json(report.data) if report.data else '',
    })


@staff_required
def ai_insights(request):
    qs = AiInsight.objects.select_related('module__programme__institution', 'student', 'owner')
    severity = request.GET.get('severity') or ''
    status = request.GET.get('status') or ''
    kind = request.GET.get('kind') or ''
    search = (request.GET.get('q') or '').strip()
    if severity in dict(AiInsight.SEVERITY_CHOICES):
        qs = qs.filter(severity=severity)
    if status in dict(AiInsight.STATUS_CHOICES):
        qs = qs.filter(status=status)
    if kind:
        qs = qs.filter(kind=kind)
    if search:
        qs = qs.filter(Q(title__icontains=search) | Q(body__icontains=search))
    return render(request, 'staffdesk/academic/ai-insights.html', {
        'page_title': 'AI insights',
        'page': _page(request, qs), 'query': _query_without_page(request),
        'severities': AiInsight.SEVERITY_CHOICES, 'statuses': AiInsight.STATUS_CHOICES,
        'kinds': list(AiInsight.objects.order_by('kind').values_list('kind', flat=True).distinct()),
        'severity': severity, 'status': status, 'kind': kind, 'search': search,
        'counts': {'reports': AiReport.objects.count(),
                   'insights': AiInsight.objects.filter(status=AiInsight.STATUS_NEW).count()},
        'section': 'insights',
    })


@staff_required
def ai_insight_detail(request, pk):
    insight = get_object_or_404(
        AiInsight.objects.select_related('module__programme__institution', 'student', 'owner'), pk=pk)
    return render(request, 'staffdesk/academic/ai-insight-detail.html', {
        'page_title': insight.title, 'insight': insight,
        'statuses': AiInsight.STATUS_CHOICES,
        'data': forms.pretty_json(insight.data) if insight.data else '',
    })


@staff_required
@require_POST
def ai_insight_status(request, pk):
    insight = get_object_or_404(AiInsight, pk=pk)
    status = request.POST.get('status')
    if status in dict(AiInsight.STATUS_CHOICES):
        insight.status = status
        insight.save(update_fields=['status', 'updated_at'])
        messages.success(request, f'Marked {insight.get_status_display().lower()}.')
    return redirect('staffdesk:ai-insight-detail', pk=pk)
