"""Study progress + readiness for one candidate, across their modules.

Two numbers drive the sidebar tiles, the programme feed rail and the dashboard:

* **Completion** — how much of each preparation block (Test 1–4, Exam 1–2) the
  candidate has actually worked through. A block's material is only counted when
  it is *trackable*: a lesson (``StudySession`` / ``LessonSectionProgress``) or
  an assessment (``AssessmentAttempt``). A PDF nobody can tell you opened is not
  evidence of study, so it is left out of the denominator rather than counted as
  never-done and dragging the number down forever.

* **Readiness** — a blunt prediction of whether the candidate is on track for the
  next assessment. It blends how much of the block is done with how they have
  actually scored, then discounts it if the block is nearly due and still thin.
  It is a teaching signal, not a mark.

Everything here is defensive: a missing table or a half-built schedule returns
zeros rather than 500-ing the page it is rendered on.
"""

import logging
from datetime import date as date_cls, datetime, timedelta

from django.utils import timezone

logger = logging.getLogger('apps')

#: Order the blocks read in on a tile strip.
PHASE_ORDER = [('test', 1), ('test', 2), ('test', 3), ('test', 4),
               ('exam', 1), ('exam', 2)]


# ---------------------------------------------------------------------------
# Which offerings are this person's
# ---------------------------------------------------------------------------
def my_offerings(person):
    """Every module offering the person is enrolled on (locked ones included —
    a locked module is still on their year plan)."""
    if person is None:
        return []
    try:
        from . import models
        return list(models.ProgrammeModule.objects
                    .filter(enrolments__person=person, is_active=True)
                    .select_related('programme__institution', 'module')
                    .distinct())
    except Exception:                                    # pragma: no cover
        logger.exception('progress: offering lookup failed')
        return []


def module_count(person):
    """How many modules the candidate is carrying — the sidebar "Modules" tile."""
    try:
        from . import models
        return (models.ModuleEnrolment.objects
                .filter(person=person, programme_module__is_active=True).count()) if person else 0
    except Exception:                                    # pragma: no cover
        return 0


# ---------------------------------------------------------------------------
# Completion
# ---------------------------------------------------------------------------
def _done_lesson_ids(user):
    """Lessons this user has finished (a completed study session, or every
    section marked complete)."""
    from . import models
    done = set(models.StudySession.objects
               .filter(student=user, status=models.StudySession.STATUS_COMPLETED)
               .values_list('lesson_id', flat=True))
    done |= set(models.LessonSectionProgress.objects
                .filter(student=user, status=models.LessonSectionProgress.STATUS_COMPLETED)
                .values_list('section__lesson_id', flat=True))
    return done


def _attempt_scores(user):
    """``{assessment_id: best percentage}`` for every assessment this user has
    submitted. Presence of a key means "attempted"."""
    try:
        from apps.assessments import models as amodels
        rows = (amodels.AssessmentAttempt.objects
                .filter(student=user)
                .exclude(status=amodels.AssessmentAttempt.STATUS_IN_PROGRESS)
                .values_list('assessment_id', 'score', 'assessment__total_marks'))
    except Exception:                                    # pragma: no cover
        return {}
    best = {}
    for assessment_id, score, total in rows:
        total = float(total or 0)
        value = (100 * float(score or 0) / total) if total else 0.0
        if assessment_id not in best or value > best[assessment_id]:
            best[assessment_id] = value
    return best


