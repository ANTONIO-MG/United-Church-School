"""The weekly teaching sequence, and the gate that enforces it.

:mod:`apps.learning.access` answers *may this person open this at all* — have
they paid, is it published, did they buy this one item. That is a commercial
question. This module answers a different one: **have they earned it yet.**

The documents state the order themselves. The MACF challenge says it outright:

    "Each week, first complete that topic's standard Mock. Then attempt the
    challenge."

So a week is a sequence, not four things presented at once:

    1. Study guide        read first — always open
    2. Questions / mock   sat cold and timed; opens once the guide is opened
    3. Answers / solution released ONLY once the attempt is submitted
    4. Challenge          this week's part of the running scenario; opens after
                          the mock
    5. Mock exam          the full sitting, at the end of the phase

Step 3 — the solution — is the one that matters. A learner who reads the
answer before attempting the question learns nothing, and the entire value of a
taught subject is in the attempt. So the release is tied to *submission*
and enforced here, server-side, rather than being a "please don't look" note
under a link.

Two deliberate design choices:

**The gate advises, it does not hide.** A locked row is still listed with the
reason it is locked — "sit the mock first" is a teaching instruction, and hiding
it would just look like missing content.

**Staff and educators are never sequenced.** They are writing the week; they
have to see the solution beside the question.
"""

import logging

logger = logging.getLogger('apps')

# --- Why a row is shut by the *teaching* sequence, not by money. -------------
LOCK_SEQUENCE = 'sequence'      # an earlier step in the week is not done
LOCK_SOLUTION = 'solution'      # the attempt has not been submitted yet
LOCK_ATTEMPT = 'attempt'        # the paper it answers has not been attempted

SEQUENCE_LOCK_LABELS = {
    LOCK_SEQUENCE: 'Work through this week in order',
    LOCK_SOLUTION: 'Submit your attempt to see the solution',
    LOCK_ATTEMPT: 'Sit the paper first',
}


def _kinds():
    from .models import ModuleMaterial as M
    return M


def sequence_rank(kind):
    """Where a material kind sits in the week's order. Lower comes first.

    Anything not part of the taught sequence (a blueprint, a live session, a
    recording, a loose document) returns ``0`` — it is reference material a
    candidate may open whenever they like, and sequencing it would be arbitrary.
    """
    M = _kinds()
    return {
        M.KIND_STUDY_GUIDE: 1,
        M.KIND_QUESTIONS: 2,
        M.KIND_ASSESSMENT: 2,
        M.KIND_ANSWERS: 3,
        M.KIND_MOCK_EXAM: 4,
    }.get(kind, 0)


#: Kinds that are a *solution* — gated on the candidate's own submission.
def solution_kinds():
    M = _kinds()
    return {M.KIND_ANSWERS}


#: Kinds that are *sat* — an attempt against them is what unlocks the solution.
def attemptable_kinds():
    M = _kinds()
    return {M.KIND_QUESTIONS, M.KIND_ASSESSMENT, M.KIND_MOCK_EXAM}


class WeekProgress:
    """One candidate's progress through one week, resolved in two queries.

    Built once per page by :class:`SequenceGate` for every week on the page at
    once, because a module's schedule is six phases of several weeks and asking
    per material would be a query per row.
    """

    __slots__ = ('opened_lessons', 'submitted_assessments', 'started_assessments')

    def __init__(self, opened_lessons, submitted_assessments, started_assessments):
        self.opened_lessons = opened_lessons
        self.submitted_assessments = submitted_assessments
        self.started_assessments = started_assessments

    def has_opened(self, lesson_id):
        return lesson_id in self.opened_lessons

    def has_submitted(self, assessment_id):
        return assessment_id in self.submitted_assessments


