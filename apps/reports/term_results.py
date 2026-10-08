"""Term results (GDE four-term year): automatic marks, mark sheets, year summary.

How a learner's subject mark is built, the way a South African school does it:

* **Automatic (``auto_pct``)** — every quiz, test, mock paper and assignment the
  learner has had marked on the platform in that subject, dated inside the term
  (the assessment's closing date, else its opening date, else when it was
  created). Weighted by each assessment's ``weight``. Extra-credit work is left
  out. Online *exam papers* (kind ``exam_section``) are kept apart as the
  automatic **exam** suggestion (:func:`compute_auto_exam`).
* **SBA (``sba_pct``)** — the term's School-Based Assessment mark the subject
  educator records on the mark sheet. Left blank, the automatic mark stands.
* **Exam (``exam_pct``)** — the mid-year (Term 2) and final (Term 4)
  examinations, from Grade 4 up (Foundation Phase, and FET Life Orientation, are
  100 % SBA).
* **Term mark** — SBA and exam combined with the CAPS weight for the phase
  (:meth:`TermResult.recompute` → ``core.school.final_mark``).
* **Final (promotion) mark** — the year's SBA (mean of the four terms) and the
  Term 4 final exam, combined with the same CAPS weight.

Learners and parents only ever see **published** results.
"""
from decimal import Decimal, InvalidOperation

from django.db.models import Q
from django.db.models.functions import Coalesce
from django.utils import timezone

from core import school

from . import terms
from .models import DEFAULT_GRADE_SCALE, TermResult

LEVEL_DESCRIPTORS = {int(band['letter']): band['label'] for band in DEFAULT_GRADE_SCALE}


def level_descriptor(level):
    try:
        return LEVEL_DESCRIPTORS.get(int(level), '')
    except (TypeError, ValueError):
        return ''


def grade_of(module):
    return module.programme.grade or 1


def exam_applies(module, term):
    """Does this subject write an examination in ``term``?"""
    return int(term) in terms.EXAM_TERMS and school.sba_weight(grade_of(module), module.code) < 100


# ---------------------------------------------------------------------------
# Automatic marks
# ---------------------------------------------------------------------------
def _term_assessments(module, year, term):
    from apps.assessments.models import Assessment
    start, end = terms.term_window(year, term)
    return (Assessment.objects
            .filter(Q(module=module) | Q(topic__programme_module=module), is_extra_credit=False)
            .annotate(term_date=Coalesce('available_to', 'available_from', 'created_at'))
            .filter(term_date__date__gte=start, term_date__date__lte=end)
            .distinct())


def _weighted(student, assessments):
    from .services import _assessment_best_pct, _weighted_mean
    pairs = []
    for assessment in assessments:
        pct = _assessment_best_pct(student, assessment)
        if pct is not None:
            pairs.append((min(100.0, max(0.0, pct)), float(assessment.weight or 1)))
    mean = _weighted_mean(pairs)
    return None if mean is None else round(mean, 1)


def compute_auto(student, module, year, term):
    """% from the learner's marked quizzes / tests / assignments / mock papers in
    ``module`` dated inside the term, or ``None`` when nothing has been marked."""
    from apps.assessments.models import Assessment
    qs = _term_assessments(module, year, term).exclude(kind=Assessment.KIND_EXAM_SECTION)
    return _weighted(student, qs)


def compute_auto_exam(student, module, year, term):
    """% from online exam papers written in the term (exam terms only), or ``None``."""
    if not exam_applies(module, term):
        return None
    from apps.assessments.models import Assessment
    qs = _term_assessments(module, year, term).filter(kind=Assessment.KIND_EXAM_SECTION)
    return _weighted(student, qs)


def _dec(value):
    return None if value is None else Decimal(str(value))


def enrolled_students(module):
    """Active learner accounts enrolled on this subject offering."""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    return (User.objects
            .filter(is_active=True, profile__module_enrolments__programme_module=module)
            .exclude(profile__user_type__in=('educator', 'staff', 'admin', 'parent'))
            .distinct().order_by('last_name', 'first_name', 'username'))


