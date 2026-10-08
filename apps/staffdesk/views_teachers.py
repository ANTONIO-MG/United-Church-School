"""/staff/class-teachers/ — set every grade's class teacher and subject
teachers for a school year on one page.

* **Class teacher** — ``Cohort.class_teacher`` for the year's class of each
  grade. A grade with no class for that year gets one (code = the year) the
  first time a teacher is chosen for it.
* **Subject teachers** — ``ProgrammeModule.educators``. Choosing a teacher for
  a subject makes them its teacher; a subject that already has several
  teachers is left as it is when one of them is chosen, so co-teaching is not
  undone by saving the page.

Admin and staff only (:func:`~apps.staffdesk.access.staff_required`).
"""

from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.shortcuts import redirect, render
from django.utils import timezone

from apps.accounts.models import Person
from apps.learning.models import Cohort, Programme, ProgrammeModule

from .access import staff_required


def _year(request):
    raw = (request.GET.get('year') or request.POST.get('year') or '').strip()
    return int(raw) if raw.isdigit() else timezone.localdate().year


def _educators():
    return list(Person.objects.filter(Q(user_type='educator') | Q(taught_modules__isnull=False),
                                      user__is_active=True)
                .select_related('user').distinct().order_by('first_name', 'last_name'))


def _year_classes(programme, year):
    return [c for c in programme.cohorts.all()
            if c.code == str(year) or (c.start_date and c.start_date.year == year)]


@staff_required
def class_teachers(request):
    year = _year(request)
    programmes = list(Programme.objects.filter(is_active=True)
                      .prefetch_related('cohorts__class_teacher', 'modules__educators', 'modules__module')
                      .order_by('grade', 'name'))
    educators = _educators()
    by_pk = {str(e.pk): e for e in educators}

    if request.method == 'POST':
        classes_set = subjects_set = 0
        with transaction.atomic():
            for programme in programmes:
                year_classes = _year_classes(programme, year)
                for cohort in year_classes:
                    raw = request.POST.get(f'class_{cohort.pk}', '')
                    chosen = by_pk.get(raw)
                    if (chosen.pk if chosen else None) != cohort.class_teacher_id:
                        cohort.class_teacher = chosen
                        cohort.save(update_fields=['class_teacher'])
                        classes_set += 1
                if not year_classes:
                    chosen = by_pk.get(request.POST.get(f'new_class_{programme.pk}', ''))
                    if chosen:
                        Cohort.objects.create(programme=programme, code=str(year),
                                              name=f'{programme.display_name} · {year}',
                                              class_teacher=chosen)
                        classes_set += 1
                for module in programme.modules.all():
                    key = f'subject_{module.pk}'
                    if key not in request.POST:
                        continue
                    chosen = by_pk.get(request.POST[key])
                    current = {e.pk for e in module.educators.all()}
                    if chosen is None:
                        if current and request.POST[key] == '':
                            module.educators.clear()
                            subjects_set += 1
                    elif chosen.pk not in current:
                        module.educators.set([chosen])
                        subjects_set += 1
        messages.success(request, f'Saved {classes_set} class teacher(s) and '
                                  f'{subjects_set} subject teacher change(s) for {year}.')
        return redirect(f'{request.path}?year={year}')

    rows = []
    for programme in programmes:
        modules = sorted(programme.modules.all(), key=lambda m: (m.order, m.code or ''))
        rows.append({
            'programme': programme,
            'classes': _year_classes(programme, year),
            'subjects': [{'module': m, 'teachers': list(m.educators.all())} for m in modules],
        })
    today = timezone.localdate().year
    return render(request, 'staffdesk/academic/class-teachers.html', {
        'page_title': f'Class & subject teachers {year}', 'year': year, 'rows': rows,
        'educators': educators, 'years': [today - 1, today, today + 1],
        'unassigned': sum(1 for r in rows if not any(c.class_teacher_id for c in r['classes'])),
    })
