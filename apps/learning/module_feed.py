"""The module feed — one page per module offering, tabbed like a class profile.

Clicking a module anywhere in the hub (the dashboard panel, My Modules, My
Programmes) lands here, on the **Schedule**: the six preparation blocks of the
year, each opening into its weeks, each week listing the material for it.

    Test 1 preparation                      ← ModulePhase   (accordion)
      Blueprint · Test 1 scope              ← phase-level ModuleMaterial
      Week 1 · Deferred tax                 ← ModuleWeek    (nested accordion)
        Study guide · Deferred tax
        Questions · IAS 12 pack
        Answers · IAS 12 pack
        Live session · Thursday 18:00
        Assessment · Deferred tax quiz
      Week 2 · …

Everything else the student needs about the module is a tab on the same shell —
Messages, Notifications, Documents, Live sessions, Mock exams, Blueprints,
Assessments — and each of those tabs is only ever a *filter over the same
material rows*, never a second source of truth.

Access is resolved once per request by :class:`apps.learning.access.Gate`: a
locked row is still listed (that is the point — you can see what you are missing)
but carries no link, and offers "unlock the module" or, if the item is sold on
its own, "buy this item".

On top of that sits the *teaching* order — :class:`apps.learning.sequence.
SequenceGate`. A week is worked through, not browsed: the guide, then the mock,
and the solution only once the attempt is in. Both gates are resolved in the
same pass, so a row carries one verdict and one reason whichever shut it.
"""

import logging

from django.contrib import messages as flash
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from core.profiles import _tabs, shell_base

from . import models
from .access import Gate
from .sequence import SequenceGate

logger = logging.getLogger('apps')

# The module's sections, in the order a student needs them. "Schedule" is first
# and is the landing tab: opening a module means opening its plan for the year.
MODULE_TABS = [
    ('schedule', 'Schedule', 'bi-calendar3-week'),
    ('messages', 'Messages', 'bi-chat-left-text'),
    ('notifications', 'Notifications', 'bi-bell'),
    ('documents', 'Documents', 'bi-folder2-open'),
    ('live', 'Live sessions', 'bi-camera-video'),
    ('mocks', 'Mock exams', 'bi-file-earmark-ruled'),
    ('blueprints', 'Assessment guides', 'bi-diagram-3'),
    ('assessments', 'Assessments', 'bi-ui-checks'),
]

# Which material kinds each filter tab shows.
TAB_KINDS = {
    'documents': [models.ModuleMaterial.KIND_DOCUMENT, models.ModuleMaterial.KIND_STUDY_GUIDE,
                  models.ModuleMaterial.KIND_QUESTIONS, models.ModuleMaterial.KIND_ANSWERS,
                  models.ModuleMaterial.KIND_BLUEPRINT],
    'live': [models.ModuleMaterial.KIND_LIVE, models.ModuleMaterial.KIND_RECORDING],
    'mocks': [models.ModuleMaterial.KIND_MOCK_EXAM],
    'blueprints': [models.ModuleMaterial.KIND_BLUEPRINT],
    'assessments': [models.ModuleMaterial.KIND_ASSESSMENT],
}


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------
def _recordings(offering, cohort):
    """Imported YouTube videos mapped to this module (+ intake) and flagged for
    the schedule. Best-effort: never breaks the module page."""
    try:
        from apps.livesessions.imported import videos_for_module
        return list(videos_for_module(offering, cohort, surface='schedule'))
    except Exception:
        return []


def _load_phases(offering, gate, cohort=None):
    """Every phase of the offering with its weeks and material, in one go.

    Students see published rows only; staff and the offering's educators see
    drafts too, because they are the ones writing them.

    Per-cohort content (Option B): when ``cohort`` is given, the schedule is the
    blocks built for **that** intake plus any shared (cohort-less) template blocks.
    A student with no cohort, and a viewer looking at no particular cohort, sees
    only the shared blocks; a staff author looking at the whole offering (no
    cohort) sees every cohort's blocks so nothing is hidden from the builder.
    """
    weeks = (models.ModuleWeek.objects.filter(is_active=True)
             .prefetch_related('week_topics__topic'))
    materials = (models.ModuleMaterial.objects
                 .select_related('lesson', 'assessment', 'meeting', 'product', 'week', 'topic'))
    phases = models.ModulePhase.objects.filter(programme_module=offering, is_active=True)

    if cohort is not None:
        phases = phases.filter(Q(cohort=cohort) | Q(cohort__isnull=True))
    elif not gate.can_author:
        phases = phases.filter(cohort__isnull=True)

    if not gate.can_author:
        weeks = weeks.filter(is_published=True)
        materials = materials.filter(is_published=True)
        phases = phases.filter(is_published=True)

    return list(
        phases.prefetch_related(
            Prefetch('weeks', queryset=weeks.prefetch_related(
                Prefetch('materials', queryset=materials))),
            Prefetch('materials', queryset=materials.filter(week__isnull=True),
                     to_attr='phase_materials'),
        ).select_related('calendar_event')
    )


