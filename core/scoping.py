"""Audience scoping — *which* people and academic objects a user may reach.

:mod:`core.roles` answers "what may this person *do*?"; this module answers "to
*whom*, and about *what*?". The two are deliberately separate: an educator has
teaching permissions (``can_teach``) but only over the modules they actually
teach, so nearly every list, dropdown and detail page needs the same narrowing.

The rule, in one line: **admin/staff are never scoped; an educator is scoped to
the modules they teach; everybody else is scoped to nothing** (their own data is
handled by the view itself, not here).

Every helper returns a queryset — never a list — so callers can keep filtering,
and every one is safe for anonymous users. Use them for *both* halves of a
change: narrowing what a form offers **and** re-validating what a POST contains.
A filtered ``<select>`` is a convenience; the queryset on the field is the
control.
"""

from django.contrib.auth import get_user_model

from core.roles import role_of_user


def is_scoped(user):
    """True when this user only ever sees their own teaching audience.

    Educators are scoped. Admin and staff are not — they see the institution.
    Students and parents return ``True`` as well, but every helper below then
    returns an empty queryset: they reach their own data through their own
    views, never through the teaching surfaces these helpers feed.
    """
    return role_of_user(user) not in ('admin', 'staff')


def _person(user):
    if user is None or not getattr(user, 'is_authenticated', False):
        return None
    return getattr(user, 'profile', None)


def taught_module_qs(user):
    """Subjects this user may teach, author for, or assign work to.

    All active modules for admin/staff; ``person.taught_modules`` for an
    educator; nothing for anyone else.
    """
    from apps.learning.models import ProgrammeModule

    if not is_scoped(user):
        return ProgrammeModule.objects.all()
    person = _person(user)
    if person is None or role_of_user(user) != 'educator':
        return ProgrammeModule.objects.none()
    return ProgrammeModule.objects.filter(pk__in=person.taught_modules.values('pk'))


def taught_programmes(user):
    """The programmes the modules this user teaches belong to."""
    from apps.learning.models import Programme

    if not is_scoped(user):
        return Programme.objects.all()
    return Programme.objects.filter(modules__in=taught_module_qs(user)).distinct()


def taught_people(user):
    """``accounts.Person`` rows enrolled in the modules this user teaches."""
    from apps.accounts.models import Person

    if not is_scoped(user):
        return Person.objects.all()
    return Person.objects.filter(module_enrolments__programme_module__in=taught_module_qs(user)).distinct()


def taught_students(user):
    """The ``User`` accounts behind :func:`taught_people` (active only)."""
    User = get_user_model()
    if not is_scoped(user):
        return User.objects.filter(is_active=True)
    return (User.objects
            .filter(is_active=True, profile__module_enrolments__programme_module__in=taught_module_qs(user))
            .distinct())


def scope_queryset(user, queryset, *, module_field='module'):
    """Narrow ``queryset`` to rows whose module this user teaches.

    A convenience for the many models hanging off a module (lessons,
    assessments, SCORM packages…). ``module_field`` names the path to the
    module FK, e.g. ``'module'`` or ``'lesson__module'``.
    """
    if not is_scoped(user):
        return queryset
    return queryset.filter(**{f'{module_field}__in': taught_module_qs(user)})


# ---------------------------------------------------------------------------
# Parents / guardians
#
# A parent's whole view of the platform is their child's. They never browse the
# institution: they see the student they are linked to and nothing beside it.
# The link is :class:`apps.accounts.models.ParentLink` (parent User ↔ student
# User) — the only source of truth, so a guardian who was never linked sees
# nothing rather than everything.
# ---------------------------------------------------------------------------
def is_parent(user):
    """True when this account is a parent/guardian."""
    return role_of_user(user) == 'parent'


def children_of(user):
    """The students this parent looks after, as a ``User`` queryset.

    Empty for anyone who is not a parent, and empty for a parent with no link —
    which is the safe direction: an unlinked guardian sees nothing at all rather
    than the whole school.
    """
    User = get_user_model()
    if not is_parent(user):
        return User.objects.none()
    from apps.accounts.models import ParentLink
    return User.objects.filter(
        pk__in=ParentLink.objects.filter(parent=user).values('student_id'))


def child_modules(user):
    """Every module this parent's children are enrolled in."""
    from apps.learning.models import ProgrammeModule
    return ProgrammeModule.objects.filter(
        enrolments__person__user__in=children_of(user)).distinct()


def parent_contacts(user):
    """Everyone a parent may message: admin, staff, and their children's educators.

    Deliberately *not* other parents or students — a parent's line of contact is
    the school and the people teaching their child, and opening it wider would
    turn the platform into a directory of families.
    """
    User = get_user_model()
    if not is_parent(user):
        return User.objects.none()
    from django.db.models import Q
    return (User.objects
            .filter(is_active=True)
            .filter(Q(profile__user_type__in=('admin', 'staff'))
                    | Q(is_staff=True)
                    | Q(profile__taught_modules__in=child_modules(user)))
            .exclude(pk=user.pk)
            .distinct())


def viewing_child(request):
    """The child a parent's page is about: ``?student=<id>`` or their first.

    Resolved against :func:`children_of`, so a parent asking for somebody else's
    student gets their own child back rather than the stranger's data.
    """
    children = children_of(getattr(request, 'user', None))
    requested = (request.GET.get('student') or '').strip()
    if requested.isdigit():
        child = children.filter(pk=int(requested)).first()
        if child is not None:
            return child
    return children.first()


