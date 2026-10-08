"""Student-facing dashboard intelligence for ``/myhub/``.

Everything the home dashboard renders is assembled here so the view stays thin
and each panel can be reasoned about (and tested) on its own. The entry point is
:func:`student_dashboard`.

Design rules followed throughout this module:

* **Never break the page.** Every section is wrapped in its own ``try`` so a
  missing app, an un-migrated table or a null-heavy row set degrades that one
  panel instead of 500-ing the dashboard (same posture as
  :mod:`apps.analytics.services`).
* **Bulk, not per-row.** Completion is resolved with a handful of ``IN`` queries
  and set membership rather than calling ``CourseItem.is_completed_by`` per item
  (which would fire 2 queries per segment).
* **Explain every number.** Each analytic returns the score *and* the reason it
  landed there, because a bare "68%" tells a student nothing about what to do
  next.

The five analytics surfaced to students:

1. :func:`assessment_readiness` — per-assessment readiness score (coverage,
   prior accuracy, study recency, pace fit) with the single best next action.
2. :func:`pace_profile` — time-pressure profile: are you rushing or
   overthinking, derived from time used vs marks earned.
3. :func:`momentum` — study streak, 7-day vs previous-7-day trend and a 12-week
   activity sparkline.
4. :func:`mastery_map` — accuracy per grade component + weakest modules, so
   revision targets the right place.
5. :func:`completion_forecast` — projected finish date per module at the
   student's current pace, compared with the course end date.

Plus five panels that surface data the hub already records but never showed the
student:

6. :func:`focus_now` — the single highest-priority next action, chosen across
   every other panel.
7. :func:`attendance_rings` — attended vs held class sessions, per module.
8. :func:`cohort_standing` — the student's rank and percentile within each
   module's cohort (counts only — never another student's name or mark).
9. :func:`marking_queue` — work submitted but not yet marked, with how long it
   has been waiting against the usual turnaround.
10. :func:`open_questions` — unanswered discussion threads in the student's
    modules, plus their own accepted-answer count.
"""

import logging
from datetime import timedelta

from django.db.models import Avg, Count, Max, Q, Sum
from django.urls import reverse
from django.utils import timezone

logger = logging.getLogger(__name__)

# Bands used by the readiness gauge and reused by the template for colouring.
READY_BAND = 75
ALMOST_BAND = 50

#: Fallback study time for a segment with no estimate attached (minutes).
DEFAULT_ITEM_MINUTES = 25


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------
def _pct(part, whole):
    """Safe percentage, rounded to a whole number."""
    try:
        return round((part or 0) / whole * 100) if whole else 0
    except Exception:
        return 0


def _f(value, default=0.0):
    """Coerce Decimal/None/str to float without ever raising."""
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def enrolled_modules(user):
    """The offerings the signed-in person studies (falls back to what they teach).

    A candidate's modules come from their :class:`ModuleEnrolment` rows —
    enrolment on the platform is by programme (grade) and its modules, never by module. An
    educator sees the offerings they teach instead, so their dashboard is useful
    rather than empty.
    """
    person = getattr(user, 'profile', None)
    if person is None:
        return []
    try:
        related = ('programme__institution', 'module')
        modules = list(person.selected_modules.filter(is_active=True).select_related(*related))
        if not modules:
            modules = list(person.taught_modules.filter(is_active=True).select_related(*related))
        return modules
    except Exception:
        logger.exception('enrolled_modules failed')
        return []


def _completion_index(user, modules):
    """Resolve published-lesson completion for every module in bulk.

    Returns ``{module_id: {'done': int, 'total': int, 'next': Lesson|None}}``.

    The platform measures coverage in lessons. The old segment layer this walked
    (``CourseItem`` over ``CourseUnit``, with SCORM and H5P attempt records
    folded in) went with the MyHub course player; a lesson is now the unit of
    progress, and a completed :class:`~apps.learning.models.StudySession` is
    what marks one done. Two queries total, not one per module.
    """
    index = {m.id: {'done': 0, 'total': 0, 'next': None} for m in modules}
    if not modules:
        return index

    try:
        from apps.learning.models import Lesson, StudySession
    except Exception:  # pragma: no cover — app always installed
        return index

    try:
        lessons = list(
            Lesson.objects
            .filter(module__in=modules, status=Lesson.STATUS_PUBLISHED)
            .only('id', 'title', 'module_id')
            .order_by('module_id', 'title', 'id')
        )
    except Exception:
        logger.exception('_completion_index: lesson lookup failed')
        return index
    if not lessons:
        return index

    try:
        done_ids = set(
            StudySession.objects
            .filter(student=user, lesson_id__in=[lesson.id for lesson in lessons],
                    status=StudySession.STATUS_COMPLETED)
            .values_list('lesson_id', flat=True)
        )
    except Exception:
        logger.exception('_completion_index: session lookup failed')
        done_ids = set()

    for lesson in lessons:
        bucket = index.get(lesson.module_id)
        if bucket is None:
            continue
        bucket['total'] += 1
        if lesson.id in done_ids:
            bucket['done'] += 1
        elif bucket['next'] is None:
            bucket['next'] = lesson

    return index


def _item_url(lesson):
    """Deep link that opens the next lesson in a module."""
    if lesson is None:
        return ''
    try:
        return reverse('learning:lesson-view', args=[lesson.id])
    except Exception:
        return ''


# ---------------------------------------------------------------------------
# 1 · ProgrammeModule progress
# ---------------------------------------------------------------------------
def student_grades(user, cache=None):
    """Every :class:`reports.Grade` this student has, fetched once.

    Four panels wanted grades — the module table, the summary tiles, the
    mastery map and the cohort ranking — and each ran its own query for what is
    at most one row per module. They now share this list and filter it in
    Python. ``cache`` is the dict :func:`student_dashboard` threads through, so
    the fetch happens once per request; called without one it simply queries.
    """
    if cache is not None and 'grades' in cache:
        return cache['grades']
    try:
        from apps.reports.models import Grade
        rows = list(Grade.objects.filter(student=user).select_related('module'))
    except Exception:  # pragma: no cover
        logger.exception('dashboard: grade lookup failed')
        rows = []
    if cache is not None:
        cache['grades'] = rows
    return rows


def module_coverage(user, modules, completion, cache=None):
    """Per-module progress bar + grade chip + "resume here" link."""
    wanted = {m.pk for m in modules}
    grades = {g.module_id: g for g in student_grades(user, cache) if g.module_id in wanted}

    rows = []
    for module in modules:
        bucket = completion.get(module.id) or {'done': 0, 'total': 0, 'next': None}
        done, total = bucket['done'], bucket['total']

        grade = grades.get(module.id)
        pct = _pct(done, total)
        rows.append({
            'module': module,
            'done': done,
            'total': total,
            'unit': 'lessons',
            'pct': pct,
            'grade_pct': round(_f(grade.final_pct)) if grade else None,
            'letter': grade.letter if grade else '',
            'passed': grade.passed if grade else None,
            'study_hours': _f(grade.study_hours) if grade else 0.0,
            'next_item': bucket['next'],
            'next_url': _item_url(bucket['next']),
            'url': _safe_url('learning:module-profile', module.id),
            'tone': 'success' if pct >= 75 else ('info' if pct >= 40 else ('warning' if pct > 0 else 'secondary')),
        })
    rows.sort(key=lambda r: (r['pct'], r['module'].name))
    return rows


def _safe_url(name, *args):
    try:
        return reverse(name, args=args)
    except Exception:
        return ''


def _ordinal(n):
    """1 → '1st', 2 → '2nd', 11 → '11th' … (teens are all 'th')."""
    if 11 <= (n % 100) <= 13:
        return f'{n}th'
    return f'{n}{ {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th") }'


