"""Presentation logic for the lesson player — the learner-facing view.

A lesson reads as **one continuous body**: an ordered run of blocks in which a
*section* is simply a collapsible element the author dropped in. This module
turns the stored rows into everything the template needs:

* :func:`body_rows` — the whole flow in order. A plain block yields
  ``{'kind': 'block'}``; a section block yields ``{'kind': 'section'}`` carrying
  its label, duration, lock state, completion and (for quiz/assessment sections)
  the learner's score card.
* :func:`section_rows` — just the section rows, for the progress/contents rail.
* :func:`lesson_rail` — the right-hand rail payload: progress, notes, bookmarks,
  score cards and the discussion messages tied to this lesson/module.
* :func:`ensure_sections` — legacy back-fill, now only used by the migration that
  moved sections into the body.

Locking rule: a section marked ``requires_previous`` stays locked until **every
earlier required section** is completed. That mirrors the course player's gate
(``CourseItem.gate_next``) so the two surfaces behave the same way.
"""

import logging

from django.utils import timezone

from . import models

logger = logging.getLogger('apps')

# Score → rating out of 5 + the message shown on the learner's score card.
_RATINGS = [
    (90, 5, 'Outstanding — you have mastered this.'),
    (75, 4, 'Strong result. A quick review and you are set.'),
    (60, 3, 'Solid pass. Revisit the parts you missed.'),
    (50, 2, 'You scraped through — work through this section again.'),
    (0, 1, 'Not yet. Re-read the section and retry the questions.'),
]


def rating_for(pct):
    """``(stars, message)`` for a percentage score."""
    for threshold, stars, message in _RATINGS:
        if pct >= threshold:
            return stars, message
    return 1, ''


def score_card(section, student):
    """The learner's result for a quiz/assessment section, or ``None``."""
    attempt = section.best_attempt_for(student)
    if attempt is None:
        return None
    total = float(attempt.assessment.total_marks or 0)
    pct = round(float(attempt.score) / total * 100) if total else 0
    stars, message = rating_for(pct)
    return {
        'attempt': attempt,
        'assessment': attempt.assessment,
        'score': attempt.score,
        'total': attempt.assessment.total_marks,
        'pct': pct,
        'passed': attempt.passed,
        'stars': stars,
        'star_range': range(5),
        'message': message,
    }


def body_rows(lesson, student, *, preview=False):
    """The lesson's whole body, in order, decorated for the player.

    Each row is either ``{'kind': 'block', 'block': …}`` for an ordinary element
    or ``{'kind': 'section', …}`` for a collapsible panel with its own blocks and
    per-learner state. Walking one list keeps the reading order the author saw in
    the builder — prose, a video, a dropdown section, more prose.

    ``preview`` (an author viewing their own lesson) unlocks everything so the
    author can see the whole lesson without completing it.
    """
    notes = {}
    if getattr(student, 'is_authenticated', False):
        notes = {n.section_id: n.body for n in
                 models.LessonNote.objects.filter(lesson=lesson, student=student)}

    rows, unmet_required = [], False
    for block in lesson.body_blocks():
        if not block.is_section:
            # ``blocks`` is a one-item list so the template renders every row
            # through the same include, whatever kind it is.
            rows.append({'kind': 'block', 'block': block, 'blocks': [block]})
            continue

        section = block.holds_section
        completed = False if preview else section.is_completed_by(student)
        locked = bool(section.requires_previous and unmet_required) and not preview
        rows.append({
            'kind': 'section',
            'block': block,
            'section': section,
            'blocks': list(block.child_blocks),
            'completed': completed,
            'locked': locked,
            'note': notes.get(section.id, ''),
            'score': None if locked else score_card(section, student),
        })
        if section.is_required and not completed:
            unmet_required = True
    return rows


def section_rows(lesson, student, *, preview=False):
    """Only the section rows of the body — the contents/progress rail."""
    return [r for r in body_rows(lesson, student, preview=preview)
            if r['kind'] == 'section']


def completion_pct(rows):
    """Percentage of required sections completed.

    Accepts either the full body or just the section rows, so callers don't have
    to filter first. A lesson with no sections at all has nothing to gate on and
    reports 0 — its completion comes from the study session instead.
    """
    required = [r for r in rows
                if r.get('kind', 'section') == 'section' and r['section'].is_required]
    if not required:
        return 0
    return round(sum(1 for r in required if r['completed']) / len(required) * 100)


