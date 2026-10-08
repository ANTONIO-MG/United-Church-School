"""Marking a numeric schedule — the computational half of a CTA paper.

A ``schedule`` question is what the source solution workbooks actually are: an
ordered ladder of scoring lines, each with a label, the authority behind it, the
figure that earns the mark, and how many marks that line is worth.

    REF │ LINE                        │ AUTHORITY │      AMOUNT │ MARKS
     a  │ Primary residence            │ s3(2)     │   4 500 000 │   1
     a  │ Listed shares                │ s3(2)     │   1 250 000 │   1
     a  │ Section 4(q) — spouse        │ s4(q)     │  -2 000 000 │   2

The candidate fills in one figure per line and each line is marked on its own.
That is the whole reason this is worth auto-marking: it is not one right answer
worth eighteen marks, it is eighteen scoring points, and a candidate who gets
the abatement right and the residence wrong should be told exactly that.

**Own-figure marking is not attempted here.** A real CTA marker follows a wrong
subtotal through to a correct final figure and awards the later marks anyway.
Guessing at that automatically would award marks the examiner would not, so a
line is right or it is not, and the teacher can override any line in the marking
queue. Being predictable matters more than being generous.

Tolerance is a *fraction* of the expected figure, defaulting to 0.5%: rounding
to the nearest rand in a multi-million-rand estate must not cost a mark, while a
genuinely wrong number still does. A line whose expected amount is zero is
compared exactly, because 0 has no proportion to be within.
"""

from decimal import Decimal, InvalidOperation

#: Matches the schema's DEFAULT_TOLERANCE — kept in step deliberately, so a pack
#: that omits the field and a question that omits it agree.
DEFAULT_TOLERANCE = Decimal('0.005')


def _decimal(value):
    """Parse a candidate's or an author's figure. ``None`` when it is not one.

    Accepts what people actually type into a schedule: thousands separators,
    spaces, a currency prefix, and brackets for a negative — ``(2 000 000)`` is
    how every accounting workbook writes a deduction, and refusing it would fail
    candidates for using their own notation.
    """
    if value is None or value == '':
        return None
    if isinstance(value, (int, float, Decimal)):
        try:
            return Decimal(str(value))
        except InvalidOperation:
            return None

    text = str(value).strip()
    if not text:
        return None
    negative = text.startswith('(') and text.endswith(')')
    if negative:
        text = text[1:-1]
    for junk in ('R', 'r', ' ', ' ', ',', "'"):
        text = text.replace(junk, '')
    if text.startswith('-'):
        negative, text = True, text[1:]
    if not text:
        return None
    try:
        amount = Decimal(text)
    except InvalidOperation:
        return None
    return -amount if negative else amount


def _within(given, expected, tolerance):
    """Is ``given`` close enough to ``expected`` to earn the line?"""
    if given is None or expected is None:
        return False
    if expected == 0:
        return given == 0
    allowed = abs(expected) * abs(tolerance)
    return abs(given - expected) <= allowed


def _lines(question):
    """The scoring lines on a schedule question, or ``[]`` if it has none."""
    config = question.config or {}
    if config.get('kind') != 'schedule':
        return []
    return config.get('lines') or []


def mark_schedule(answer):
    """Score one schedule answer. Returns ``(awarded, is_correct, breakdown)``.

    ``breakdown`` is one row per line — what the candidate put, what was
    expected, whether it earned the mark and why. It is stored on the answer so
    the result page and the marking queue can show the candidate their ladder
    beside the model one, which is the actual teaching moment.

    A question with no lines scores nothing rather than everything: a schedule
    whose marking data failed to import must not silently award full marks.
    """
    question = answer.question
    lines = _lines(question)
    if not lines:
        return Decimal('0'), False, []

    given_values = (answer.response or {}).get('lines') or {}
    if isinstance(given_values, list):
        # Tolerated shape: a positional list rather than a keyed object.
        given_values = {str(i): v for i, v in enumerate(given_values)}

    awarded = Decimal('0')
    breakdown = []
    for index, line in enumerate(lines):
        expected = _decimal(line.get('amount'))
        marks = _decimal(line.get('marks')) or Decimal('0')
        tolerance = _decimal(line.get('tolerance'))
        if tolerance is None:
            tolerance = DEFAULT_TOLERANCE

        raw = given_values.get(str(index), given_values.get(index))
        given = _decimal(raw)
        correct = _within(given, expected, tolerance)
        if correct:
            awarded += marks

        breakdown.append({
            'index': index,
            'label': line.get('label', ''),
            'authority': line.get('authority', ''),
            'expected': str(expected) if expected is not None else '',
            'given': '' if raw in (None, '') else str(raw),
            'marks': str(marks),
            'awarded': str(marks if correct else Decimal('0')),
            'correct': correct,
            'answered': given is not None,
        })

    total = sum((_decimal(l.get('marks')) or Decimal('0')) for l in lines)
    # "Correct" for a schedule means every line — the badge on the result page
    # is all-or-nothing, while the marks are not.
    return awarded, bool(total) and awarded == total, breakdown


def store_breakdown(answer, breakdown):
    """Keep the per-line result on the answer, beside the candidate's figures.

    Written under its own key so the candidate's response is never overwritten:
    a re-mark has to be able to see what they originally put.
    """
    response = dict(answer.response or {})
    response['breakdown'] = breakdown
    answer.response = response