# ---------------------------------------------------------------------------
# 2 · Academic summary (the top strip)
# ---------------------------------------------------------------------------
def academic_summary(user, modules, completion, progress_rows, cache=None):
    """Headline numbers: programmes, lessons, study time, average mark, standing."""
    data = {
        'programmes': 0, 'modules': len(modules),
        'lessons_total': 0, 'lessons_done': 0, 'lessons_pct': 0,
        'study_hours': 0.0, 'sessions': 0,
        'avg_mark': None, 'letter': '', 'modules_passed': 0,
        'assessments_taken': 0, 'assessments_passed': 0, 'accuracy': None,
        'certificates': 0, 'attendance_pct': None,
    }

    person = getattr(user, 'profile', None)
    if person is not None:
        try:
            from apps.learning.models import ProgrammeEnrolment
            data['programmes'] = ProgrammeEnrolment.objects.filter(person=person).count()
        except Exception:
            logger.exception('academic_summary: programme count failed')

    try:
        from apps.learning.models import Lesson, StudySession
        data['lessons_total'] = Lesson.objects.filter(
            module__in=modules, status=Lesson.STATUS_PUBLISHED).count()
        data['lessons_done'] = (StudySession.objects
                                .filter(student=user, status=StudySession.STATUS_COMPLETED)
                                .values('lesson_id').distinct().count())
        data['lessons_pct'] = _pct(data['lessons_done'], data['lessons_total'])
        agg = StudySession.objects.filter(student=user).aggregate(secs=Sum('total_seconds'), n=Count('id'))
        data['study_hours'] = round((agg['secs'] or 0) / 3600.0, 1)
        data['sessions'] = agg['n'] or 0
    except Exception:
        logger.exception('academic_summary: study failed')

    try:
        from apps.reports.models import Certificate, Grade
        grade_rows = student_grades(user, cache)
        if grade_rows:
            data['avg_mark'] = round(sum(_f(g.final_pct) for g in grade_rows) / len(grade_rows), 1)
            data['modules_passed'] = sum(1 for g in grade_rows if g.passed)
            attendance = [_f(g.attendance_pct) for g in grade_rows if _f(g.attendance_pct) > 0]
            if attendance:
                data['attendance_pct'] = round(sum(attendance) / len(attendance))
            best = max(grade_rows, key=lambda g: _f(g.final_pct))
            data['letter'] = best.letter or ''
        data['certificates'] = Certificate.objects.filter(student=user).count()
    except Exception:
        logger.exception('academic_summary: grades failed')

    try:
        from apps.assessments.models import Answer, AssessmentAttempt
        attempts = AssessmentAttempt.objects.filter(student=user, status__in=['submitted', 'marked'])
        data['assessments_taken'] = attempts.count()
        data['assessments_passed'] = attempts.filter(passed=True).count()
        marked = Answer.objects.filter(attempt__student=user, marked=True).aggregate(
            n=Count('id'), ok=Count('id', filter=Q(is_correct=True)))
        if marked['n']:
            data['accuracy'] = _pct(marked['ok'], marked['n'])
    except Exception:
        logger.exception('academic_summary: assessments failed')

    # Overall journey completion, measured in published lessons.
    data['overall_pct'] = data['lessons_pct']
    return data


# ---------------------------------------------------------------------------
# 3 · Analytic #1 — assessment readiness
# ---------------------------------------------------------------------------
def assessment_readiness(user, modules, completion, limit=5):
    """Score how ready the student is for each open/upcoming assessment.

    The score blends four signals, each 0–100, then weights them:

    ===============  ======  ==================================================
    Signal           Weight  Source
    ===============  ======  ==================================================
    Coverage           40%   required segments completed in the parent module
                             (falls back to the whole module)
    Prior accuracy     30%   past marks in the same grade component, else the
                             module grade, else overall answer accuracy
    Study recency      15%   days since the last study session in that module
    Pace fit           15%   past seconds-per-mark vs the time this paper allows
    ===============  ======  ==================================================

    Each row carries ``advice`` — the weakest signal expressed as one action.
    """
    now = timezone.now()
    out = []
    try:
        from apps.assessments.models import Assessment, AssessmentAttempt
    except Exception:
        return out

    try:
        upcoming = list(
            Assessment.objects
            .filter(module__in=modules, status__in=['open', 'scheduled'])
            .filter(Q(available_to__isnull=True) | Q(available_to__gte=now))
            .select_related('module')
            .order_by('available_to', 'created_at')[:20]
        )
    except Exception:
        logger.exception('assessment_readiness: query failed')
        return out
    if not upcoming:
        return out

    # --- Attempt history, once ---
    history = list(
        AssessmentAttempt.objects
        .filter(student=user, status__in=['submitted', 'marked'])
        .select_related('assessment')
        .values('assessment_id', 'assessment__module_id', 'assessment__component',
                'assessment__kind', 'assessment__total_marks', 'score', 'passed',
                'time_spent_seconds')
    )
    attempts_by_assessment = {}
    for row in history:
        attempts_by_assessment.setdefault(row['assessment_id'], []).append(row)

    def _component_of(kind, component):
        if component:
            return component
        return Assessment.DEFAULT_COMPONENT_BY_KIND.get(kind, Assessment.COMPONENT_QUIZZES)

    # Prior accuracy per (module, component) and seconds-per-mark overall.
    acc_bucket, pace_samples = {}, []
    for row in history:
        total = _f(row['assessment__total_marks'])
        if total > 0:
            pct = min(100.0, _f(row['score']) / total * 100)
            key = (row['assessment__module_id'], _component_of(row['assessment__kind'],
                                                                row['assessment__component']))
            acc_bucket.setdefault(key, []).append(pct)
            acc_bucket.setdefault((row['assessment__module_id'], None), []).append(pct)
            # Seconds per *available* mark — how long a mark's worth of paper
            # takes this student. Using marks *earned* would assume they score
            # 100% on the next paper and wildly overstate the time needed.
            if row['time_spent_seconds']:
                pace_samples.append(row['time_spent_seconds'] / total)
    avg_pace = (sum(pace_samples) / len(pace_samples)) if pace_samples else None

    # --- Study recency per module ---
    last_study = {}
    try:
        from apps.learning.models import StudySession
        # Ordered newest-first per module; setdefault keeps only the newest row.
        for session in (StudySession.objects.filter(student=user, lesson__module__in=modules)
                        .order_by('lesson__module_id', '-updated_at')
                        .values('lesson__module_id', 'updated_at')):
            last_study.setdefault(session['lesson__module_id'], session['updated_at'])
    except Exception:
        pass

    # Answer-level accuracy across everything marked — the fallback when a
    # module has no history of its own yet.
    overall_accuracy = None
    try:
        from apps.assessments.models import Answer
        marked = Answer.objects.filter(attempt__student=user, marked=True).aggregate(
            n=Count('id'), ok=Count('id', filter=Q(is_correct=True)))
        if marked['n']:
            overall_accuracy = _pct(marked['ok'], marked['n'])
    except Exception:
        logger.exception('assessment_readiness: accuracy lookup failed')

    for assessment in upcoming:
        taken = attempts_by_assessment.get(assessment.id, [])
        allowed = assessment.attempts_allowed or 0
        if allowed and len(taken) >= allowed:
            continue  # no attempts left — nothing to prepare for

        # -- Coverage --
        bucket = completion.get(assessment.module_id) or {}
        coverage = _pct(bucket.get('done'), bucket.get('total')) if bucket.get('total') else 50
        coverage_label = (f"{bucket.get('done', 0)}/{bucket.get('total', 0)} lessons "
                          f'of the module done')

        # -- Prior accuracy --
        component = _component_of(assessment.kind, assessment.component)
        samples = (acc_bucket.get((assessment.module_id, component))
                   or acc_bucket.get((assessment.module_id, None)))
        if samples:
            accuracy = round(sum(samples) / len(samples))
            accuracy_label = f'{accuracy}% average in past {component}'
        elif overall_accuracy is not None:
            accuracy = overall_accuracy
            accuracy_label = f'{accuracy}% overall answer accuracy (no history in this subject yet)'
        else:
            accuracy = 50
            accuracy_label = 'No marked work yet — assumed neutral'

        # -- Study recency (full marks inside 3 days, zero past 21) --
        when = last_study.get(assessment.module_id)
        if when:
            days = max(0, (now - when).days)
            recency = 100 if days <= 3 else max(0, round(100 - (days - 3) * (100 / 18)))
            recency_label = ('Studied this subject today' if days == 0
                             else f'Last studied {days} day{"s" if days != 1 else ""} ago')
        else:
            days, recency = None, 20
            recency_label = 'No study session logged for this subject'

        # -- Pace fit: can you finish in the time allowed at your usual speed? --
        limit_seconds = (assessment.time_limit_minutes or 0) * 60
        total_marks = _f(assessment.total_marks) or 1
        if avg_pace and limit_seconds:
            needed = avg_pace * total_marks
            ratio = needed / limit_seconds
            pace = 100 if ratio <= 0.7 else max(0, round(100 - (ratio - 0.7) * 200))
            pace_label = (f'Your usual pace needs ~{round(needed / 60)} min of the '
                          f'{assessment.time_limit_minutes} min allowed')
        elif avg_pace:
            pace, pace_label = 85, 'No time limit on this paper'
        else:
            pace, pace_label = 60, 'Not enough timed attempts to judge your pace'

        score = round(coverage * 0.40 + accuracy * 0.30 + recency * 0.15 + pace * 0.15)
        signals = [
            {'name': 'Content covered', 'value': coverage, 'detail': coverage_label, 'icon': 'bi-collection'},
            {'name': 'Past accuracy', 'value': accuracy, 'detail': accuracy_label, 'icon': 'bi-bullseye'},
            {'name': 'Study recency', 'value': recency, 'detail': recency_label, 'icon': 'bi-clock-history'},
            {'name': 'Pace fit', 'value': pace, 'detail': pace_label, 'icon': 'bi-speedometer2'},
        ]
        weakest = min(signals, key=lambda s: s['value'])
        advice = {
            'Content covered': 'Finish the outstanding lessons in this subject first.',
            'Past accuracy': 'Redo the practice questions you got wrong in this component.',
            'Study recency': 'Do a short revision session on this subject before the test.',
            'Pace fit': 'Practise under a timer — you are close to running out of time.',
        }[weakest['name']]

        if score >= READY_BAND:
            band, tone = 'Ready', 'success'
        elif score >= ALMOST_BAND:
            band, tone = 'Almost ready', 'warning'
        else:
            band, tone = 'Not ready', 'danger'

        closes_in = None
        if assessment.available_to:
            delta = assessment.available_to - now
            closes_in = max(0, delta.days)

        out.append({
            'assessment': assessment,
            'module': assessment.module,
            'score': score,
            'band': band,
            'tone': tone,
            'signals': signals,
            'advice': advice,
            'closes_at': assessment.available_to,
            'closes_in_days': closes_in,
            'attempts_used': len(taken),
            'attempts_allowed': allowed,
            'url': _safe_url('assessments:take', assessment.id),
        })

    # Most urgent first: soonest close date, then lowest readiness.
    out.sort(key=lambda r: (r['closes_in_days'] if r['closes_in_days'] is not None else 999, r['score']))
    return out[:limit]