def lesson_messages(lesson, limit=8):
    """Discussions attached to this lesson's module — the "messages" rail.

    Threads that name the lesson (title in the module-scoped discussion's title
    or tags) sort first so lesson-specific chatter surfaces above general
    module talk.
    """
    try:
        from apps.communication.models import Discussion
        qs = (Discussion.objects.filter(module_id=lesson.module_id)
              .select_related('author')
              .order_by('-is_pinned', '-created_at')[:40])
        title = (lesson.title or '').lower()
        rows = list(qs)
        rows.sort(key=lambda d: (title not in (d.title or '').lower()
                                 and title not in (d.tags or '').lower()))
        return rows[:limit]
    except Exception:  # pragma: no cover - the rail must never break the lesson
        logger.exception('player: lesson messages lookup failed')
        return []


def lesson_note(lesson, student):
    """The learner's whole-lesson note (the one shown before any section opens)."""
    if not getattr(student, 'is_authenticated', False):
        return ''
    note = models.LessonNote.objects.filter(
        lesson=lesson, section__isnull=True, student=student).first()
    return note.body if note else ''


def lesson_rail(lesson, student, rows):
    """Everything the right-hand rail renders.

    ``rows`` may be the full body flow or just its sections.
    """
    sections = [r for r in rows if r.get('kind', 'section') == 'section']
    bookmarks = []
    if getattr(student, 'is_authenticated', False):
        bookmarks = list(models.LessonBookmark.objects
                         .filter(lesson=lesson, student=student)
                         .select_related('section')[:100])
    scores = [r for r in sections if r['score']]
    total_minutes = sum(r['section'].minutes for r in sections) or lesson.estimated_minutes
    return {
        'rail_bookmarks': bookmarks,
        'rail_scores': scores,
        'rail_messages': lesson_messages(lesson),
        'total_minutes': total_minutes,
        'section_count': len(sections),
        'completed_count': sum(1 for r in sections if r['completed']),
    }


def mark_section(section, student, *, completed=True, seconds=0):
    """Record a learner's progress on a section and return the fresh row."""
    progress, _ = models.LessonSectionProgress.objects.get_or_create(
        section=section, student=student)
    if seconds:
        progress.seconds_spent += max(0, min(3600, int(seconds)))
    if completed:
        progress.status = models.LessonSectionProgress.STATUS_COMPLETED
        progress.completed_at = progress.completed_at or timezone.now()
    elif progress.status == models.LessonSectionProgress.STATUS_NOT_STARTED:
        progress.status = models.LessonSectionProgress.STATUS_IN_PROGRESS
    progress.save()
    return progress


# ---------------------------------------------------------------------------
# Back-fill: turn a block-only lesson into sections
# ---------------------------------------------------------------------------
def ensure_sections(lesson):
    """Group an unsectioned lesson's blocks into sections, in place.

    Split points are heading blocks and any "standalone" block (quiz, live
    session, video) — each of those becomes its own tear-drop so the
    learner sees a labelled, timed panel rather than one long page. Blocks
    before the first split stay unsectioned and render as the lesson intro.

    Returns the number of sections created (0 if the lesson already has some).
    """
    if lesson.sections.exists():
        return 0
    blocks = list(lesson.blocks.all())
    if not blocks:
        return 0

    standalone = {models.LessonBlock.TYPE_QUIZ, models.LessonBlock.TYPE_MEETING,
                  models.LessonBlock.TYPE_VIDEO}
    groups, current = [], None
    for block in blocks:
        starts = (block.block_type == models.LessonBlock.TYPE_HEADING
                  or block.block_type in standalone)
        if starts or current is None:
            title = ''
            if block.block_type == models.LessonBlock.TYPE_HEADING:
                title = (block.data or {}).get('text') or ''
            else:
                title = (block.data or {}).get('title') or ''
            current = {'title': title, 'blocks': []}
            groups.append(current)
        current['blocks'].append(block)

    # A leading group with no heading is the intro — leave it unsectioned.
    if groups and not groups[0]['title']:
        groups.pop(0)
    if not groups:
        return 0

    created = 0
    for index, group in enumerate(groups):
        section = models.LessonSection.objects.create(
            lesson=lesson, order=index,
            title=(group['title'] or f'Section {index + 1}')[:200],
            open_by_default=(index == 0),
        )
        for block in group['blocks']:
            block.section = section
        models.LessonBlock.objects.bulk_update(group['blocks'], ['section'])
        created += 1
    return created
