"""Auto-marking for objective questions + attempt grading.

``mark_answer`` scores a single :class:`Answer` where the type allows it:

* ``mcq`` / ``tf``      — one selected choice, must be the correct one.
* ``multi``            — the selected choice set must equal the correct set.
* ``fill`` / ``short`` — free text matched against the question ``marking`` key
  (keywords / synonyms / alt spellings, and any required phrases).
* ``matching`` / ``ordering`` — the response is compared to the answer key in
  the question ``config``.
* ``schedule``         — a numeric computation, marked line by line against the
  solution workbook's own mark grid. See :mod:`apps.assessments.schedule_marking`;
  it is the only type here that awards *partial* marks, because a ladder of
  eighteen scoring points is eighteen decisions, not one.

Subjective types (``long``/``essay``/``file_upload``/…) can't be auto-marked, so
they are left for an educator; :func:`grade_attempt` sets the attempt to
``submitted`` (awaiting marking) when any exist, else ``marked``.
"""

import re

from django.utils import timezone


def _norm(text):
    return re.sub(r'\s+', ' ', str(text or '')).strip().lower()


def _text_matches(text, marking):
    """True when ``text`` satisfies a free-text ``marking`` key."""
    answer = _norm(text)
    if not answer:
        return False
    accepted = set()
    for field in ('keywords', 'synonyms', 'alt_spellings', 'answers'):
        for value in (marking.get(field) or []):
            accepted.add(_norm(value))
    required = [_norm(p) for p in (marking.get('required_phrases') or []) if _norm(p)]

    if required and not all(phrase in answer for phrase in required):
        return False
    if not accepted:
        # No accepted list but required phrases were all present → correct.
        return bool(required)
    # Correct if the answer equals or contains any accepted term.
    return any(term and (term == answer or term in answer or answer in term) for term in accepted)


def mark_answer(answer):
    """Return ``(awarded_marks, is_correct)`` for an objective answer.

    Non-objective questions return ``(0, False)`` — they are marked by a human.
    """
    question = answer.question
    marks = float(question.marks or 0)
    qtype = question.type

    if qtype in ('mcq', 'tf'):
        correct = set(question.choices.filter(is_correct=True).values_list('id', flat=True))
        chosen = set(answer.selected_choices.values_list('id', flat=True))
        ok = bool(correct) and chosen == correct
        return (marks if ok else 0, ok)

    if qtype == 'multi':
        correct = set(question.choices.filter(is_correct=True).values_list('id', flat=True))
        chosen = set(answer.selected_choices.values_list('id', flat=True))
        ok = bool(correct) and chosen == correct
        return (marks if ok else 0, ok)

    if qtype in ('fill', 'short'):
        text = (answer.response or {}).get('text', '')
        ok = _text_matches(text, question.marking or {})
        return (marks if ok else 0, ok)

    if qtype in ('matching', 'ordering'):
        key = (question.config or {}).get('answer')
        given = (answer.response or {}).get('value')
        ok = key is not None and given == key
        return (marks if ok else 0, ok)

    if qtype == 'schedule':
        # The one partially-marked type: each line of the computation is its own
        # scoring decision, and the per-line breakdown is kept on the answer so
        # the candidate can see their ladder beside the model one.
        from .schedule_marking import mark_schedule, store_breakdown
        awarded, ok, breakdown = mark_schedule(answer)
        store_breakdown(answer, breakdown)
        return (float(awarded), ok)

    # Subjective — needs a human.
    return (0, False)


def _has_response(answer):
    """Whether the student actually gave an answer (worth manual marking)."""
    response = answer.response or {}
    return bool(response.get('text') or response.get('value') or response.get('lines')
                or answer.file or answer.selected_choices.exists())


def grade_attempt(attempt):
    """(Re)grade an attempt: auto-mark ``auto`` questions, tally educator-marked
    ``manual`` ones, and set score/passed/status.

    Idempotent — safe to call on first submit *and* after each manual mark. The
    attempt stays ``submitted`` while any answered manual question is unmarked,
    and flips to ``marked`` once none remain. Saving fires the reports signal
    that recomputes the module grade."""
    assessment = attempt.assessment
    questions = _assessment_questions(assessment)
    answers = {a.question_id: a for a in attempt.answers.prefetch_related('selected_choices').all()}

    total_awarded = 0.0
    pending_manual = 0
    for question in questions:
        answer = answers.get(question.id)
        if answer is None:
            continue
        if question.is_auto_marked:
            marks, ok = mark_answer(answer)
            answer.awarded_marks = marks
            answer.is_correct = ok
            answer.marked = True
            # ``response`` is in the update list because a schedule's marker
            # writes its per-line breakdown back onto it.
            answer.save(update_fields=['awarded_marks', 'is_correct', 'marked', 'response'])
            total_awarded += marks
        elif _has_response(answer):
            # Manual question with a real response: pending until an educator marks it.
            if not answer.marked:
                pending_manual += 1
            total_awarded += float(answer.awarded_marks or 0)
        elif not answer.marked:
            # Manual question left blank → nothing to mark, award 0.
            answer.marked = True
            answer.save(update_fields=['marked'])

    from .models import AssessmentAttempt
    attempt.score = round(total_awarded, 2)
    total_marks = float(assessment.total_marks or 0)
    pct = (attempt.score / total_marks * 100) if total_marks else 0
    attempt.passed = pct >= float(assessment.pass_mark_pct or 0)
    attempt.status = (AssessmentAttempt.STATUS_SUBMITTED if pending_manual
                      else AssessmentAttempt.STATUS_MARKED)
    if not attempt.submitted_at:
        attempt.submitted_at = timezone.now()
    attempt.save()
    return attempt


def pending_manual_count(attempt):
    """How many answered manual questions still await an educator's mark."""
    count = 0
    answers = {a.question_id: a for a in attempt.answers.prefetch_related('selected_choices').all()}
    for question in _assessment_questions(attempt.assessment):
        answer = answers.get(question.id)
        if answer and not question.is_auto_marked and not answer.marked and _has_response(answer):
            count += 1
    return count


def _assessment_questions(assessment):
    """All questions across an assessment's sections, in order."""
    from .models import Question
    return list(Question.objects.filter(section__assessment=assessment)
                .select_related('section').order_by('section__order', 'order', 'id'))