# ---------------------------------------------------------------------------
# 4 · Analytic #2 — pace / time-pressure profile
# ---------------------------------------------------------------------------
def pace_profile(user):
    """Classify the student's exam-time behaviour from marks vs time used.

    Compares the share of allotted time consumed against the mark earned:

    * fast **and** low-scoring → *Rushing* (careless-error risk)
    * slow **and** high-scoring → *Thorough but tight* (time-out risk)
    * slow **and** low-scoring → *Struggling for time*
    * otherwise → *Well paced*
    """
    data = {'has_data': False}
    try:
        from apps.assessments.models import AssessmentAttempt
        rows = list(AssessmentAttempt.objects
                    .filter(student=user, status__in=['submitted', 'marked'], time_spent_seconds__gt=0)
                    .select_related('assessment')
                    .values('score', 'assessment__total_marks', 'assessment__time_limit_minutes',
                            'time_spent_seconds')[:200])
    except Exception:
        logger.exception('pace_profile failed')
        return data
    if not rows:
        return data

    marks, time_use, minutes = [], [], []
    for row in rows:
        total = _f(row['assessment__total_marks'])
        if total > 0:
            marks.append(min(100.0, _f(row['score']) / total * 100))
        minutes.append(row['time_spent_seconds'] / 60.0)
        limit = (row['assessment__time_limit_minutes'] or 0) * 60
        if limit:
            time_use.append(min(200.0, row['time_spent_seconds'] / limit * 100))

    avg_mark = round(sum(marks) / len(marks)) if marks else None
    avg_use = round(sum(time_use) / len(time_use)) if time_use else None
    avg_minutes = round(sum(minutes) / len(minutes))

    if avg_use is None or avg_mark is None:
        label, tone, note = 'Building your profile', 'info', \
            'Sit a couple of timed assessments and this will calibrate.'
    elif avg_use < 55 and avg_mark < 60:
        label, tone, note = 'Rushing', 'danger', \
            f'You use only {avg_use}% of the time allowed and average {avg_mark}%. Slowing down and ' \
            're-reading each question is the cheapest mark you can buy.'
    elif avg_use > 90 and avg_mark >= 60:
        label, tone, note = 'Thorough but tight', 'warning', \
            f'You score {avg_mark}% but use {avg_use}% of the clock. Bank the easy marks first so a ' \
            'slow question never costs you the end of the paper.'
    elif avg_use > 90:
        label, tone, note = 'Struggling for time', 'danger', \
            f'You use {avg_use}% of the time and average {avg_mark}%. Timed practice on the basics ' \
            'will lift both.'
    else:
        label, tone, note = 'Well paced', 'success', \
            f'{avg_use}% of the time allowed for {avg_mark}% average — a healthy margin.'

    data.update({
        'has_data': True, 'label': label, 'tone': tone, 'note': note,
        'avg_mark': avg_mark, 'avg_time_use': avg_use, 'avg_minutes': avg_minutes,
        'samples': len(rows),
    })
    return data


# ---------------------------------------------------------------------------
# 5 · Analytic #3 — momentum (streak + trend + sparkline)
# ---------------------------------------------------------------------------
def momentum(user, weeks=12):
    """Study streak, week-on-week trend and a weekly activity sparkline."""
    data = {'streak': 0, 'best_streak': 0, 'this_week_minutes': 0, 'last_week_minutes': 0,
            'trend_pct': None, 'spark': [], 'active_days_30': 0, 'has_data': False}
    try:
        from apps.learning.models import StudySession
        since = timezone.now() - timedelta(weeks=weeks)
        rows = list(StudySession.objects.filter(student=user, updated_at__gte=since)
                    .values('updated_at', 'total_seconds')[:2000])
    except Exception:
        logger.exception('momentum failed')
        return data
    if not rows:
        return data

    today = timezone.localdate()
    per_day = {}
    for row in rows:
        day = timezone.localtime(row['updated_at']).date()
        per_day[day] = per_day.get(day, 0) + (row['total_seconds'] or 0)

    # Current streak — consecutive days with any study, ending today or yesterday.
    streak, cursor = 0, today
    if cursor not in per_day and (cursor - timedelta(days=1)) in per_day:
        cursor -= timedelta(days=1)
    while cursor in per_day:
        streak += 1
        cursor -= timedelta(days=1)

    # Best streak in the window.
    best, run, previous = 0, 0, None
    for day in sorted(per_day):
        run = run + 1 if previous and (day - previous).days == 1 else 1
        best = max(best, run)
        previous = day

    def _minutes(start, end):
        return round(sum(secs for day, secs in per_day.items() if start <= day < end) / 60)

    this_week = _minutes(today - timedelta(days=7), today + timedelta(days=1))
    last_week = _minutes(today - timedelta(days=14), today - timedelta(days=7))
    trend = round((this_week - last_week) / last_week * 100) if last_week else None

    spark = []
    for index in range(weeks - 1, -1, -1):
        end = today - timedelta(days=7 * index)
        spark.append({'minutes': _minutes(end - timedelta(days=7), end + timedelta(days=1))})
    peak = max([s['minutes'] for s in spark] or [0]) or 1
    for slot in spark:
        slot['height'] = max(4, round(slot['minutes'] / peak * 100))

    data.update({
        'streak': streak, 'best_streak': best,
        'this_week_minutes': this_week, 'last_week_minutes': last_week, 'trend_pct': trend,
        'spark': spark, 'has_data': True,
        'active_days_30': sum(1 for day in per_day if (today - day).days <= 30),
    })
    return data


# ---------------------------------------------------------------------------
# 6 · Analytic #4 — mastery map
# ---------------------------------------------------------------------------
def mastery_map(user, modules, cache=None):
    """Average mark per grade component + the weakest modules to revise."""
    data = {'components': [], 'weakest': [], 'strongest': None, 'has_data': False}
    labels = {'assignments': 'Assignments', 'quizzes': 'Quizzes', 'tests': 'Tests',
              'exams': 'Exams', 'tasks': 'Tasks'}
    try:
        from apps.reports.models import Grade
        grades = student_grades(user, cache)
    except Exception:
        logger.exception('mastery_map failed')
        return data
    if not grades:
        return data

    buckets = {}
    for grade in grades:
        for key, value in (grade.components or {}).items():
            buckets.setdefault(key, []).append(_f(value))

    for key, label in labels.items():
        values = buckets.get(key)
        if not values:
            continue
        avg = round(sum(values) / len(values))
        data['components'].append({
            'key': key, 'label': label, 'value': avg,
            'tone': 'success' if avg >= 70 else ('warning' if avg >= 50 else 'danger'),
        })

    ranked = sorted(grades, key=lambda g: _f(g.final_pct))
    data['weakest'] = [{
        'module': g.module,
        'value': round(_f(g.final_pct)),
        'letter': g.letter,
        'url': _safe_url('learning:module-profile', g.module_id),
    } for g in ranked[:3] if _f(g.final_pct) < 75]
    top = ranked[-1]
    data['strongest'] = {'module': top.module, 'value': round(_f(top.final_pct))}
    data['has_data'] = bool(data['components'] or data['weakest'])
    return data


# ---------------------------------------------------------------------------
# 7 · Analytic #5 — completion forecast
# ---------------------------------------------------------------------------
def completion_forecast(user, progress_rows, weekly_minutes, deadline=None):
    """Project a finish date per module from the student's weekly study pace.

    Uses the module's average lesson estimate (falling back to
    :data:`DEFAULT_ITEM_MINUTES`) for the work left, divided by the minutes the
    student actually studies per week. ``deadline`` is the next examination date
    off the institution calendar (see :func:`exam_countdown`); any module that
    lands after it is flagged late.
    """
    out = []
    if weekly_minutes <= 0:
        return out
    today = timezone.localdate()

    estimates = {}
    try:
        from apps.learning.models import Lesson
        for row in (Lesson.objects.filter(module__in=[r['module'] for r in progress_rows],
                                          status=Lesson.STATUS_PUBLISHED)
                    .values('module_id').annotate(avg=Avg('estimated_minutes'))):
            estimates[row['module_id']] = row['avg'] or DEFAULT_ITEM_MINUTES
    except Exception:
        pass

    for row in progress_rows:
        remaining = max(0, (row['total'] or 0) - (row['done'] or 0))
        if not remaining:
            continue
        per_item = _f(estimates.get(row['module'].id), DEFAULT_ITEM_MINUTES) or DEFAULT_ITEM_MINUTES
        weeks = max(1, round(remaining * per_item / weekly_minutes))
        finish = today + timedelta(weeks=weeks)
        late = bool(deadline and finish > deadline)
        out.append({
            'module': row['module'],
            'remaining': remaining,
            'weeks': weeks,
            'finish': finish,
            'deadline': deadline,
            'late': late,
            'tone': 'danger' if late else ('warning' if weeks > 12 else 'success'),
        })
    out.sort(key=lambda r: (not r['late'], r['finish']))
    return out[:5]


