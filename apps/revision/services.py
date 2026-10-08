"""Revision: building review cards from marked attempts and scheduling them.

Two gates decide whether a due card may be shown:

* **Module access** — a card from a module the student can no longer open
  (trial lapsed, subscription unpaid) waits until access returns, exactly as
  the module's lessons do. :meth:`ProgrammeModule.is_unlocked_for`.
* **Memo release** — revising a question means seeing its answer, so a card
  whose paper's solution is not yet released to this student is held back.
  :meth:`Assessment.solution_released_for`.

Held cards are not deleted or rescheduled; they surface the moment both gates
open. :func:`due_count` counts only what a review session would actually show.
"""

from collections import OrderedDict
from datetime import timedelta

from django.db import transaction
from django.db.models.functions import TruncDate
from django.utils import timezone

from .models import ReviewCard, ReviewLog

CHOICE_TYPES = ('mcq', 'tf', 'multi')
GRADES = (ReviewLog.AGAIN, ReviewLog.HARD, ReviewLog.GOOD, ReviewLog.EASY)


# ---------------------------------------------------------------------------
# Card creation
# ---------------------------------------------------------------------------
def _when(attempt):
    return attempt.submitted_at or attempt.created_at


def cards_from_attempt(attempt, now=None):
    """Create (or lapse) a card for every answer in ``attempt`` scored below full
    marks. Idempotent: re-running for the same attempt changes nothing, and an
    older attempt never overrides a card a newer attempt already touched.

    Returns ``(created, lapsed)``.
    """
    from apps.assessments.models import AssessmentAttempt

    if attempt.status != AssessmentAttempt.STATUS_MARKED:
        return (0, 0)
    now = now or timezone.now()
    created = lapsed = 0
    answers = attempt.answers.select_related('question')
    for answer in answers:
        question = answer.question
        full = question.marks or 0
        if full <= 0 or not answer.marked or (answer.awarded_marks or 0) >= full:
            continue
        with transaction.atomic():
            card, made = ReviewCard.objects.select_for_update().get_or_create(
                user_id=attempt.student_id, question=question,
                defaults={'source_attempt': attempt, 'due_at': now, 'box': 1})
            if made:
                created += 1
                continue
            if card.source_attempt_id == attempt.id:
                continue
            source = card.source_attempt
            if source is not None and _when(attempt) <= _when(source):
                continue
            # Wrong again in a later paper: it has been forgotten, start over.
            card.box = 1
            card.streak = 0
            card.lapses += 1
            card.due_at = min(card.due_at, now)
            card.source_attempt = attempt
            card.save(update_fields=['box', 'streak', 'lapses', 'due_at', 'source_attempt'])
            lapsed += 1
    return (created, lapsed)


# ---------------------------------------------------------------------------
# Scheduling
# ---------------------------------------------------------------------------
def grade_card(card, grade, now=None):
    """Apply a self-grade and reschedule. Again → box 1; Hard → same box;
    Good → up one box; Easy → up two. Returns the :class:`ReviewLog`."""
    if grade not in GRADES:
        raise ValueError(f'Unknown grade {grade!r}')
    now = now or timezone.now()
    before = card.box
    if grade == ReviewLog.AGAIN:
        card.box = ReviewCard.BOX_MIN
        card.streak = 0
        card.lapses += 1
    else:
        step = {ReviewLog.HARD: 0, ReviewLog.GOOD: 1, ReviewLog.EASY: 2}[grade]
        card.box = max(ReviewCard.BOX_MIN, min(ReviewCard.BOX_MAX, before + step))
        card.streak += 1
    card.due_at = now + ReviewCard.interval_for(card.box)
    card.last_reviewed_at = now
    card.save(update_fields=['box', 'streak', 'lapses', 'due_at', 'last_reviewed_at'])
    return ReviewLog.objects.create(card=card, user_id=card.user_id, grade=grade,
                                    box_before=before, box_after=card.box, reviewed_at=now)


def check_choices(question, chosen_ids):
    """Whether the chosen choice ids are exactly the correct set."""
    correct = set(question.choices.filter(is_correct=True).values_list('id', flat=True))
    return bool(correct) and set(chosen_ids) == correct


# ---------------------------------------------------------------------------
# What may be shown
# ---------------------------------------------------------------------------
def module_of(question):
    """The ProgrammeModule a question's paper belongs to, or ``None``."""
    assessment = question.section.assessment
    if assessment.module_id:
        return assessment.module
    if assessment.topic_id:
        return assessment.topic.programme_module
    return None