# ---------------------------------------------------------------------------
# Academic-spine scoping — Institution → Programme → Cohort → module offering
#
# The helpers above scope by the legacy course/module pair. These scope by the
# spine the platform actually runs on now, and they are what the global search
# and the people directory use.
#
# The rule, in one line: **you can reach the people and the material of your own
# institution, programme and cohort — plus every admin, staff member and
# educator, who have to be reachable by everybody.**
#
# A student's spine comes from their enrolments; an educator's comes from the
# offerings they teach; admin and staff are not scoped at all.
# ---------------------------------------------------------------------------
def _spine_ids(user):
    """``(institution_ids, programme_ids, cohort_ids, offering_ids)`` for a user.

    One query set per level, resolved once so a caller can narrow several
    different models without re-deriving the same answer. Returns four empty
    sets for anonymous users, and is never called for admin/staff (who are not
    scoped — see :func:`is_scoped`).
    """
    person = _person(user)
    if person is None:
        return set(), set(), set(), set()

    from apps.learning.models import ProgrammeEnrolment, ProgrammeModule

    role = role_of_user(user)
    if role == 'educator':
        # An educator's spine is what they teach, not what they study.
        offerings = ProgrammeModule.objects.filter(educators=person)
        offering_ids = set(offerings.values_list('id', flat=True))
        programme_ids = set(offerings.values_list('programme_id', flat=True))
        institution_ids = set(offerings.values_list('programme__institution_id', flat=True))
        # Teachers see every year group of the grades they teach.
        from apps.learning.models import Cohort
        cohort_ids = set(Cohort.objects.filter(programme_id__in=programme_ids)
                         .values_list('id', flat=True))
        return institution_ids, programme_ids, cohort_ids, offering_ids

    enrolments = (ProgrammeEnrolment.objects
                  .filter(person=person, is_active=True)
                  .values_list('programme_id', 'programme__institution_id', 'cohort_id'))
    programme_ids, institution_ids, cohort_ids = set(), set(), set()
    for programme_id, institution_id, cohort_id in enrolments:
        programme_ids.add(programme_id)
        institution_ids.add(institution_id)
        if cohort_id:
            cohort_ids.add(cohort_id)
    # Every module they hold a row for — locked ones included. You should be able
    # to search for a module you have registered for but not yet paid; the feed
    # is what decides whether its material opens.
    offering_ids = set(ProgrammeModule.objects
                       .filter(enrolments__person=person)
                       .values_list('id', flat=True))
    # A student registered for a programme can reach that programme's modules
    # even before picking them, which is how "modules on my programme" reads.
    offering_ids |= set(ProgrammeModule.objects
                        .filter(programme_id__in=programme_ids, is_active=True)
                        .values_list('id', flat=True))
    return institution_ids, programme_ids, cohort_ids, offering_ids


def my_institutions(user):
    """Institutions this user belongs to (all of them for admin/staff)."""
    from apps.learning.models import Institution
    if not is_scoped(user):
        return Institution.objects.all()
    institution_ids, _p, _c, _o = _spine_ids(user)
    return Institution.objects.filter(id__in=institution_ids)


def my_programmes(user):
    """Programmes (grades) this user is registered for, or teaches on."""
    from apps.learning.models import Programme
    if not is_scoped(user):
        return Programme.objects.all()
    _i, programme_ids, _c, _o = _spine_ids(user)
    return Programme.objects.filter(id__in=programme_ids)


def my_cohorts(user):
    """The intakes this user sits with (every intake of a programme they teach)."""
    from apps.learning.models import Cohort
    if not is_scoped(user):
        return Cohort.objects.all()
    _i, _p, cohort_ids, _o = _spine_ids(user)
    return Cohort.objects.filter(id__in=cohort_ids)


def my_offerings(user):
    """Module offerings this user may see — registered for, or on their programme."""
    from apps.learning.models import ProgrammeModule
    if not is_scoped(user):
        return ProgrammeModule.objects.all()
    _i, _p, _c, offering_ids = _spine_ids(user)
    return ProgrammeModule.objects.filter(id__in=offering_ids)


def directory_users(user, *, include_self=False):
    """Everyone this user is allowed to find in a search or a people picker.

    Two groups, unioned:

    * **Your class, in the widest sense** — learners and teachers who share your
      school, your grade or your year group. Sharing any one of the three
      is enough: a Grade 10 learner can find another Grade 10 learner even in
      a different year group.
    * **Everyone whose job is to be reachable** — admins, staff and educators,
      always, whatever spine they sit on. A student must be able to find the
      office and a teacher without knowing which programme they are attached to.

    Admin and staff are not scoped and get the whole active directory. Parents
    are handled separately by :func:`parent_contacts`, whose narrower rule wins.
    """
    from django.db.models import Q

    User = get_user_model()
    if user is None or not getattr(user, 'is_authenticated', False):
        return User.objects.none()
    if is_parent(user):
        return parent_contacts(user)

    qs = User.objects.filter(is_active=True)
    if not include_self:
        qs = qs.exclude(pk=user.pk)
    if not is_scoped(user):
        return qs.distinct()

    institution_ids, programme_ids, cohort_ids, _offerings = _spine_ids(user)

    # Always reachable, whoever they are attached to.
    reachable = (Q(profile__user_type__in=('admin', 'staff', 'educator'))
                 | Q(is_staff=True) | Q(is_superuser=True))
    # …plus anyone sharing a level of your spine.
    same_spine = (Q(profile__programme_enrolments__programme__institution_id__in=institution_ids)
                  | Q(profile__programme_enrolments__programme_id__in=programme_ids)
                  | Q(profile__programme_enrolments__cohort_id__in=cohort_ids))
    return qs.filter(reachable | same_spine).distinct()