# ---------------------------------------------------------------------------
# 8 · Finance summary
# ---------------------------------------------------------------------------
def finance_summary(user):
    """Billed / paid / outstanding for the signed-in student, plus what's due."""
    data = {'has_data': False, 'billed': 0.0, 'paid': 0.0, 'outstanding': 0.0,
            'paid_pct': 0, 'overdue': 0, 'next_due': None, 'currency': 'R', 'invoices': []}
    try:
        from apps.finance.models import Invoice
        invoices = list(Invoice.objects.filter(customer=user)
                        .exclude(status=Invoice.STATUS_CANCELLED)
                        .prefetch_related('payments').order_by('due_date', '-issue_date')[:50])
    except Exception:
        logger.exception('finance_summary failed')
        return data
    if not invoices:
        return data

    today = timezone.localdate()
    billed = paid = 0.0
    next_due = None
    overdue = 0
    for invoice in invoices:
        total = _f(invoice.total)
        settled = sum(_f(p.amount) for p in invoice.payments.all()
                      if getattr(p, 'status', 'completed') == 'completed')
        billed += total
        paid += min(settled, total)
        outstanding = max(0.0, total - settled)
        if outstanding > 0 and invoice.due_date:
            if invoice.due_date < today:
                overdue += 1
            elif next_due is None or invoice.due_date < next_due['due_date']:
                next_due = {'due_date': invoice.due_date, 'amount': outstanding,
                            'number': invoice.number,
                            'url': _safe_url('finance:invoice-detail', invoice.id)}

    data.update({
        'has_data': True,
        'billed': round(billed, 2), 'paid': round(paid, 2),
        'outstanding': round(max(0.0, billed - paid), 2),
        'paid_pct': _pct(paid, billed),
        'overdue': overdue, 'next_due': next_due,
        'invoices': invoices[:4],
    })
    return data


# ---------------------------------------------------------------------------
# 9 · Achievements
# ---------------------------------------------------------------------------
def achievements(user, summary, streak_days):
    """Earned badges (with the locked ones shown as goals).

    Certificates are deliberately absent for educators — the whole certificate
    surface is closed to them (see :mod:`apps.reports.views`), so linking to one
    from the dashboard would only dead-end in a 404.
    """
    certificates = []
    try:
        from core.roles import role_of_user
        from apps.reports.models import Certificate
        if role_of_user(user) != 'educator':
            certificates = list(Certificate.objects.filter(student=user)
                                .select_related('module')[:6])
    except Exception:
        certificates = []

    catalogue = [
        ('First steps', 'bi-flag', summary.get('lessons_done', 0) >= 1, 'Complete your first lesson'),
        ('Ten down', 'bi-journal-check', summary.get('lessons_done', 0) >= 10, 'Complete 10 lessons'),
        ('Assessed', 'bi-ui-checks', summary.get('assessments_taken', 0) >= 1, 'Submit your first assessment'),
        ('Sharpshooter', 'bi-bullseye', (summary.get('accuracy') or 0) >= 80, 'Hit 80% answer accuracy'),
        ('On a roll', 'bi-fire', streak_days >= 7, 'Study 7 days in a row'),
        ('Distinction', 'bi-mortarboard', (summary.get('avg_mark') or 0) >= 75, 'Average 75% overall'),
        ('Certified', 'bi-patch-check', summary.get('certificates', 0) >= 1, 'Earn a certificate'),
        ('Marathon', 'bi-hourglass-split', summary.get('study_hours', 0) >= 50, 'Log 50 study hours'),
    ]
    badges = [{'name': n, 'icon': i, 'earned': bool(e), 'goal': g} for n, i, e, g in catalogue]
    return {
        'badges': badges,
        'earned': sum(1 for b in badges if b['earned']),
        'total': len(badges),
        'certificates': certificates,
    }


# ---------------------------------------------------------------------------
# 10 · Right-rail feeds: live sessions, notices, messages, notifications
# ---------------------------------------------------------------------------
def live_sessions(user, modules, limit=5):
    """Upcoming (and currently live) online sessions for the user's modules."""
    out = []
    try:
        from apps.communication.models import MeetingRoom
        now = timezone.now()
        rooms = (MeetingRoom.objects
                 .filter(is_active=True)
                 .filter(Q(module__in=modules) | Q(host=user) | Q(participants__user=user))
                 .filter(Q(scheduled_end__gte=now) | Q(scheduled_start__gte=now))
                 .select_related('module', 'host')
                 .distinct().order_by('scheduled_start')[:limit])
        for room in rooms:
            starts = room.scheduled_start
            out.append({
                'room': room,
                'module': room.module,
                'starts_at': starts,
                'is_live': room.is_live_now,
                'starts_in_minutes': round((starts - now).total_seconds() / 60) if starts and starts > now else 0,
                'url': room.get_join_url(),
            })
    except Exception:
        logger.exception('live_sessions failed')
    return out


def notice_board(user, limit=5):
    """Announcements addressed to this user, newest first."""
    try:
        from apps.communication.models import Announcement, Notification
        ids = list(Notification.objects.filter(recipient=user, announcement__isnull=False)
                   .values_list('announcement_id', flat=True)[:60])
        qs = Announcement.objects.filter(sent_at__isnull=False)
        qs = qs.filter(Q(id__in=ids) | Q(audience=Announcement.AUDIENCE_ALL)) if ids \
            else qs.filter(audience=Announcement.AUDIENCE_ALL)
        return list(qs.select_related('sender').order_by('-sent_at')[:limit])
    except Exception:
        logger.exception('notice_board failed')
        return []


def recent_messages(user, limit=5):
    """Latest message in each of the user's chat groups (skips their own)."""
    out = []
    try:
        from apps.communication.models import ChatMembership, Message
        group_ids = list(ChatMembership.objects.filter(user=user).values_list('group_id', flat=True)[:60])
        if not group_ids:
            return out
        seen = set()
        for message in (Message.objects.filter(group_id__in=group_ids, is_deleted=False,
                                               sender__isnull=False)
                        .exclude(sender=user)
                        .select_related('sender', 'sender__profile', 'group')
                        .order_by('-created_at')[:80]):
            if message.group_id in seen:
                continue
            seen.add(message.group_id)
            out.append(message)
            if len(out) >= limit:
                break
    except Exception:
        logger.exception('recent_messages failed')
    return out


def recent_notifications(user, limit=6):
    try:
        from apps.communication.models import Notification
        return list(Notification.objects.filter(recipient=user)
                    .select_related('actor').order_by('-created_at')[:limit])
    except Exception:
        logger.exception('recent_notifications failed')
        return []


def unread_counts(user):
    data = {'notifications': 0, 'messages': 0}
    try:
        from apps.communication.models import Notification
        data['notifications'] = Notification.objects.filter(recipient=user, is_read=False).count()
    except Exception:
        pass
    return data