def _load_progress(user, materials):
    """What this candidate has already done, across every material on the page."""
    lesson_ids = {m.lesson_id for m in materials if m.lesson_id}
    assessment_ids = {m.assessment_id for m in materials if m.assessment_id}

    opened, submitted, started = set(), set(), set()
    if not getattr(user, 'is_authenticated', False):
        return WeekProgress(opened, submitted, started)

    if lesson_ids:
        try:
            from .models import StudySession
            opened = set(
                StudySession.objects
                .filter(student=user, lesson_id__in=lesson_ids)
                .values_list('lesson_id', flat=True))
        except Exception:  # pragma: no cover
            logger.exception('sequence: study-session lookup failed')

    if assessment_ids:
        try:
            from apps.assessments.models import AssessmentAttempt as A
            rows = (A.objects
                    .filter(student=user, assessment_id__in=assessment_ids)
                    .values_list('assessment_id', 'status'))
            for assessment_id, status in rows:
                started.add(assessment_id)
                if status in (A.STATUS_SUBMITTED, A.STATUS_MARKED):
                    submitted.add(assessment_id)
        except Exception:  # pragma: no cover
            logger.exception('sequence: attempt lookup failed')

    return WeekProgress(opened, submitted, started)


class SequenceGate:
    """Does the candidate's own work entitle them to this row *yet*?

    Composed with :class:`apps.learning.access.Gate` rather than folded into it:
    money and pedagogy are different questions with different answers, and a row
    can be perfectly paid-for and still not yet earned.

        seq = SequenceGate(request.user, materials, bypass=gate.can_author)
        verdict = seq.check(material, siblings_in_week)
    """

    def __init__(self, user, materials, *, bypass=False):
        self.user = user
        # Staff and the offering's educators write the week — never sequenced.
        self.bypass = bool(bypass)
        self.materials = list(materials)
        self.progress = (WeekProgress(set(), set(), set()) if self.bypass
                         else _load_progress(user, self.materials))

    # -- the rules -----------------------------------------------------------
    def check(self, material, week_materials):
        """``(is_open, reason)`` — ``reason`` is ``None`` when it is open.

        ``week_materials`` is every material in the same week, which is what
        makes "the step before this one" answerable without another query.
        """
        if self.bypass:
            return True, None

        M = _kinds()
        rank = sequence_rank(material.kind)
        if rank == 0:
            return True, None                 # reference material, never sequenced

        # --- The solution gate. The one that matters. ---
        if material.kind in solution_kinds():
            papers = [m for m in week_materials
                      if m.kind in attemptable_kinds() and m.assessment_id]
            if not papers:
                # A solution with no paper beside it is reference material —
                # refusing it would lock a candidate out of something with no
                # way to earn it.
                return True, None
            if any(self.progress.has_submitted(p.assessment_id) for p in papers):
                return True, None
            return False, LOCK_SOLUTION

        # --- Everything else: the step before it must be done. ---
        earlier = [m for m in week_materials
                   if 0 < sequence_rank(m.kind) < rank
                   and m.kind not in solution_kinds()]
        if not earlier:
            return True, None

        for step in earlier:
            if step.lesson_id and not self.progress.has_opened(step.lesson_id):
                return False, LOCK_SEQUENCE
            if step.assessment_id and not self.progress.has_submitted(step.assessment_id):
                return False, LOCK_SEQUENCE
        return True, None

    def next_step(self, week_materials):
        """The one row this candidate should open next in this week, or ``None``.

        What the module page puts a "Start here" / "Continue" button on, so the
        sequence reads as guidance rather than as a wall of padlocks.
        """
        if self.bypass:
            return None
        ordered = sorted((m for m in week_materials if sequence_rank(m.kind)),
                         key=lambda m: (sequence_rank(m.kind), m.order, m.pk))
        for material in ordered:
            is_open, _ = self.check(material, week_materials)
            if not is_open:
                continue
            if material.lesson_id and not self.progress.has_opened(material.lesson_id):
                return material
            if material.assessment_id and not self.progress.has_submitted(material.assessment_id):
                return material
        return None