def phase_rows(user, person=None):
    """One row per preparation block across all of the candidate's modules.

    Blocks with the same kind+sequence in different modules are merged, because
    "Test 2" is one event in a candidate's year even when three modules each
    prepare for it.

    Returns ``[{'key', 'label', 'kind', 'sequence', 'pct', 'tracked', 'done',
    'days_away', 'is_current', 'avg_score'}]`` in :data:`PHASE_ORDER`.
    """
    person = person if person is not None else getattr(user, 'profile', None)
    offerings = my_offerings(person)
    if not offerings:
        return []

    try:
        from django.db.models import Prefetch

        from . import models
        # ``phase.materials`` spans the whole phase INCLUDING everything hanging
        # off its weeks, so it is narrowed to the phase-level rows (``week=None``
        # — a test's own blueprint). Without that, every week's material is
        # counted once here and again through ``weeks__materials``, which doubles
        # the denominator. Same split as apps.learning.module_feed._load_phases.
        phases = (models.ModulePhase.objects
                  .filter(programme_module__in=offerings, is_active=True, is_published=True)
                  .select_related('calendar_event')
                  .prefetch_related(
                      Prefetch('materials',
                               queryset=models.ModuleMaterial.objects.filter(week__isnull=True),
                               to_attr='phase_materials'),
                      'weeks__materials'))
        lessons_done = _done_lesson_ids(user)
        scores = _attempt_scores(user)
    except Exception:                                    # pragma: no cover
        logger.exception('progress: phase lookup failed')
        return []

    buckets = {}
    for phase in phases:
        key = (phase.kind, phase.sequence)
        bucket = buckets.setdefault(key, {
            'key': f'{phase.kind}{phase.sequence}',
            'label': phase.short_label, 'kind': phase.kind, 'sequence': phase.sequence,
            'tracked': 0, 'done': 0, 'scores': [],
            'days_away': None, 'is_current': False,
        })

        materials = list(getattr(phase, 'phase_materials', []))
        for week in phase.weeks.all():
            materials.extend(week.materials.all())

        for material in materials:
            if material.lesson_id:
                bucket['tracked'] += 1
                if material.lesson_id in lessons_done:
                    bucket['done'] += 1
            elif material.assessment_id:
                bucket['tracked'] += 1
                if material.assessment_id in scores:
                    bucket['done'] += 1
                    bucket['scores'].append(scores[material.assessment_id])

        days = phase.days_away
        if days is not None and (bucket['days_away'] is None or days < bucket['days_away']):
            bucket['days_away'] = days
        bucket['is_current'] = bucket['is_current'] or phase.is_current

    rows = []
    for kind, sequence in PHASE_ORDER:
        bucket = buckets.pop((kind, sequence), None)
        if bucket is None:
            continue
        rows.append(_finish(bucket))
    # Anything non-standard the institution added, after the six defaults.
    for bucket in buckets.values():
        rows.append(_finish(bucket))
    return rows


def _finish(bucket):
    tracked, done = bucket['tracked'], bucket['done']
    bucket['pct'] = int(round(100 * done / tracked)) if tracked else 0
    scores = bucket.pop('scores')
    bucket['avg_score'] = int(round(sum(scores) / len(scores))) if scores else None
    return bucket


def overall_completion(user, person=None, rows=None):
    """One number for the whole year — the sidebar "Tests 1–4" tile."""
    rows = phase_rows(user, person) if rows is None else rows
    tracked = sum(r['tracked'] for r in rows)
    done = sum(r['done'] for r in rows)
    return int(round(100 * done / tracked)) if tracked else 0


# ---------------------------------------------------------------------------
# Readiness
# ---------------------------------------------------------------------------
#: Bands the readiness percentage is read in, worst first.
READINESS_BANDS = [
    (0,  'At risk',    'danger'),
    (40, 'Behind',     'warning'),
    (60, 'On track',   'info'),
    (80, 'Well ahead', 'success'),
]


def readiness(user, person=None, rows=None):
    """A prediction for the block the candidate is preparing for right now.

    ``{'pct', 'label', 'tone', 'phase', 'days_away', 'basis'}``. ``pct`` is
    ``None`` when there is nothing to predict from yet, and the label says so
    rather than inventing a number.
    """
    rows = phase_rows(user, person) if rows is None else rows
    target = _next_block(rows)
    if target is None or not target['tracked']:
        return {'pct': None, 'label': 'Not enough data', 'tone': 'secondary',
                'phase': target['label'] if target else '', 'days_away': None,
                'basis': 'Work through this block’s lessons and quizzes to get a prediction.'}

    completion = target['pct']
    score = target['avg_score']
    # Coverage is what you have done; score is how well it went. With no marks
    # yet, coverage carries the whole prediction rather than being averaged
    # against a zero the candidate never earned.
    pct = completion if score is None else int(round(0.6 * completion + 0.4 * score))

    # Close to the date and still thin: the same coverage means less.
    days = target['days_away']
    if days is not None and 0 <= days <= 14 and completion < 70:
        pct = int(round(pct * 0.85))
    pct = max(0, min(100, pct))

    label, tone = 'At risk', 'danger'
    for floor, band_label, band_tone in READINESS_BANDS:
        if pct >= floor:
            label, tone = band_label, band_tone

    if score is None:
        basis = f'{completion}% of {target["label"]} material worked through.'
    else:
        basis = f'{completion}% worked through · {score}% average so far.'
    return {'pct': pct, 'label': label, 'tone': tone, 'phase': target['label'],
            'days_away': days, 'basis': basis}