# ---------------------------------------------------------------------------
# Study-insight cards (the plain-English read-out of the analytics above)
# ---------------------------------------------------------------------------
def study_insights(summary, pace, trend, forecast, readiness, mastery,
                   attendance=None, marking=None, engagement=None):
    """Turn the raw analytics into at most four "do this next" cards."""
    cards = []
    attendance = attendance or {}
    marking = marking or {}
    engagement = engagement or {}

    # A module the student has largely stopped engaging with outranks
    # everything else — it is the earliest warning available.
    weak = [r for r in engagement.get('rows', []) if r['score'] is not None and r['score'] < 40]
    if weak:
        worst = min(weak, key=lambda r: r['score'])
        thin = [c['key'] for c in worst['cells'] if c['value'] is not None and c['value'] < 40]
        cards.append({'icon': 'bi-activity', 'tone': 'danger',
                      'title': f"Engagement slipping in {worst['module'].name}",
                      'body': f"Scoring {worst['score']}/100 overall"
                              + (f", weakest on {' and '.join(thin[:2])}." if thin else '.')
                              + ' Picking one of those back up moves it fastest.'})

    # Attendance and stalled marking are time-critical, so they lead.
    if attendance.get('has_data') and attendance['overall'] < 80:
        cards.append({'icon': 'bi-person-check', 'tone': attendance['tone'],
                      'title': f"Attendance at {attendance['overall']}%",
                      'body': f"You've attended {attendance['attended']} of {attendance['held']} classes. "
                              'Aim for at least 80% to be well prepared for the exam.'})

    if marking.get('overdue'):
        n = marking['overdue']
        cards.append({'icon': 'bi-hourglass-split', 'tone': 'warning',
                      'title': f"{n} submission{'s' if n != 1 else ''} overdue for marking",
                      'body': f"{marking['count']} item{'s' if marking['count'] != 1 else ''} still out; the "
                              f"longest has waited {marking['pending'][0]['days']} days"
                              + (f" against a usual turnaround of {marking['typical_days']}."
                                 if marking.get('typical_days') else '.')
                              + ' Worth a polite nudge to your educator.'})

    if trend.get('has_data'):
        change = trend.get('trend_pct')
        if change is None:
            cards.append({'icon': 'bi-graph-up-arrow', 'tone': 'info', 'title': 'Getting started',
                          'body': f"{trend['this_week_minutes']} minutes studied this week. "
                                  'One more session sets your first trend line.'})
        elif change >= 10:
            cards.append({'icon': 'bi-graph-up-arrow', 'tone': 'success', 'title': f'Up {change}% this week',
                          'body': f"{trend['this_week_minutes']} min this week vs "
                                  f"{trend['last_week_minutes']} min last week. Keep the streak alive."})
        elif change <= -10:
            cards.append({'icon': 'bi-graph-down-arrow', 'tone': 'warning', 'title': f'Down {abs(change)}% this week',
                          'body': f"{trend['this_week_minutes']} min this week vs "
                                  f"{trend['last_week_minutes']} min last week. A 20-minute session today "
                                  'puts you back on pace.'})

    if readiness:
        weakest = min(readiness, key=lambda r: r['score'])
        cards.append({'icon': 'bi-clipboard-pulse', 'tone': weakest['tone'],
                      'title': f"{weakest['band']} for {weakest['assessment'].title}",
                      'body': weakest['advice']})

    if pace.get('has_data'):
        cards.append({'icon': 'bi-speedometer2', 'tone': pace['tone'],
                      'title': f"Exam pace: {pace['label']}", 'body': pace['note']})

    late = [f for f in forecast if f['late']]
    if late:
        item = late[0]
        cards.append({'icon': 'bi-calendar-x', 'tone': 'danger',
                      'title': f"{item['module'].name} will finish late",
                      'body': f"At your current pace you finish around {item['finish']:%d %b %Y}, "
                              f"after the {item['deadline']:%d %b %Y} course end date. "
                              f"{item['remaining']} segments left."})
    elif mastery.get('weakest'):
        weak = mastery['weakest'][0]
        cards.append({'icon': 'bi-bullseye', 'tone': 'warning',
                      'title': f"Weakest subject: {weak['module'].name}",
                      'body': f"Sitting at {weak['value']}%. Revising this one lifts your average "
                              'more than anything else on your list.'})

    return cards[:4]


# ---------------------------------------------------------------------------
# 11 · Attendance rings
# ---------------------------------------------------------------------------
def attendance_rings(user, modules):
    """Attended vs held class sessions, per module and overall.

    ``present`` and ``late`` both count as attended; ``excused`` is removed from
    the denominator rather than counted as a miss, so a signed-off absence never
    drags the ring down. Sessions with no attendance row for this student are
    treated as misses — a class was held and nothing was recorded.
    """
    data = {'has_data': False, 'overall': 0, 'rows': [], 'attended': 0, 'held': 0, 'excused': 0}
    if not modules:
        return data
    try:
        from apps.communication.models import Attendance, ClassSession
    except Exception:
        return data

    try:
        held = {row['module_id']: row['n'] for row in
                ClassSession.objects.filter(module__in=modules)
                .values('module_id').annotate(n=Count('id'))}
        if not held:
            return data
        marks = (Attendance.objects
                 .filter(student=user, session__module__in=modules)
                 .values('session__module_id', 'status')
                 .annotate(n=Count('id')))
    except Exception:
        logger.exception('attendance_rings failed')
        return data

    per_module = {}
    for row in marks:
        bucket = per_module.setdefault(row['session__module_id'], {})
        bucket[row['status']] = bucket.get(row['status'], 0) + row['n']

    total_attended = total_held = total_excused = 0
    for module in modules:
        sessions = held.get(module.id, 0)
        if not sessions:
            continue
        bucket = per_module.get(module.id, {})
        attended = bucket.get(Attendance.STATUS_PRESENT, 0) + bucket.get(Attendance.STATUS_LATE, 0)
        excused = bucket.get(Attendance.STATUS_EXCUSED, 0)
        countable = max(0, sessions - excused)
        pct = _pct(attended, countable) if countable else 100
        total_attended += attended
        total_held += countable
        total_excused += excused
        data['rows'].append({
            'module': module,
            'pct': pct,
            'attended': attended,
            'held': countable,
            'late': bucket.get(Attendance.STATUS_LATE, 0),
            'excused': excused,
            'tone': 'success' if pct >= 85 else ('warning' if pct >= 70 else 'danger'),
        })

    if not data['rows']:
        return data
    data['rows'].sort(key=lambda r: r['pct'])
    data.update({
        'has_data': True,
        'attended': total_attended, 'held': total_held, 'excused': total_excused,
        'overall': _pct(total_attended, total_held) if total_held else 100,
    })
    data['tone'] = 'success' if data['overall'] >= 85 else ('warning' if data['overall'] >= 70 else 'danger')
    return data


# ---------------------------------------------------------------------------
# 12 · Cohort standing
# ---------------------------------------------------------------------------
def cohort_standing(user, modules, cache=None):
    """Where the student sits in each module's cohort.

    Reads the standing persisted on :class:`apps.reports.models.Grade` by
    :func:`apps.reports.services.rank_module` (position, cohort size and class
    average, refreshed module-wide whenever any grade in it changes). Rows that
    predate ranking — or that a bulk import wrote without going through the
    signal — fall back to deriving the rank live, so the panel never blanks out
    while ``manage.py rank_classes`` has yet to be run.

    Only counts and the student's own mark are returned — never another
    student's identity or result.
    """
    data = {'has_data': False, 'rows': [], 'best': None, 'stale': 0}
    if not modules:
        return data
    try:
        from apps.reports.models import Grade
        wanted = {s.pk for s in modules}
        mine = {g.module_id: g for g in student_grades(user, cache) if g.module_id in wanted}
        if not mine:
            return data
        # Only pull the full cohort for modules whose stored ranking is missing.
        unranked = [sid for sid, g in mine.items() if not g.class_position or not g.cohort_size]
        cohort = (Grade.objects.filter(module_id__in=unranked).values('module_id', 'final_pct')
                  if unranked else [])
    except Exception:
        logger.exception('cohort_standing failed')
        return data

    marks_by_module = {}
    for row in cohort:
        marks_by_module.setdefault(row['module_id'], []).append(_f(row['final_pct']))

    for module in modules:
        grade = mine.get(module.id)
        if grade is None:
            continue
        my_mark = _f(grade.final_pct)

        if grade.class_position and grade.cohort_size:
            size = grade.cohort_size
            position = grade.class_position
            average = _f(grade.cohort_average)
        else:
            # Not ranked yet — derive it for display only, nothing is written.
            marks = marks_by_module.get(module.id) or []
            size = len(marks)
            if size < 2:
                continue
            position = sum(1 for m in marks if m > my_mark) + 1
            average = sum(marks) / size
            data['stale'] += 1

        if size < 2:
            continue  # a cohort of one tells the student nothing
        # Percentile = share of the cohort at or below this mark.
        percentile = round((size - position + 1) / size * 100)
        delta = round(my_mark - average)
        data['rows'].append({
            'module': module,
            'position': position,
            'ordinal': _ordinal(position),
            'size': size,
            'percentile': percentile,
            # "Top N%" is your position as a share of the cohort — 1st of 20 is
            # the top 5%. Only meaningful once the cohort is big enough that a
            # percentage says more than the raw position does ("top 25%" in a
            # class of 4 is just "1st of 4" dressed up), so it is gated below.
            'top_pct': max(1, round(position / size * 100)),
            'show_percentile': size >= 10,
            'mark': round(my_mark),
            'average': round(average),
            'delta': delta,
            'delta_abs': abs(delta),
            'tone': 'success' if percentile >= 75 else ('info' if percentile >= 50 else 'warning'),
        })

    if not data['rows']:
        return data
    data['rows'].sort(key=lambda r: -r['percentile'])
    data['best'] = data['rows'][0]
    data['has_data'] = True
    return data


