"""Year-end promotion pages.

* ``promotion_index`` — every grade for the year with its decision counts.
* ``promotion_class`` — one grade's class: final marks, the CAPS requirements
  met or missed, the recommended outcome and the teacher's decision. Open to the
  grade's class teacher (Cohort.class_teacher) and admin/staff; when no class
  teacher is set, to the grade's subject teachers.
* ``new_year`` — the office: confirm pre-registered learners are returning
  (admitted + January invoice), mark those not returning, and start the year.
"""
from collections import Counter

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from core.roles import role_flags

from . import promotion
from .models import Application, PromotionDecision


def _is_office(request):
    return role_flags(request).get('is_admin_staff', False) or request.user.is_superuser


def _may_decide(request, programme, year):
    if _is_office(request):
        return True
    person = getattr(request.user, 'profile', None)
    if person is None:
        return False
    cohort = programme.cohorts.filter(code=str(year)).first()
    if cohort is not None and cohort.class_teacher_id:
        return cohort.class_teacher_id == person.pk
    return programme.modules.filter(educators=person).exists()


def _year(request):
    raw = (request.GET.get('year') or request.POST.get('year') or '').strip()
    return int(raw) if raw.isdigit() else timezone.localdate().year


@login_required
def promotion_index(request):
    from apps.learning.models import Programme
    year = _year(request)
    rows = []
    for programme in (Programme.objects.filter(is_active=True, institution__code='UCS')
                      .order_by('grade')):
        if not _may_decide(request, programme, year):
            continue
        counts = Counter(PromotionDecision.objects.filter(programme=programme, year=year)
                         .values_list('outcome', flat=True))
        cohort = programme.cohorts.filter(code=str(year)).select_related('class_teacher').first()
        rows.append({'programme': programme,
                     'promoted': counts['promote'] + counts['progress'],
                     'retained': counts['retain'],
                     'finished': counts['complete'] + counts['leaving'],
                     'learners': promotion.learners_in(programme, year).count(),
                     'class_teacher': cohort.class_teacher if cohort else None,
                     'decided': sum(n for k, n in counts.items() if k != 'pending')})
    return render(request, 'admissions/promotion-index.html', {
        'page_title': f'Promotion {year}', 'rows': rows, 'year': year,
        'is_office': _is_office(request),
    })


@login_required
def promotion_class(request, programme_id, year):
    from apps.learning.models import Programme
    programme = get_object_or_404(Programme, pk=programme_id)
    if not _may_decide(request, programme, year):
        raise Http404
    if request.method == 'POST':
        saved = 0
        for decision in PromotionDecision.objects.filter(programme=programme, year=year):
            outcome = request.POST.get(f'outcome_{decision.pk}')
            if outcome and outcome in dict(PromotionDecision.OUTCOME_CHOICES) and (
                    outcome != decision.outcome or request.POST.get(f'note_{decision.pk}', '') != decision.note):
                promotion.decide(decision, outcome, request.user,
                                 note=request.POST.get(f'note_{decision.pk}', '').strip())
                saved += 1
        messages.success(request, f'{saved} decision(s) saved. Promoted and retained learners are '
                                  f'pre-registered for {year + 1}.')
        return redirect('admissions:promotion-class', programme_id=programme.pk, year=year)
    decisions = promotion.build_decisions(programme, year)
    return render(request, 'admissions/promotion-class.html', {
        'page_title': f'Promotion — {programme.display_name} {year}', 'programme': programme,
        'year': year, 'decisions': decisions, 'outcomes': PromotionDecision.OUTCOME_CHOICES,
        'next_grade': promotion.next_programme(programme, PromotionDecision.OUTCOME_PROMOTE),
    })


@login_required
def new_year(request):
    if not _is_office(request):
        raise Http404
    year = _year(request)
    target = year if request.GET.get('year') else year + (1 if timezone.localdate().month >= 9 else 0)
    if request.method == 'POST':
        action = request.POST.get('action')
        ids = [int(i) for i in request.POST.getlist('application') if i.isdigit()]
        chosen = Application.objects.filter(pk__in=ids, year=target)
        if action == 'confirm':
            for application in chosen.filter(status=Application.STATUS_PREREGISTERED):
                promotion.confirm_returning(application, request.user)
            messages.success(request, f'{len(ids)} learner(s) confirmed as returning for {target}; '
                                      'January invoices raised.')
        elif action == 'not-returning':
            chosen.update(status=Application.STATUS_WITHDRAWN, decided_by=request.user,
                          decided_at=timezone.now())
            messages.info(request, f'{len(ids)} learner(s) marked as not returning.')
        elif action == 'start':
            started = promotion.start_school_year(target, request.user)
            messages.success(request, f'{target} school year started: {started} learner(s) enrolled '
                                      'in their new grades and classes.')
        return redirect(f"{request.path}?year={target}")
    applications = (Application.objects.filter(year=target)
                    .select_related('person__user', 'programme', 'previous__programme')
                    .order_by('programme__grade', 'person__last_name'))
    counts = Counter(applications.values_list('status', flat=True))
    return render(request, 'admissions/new-year.html', {
        'page_title': f'School year {target}', 'year': target,
        'preregistered': [a for a in applications if a.status == Application.STATUS_PREREGISTERED],
        'admitted': [a for a in applications if a.status == Application.STATUS_ADMITTED],
        'counts': sorted(counts.items()),
    })