def refresh_term(module, year, term):
    """Create / update a :class:`TermResult` per enrolled learner.

    Refills ``auto_pct`` and recomputes the term mark; everything the educator
    entered (SBA, exam, comment, status) is kept. Returns the results, in the
    order of :func:`enrolled_students`.
    """
    year, term = int(year), int(term)
    existing = {r.student_id: r for r in
                TermResult.objects.filter(module=module, year=year, term=term)}
    rows = []
    for student in enrolled_students(module):
        result = existing.get(student.pk) or TermResult(
            student=student, module=module, year=year, term=term)
        result.module = module
        auto = _dec(compute_auto(student, module, year, term))
        before = (result.auto_pct, result.term_pct, result.level)
        result.auto_pct = auto
        result.recompute()
        if result.pk is None or before != (result.auto_pct, result.term_pct, result.level):
            result.save()
        result.student = student
        rows.append(result)
    return rows


def parse_pct(raw):
    """``'' → None``; ``'67.5' → Decimal('67.5')``; raises ``ValueError`` outside 0–100."""
    raw = (raw or '').strip().replace('%', '').replace(',', '.')
    if not raw:
        return None
    try:
        value = Decimal(raw)
    except InvalidOperation:
        raise ValueError(f'"{raw}" is not a number')
    if value < 0 or value > 100:
        raise ValueError(f'{raw} is outside 0 – 100')
    return value.quantize(Decimal('0.1'))


def publish(result, by=None):
    """Mark ``result`` published. A blank SBA is frozen to the automatic mark, so
    a quiz marked later never silently moves a published term mark."""
    if result.sba_pct is None and result.auto_pct is not None:
        result.sba_pct = result.auto_pct
    result.recompute()
    result.status = TermResult.STATUS_PUBLISHED
    result.published_at = timezone.now()
    if by is not None:
        result.entered_by = by


def notify_published(results, *, actor=None):
    """Tell each learner (and their linked parents) their term results are out.
    One notification per person per subject sheet; failures never block saving."""
    import logging
    logger = logging.getLogger('apps')
    try:
        from apps.accounts.models import ParentLink
        from apps.communication.services import notify
    except Exception:  # pragma: no cover
        return 0
    sent = 0
    for result in results:
        subject = result.module.display_name
        label = terms.term_label(result.term)
        url = f'/reports/report-card/?year={result.year}&term={result.term}'
        name = result.student.get_full_name() or result.student.get_username()
        try:
            notify(result.student, title=f'{label} results: {subject}',
                   body=f'Your {label} mark for {subject} has been published.',
                   verb='published term results', url=url, actor=actor, category='grades')
            sent += 1
            for link in ParentLink.objects.filter(student=result.student).select_related('parent'):
                notify(link.parent, title=f'{label} results for {name}: {subject}',
                       body=f"{name}'s {label} mark for {subject} has been published.",
                       verb='published term results', url=f'{url}&student={result.student_id}',
                       actor=actor, category='grades')
                sent += 1
        except Exception:
            logger.exception('reports: term-result notification failed for %s', result.pk)
    return sent


# ---------------------------------------------------------------------------
# The year — final marks and promotion
# ---------------------------------------------------------------------------
def programme_for(student, year=None):
    """The grade (Programme) the learner is registered in — the active one first."""
    from apps.learning.models import ProgrammeEnrolment
    enrolment = (ProgrammeEnrolment.objects
                 .filter(person__user=student)
                 .select_related('programme', 'cohort')
                 .order_by('-is_active', '-created_at').first())
    return enrolment