# ---------------------------------------------------------------------------
# 13 · Marking turnaround
# ---------------------------------------------------------------------------
def marking_queue(user, limit=5):
    """Work the student has submitted that is still waiting to be marked.

    Also reports the median turnaround on their *already marked* work, so
    "waiting 6 days" can be read against "usually marked in 2".
    """
    data = {'has_data': False, 'pending': [], 'count': 0, 'typical_days': None, 'overdue': 0}
    now = timezone.now()
    pending, turnarounds = [], []

    try:
        from apps.assessments.models import AssessmentAttempt
        for attempt in (AssessmentAttempt.objects
                        .filter(student=user, status=AssessmentAttempt.STATUS_SUBMITTED,
                                submitted_at__isnull=False)
                        .select_related('assessment', 'assessment__module')
                        .order_by('submitted_at')[:20]):
            pending.append({
                'title': attempt.assessment.title,
                'module': attempt.assessment.module,
                'kind': attempt.assessment.get_kind_display(),
                'submitted_at': attempt.submitted_at,
                'days': max(0, (now - attempt.submitted_at).days),
                'url': _safe_url('assessments:result', attempt.public_id),
            })
        # Turnaround on marked attempts: submitted_at → updated_at.
        for row in (AssessmentAttempt.objects
                    .filter(student=user, status=AssessmentAttempt.STATUS_MARKED,
                            submitted_at__isnull=False)
                    .values('submitted_at', 'updated_at')[:50]):
            days = (row['updated_at'] - row['submitted_at']).total_seconds() / 86400.0
            if days >= 0:
                turnarounds.append(days)
    except Exception:
        logger.exception('marking_queue: attempts failed')

    try:
        from apps.assessments.models import AssignmentSubmission
        for submission in (AssignmentSubmission.objects
                           .filter(student=user, status='submitted', submitted_at__isnull=False)
                           .select_related('assessment', 'assessment__module')
                           .order_by('submitted_at')[:20]):
            pending.append({
                'title': submission.assessment.title,
                'module': submission.assessment.module,
                'kind': 'Assignment',
                'submitted_at': submission.submitted_at,
                'days': max(0, (now - submission.submitted_at).days),
                'url': _safe_url('assessments:index'),
            })
        for row in (AssignmentSubmission.objects
                    .filter(student=user, status__in=['marked', 'returned', 'completed'],
                            submitted_at__isnull=False)
                    .values('submitted_at', 'updated_at')[:50]):
            days = (row['updated_at'] - row['submitted_at']).total_seconds() / 86400.0
            if days >= 0:
                turnarounds.append(days)
    except Exception:
        logger.exception('marking_queue: assignments failed')

    if not pending:
        return data

    typical = None
    if turnarounds:
        turnarounds.sort()
        typical = max(1, round(turnarounds[len(turnarounds) // 2]))

    for item in pending:
        # Late once it has waited more than twice the usual turnaround (min 7 days).
        threshold = max(7, (typical or 3) * 2)
        item['tone'] = 'danger' if item['days'] > threshold else (
            'warning' if item['days'] > (typical or 3) else 'success')
        item['late'] = item['tone'] == 'danger'

    pending.sort(key=lambda i: -i['days'])
    data.update({
        'has_data': True, 'pending': pending[:limit], 'count': len(pending),
        'more': max(0, len(pending) - limit),
        'typical_days': typical, 'overdue': sum(1 for i in pending if i['late']),
    })
    return data


# ---------------------------------------------------------------------------
# 14 · Open questions (discussions)
# ---------------------------------------------------------------------------
def open_questions(user, modules, limit=4):
    """Unanswered discussion threads in the student's modules.

    "Unanswered" means open (not closed) with no reply flagged
    :attr:`DiscussionReply.is_answer`. Also counts how many of the student's own
    replies have been accepted as the answer — their answer streak.
    """
    data = {'has_data': False, 'threads': [], 'count': 0, 'answers_given': 0, 'mine_open': 0}
    try:
        from apps.communication.models import Discussion, DiscussionReply
    except Exception:
        return data

    try:
        threads = list(Discussion.objects
                       .filter(module__in=modules, is_closed=False)
                       .exclude(replies__is_answer=True)
                       .select_related('author', 'module')
                       .annotate(replies_n=Count('replies', distinct=True))
                       .order_by('-is_pinned', '-created_at')[:limit * 3])
        data['answers_given'] = DiscussionReply.objects.filter(author=user, is_answer=True).count()
        data['mine_open'] = sum(1 for t in threads if t.author_id == user.id)
    except Exception:
        logger.exception('open_questions failed')
        return data

    if not threads:
        return data
    now = timezone.now()
    for thread in threads[:limit]:
        data['threads'].append({
            'discussion': thread,
            'is_mine': thread.author_id == user.id,
            'replies': thread.replies_n,
            'age_days': max(0, (now - thread.created_at).days),
            'scope': thread.module.name if thread.module_id else 'General',
            'url': thread.get_absolute_url(),
        })
    data['count'] = len(threads)
    data['has_data'] = True
    return data


# ---------------------------------------------------------------------------
# 15 · Engagement matrix (attendance + interaction, per module)
# ---------------------------------------------------------------------------
#: The four things measured per module, and their weight in the overall score.
#: Attendance is measured time in class; the rest is measured time/work on
#: content. Together they answer "is this student actually engaging?".
ENGAGEMENT_COLUMNS = [
    ('lessons', 'Lessons', 'bi-journal-richtext', 0.35),
    ('assessments', 'Assessments', 'bi-ui-checks', 0.30),
    ('attendance', 'Attendance', 'bi-person-check', 0.25),
    ('tasks', 'Tasks', 'bi-check2-square', 0.10),
]


def engagement_matrix(user, modules, attendance=None):
    """A module × activity matrix of how much the student is actually doing.

    Each cell is 0–100 and comes from measured behaviour, not self-reporting:

    * **Lessons** — mean ``StudySession.completion_pct`` over the module's
      published lessons, counting un-started lessons as zero so the number
      reflects coverage rather than only what was opened.
    * **Assessments** — share of the module's open/closed assessments the
      student has actually submitted.
    * **Attendance** — measured share of class sessions attended (from
      :func:`attendance_rings`, which is itself driven by heartbeat time).
    * **Tasks** — mean ``TaskAssignment.progress`` for that module.

    A column with nothing to measure yet is ``None`` and drops out of the row's
    score rather than dragging it to zero. Returns ``{'columns', 'rows',
    'overall', 'has_data'}``.
    """
    data = {'columns': [{'key': k, 'label': l, 'icon': i} for k, l, i, _w in ENGAGEMENT_COLUMNS],
            'rows': [], 'overall': 0, 'has_data': False}
    if not modules:
        return data

    lesson_totals, lesson_done = {}, {}
    try:
        from apps.learning.models import Lesson, StudySession
        for row in (Lesson.objects.filter(module__in=modules, status=Lesson.STATUS_PUBLISHED)
                    .values('module_id').annotate(n=Count('id'))):
            lesson_totals[row['module_id']] = row['n']
        # Sum of completion across the student's sessions, best per lesson.
        best = {}
        for row in (StudySession.objects.filter(student=user, lesson__module__in=modules)
                    .values('lesson_id', 'lesson__module_id')
                    .annotate(pct=Max('completion_pct'))):
            best.setdefault(row['lesson__module_id'], []).append(min(100, row['pct'] or 0))
        lesson_done = best
    except Exception:
        logger.exception('engagement_matrix: lessons failed')

    assess_totals, assess_done = {}, {}
    try:
        from apps.assessments.models import Assessment, AssessmentAttempt
        for row in (Assessment.objects.filter(module__in=modules, status__in=['open', 'closed'])
                    .values('module_id').annotate(n=Count('id'))):
            assess_totals[row['module_id']] = row['n']
        for row in (AssessmentAttempt.objects
                    .filter(student=user, assessment__module__in=modules,
                            status__in=['submitted', 'marked'])
                    .values('assessment__module_id')
                    .annotate(n=Count('assessment_id', distinct=True))):
            assess_done[row['assessment__module_id']] = row['n']
    except Exception:
        logger.exception('engagement_matrix: assessments failed')

    task_pct = {}
    try:
        from apps.tasks.models import TaskAssignment
        for row in (TaskAssignment.objects.filter(user=user, task__module__in=modules)
                    .values('task__module_id').annotate(p=Avg('progress'))):
            task_pct[row['task__module_id']] = round(row['p'] or 0)
    except Exception:
        pass  # the tasks app may not scope tasks to a module

    attendance_pct = {}
    for row in (attendance or {}).get('rows', []):
        attendance_pct[row['module'].id] = row['pct']

    weights = {k: w for k, _l, _i, w in ENGAGEMENT_COLUMNS}
    scores = []
    for module in modules:
        cells = {}

        total = lesson_totals.get(module.id, 0)
        if total:
            # Un-started lessons count as 0 — coverage, not just what was opened.
            pcts = lesson_done.get(module.id, [])
            cells['lessons'] = round(sum(pcts) / total) if pcts else 0
        else:
            cells['lessons'] = None

        total = assess_totals.get(module.id, 0)
        cells['assessments'] = _pct(assess_done.get(module.id, 0), total) if total else None
        cells['attendance'] = attendance_pct.get(module.id)
        cells['tasks'] = task_pct.get(module.id)

        available = {k: v for k, v in cells.items() if v is not None}
        if available:
            weight_sum = sum(weights[k] for k in available) or 1
            score = round(sum(v * weights[k] for k, v in available.items()) / weight_sum)
        else:
            score = None

        data['rows'].append({
            'module': module,
            'cells': [{'key': k, 'value': cells[k],
                       'tone': _engagement_tone(cells[k])} for k, _l, _i, _w in ENGAGEMENT_COLUMNS],
            'score': score,
            'tone': _engagement_tone(score),
            'label': _engagement_label(score),
        })
        if score is not None:
            scores.append(score)

    if scores:
        data['overall'] = round(sum(scores) / len(scores))
        data['has_data'] = True
    data['overall_tone'] = _engagement_tone(data['overall'])
    data['overall_label'] = _engagement_label(data['overall'])
    return data


def _engagement_tone(value):
    if value is None:
        return 'secondary'
    return 'success' if value >= 70 else ('warning' if value >= 40 else 'danger')


def _engagement_label(value):
    if value is None:
        return 'No data'
    return 'Strong' if value >= 70 else ('Patchy' if value >= 40 else 'At risk')


# ---------------------------------------------------------------------------
# 16 · "Right now" focus bar
# ---------------------------------------------------------------------------
def focus_now(user, context):
    """Pick the single highest-priority next action from everything else.

    Ordered by how time-critical it is: a call already running beats a paper
    closing today, which beats overdue marking, which beats resuming a course.
    Returns ``None`` when there is genuinely nothing to nudge about.
    """
    # 1. A live session in progress — you can only join it now.
    for session in context.get('live_sessions') or []:
        if session['is_live']:
            return {'kicker': 'Happening now', 'tone': 'danger', 'icon': 'bi-broadcast',
                    'title': session['room'].title,
                    'body': f"Your {session['module'].name} session is live." if session['module']
                            else 'Your live session has started.',
                    'cta': 'Join now', 'url': session['url']}

    # 2. A session starting within the hour.
    for session in context.get('live_sessions') or []:
        if 0 < (session['starts_in_minutes'] or 0) <= 60:
            return {'kicker': 'Starting soon', 'tone': 'warning', 'icon': 'bi-camera-video',
                    'title': session['room'].title,
                    'body': f"Starts in {session['starts_in_minutes']} minutes.",
                    'cta': 'Open room', 'url': session['url']}

    # 3. An assessment closing within 2 days.
    closing = [r for r in (context.get('readiness') or [])
               if r['closes_in_days'] is not None and r['closes_in_days'] <= 2]
    if closing:
        item = min(closing, key=lambda r: (r['closes_in_days'], r['score']))
        when = 'today' if item['closes_in_days'] == 0 else f"in {item['closes_in_days']} day" \
                                                           f"{'s' if item['closes_in_days'] != 1 else ''}"
        return {'kicker': f'Closes {when}', 'tone': item['tone'], 'icon': 'bi-clipboard-pulse',
                'title': item['assessment'].title,
                'body': f"{item['band']} — {item['advice']}",
                'cta': 'Open assessment', 'url': item['url']}

    # 4. An overdue task.
    for assignment in context.get('my_tasks') or []:
        due = getattr(getattr(assignment, 'task', None), 'due_date', None)
        # ``Task.due_date`` is a DateTimeField — compare it against ``now()``,
        # not ``localdate()``, which raises TypeError and takes the whole focus
        # panel down with it (matches Task.is_overdue).
        if due and due < timezone.now():
            return {'kicker': 'Overdue', 'tone': 'danger', 'icon': 'bi-exclamation-triangle',
                    'title': assignment.task.title,
                    'body': f'Was due {due:%d %b}. Clear it before it stacks up.',
                    'cta': 'Open task', 'url': getattr(assignment.task, 'get_absolute_url', lambda: '/tasks/')()
                           if callable(getattr(assignment.task, 'get_absolute_url', None)) else '/tasks/'}

    # 5. The least-ready assessment still open.
    if context.get('readiness'):
        item = min(context['readiness'], key=lambda r: r['score'])
        if item['score'] < READY_BAND:
            return {'kicker': 'Prepare next', 'tone': item['tone'], 'icon': 'bi-clipboard-pulse',
                    'title': item['assessment'].title,
                    'body': f"{item['score']}/100 ready — {item['advice']}",
                    'cta': 'Start preparing', 'url': item['url']}

    # 6. Resume the least-complete module that has somewhere to resume.
    for row in context.get('coverage_rows') or []:
        if row['next_url'] and row['pct'] < 100:
            title = getattr(row['next_item'], 'display_title', None) or row['module'].name
            return {'kicker': 'Pick up where you left off', 'tone': 'info', 'icon': 'bi-play-circle',
                    'title': title,
                    'body': f"{row['module'].name} — {row['done']} of {row['total']} {row['unit']} done.",
                    'cta': 'Resume', 'url': row['next_url']}

    # 7. A question you could answer.
    questions = context.get('questions') or {}
    for thread in questions.get('threads') or []:
        if not thread['is_mine']:
            return {'kicker': 'Help a classmate', 'tone': 'info', 'icon': 'bi-question-circle',
                    'title': thread['discussion'].title,
                    'body': f"Unanswered in {thread['scope']} for {thread['age_days']} day"
                            f"{'s' if thread['age_days'] != 1 else ''}.",
                    'cta': 'Answer', 'url': thread['url']}

    # 8. Keep the streak alive.
    trend = context.get('trend') or {}
    if trend.get('streak'):
        return {'kicker': 'Keep it going', 'tone': 'success', 'icon': 'bi-fire',
                'title': f"{trend['streak']}-day study streak",
                'body': 'A short session today keeps the run alive.',
                'cta': 'Open lessons', 'url': '/learning/'}
    return None


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def student_dashboard(user, my_tasks=None):
    """Assemble every panel the ``/myhub/`` dashboard renders, in one call.

    ``my_tasks`` is the task-assignment list the view already loaded; passing it
    in lets :func:`focus_now` consider an overdue task without re-querying.
    """
    if not getattr(user, 'is_authenticated', False):
        return {}

    # One bag of per-request loads shared by every panel below, so the same
    # rows are not fetched four times over.
    cache = {}
    modules = enrolled_modules(user)
    completion = _completion_index(user, modules)
    progress_rows = module_coverage(user, modules, completion, cache)
    summary = academic_summary(user, modules, completion, progress_rows, cache)
    trend = momentum(user)
    pace = pace_profile(user)
    mastery = mastery_map(user, modules, cache)
    readiness = assessment_readiness(user, modules, completion)
    countdown = exam_countdown(user, cache=cache)
    exam_day = (countdown or {}).get('date')
    forecast = completion_forecast(user, progress_rows, trend.get('this_week_minutes') or 0,
                                   deadline=exam_day.date() if exam_day else None)
    finance = finance_summary(user)
    badges = achievements(user, summary, trend.get('streak', 0))

    context = {
        'summary': summary,
        'coverage_rows': progress_rows,
        'readiness': readiness,
        'pace': pace,
        'trend': trend,
        'mastery': mastery,
        'forecast': forecast,
        'finance': finance,
        'achievements': badges,
        'attendance': attendance_rings(user, modules),
        'cohort': cohort_standing(user, modules, cache),
        'engagement': None,   # filled below — it reads the attendance rows

        'marking': marking_queue(user),
        'questions': open_questions(user, modules),
        'live_sessions': live_sessions(user, modules),
        'notices': notice_board(user),
        'recent_messages': recent_messages(user),
        'recent_notifications': recent_notifications(user),
        'unread': unread_counts(user),
    }
    context['engagement'] = engagement_matrix(user, modules, context['attendance'])
    context['insights'] = study_insights(summary, pace, trend, forecast, readiness, mastery,
                                         context['attendance'], context['marking'],
                                         context['engagement'])
    # The academic spine: what they are registered for, and the exam they are
    # counting down to. These replace the old course/module framing.
    context['standing'] = programme_standing(user, cache)
    context['module_rows'] = module_progress(user, completion)
    context['countdown'] = countdown
    context['prediction'] = exam_readiness(user)
    # The focus bar reads every other panel, so it is resolved last.
    context['focus'] = focus_now(user, dict(context, my_tasks=my_tasks or []))
    return context


# ---------------------------------------------------------------------------
# Exam readiness — predicted from results, and nothing else
# ---------------------------------------------------------------------------
#: How much each kind of result counts toward the prediction.
#:
#: A mock exam / past paper under exam conditions is the closest thing there is
#: to the real paper, so it dominates; a quiz says the least. These are the one
#: place to tune the model — change the numbers here and the whole prediction
#: moves. They are a starting position, set to be replaced once the real
#: assessment blueprints and past papers land.
READINESS_WEIGHTS = {
    'mock_exam': 5.0,
    'exam_section': 4.0,
    'test': 3.0,
    'assignment': 2.0,
    'quiz': 1.0,
}

#: Results older than this contribute at a reduced weight — a mark from eight
#: months ago describes a different candidate to the one sitting next month.
READINESS_HALF_LIFE_DAYS = 120

#: Below this many weighted results the prediction is labelled provisional
#: rather than presented as a number to trust.
READINESS_MIN_RESULTS = 3

READINESS_LABELS = {
    'mock_exam': 'Mock exams', 'exam_section': 'Exam sections',
    'test': 'Tests', 'assignment': 'Assignments', 'quiz': 'Quizzes',
}

READINESS_BANDS = [
    (75, 'On track', 'success', 'Your marks are where they need to be. Hold the pattern.'),
    (60, 'Nearly there', 'info', 'Close. Convert the near-misses and you are through.'),
    (45, 'At risk', 'warning', 'The marks say more work is needed before the paper.'),
    (0, 'Off track', 'danger', 'Start with the weakest subject and get a practice test marked.'),
]


def exam_readiness(user):
    """Predict how ready the candidate is, from their marked results alone.

    Deliberately narrow. Coverage of study material used to be 40% of this
    score, and it cannot be any more — modules carry study guides, blueprints
    and past papers rather than a fixed set of segments to complete, so there is
    nothing honest to measure "coverage" against. What is left is the thing that
    actually predicts an exam result: previous exam results.

    Each marked attempt contributes its percentage, weighted by
    :data:`READINESS_WEIGHTS` for its kind and decayed by age. Returns ``None``
    when there is nothing marked yet — an unbacked prediction is worse than no
    prediction, so the panel says "not enough yet" instead of inventing one.
    """
    try:
        from apps.assessments.models import AssessmentAttempt

        # `score` is raw marks; the percentage is against the paper's total, so
        # a 40/50 test and an 80/100 exam compare on the same scale.
        attempts = list(
            AssessmentAttempt.objects
            .filter(student=user, status='marked')
            .select_related('assessment')
            .order_by('-submitted_at')[:60])
        if not attempts:
            return None

        now = timezone.now()
        counted = 0
        total_weight = weighted_sum = 0.0
        per_kind, best_mock = {}, None

        for attempt in attempts:
            kind = getattr(attempt.assessment, 'kind', 'quiz')
            base = READINESS_WEIGHTS.get(kind, 1.0)
            when = attempt.submitted_at or attempt.created_at or now
            age_days = max((now - when).days, 0)
            decay = 0.5 ** (age_days / READINESS_HALF_LIFE_DAYS)
            weight = base * decay
            total_marks = _f(getattr(attempt.assessment, 'total_marks', 0))
            if total_marks <= 0:
                continue                       # nothing to take a percentage of
            pct = max(0.0, min(_f(attempt.score) / total_marks * 100, 100))

            weighted_sum += pct * weight
            total_weight += weight
            bucket = per_kind.setdefault(kind, {'n': 0, 'sum': 0.0})
            bucket['n'] += 1
            bucket['sum'] += pct
            if kind == 'mock_exam' and (best_mock is None or pct > best_mock):
                best_mock = pct
            counted += 1

        if total_weight <= 0:
            return None

        score = round(weighted_sum / total_weight)
        band, tone, advice = next(
            (label, tone, advice) for floor, label, tone, advice in READINESS_BANDS
            if score >= floor)

        breakdown = [
            {'kind': kind,
             'label': READINESS_LABELS.get(kind, kind.replace('_', ' ').title()),
             'count': data['n'],
             'average': round(data['sum'] / data['n']),
             'weight': READINESS_WEIGHTS.get(kind, 1.0)}
            for kind, data in sorted(per_kind.items(),
                                     key=lambda kv: -READINESS_WEIGHTS.get(kv[0], 1.0))
        ]

        return {
            'score': score,
            'band': band,
            'tone': tone,
            'advice': advice,
            'results_counted': counted,
            'breakdown': breakdown,
            'best_mock': best_mock,
            'is_provisional': counted < READINESS_MIN_RESULTS,
            'has_mock': 'mock_exam' in per_kind,
        }
    except Exception:  # pragma: no cover
        logger.exception('dashboard: exam readiness failed')
        return None


# ---------------------------------------------------------------------------
# The academic spine — programme standing, modules, and the run to the exam
# ---------------------------------------------------------------------------
def programme_standing(user, cache=None):
    """Where this candidate sits on the spine: institution, programme, cohort.

    Returns ``None`` when they are not registered for anything, which is what
    the dashboard checks before drawing the strip.
    """
    try:
        from apps.learning.models import ModuleEnrolment

        enrolment = _programme_enrolment(user, cache)
        if enrolment is None:
            return None
        person = enrolment.person

        modules = list(ModuleEnrolment.objects.filter(person=person)
                       .select_related('programme_module__module'))
        unlocked = [m for m in modules if m.is_unlocked]
        monthly = sum((m.price or 0) for m in modules)
        return {
            'programme': enrolment.programme,
            'institution': enrolment.programme.institution,
            'cohort': enrolment.cohort,
            'modules_total': len(modules),
            'modules_unlocked': len(unlocked),
            'modules_locked': len(modules) - len(unlocked),
            'monthly': monthly,
            'on_trial': any(m.status == ModuleEnrolment.STATUS_TRIAL for m in modules),
        }
    except Exception:  # pragma: no cover - never break the dashboard
        logger.exception('dashboard: programme standing failed')
        return None


def module_progress(user, completion=None):
    """One row per registered module: what it is, and whether it is open.

    Deliberately thin on "progress". A module's teaching content is authored per
    institution and is not modelled yet, so anything richer than lock state and
    price would be inventing a number. The row carries what is actually known
    and leaves room for coverage once modules carry material.
    """
    rows = []
    try:
        from apps.learning.models import ModuleEnrolment

        person = getattr(user, 'profile', None)
        if person is None:
            return rows
        for enrolment in (ModuleEnrolment.objects.filter(person=person)
                          .select_related('programme_module__module',
                                          'programme_module__programme__institution')
                          .order_by('programme_module__order', 'programme_module__id')):
            offering = enrolment.programme_module
            rows.append({
                'enrolment': enrolment,
                'offering': offering,
                'name': offering.display_name,
                'code': offering.code,
                'institution': offering.programme.institution,
                'status': enrolment.status,
                'status_label': enrolment.get_status_display(),
                'is_unlocked': enrolment.is_unlocked,
                'price': enrolment.price,
                'trial_ends_at': enrolment.trial_ends_at,
                'paid_until': enrolment.paid_until,
                'tone': {'active': 'success', 'trial': 'info',
                         'locked': 'warning', 'expired': 'danger'}.get(enrolment.status, 'secondary'),
            })
    except Exception:  # pragma: no cover
        logger.exception('dashboard: module progress failed')
    return rows


def _programme_enrolment(user, cache=None):
    """The candidate's current registration, fetched once per request.

    ``programme_standing``, ``module_progress`` and ``exam_countdown`` all
    needed it and each looked it up separately.
    """
    if cache is not None and 'enrolment' in cache:
        return cache['enrolment']
    row = None
    try:
        from apps.learning.models import ProgrammeEnrolment
        person = getattr(user, 'profile', None)
        if person is not None:
            row = (ProgrammeEnrolment.objects.filter(person=person)
                   .select_related('programme__institution', 'cohort')
                   .order_by('-created_at').first())
    except Exception:  # pragma: no cover
        logger.exception('dashboard: programme enrolment lookup failed')
    if cache is not None:
        cache['enrolment'] = row
    return row


def exam_countdown(user, window_days=400, cache=None):
    """The next examination on the candidate's institution calendar.

    Returns the date, the days remaining, and how far along the run-up is as a
    percentage — a line that fills a little every day rather than a ring that
    means nothing in particular. ``elapsed_pct`` is measured from the day the
    countdown started (the previous exam, or the registration date, whichever is
    later) so the bar grows at a real rate instead of a guessed one.

    Unpublished (provisional) dates are included and flagged — the seeded
    academic calendars start that way, and a provisional date a candidate can
    see beats an empty panel. ``None`` when there is no dated exam ahead.
    """
    try:
        from apps.learning.models import CalendarEvent

        enrolment = _programme_enrolment(user, cache)
        if enrolment is None:
            return None

        now = timezone.now()
        # One window spanning both directions: the dates ahead (the countdown)
        # and the last one behind it (where the run-up started). Two separate
        # queries fetched overlapping rows off the same index for no reason.
        window = (CalendarEvent.objects
                  .filter(calendar__institution=enrolment.programme.institution,
                          kind__in=[CalendarEvent.KIND_EXAM, CalendarEvent.KIND_TEST],
                          start__gte=now - timedelta(days=window_days),
                          start__lte=now + timedelta(days=window_days))
                  .select_related('calendar', 'programme_module')
                  .order_by('start'))
        # Whole-school dates and the candidate's own grade only — another
        # grade's exam (or a subject test in another grade) is not their countdown.
        mine = enrolment.programme_id
        rows = [e for e in window
                if e.programme_id == mine
                or (e.programme_id is None
                    and (e.programme_module_id is None or e.programme_module.programme_id == mine))]
        upcoming = [e for e in rows if e.start >= now]
        if not upcoming:
            return None

        exam = upcoming[0]
        days_left = max((exam.start.date() - now.date()).days, 0)

        # Where the run-up started: the last exam/test that has already passed,
        # else the day they registered. That is the honest zero point.
        past = [e for e in rows if e.start < now]
        previous = past[-1] if past else None
        started = previous.start if previous else enrolment.created_at
        total_days = max((exam.start.date() - started.date()).days, 1)
        elapsed = max(total_days - days_left, 0)

        return {
            'event': exam,
            'title': exam.title,
            'kind': exam.get_kind_display(),
            'date': exam.start,
            'days_left': days_left,
            'total_days': total_days,
            'elapsed_days': elapsed,
            'elapsed_pct': min(round(elapsed / total_days * 100), 100),
            'is_imminent': days_left <= 7,
            # Spine dates start life provisional: the shape of the year comes
            # from the institution's brand pack, the exact day does not. Say so
            # rather than let someone plan around a date we guessed.
            'is_provisional': not exam.is_published,
            'institution': enrolment.programme.institution,
            'programme': enrolment.programme,
            'later': list(upcoming[1:4]),
        }
    except Exception:  # pragma: no cover
        logger.exception('dashboard: exam countdown failed')
        return None
