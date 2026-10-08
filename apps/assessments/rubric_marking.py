"""Rubric-assisted marking — a *suggestion* for the teacher, never a mark.

A CTA discussion answer is marked against the solution workbook's rubric: one
row per point that earns a mark, with the authority behind it.

    (3) s4(q) removes assets accruing to the surviving spouse from the estate
    (2) the abatement is applied after s4 deductions, not before
    (2) the effect is a deferral, not an exemption

This module asks Claude, for one answer, which of those rows the candidate
actually made — and returns a per-row verdict with a quotation from their script
as the evidence. The teacher sees it beside the answer in the existing marking
queue and confirms or overrides it.

**It never writes a mark.** :func:`suggest` returns data; nothing here touches
``Answer.awarded_marks``. That is the whole design:

* A model that silently gives an essay 8/12 on keyword overlap teaches candidates
  to write for the marker, and CTA examiners mark the opposite way.
* A suggestion a teacher confirms is slower to build than auto-marking and is the
  only version worth having — it speeds up the marking without moving the
  judgement.
* Every suggestion carries the quotation it relied on, so a teacher can check it in
  a second rather than re-reading the whole script to trust it.

With no ``ANTHROPIC_API_KEY`` this is inert and the queue marks by hand exactly
as it does today.
"""

import logging
from decimal import Decimal

logger = logging.getLogger('apps')


class SuggestionError(Exception):
    """The suggestion could not be produced. Never fatal — marking goes on."""


SYSTEM = """You assist a South African CTA marker. You do NOT award marks; you report
which rubric points a candidate's answer actually made, so a human can mark faster.

You are given one question, its rubric (each row is a point that earns marks),
and the candidate's answer. For every rubric row, decide:

  "made"      — the answer clearly makes this point. Quote the words that do it.
  "partial"   — the point is gestured at but incomplete, or stated without the
                reasoning or the authority that the row requires.
  "missed"    — the point is not there.

How CTA is marked, and how you must judge:
- Substance over wording. A candidate who explains the effect of s4(q) correctly
  has made the point even if they never cite "s4(q)".
- But a bare citation with no explanation is "partial", not "made". Naming a
  section is not applying it.
- Reward application to the scenario. Generic textbook recitation that never
  touches the facts given is at best "partial".
- Be sceptical. If you are unsure, say "partial" — a teacher reviewing an
  understatement costs a moment; an overstatement they accept costs a candidate
  a mark they did not earn.

`quote` must be VERBATIM from the candidate's answer, and short — one sentence at
most. If you cannot quote it, you cannot claim they made it: say "missed".

`comment` is one plain sentence a marker could paste into feedback. No praise, no
padding, no restating the rubric row.
"""

SUGGESTION_SCHEMA = {
    'type': 'object',
    'additionalProperties': False,
    'required': ['rows'],
    'properties': {
        'rows': {
            'type': 'array',
            'items': {
                'type': 'object',
                'additionalProperties': False,
                'required': ['index', 'verdict', 'comment'],
                'properties': {
                    'index': {'type': 'integer'},
                    'verdict': {'type': 'string', 'enum': ['made', 'partial', 'missed']},
                    'quote': {'type': 'string'},
                    'comment': {'type': 'string'},
                },
            },
        },
        'overall': {'type': 'string'},
    },
}

#: What each verdict is worth, as a fraction of the row's marks. "partial" is a
#: half — the conventional CTA treatment of a point made without its reasoning.
VERDICT_WEIGHT = {'made': Decimal('1'), 'partial': Decimal('0.5'), 'missed': Decimal('0')}


def is_enabled():
    try:
        from apps.ai_assistant import generate
        return generate.is_enabled()
    except Exception:  # pragma: no cover
        return False


def rubric_of(question):
    """The rubric rows on a question, or ``[]`` when it has none."""
    config = question.config or {}
    if config.get('kind') != 'rubric':
        return []
    return config.get('rubric') or []


def wants_suggestion(question):
    """Whether this question was imported as one a model may help mark.

    Only ``ai_assisted`` — a part the pack marked ``manual`` is professional
    skills (how the candidate wrote, not what they concluded), and that is a
    judgement about their writing that a model has no business estimating.
    """
    config = question.config or {}
    return (config.get('kind') == 'rubric'
            and config.get('marking_intent') == 'ai_assisted'
            and bool(config.get('rubric')))


def _answer_text(answer):
    return ((answer.response or {}).get('text') or '').strip()


def suggest(answer, *, max_tokens=4000):
    """Suggest a mark for one answer. Returns a dict, or raises.

        {'rows': [{index, verdict, quote, comment, marks, awarded, label}],
         'suggested': Decimal, 'total': Decimal, 'overall': str}

    ``suggested`` is what the rows add up to — a number for the teacher to accept
    or change, never a mark that has been given.
    """
    question = answer.question
    rubric = rubric_of(question)
    if not rubric:
        raise SuggestionError('This question has no rubric to mark against.')
    text = _answer_text(answer)
    if not text:
        raise SuggestionError('There is no answer to mark.')
    if not is_enabled():
        raise SuggestionError(
            'Marking assistance needs ANTHROPIC_API_KEY and ADMIN_AI_ENABLED.')

    from apps.ai_assistant import generate

    rows_text = '\n'.join(
        f'[{i}] ({row.get("marks")} mark(s)) {row.get("point")}'
        + (f'  — authority: {row["authority"]}' if row.get('authority') else '')
        for i, row in enumerate(rubric))
    prompt = (
        f'QUESTION ({question.marks} marks):\n{question.text}\n\n'
        f'RUBRIC — one row per point that earns marks:\n{rows_text}\n\n'
        f"CANDIDATE'S ANSWER:\n{text[:40000]}"
    )
    try:
        data = generate.generate_from_prompt(
            prompt, system=SYSTEM, schema=SUGGESTION_SCHEMA,
            instruction='Report one row per rubric point, in the same order, using the '
                        'same index. Return only the JSON object.',
            constrain=False, max_tokens=max_tokens)
    except Exception as exc:
        logger.exception('rubric suggestion failed for answer %s', answer.pk)
        raise SuggestionError(str(exc))

    return _shape(data, rubric)


def _shape(data, rubric):
    """Model output + rubric → the rows the marking queue renders.

    Defensive on purpose: a row the model omitted becomes "missed" rather than
    disappearing, and an index it invented is dropped. A suggestion that quietly
    left out half the rubric would read as a low mark rather than as a failure.
    """
    by_index = {}
    for row in (data.get('rows') or []):
        try:
            by_index[int(row.get('index'))] = row
        except (TypeError, ValueError):
            continue

    rows, suggested, total = [], Decimal('0'), Decimal('0')
    for index, point in enumerate(rubric):
        marks = Decimal(str(point.get('marks') or 0))
        total += marks
        found = by_index.get(index) or {}
        verdict = found.get('verdict') if found.get('verdict') in VERDICT_WEIGHT else 'missed'
        awarded = (marks * VERDICT_WEIGHT[verdict]).quantize(Decimal('0.01'))
        suggested += awarded
        rows.append({
            'index': index,
            'label': point.get('point', ''),
            'authority': point.get('authority', ''),
            'marks': marks,
            'verdict': verdict,
            'awarded': awarded,
            'quote': (found.get('quote') or '').strip(),
            'comment': (found.get('comment') or '').strip(),
        })

    return {
        'rows': rows,
        'suggested': suggested.quantize(Decimal('0.01')),
        'total': total,
        'overall': (data.get('overall') or '').strip(),
    }