def _next_block(rows):
    """The block being prepared for: the current one, else the next dated one,
    else the first block with work outstanding."""
    current = [r for r in rows if r['is_current']]
    if current:
        return current[0]
    upcoming = [r for r in rows if r['days_away'] is not None and r['days_away'] >= 0]
    if upcoming:
        return min(upcoming, key=lambda r: r['days_away'])
    outstanding = [r for r in rows if r['pct'] < 100]
    return outstanding[0] if outstanding else (rows[0] if rows else None)


# ---------------------------------------------------------------------------
# What is coming up
# ---------------------------------------------------------------------------
def current_week(user, person=None):
    """The week of the schedule the candidate is inside right now, if any."""
    person = person if person is not None else getattr(user, 'profile', None)
    offerings = my_offerings(person)
    if not offerings:
        return None
    try:
        from . import models
        today = timezone.now().date()
        week = (models.ModuleWeek.objects
                .filter(phase__programme_module__in=offerings,
                        is_active=True, is_published=True,
                        starts_on__lte=today, ends_on__gte=today)
                .select_related('phase__programme_module__module')
                .prefetch_related('week_topics__topic')
                .order_by('phase__order', 'order')
                .first())
    except Exception:                                    # pragma: no cover
        logger.exception('progress: current week lookup failed')
        return None
    if week is None:
        return None
    return {
        'week': week,
        'title': week.display_title,
        'phase': week.phase.display_title,
        'module': week.phase.programme_module.display_name,
        'module_id': week.phase.programme_module_id,
        'ends_on': week.ends_on,
        'days_left': (week.ends_on - timezone.now().date()).days if week.ends_on else None,
    }


def upcoming_dates(user, person=None, limit=6, days=180):
    """The candidate's next key dates, newest deadline first.

    Two sources, merged: the institution's own calendar events for the modules
    they are on, and the dates they typed into their settings calendar. Both are
    normalised to ``{'label', 'date', 'kind', 'source', 'days_away', 'url'}``.
    """
    person = person if person is not None else getattr(user, 'profile', None)
    today = timezone.now().date()
    horizon = today + timedelta(days=days)
    out = []

    offerings = my_offerings(person)
    if offerings:
        try:
            from . import models
            events = (models.CalendarEvent.objects
                      .filter(programme_module__in=offerings,
                              start__date__gte=today, start__date__lte=horizon)
                      .select_related('programme_module__module')
                      .order_by('start')[:limit * 2])
            for event in events:
                out.append({
                    'label': event.title,
                    'date': event.start.date(),
                    'kind': event.get_kind_display(),
                    'tone': 'danger' if event.kind in ('exam', 'test', 'deadline') else 'primary',
                    'source': event.programme_module.code if event.programme_module_id else '',
                    'url': f'/learning/modules/{event.programme_module_id}/feed/' if event.programme_module_id else '',
                })
        except Exception:                                # pragma: no cover
            logger.exception('progress: calendar lookup failed')

    # The candidate's own dates from Settings → Academic calendar.
    study_profile = getattr(person, 'study_profile', None) if person else None
    if study_profile is not None:
        buckets = [('exam_dates', 'Exam', 'danger'),
                   ('assignment_dates', 'Assignment', 'primary'),
                   ('practical_dates', 'Practical', 'info')]
        for field, kind, tone in buckets:
            for row in (getattr(study_profile, field, None) or []):
                date = _parse_date(row.get('date'))
                if date is None or not (today <= date <= horizon):
                    continue
                out.append({'label': row.get('label') or kind, 'date': date, 'kind': kind,
                            'tone': tone, 'source': 'My calendar', 'url': '/community/settings/'})

    out.sort(key=lambda r: r['date'])
    for row in out:
        row['days_away'] = (row['date'] - today).days
    return out[:limit]


def _parse_date(value):
    if isinstance(value, date_cls):
        return value
    try:
        return datetime.strptime(str(value)[:10], '%Y-%m-%d').date()
    except (TypeError, ValueError):
        return None