class _Gate:
    """Per-request memo of the access and release checks — one query per module
    and per paper, not per card."""

    def __init__(self, user):
        self.user = user
        self.person = getattr(user, 'profile', None)
        self.staff = bool(user.is_staff or user.is_superuser)
        self._modules = {}
        self._released = {}

    def module_open(self, module):
        if module is None or self.staff:
            return True
        if module.pk not in self._modules:
            self._modules[module.pk] = bool(self.person and module.is_unlocked_for(self.person))
        return self._modules[module.pk]

    def released(self, assessment):
        if assessment.pk not in self._released:
            self._released[assessment.pk] = assessment.solution_released_for(self.user)
        return self._released[assessment.pk]

    def status(self, card):
        """``'ok'``, ``'locked'`` (module closed) or ``'memo'`` (solution not released)."""
        question = card.question
        if not self.module_open(module_of(question)):
            return 'locked'
        if not self.released(question.section.assessment):
            return 'memo'
        return 'ok'


def _card_qs(user):
    return (ReviewCard.objects.filter(user=user, suspended=False)
            .select_related('question__section__assessment__module__module',
                            'question__section__assessment__topic__programme_module__module'))


def due_cards(user, now=None, module_id=None):
    """Due cards a review session may show now, oldest-due first."""
    if not getattr(user, 'is_authenticated', False):
        return []
    now = now or timezone.now()
    gate = _Gate(user)
    cards = []
    for card in _card_qs(user).filter(due_at__lte=now).order_by('due_at', 'id'):
        if gate.status(card) != 'ok':
            continue
        if module_id is not None:
            module = module_of(card.question)
            if (module.pk if module else 0) != module_id:
                continue
        cards.append(card)
    return cards


def due_count(user, now=None):
    """Number of review cards due now that this user may actually review.

    Excludes suspended cards, cards whose module is locked to the user and
    cards whose memo is not yet released to them. Returns 0 for anonymous users.
    Costs one query when nothing is due (the common case on a dashboard)."""
    if not getattr(user, 'is_authenticated', False):
        return 0
    now = now or timezone.now()
    if not ReviewCard.objects.filter(user=user, suspended=False, due_at__lte=now).exists():
        return 0
    return len(due_cards(user, now=now))


def overview(user, now=None):
    """Everything the revision home page shows."""
    now = now or timezone.now()
    gate = _Gate(user)
    groups = OrderedDict()
    held = {'locked': 0, 'memo': 0}
    total = upcoming_week = 0
    next_due = None
    boxes = {b: 0 for b in range(ReviewCard.BOX_MIN, ReviewCard.BOX_MAX + 1)}
    for card in _card_qs(user).order_by('due_at', 'id'):
        total += 1
        boxes[card.box] = boxes.get(card.box, 0) + 1
        if card.due_at > now:
            if card.due_at <= now + timedelta(days=7):
                upcoming_week += 1
            if next_due is None:
                next_due = card.due_at
            continue
        state = gate.status(card)
        if state != 'ok':
            held[state] += 1
            continue
        module = module_of(card.question)
        key = module.pk if module else 0
        if key not in groups:
            groups[key] = {'id': key, 'module': module, 'count': 0,
                           'label': (module.name or module.module.name) if module else 'Other papers',
                           'code': module.code if module else ''}
        groups[key]['count'] += 1
    streak, today = day_streak(user)
    return {
        'due_total': sum(g['count'] for g in groups.values()),
        'by_module': sorted(groups.values(), key=lambda g: (-g['count'], g['label'])),
        'held': held, 'total': total, 'upcoming_week': upcoming_week, 'next_due': next_due,
        'boxes': boxes, 'streak': streak, 'reviewed_today': today,
        'suspended': ReviewCard.objects.filter(user=user, suspended=True).count(),
    }


def day_streak(user, today=None):
    """``(streak, reviewed_today)``: consecutive days with at least one review,
    counting back from today — or from yesterday, so a streak is not lost before
    the day's review is done."""
    today = today or timezone.localdate()
    start = today - timedelta(days=400)
    days = set(ReviewLog.objects.filter(user=user, reviewed_at__date__gte=start)
               .annotate(day=TruncDate('reviewed_at', tzinfo=timezone.get_current_timezone()))
               .values_list('day', flat=True))
    reviewed_today = ReviewLog.objects.filter(
        user=user, reviewed_at__date=today).count() if today in days else 0
    cursor = today if today in days else today - timedelta(days=1)
    streak = 0
    while cursor in days:
        streak += 1
        cursor -= timedelta(days=1)
    return streak, reviewed_today


# ---------------------------------------------------------------------------
# Card content
# ---------------------------------------------------------------------------
def is_choice_card(question):
    return question.type in CHOICE_TYPES and question.choices.exists()


def solution_for(question):
    """The model answer for one question — same shapes as the assessment result
    page (schedule lines / rubric points / free text), plus any ``explanation``
    the question config carries. Callers must have checked release first."""
    config = question.config or {}
    kind = config.get('kind')
    explanation = config.get('explanation') or ''
    if kind == 'schedule' and config.get('lines'):
        return {'kind': 'schedule', 'lines': config['lines'], 'text': explanation}
    if kind == 'rubric' and config.get('rubric'):
        return {'kind': 'rubric', 'rubric': config['rubric'], 'text': explanation}
    text = '\n\n'.join(t for t in (explanation, question.guidance) if t)
    if text:
        return {'kind': 'text', 'text': text}
    return None