def _schedule(phases, gate, sequence=None):
    """Phases → weeks → material states: the accordion the Schedule tab renders.

    Each level carries its own counts so the collapsed header can say what is
    inside it without the template walking the tree twice.

    ``sequence`` applies the teaching order *within a week*, which is the only
    scope it makes sense in: week 3's guide does not gate week 4's mock.
    """
    rows = []
    for phase in phases:
        week_rows = []
        for week in phase.weeks.all():
            week_materials = list(week.materials.all())
            states = gate.states_for(week_materials, sequence=sequence,
                                     week_materials=week_materials)
            next_step = sequence.next_step(week_materials) if sequence else None
            # Group the week's materials under the topics it works through, in the
            # topic order set on the week. Materials with no topic (or a topic not
            # in this week's series) render at week level under `loose`.
            pairs = list(zip(week_materials, states))
            week_topic_ids = [t.id for t in week.topic_list]
            topic_groups = [
                {'topic': topic,
                 'materials': [s for m, s in pairs if m.topic_id == topic.id]}
                for topic in week.topic_list
            ]
            loose = [s for m, s in pairs if m.topic_id not in week_topic_ids]
            week_rows.append({
                'week': week,
                'materials': states,
                'topic_groups': topic_groups,
                'loose': loose,
                'total': len(states),
                'locked': sum(1 for s in states if s.locked),
                'is_current': week.is_current,
                'next_step_id': getattr(next_step, 'pk', None),
            })
        phase_states = gate.states_for(getattr(phase, 'phase_materials', []))
        total = len(phase_states) + sum(w['total'] for w in week_rows)
        rows.append({
            'phase': phase,
            'materials': phase_states,       # spans the whole block (the blueprint)
            'weeks': week_rows,
            'total': total,
            'locked': len([s for s in phase_states if s.locked]) + sum(w['locked'] for w in week_rows),
            'days_away': phase.days_away,
            'is_current': phase.is_current,
        })
    return rows


def _all_materials(phases):
    """Every material on the page, flat — what the sequence gate preloads from."""
    out = []
    for phase in phases:
        out.extend(getattr(phase, 'phase_materials', []))
        for week in phase.weeks.all():
            out.extend(week.materials.all())
    return out


def _flat_materials(phases, gate, kinds=None, sequence=None):
    """Every material of the offering as a flat, viewer-resolved list.

    The filter tabs are all this: same rows as the schedule, narrowed by kind
    and sorted so the newest-released sits at the top rather than by phase.
    """
    out = []
    for phase in phases:
        buckets = [(None, list(getattr(phase, 'phase_materials', [])))]
        buckets += [(week, list(week.materials.all())) for week in phase.weeks.all()]
        for week, items in buckets:
            for material in items:
                if kinds and material.kind not in kinds:
                    continue
                state = gate.for_material(material)
                if not state.visible:
                    continue
                # A filter tab shows the same rows as the schedule, so it must
                # reach the same verdict: a solution listed under "Documents"
                # cannot be a way around the sequence.
                if sequence is not None and state.open:
                    is_open, reason = sequence.check(material, items)
                    if not is_open:
                        state.open, state.reason = False, reason
                out.append({'state': state, 'material': material, 'phase': phase, 'week': week})
    return out


def _counts(phases, gate):
    """Badge numbers for the tab strip — how much material sits behind each."""
    counts = {}
    for key, kinds in TAB_KINDS.items():
        n = len(_flat_materials(phases, gate, kinds))
        if n:
            counts[key] = n
    return counts


