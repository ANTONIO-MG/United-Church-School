"""Global navbar search — access-scoped suggestions across the whole hub.

Returns a JSON list of results (people, modules, lessons, assessments, study
material, your tasks, events), each with a label and a URL to the item's own
page.

**Everything here is scoped to the searcher's own academic spine**, via
:mod:`core.scoping`:

* **People** — :func:`core.scoping.directory_users`: your institution, your
  programme or your intake, plus every admin, staff member and educator (who
  have to be findable by everybody).
* **Material** — your module offerings and the programmes you are registered
  for. A Grade 3 learner does not turn up Grade 12 past papers.

Admin and staff are not scoped and search the whole platform; a parent's
directory is narrower still and comes from
:func:`core.scoping.parent_contacts`. Each section is wrapped so one failing
section never breaks the whole search.
"""

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse

from core.roles import role_flags, role_of_user
from core.scoping import _spine_ids, directory_users, is_scoped
from core.utils import avatar_url, display_name

PER = 5


def _staff_like(request):
    f = role_flags(request)
    return f['is_admin_staff'] or f['is_educator']


def _scope(user):
    """The searcher's spine, resolved once and shared by every section."""
    if not is_scoped(user):
        return None      # admin/staff — no narrowing anywhere below
    institution_ids, programme_ids, cohort_ids, offering_ids = _spine_ids(user)
    return {'institutions': institution_ids, 'programmes': programme_ids,
            'cohorts': cohort_ids, 'offerings': offering_ids}


def _my_module_ids(person):
    """Legacy course/module membership, still used by lessons and assessments."""
    if not person:
        return set()
    return (set(person.selected_modules.values_list('id', flat=True))
            | set(person.taught_modules.values_list('id', flat=True)))


# ---------------------------------------------------------------------------
# Sections
# ---------------------------------------------------------------------------
def _people(request, q):
    """People the searcher may reach — the directory rule, nothing wider.

    ``directory_users`` already unions "shares my institution / programme /
    cohort" with "is an admin, staff member or educator", so this section only
    has to match the query against it.
    """
    # By name only: people are found, and shown, by who they are, not by an
    # e-mail address (which searching would otherwise let anyone confirm).
    name_q = Q()
    for word in q.split()[:3]:
        name_q &= (Q(first_name__icontains=word) | Q(last_name__icontains=word)
                   | Q(profile__first_name__icontains=word) | Q(profile__last_name__icontains=word))
    users = (directory_users(request.user).filter(name_q)
             .select_related('profile').distinct()
             .order_by('first_name', 'last_name', 'id')[:PER])
    out = []
    for u in users:
        role = role_of_user(u)
        profile = getattr(u, 'profile', None)
        out.append({'type': 'Person', 'label': display_name(u),
                    'sub': role.title() or 'Member', 'icon': 'bi-person-circle',
                    'avatar': avatar_url(u),
                    # The profile link opens the person card (static/js/person-card.js),
                    # which has the Message button.
                    'url': (reverse('accounts:profile', args=[profile.pk]) if profile is not None
                            else reverse('communication:chat-direct', args=[u.pk]))})
    return out


def _modules(request, q, scope):
    """Module offerings on your own spine — straight to the module feed."""
    from apps.learning.models import ProgrammeModule

    qs = (ProgrammeModule.objects.filter(is_active=True)
          .filter(Q(code__icontains=q) | Q(name__icontains=q) | Q(module__name__icontains=q))
          .select_related('module', 'programme__institution'))
    if scope is not None:
        qs = qs.filter(id__in=scope['offerings'])
    return [{'type': 'Module', 'label': f'{m.code} — {m.display_name}',
             'sub': f'{m.programme.institution.code} · {m.programme.short_code}',
             'icon': 'bi-grid-1x2', 'url': reverse('learning:module-feed', args=[m.pk])}
            for m in qs[:PER]]


def _materials(request, q, scope):
    """Blueprints, study guides, question packs and mock papers on your modules.

    Locked items are still returned — you may search for what you have not paid
    for, exactly as the schedule lists it. The feed is what decides whether the
    row opens.
    """
    from apps.learning.models import ModuleMaterial

    qs = (ModuleMaterial.objects.filter(is_published=True)
          .filter(Q(title__icontains=q) | Q(description__icontains=q))
          .select_related('phase__programme_module__programme__institution'))
    if scope is not None:
        qs = qs.filter(phase__programme_module_id__in=scope['offerings'])
    out = []
    for material in qs[:PER]:
        offering = material.phase.programme_module
        out.append({'type': material.get_kind_display(), 'label': material.title,
                    'sub': f'{offering.code} · {material.phase.display_title}',
                    'icon': material.icon,
                    'url': reverse('learning:module-feed', args=[offering.pk])})
    return out


