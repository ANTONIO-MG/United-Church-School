"""Who sees which dates on the school calendar.

The school calendar (:class:`apps.learning.models.AcademicCalendar` and its
:class:`~apps.learning.models.CalendarEvent` rows) carries two sorts of date:

* **whole-school** dates — no grade, no subject (``programme`` and
  ``programme_module`` both blank): term days, holidays, fee deadlines; and
* **grade** dates — tied to a grade (``programme``) or to one subject in a grade
  (``programme_module``): the NSC for Grade 12, the June exams for Grade 4 – 11,
  a Grade 10 Mathematics test.

Every surface that shows those rows asks :func:`visible_events` and nothing
else, so the calendar page, its JSON feed, the ``.ics`` export, the subscribed
feed, the dashboard and search all agree:

=================  ==========================================================
admin / staff      everything, published or not (optionally one grade)
educator           whole-school + the grades they teach (``ProgrammeModule.educators``)
learner            whole-school + their own grade (active ``ProgrammeEnrolment``)
parent             whole-school + their linked children's grades
anyone else        whole-school only
=================  ==========================================================

Unpublished rows (template / estimated dates) are staff-only, as before.
"""

from django.db.models import Q

from core.roles import role_of_user

STAFF_ROLES = ('admin', 'staff')


class Scope:
    """The grades (programmes), classes (cohorts) and schools a reader belongs to."""

    def __init__(self):
        self.programme_ids = set()
        self.institution_ids = set()
        self.cohort_ids = set()
        #: Grades where the reader is on every class (an educator, or a learner
        #: registered without a class) — any cohort-narrowed date there applies.
        self.open_programme_ids = set()

    def add_enrolments(self, enrolments):
        for programme_id, institution_id, cohort_id in enrolments:
            self.programme_ids.add(programme_id)
            self.institution_ids.add(institution_id)
            if cohort_id:
                self.cohort_ids.add(cohort_id)
            else:
                self.open_programme_ids.add(programme_id)


def scope_for(user):
    """The :class:`Scope` for a non-staff reader."""
    from apps.learning.models import ProgrammeEnrolment, ProgrammeModule

    scope = Scope()
    person = getattr(user, 'profile', None) if user is not None else None
    role = role_of_user(user)
    if role == 'educator' and person is not None:
        rows = (ProgrammeModule.objects.filter(educators=person)
                .values_list('programme_id', 'programme__institution_id'))
        for programme_id, institution_id in rows:
            scope.programme_ids.add(programme_id)
            scope.institution_ids.add(institution_id)
        scope.open_programme_ids = set(scope.programme_ids)
        return scope

    if role == 'parent':
        from core.scoping import children_of
        enrolments = ProgrammeEnrolment.objects.filter(
            person__user__in=children_of(user), is_active=True)
    elif person is not None:
        enrolments = ProgrammeEnrolment.objects.filter(person=person, is_active=True)
    else:
        return scope
    scope.add_enrolments(enrolments.values_list('programme_id', 'programme__institution_id',
                                                'cohort_id'))
    return scope


#: A whole-school date: on the calendar, for no grade and no subject.
WHOLE_SCHOOL = Q(programme__isnull=True, programme_module__isnull=True)


def for_grade(grade):
    """``Q`` for whole-school dates plus one grade's (by grade number)."""
    return (WHOLE_SCHOOL | Q(programme__grade=grade)
            | Q(programme__isnull=True, programme_module__programme__grade=grade))


def visible_events(user, queryset=None, *, grade=None):
    """The :class:`CalendarEvent` rows ``user`` may see (a queryset).

    ``grade`` (a grade number) narrows the result to whole-school dates plus
    that grade — the staff calendar's grade filter. For everyone else it can
    only narrow further, never widen.
    """
    from apps.learning.models import CalendarEvent

    query = queryset if queryset is not None else CalendarEvent.objects.all()
    if grade:
        query = query.filter(for_grade(grade))
    if role_of_user(user) in STAFF_ROLES:
        return query

    query = query.filter(is_published=True)
    scope = scope_for(user)
    whole = WHOLE_SCHOOL
    if scope.institution_ids:
        whole = whole & Q(calendar__institution_id__in=scope.institution_ids)
    mine = Q(programme_id__in=scope.programme_ids) | Q(
        programme__isnull=True, programme_module__programme_id__in=scope.programme_ids)
    in_class = (Q(cohort__isnull=True) | Q(cohort_id__in=scope.cohort_ids)
                | Q(cohort__programme_id__in=scope.open_programme_ids))
    if not scope.programme_ids:
        return query.filter(whole & Q(cohort__isnull=True))
    return query.filter((whole | mine) & in_class)


def sees_every_grade(user):
    return role_of_user(user) in STAFF_ROLES


def grade_choices(user):
    """``[grade numbers]`` the reader can filter by — every grade for staff,
    their own grades for everyone else."""
    from apps.learning.models import Programme

    if sees_every_grade(user):
        query = Programme.objects.filter(is_active=True, grade__isnull=False)
    else:
        query = Programme.objects.filter(pk__in=scope_for(user).programme_ids,
                                         grade__isnull=False)
    return sorted(set(query.values_list('grade', flat=True)))


def grades_label(grades):
    """``[4, 5, 6, 7, 9]`` → ``'Grades 4–7, 9'``; ``[12]`` → ``'Grade 12'``."""
    grades = sorted(set(g for g in grades if g is not None))
    if not grades:
        return ''
    runs, first, last = [], grades[0], grades[0]
    for g in grades[1:]:
        if g == last + 1:
            last = g
            continue
        runs.append((first, last))
        first = last = g
    runs.append((first, last))
    text = ', '.join(str(a) if a == b else (f'{a} & {b}' if b == a + 1 else f'{a}–{b}')
                     for a, b in runs)
    return f'Grade {text}' if len(grades) == 1 else f'Grades {text}'