# ---------------------------------------------------------------------------
# The view
# ---------------------------------------------------------------------------
@login_required
def module_feed(request, pk, tab='schedule'):
    """One module offering, tabbed. Defaults to the schedule."""
    offering = get_object_or_404(
        models.ProgrammeModule.objects.select_related(
            'module', 'programme__institution', 'chat_group'),
        pk=pk, is_active=True)

    person = getattr(request.user, 'profile', None)
    gate = Gate(request.user, offering, person=person)

    # Registration gate: you may look at a module you are enrolled on (locked or
    # not) — but a module you never registered for is not yours to browse.
    if not gate.can_author and gate.enrolment is None and not offering.is_free:
        flash.error(request, f'You are not registered for {offering.display_name}.')
        return redirect('learning:my-modules')

    valid = {key for key, _label, _icon in MODULE_TABS}
    if tab not in valid:
        tab = 'schedule'

    # Per-cohort schedule (Option B): a student sees their intake's blocks (plus
    # shared templates); a staff author previews a cohort with ?cohort=<id>, and
    # with none sees every cohort's blocks.
    view_cohort = None
    if gate.can_author:
        _cid = request.GET.get('cohort')
        if _cid and _cid.isdigit():
            view_cohort = offering.programme.cohorts.filter(pk=_cid).first()
    elif person is not None:
        _pe = (person.programme_enrolments.filter(programme=offering.programme)
               .select_related('cohort').first())
        view_cohort = _pe.cohort if _pe else None

    phases = _load_phases(offering, gate, cohort=view_cohort)
    # The teaching order, resolved once for every material on the page. Staff and
    # the offering's educators bypass it — they are writing the week.
    sequence = SequenceGate(request.user, _all_materials(phases),
                            bypass=gate.can_author)

    def url_for(key):
        return reverse('learning:module-feed-tab', args=[offering.pk, key])

    institution = offering.programme.institution
    ctx = {
        # HTMX (Phase 4): a tab click renders only #profContent; a full load or a
        # boosted nav renders the whole shell. See core.profiles.shell_base.
        'base_template': shell_base(request),
        'page_title': offering.display_name,
        'offering': offering,
        'gate': gate,
        # The cohort whose schedule is shown, and (for staff) the intakes they can
        # switch between — Option B per-cohort content.
        'view_cohort': view_cohort,
        'cohorts': list(offering.programme.cohorts.filter(is_active=True)),
        'profile': {
            'kind': 'module',
            'title': offering.display_name,
            'subtitle': f'{institution.display_name} · {offering.programme.display_name}',
            'avatar': institution.logo.url if institution.logo else '',
            'meta': _header_meta(offering, gate),
            'actions': _header_actions(offering, gate),
        },
        'tabs': _tabs(MODULE_TABS, url_for, tab, _counts(phases, gate)),
        'active_tab': tab,
        'accent': institution.accent_colour or '#1F3864',
        # Imported YouTube recordings mapped to this module + intake and flagged
        # for the schedule (see apps/livesessions/imported.py).
        'recordings': _recordings(offering, view_cohort),
        'next_phase': _next_phase(phases),
        # Rail panels of the shared shell.
        'activity_items': [],
        'files': _rail_files(phases, gate, sequence=sequence),
    }
    ctx.update(_tab_payload(request, offering, phases, gate, tab, sequence))
    return render(request, 'learning/module_feed.html', ctx)


def _header_meta(offering, gate):
    rows = [{'icon': 'bi-hash', 'text': offering.code}]
    if offering.is_free:
        rows.append({'icon': 'bi-unlock', 'text': 'Open to all'})
    elif offering.price_per_month:
        rows.append({'icon': 'bi-cash-coin', 'text': f'R{offering.price_per_month:.0f} / month'})
    else:
        rows.append({'icon': 'bi-cash-coin',
                     'text': f'Included in {offering.programme.display_name} school fees'})
    enrolment = gate.enrolment
    if enrolment and enrolment.status == enrolment.STATUS_TRIAL and enrolment.trial_ends_at:
        rows.append({'icon': 'bi-hourglass-split',
                     'text': f'Free week ends {enrolment.trial_ends_at:%d %b}'})
    elif enrolment and enrolment.status == enrolment.STATUS_ACTIVE and enrolment.paid_until:
        rows.append({'icon': 'bi-check-circle', 'text': f'Paid to {enrolment.paid_until:%d %b %Y}'})
    elif not gate.module_open:
        rows.append({'icon': 'bi-lock-fill', 'text': gate.module_status_label})
    return rows