def _programmes(request, q, scope):
    from apps.learning.models import Programme

    qs = (Programme.objects.filter(is_active=True)
          .filter(Q(code__icontains=q) | Q(name__icontains=q) | Q(full_name__icontains=q))
          .select_related('institution'))
    if scope is not None:
        qs = qs.filter(id__in=scope['programmes'])
    return [{'type': 'Programme', 'label': p.display_name,
             'sub': p.institution.display_name, 'icon': 'bi-mortarboard',
             'url': reverse('learning:my-modules')} for p in qs[:PER]]


def _lessons(request, q, person, is_staff, scope):
    """Lessons: those on your own modules, or attached to your modules."""
    from apps.learning.models import Lesson
    qs = Lesson.objects.filter(title__icontains=q)
    if not is_staff:
        qs = qs.filter(status='published')
        reachable = Q(module_id__in=_my_module_ids(person))
        if scope is not None:
            reachable |= Q(module_materials__phase__programme_module_id__in=scope['offerings'])
        qs = qs.filter(reachable).distinct()
    return [{'type': 'Lesson', 'label': l.title, 'sub': 'Lesson', 'icon': 'bi-journal-text',
             'url': reverse('learning:lesson-view', args=[l.pk])} for l in qs[:PER]]


def _assessments(request, q, person, is_staff, scope):
    from apps.assessments.models import Assessment
    qs = Assessment.objects.filter(title__icontains=q)
    if not is_staff:
        reachable = Q(module_id__in=_my_module_ids(person))
        if scope is not None:
            reachable |= Q(module_materials__phase__programme_module_id__in=scope['offerings'])
        qs = qs.filter(reachable).distinct()
    out = []
    for a in qs[:PER]:
        url = reverse('assessments:builder', args=[a.pk]) if is_staff else reverse('assessments:take', args=[a.pk])
        out.append({'type': 'Assessment', 'label': a.title, 'sub': a.get_kind_display(),
                    'icon': 'bi-ui-checks', 'url': url})
    return out


def _tasks(request, q):
    from apps.tasks.models import Task
    rows = (Task.objects.filter(Q(assignments__user=request.user) | Q(created_by=request.user))
            .filter(title__icontains=q).distinct()[:PER])
    return [{'type': 'Task', 'label': t.title, 'sub': 'Task', 'icon': 'bi-check2-square',
             'url': reverse('orgtasks:task-detail', args=[t.pk])} for t in rows]


def _events(request, q, scope):
    """Institution calendar dates on your spine, plus general hub events."""
    from apps.learning.models import CalendarEvent
    from apps.myhub.models import Event

    out = [{'type': 'Event', 'label': e.title, 'sub': 'Event', 'icon': 'bi-calendar-event',
            'url': reverse('myhub:event-detail', args=[e.pk])}
           for e in Event.objects.filter(title__icontains=q)[:PER]]

    from apps.livesessions.academic import visible_events

    # Whole-school dates plus the reader's own grade(s) — see apps.livesessions.academic.
    dates = (visible_events(request.user, CalendarEvent.objects.filter(title__icontains=q))
             .filter(is_published=True)
             .select_related('calendar__institution'))
    if scope is not None:
        dates = dates.filter(calendar__institution_id__in=scope['institutions'])
    out += [{'type': 'Date', 'label': d.title,
             'sub': f'{d.calendar.institution.code} · {d.start:%d %b %Y}',
             'icon': 'bi-calendar3', 'url': reverse('learning:my-modules')}
            for d in dates[:PER]]
    return out


@login_required
def suggest(request):
    q = (request.GET.get('q') or '').strip()
    if len(q) < 2:
        return JsonResponse({'results': [], 'q': q})

    person = getattr(request.user, 'profile', None)
    is_staff = _staff_like(request)
    scope = _scope(request.user)

    results = []
    sections = [
        lambda: _people(request, q),
        lambda: _modules(request, q, scope),
        lambda: _materials(request, q, scope),
        lambda: _programmes(request, q, scope),
        lambda: _lessons(request, q, person, is_staff, scope),
        lambda: _assessments(request, q, person, is_staff, scope),
        lambda: _tasks(request, q),
        lambda: _events(request, q, scope),
    ]
    for section in sections:
        try:
            results += section()
        except Exception:  # a bad section never breaks the whole search
            continue
    return JsonResponse({'results': results[:30], 'q': q})