def _subject_rows(student, programme, year, published_only):
    from apps.learning.models import ProgrammeModule
    results = (TermResult.objects
               .filter(student=student, year=year, module__programme=programme)
               .select_related('module', 'module__module', 'module__programme'))
    if published_only:
        results = results.filter(status=TermResult.STATUS_PUBLISHED)
    by_module = {}
    for result in results:
        by_module.setdefault(result.module_id, {})[result.term] = result
    modules = (ProgrammeModule.objects
               .filter(Q(programme=programme, enrolments__person__user=student)
                       | Q(pk__in=list(by_module)))
               .select_related('module', 'programme').distinct().order_by('order', 'id'))
    return [(module, by_module.get(module.pk, {})) for module in modules]


def subject_final(module, term_results):
    """``(sba year mark, final exam, final mark)`` from ``{term: TermResult}``."""
    sbas = []
    for term in terms.TERM_NUMBERS:
        result = term_results.get(term)
        if result is None:
            continue
        value = result.sba_pct if result.sba_pct is not None else result.auto_pct
        if value is not None:
            sbas.append(float(value))
    sba = round(sum(sbas) / len(sbas), 1) if sbas else None
    t4 = term_results.get(4)
    exam = float(t4.exam_pct) if (t4 is not None and t4.exam_pct is not None
                                  and exam_applies(module, 4)) else None
    final = school.final_mark(grade_of(module), module.code, sba, exam)
    return sba, exam, (None if final is None else round(float(final), 1))


def year_summary(student, year, *, programme=None, published_only=True):
    """Everything a year-end report needs, per subject.

    Returns ``{'programme', 'grade', 'year', 'subjects': [...], 'final_marks':
    {code: %}, 'promotion': core.school.evaluate_promotion(...) | None,
    'complete': bool}``. Each subject row carries ``terms`` ({1..4: TermResult or
    None}), ``sba``, ``exam``, ``final``, ``level``, ``descriptor``,
    ``pass_mark`` and ``passed``.
    """
    year = int(year)
    if programme is None:
        enrolment = programme_for(student, year)
        programme = enrolment.programme if enrolment else None
    if programme is None:
        return {'programme': None, 'grade': None, 'year': year, 'subjects': [],
                'final_marks': {}, 'promotion': None, 'complete': False}
    grade = programme.grade or 1
    subjects, finals = [], {}
    for module, results in _subject_rows(student, programme, year, published_only):
        sba, exam, final = subject_final(module, results)
        minimum = school.pass_mark(grade, module.code)
        level = school.achievement_level(final) if final is not None else None
        if final is not None:
            finals[module.code] = final
        subjects.append({
            'module': module, 'code': module.code, 'name': module.display_name,
            'terms': {t: results.get(t) for t in terms.TERM_NUMBERS},
            'sba': sba, 'exam': exam, 'final': final, 'level': level,
            'descriptor': level_descriptor(level), 'pass_mark': minimum,
            'passed': None if final is None else final >= minimum,
            'sba_weight': school.sba_weight(grade, module.code),
        })
    promotion = school.evaluate_promotion(grade, finals) if finals else None
    return {
        'programme': programme, 'grade': grade, 'year': year, 'subjects': subjects,
        'final_marks': finals, 'promotion': promotion,
        'complete': bool(subjects) and all(s['final'] is not None for s in subjects),
    }


def final_marks_for(student, programme, year, *, published_only=False):
    """``{subject code: final %}`` for the learner's subjects in ``programme``.

    Subjects without any mark yet are left out. Draft results count by default
    (the promotion meeting works from the mark sheets); pass
    ``published_only=True`` for what the family has seen.
    """
    summary = year_summary(student, year, programme=programme, published_only=published_only)
    return dict(summary['final_marks'])


# ---------------------------------------------------------------------------
# Office overview
# ---------------------------------------------------------------------------
def sheet_status(modules, year):
    """``{(module id, term): {'draft': n, 'published': n}}`` for ``modules``."""
    from django.db.models import Count
    out = {}
    rows = (TermResult.objects.filter(module__in=modules, year=year)
            .values('module_id', 'term', 'status').annotate(n=Count('id')))
    for row in rows:
        out.setdefault((row['module_id'], row['term']), {'draft': 0, 'published': 0})[row['status']] = row['n']
    return out