def _header_actions(offering, gate):
    actions = []
    if not gate.module_open:
        actions.append({'label': 'Unlock module', 'icon': 'bi-unlock',
                        'url': reverse('learning:module-unlock', args=[offering.pk]),
                        'style': 'primary'})
    if gate.can_author:
        actions.append({'label': 'Build schedule', 'icon': 'bi-tools',
                        'url': reverse('learning:module-build', args=[offering.pk]),
                        'style': 'secondary-soft'})
    return actions


def _next_phase(phases):
    """The block being prepared for right now — the countdown at the top."""
    dated = [p for p in phases if p.days_away is not None and p.days_away >= 0]
    if dated:
        return min(dated, key=lambda p: p.days_away)
    current = [p for p in phases if p.is_current]
    return current[0] if current else (phases[0] if phases else None)


def _rail_files(phases, gate, limit=12, *, sequence=None):
    """The Files rail: downloadable material this viewer can actually open."""
    out = []
    for row in _flat_materials(phases, gate, sequence=sequence):
        material = row['material']
        if not material.file or row['state'].locked:
            continue
        out.append({'name': material.title, 'url': row['state'].url,
                    'meta': material.get_kind_display(), 'icon': material.icon})
        if len(out) >= limit:
            break
    return out


# ---------------------------------------------------------------------------
# Per-tab payloads
# ---------------------------------------------------------------------------
def _tab_payload(request, offering, phases, gate, tab, sequence=None):
    if tab == 'schedule':
        return {'schedule': _schedule(phases, gate, sequence)}

    if tab == 'messages':
        return _messages_tab(request, offering, gate)

    if tab == 'notifications':
        return {'notifications': _notifications_for(request, offering)}

    kinds = TAB_KINDS.get(tab)
    rows = _flat_materials(phases, gate, kinds, sequence)
    if tab == 'live':
        # Sessions read chronologically, upcoming first — a past recording is a
        # different thing from a class that has not happened yet.
        now = timezone.now()
        upcoming, past = [], []
        for row in rows:
            start = getattr(row['material'].meeting, 'scheduled_start', None)
            (upcoming if (start and start >= now) else past).append(row)
        upcoming.sort(key=lambda r: r['material'].meeting.scheduled_start)
        return {'rows': rows, 'live_upcoming': upcoming, 'live_past': past}
    return {'rows': rows}


def _messages_tab(request, offering, gate):
    """The module's group chat, rendered **in this page**.

    The tab used to be a card with an "Open chat" button, which dropped the
    student on the Messages page with every conversation they belong to and left
    them to find this one. So the thread is embedded here instead — the same
    component the Messages page renders (``communication/_chat_thread.html``),
    which is why it behaves identically rather than approximately.

    The template reads ``active_group``, so the group is published under that
    name. Membership is topped up on the way in: someone who can open this tab
    has access to the module, and therefore belongs in its room — without a
    membership row the API would refuse to show them a word of it.
    """
    group = offering.chat_group
    if group is None:
        return {'chat_group': None, 'active_group': None}

    try:
        from apps.communication import models as cmodels, services as cservices
        if not cmodels.ChatMembership.objects.filter(group=group, user=request.user).exists():
            if gate.can_author or gate.module_open:
                cmodels.ChatMembership.objects.get_or_create(
                    group=group, user=request.user, defaults={'is_auto': True})
        group = cservices.decorate_group(
            cmodels.ChatGroup.objects.prefetch_related('memberships__user__profile')
            .get(pk=group.pk),
            request.user)
    except Exception:                                    # pragma: no cover
        logger.exception('module feed: chat membership top-up failed')

    return {'chat_group': group, 'active_group': group}


def _notifications_for(request, offering, limit=40):
    """This module's notifications for this reader.

    Matched on the notification's ``url``: everything the module raises points
    at the module feed, so the link is the scope. That keeps ``communication``
    free of a hard dependency on the learning spine — the same reason
    ``ModuleEnrolment`` references an invoice by UUID rather than by FK.
    """
    try:
        from apps.communication.models import Notification

        prefix = reverse('learning:module-feed', args=[offering.pk])
        return list(Notification.objects
                    .filter(recipient=request.user, url__startswith=prefix)
                    .order_by('-created_at')[:limit])
    except Exception:  # pragma: no cover
        logger.exception('module feed: notifications lookup failed')
        return []
