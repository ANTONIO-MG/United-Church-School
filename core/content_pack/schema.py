"""The ``thrive-pack/1`` contract, and a validator for it.

Hand-rolled rather than ``jsonschema``, for two reasons. It adds no dependency
to a project that deliberately keeps few; and the errors it produces name the
path and say what to do — ``items[1].parts[0].lines[2].marks: must be a positive
number, got '1 mark'`` — which matters because the other producer of these packs
is a language model whose output someone has to correct.

Validation is *total*: it collects every problem rather than raising on the
first, so one pass tells you everything wrong with a pack.
"""

from decimal import Decimal, InvalidOperation

PACK_VERSION = 'thrive-pack/1'

#: Artefact types a pack may carry, in the order a learner meets them.
ITEM_TYPES = ('study_guide', 'mock', 'challenge', 'exam')

#: How a part is marked. ``auto`` needs ``lines``; the other two need ``rubric``.
MARKING_MODES = ('auto', 'ai_assisted', 'manual')

#: When the memorandum becomes visible to the learner.
RELEASE_MODES = ('on_submit', 'on_close', 'manual')

#: Blocks of the year a pack may be placed in — mirrors ModulePhase.KIND_CHOICES.
PHASE_KINDS = ('test', 'exam', 'supp', 'other')

#: Default tolerance for an auto-marked figure, as a fraction of the expected
#: amount. Rounding in the last digit should not cost a mark; a wrong
#: number still will.
DEFAULT_TOLERANCE = Decimal('0.005')


class ValidationError(Exception):
    """Raised by :func:`validate_or_raise`. Carries every problem found."""

    def __init__(self, errors):
        self.errors = list(errors)
        super().__init__(f'{len(self.errors)} problem(s) in the content pack')

    def __str__(self):
        return '\n'.join(f'  · {e}' for e in self.errors)


# ---------------------------------------------------------------------------
# Small checkers. Each appends to ``errors`` and returns the coerced value.
# ---------------------------------------------------------------------------
def _text(value, path, errors, *, required=True, max_length=None):
    if value is None or value == '':
        if required:
            errors.append(f'{path}: required')
        return ''
    if not isinstance(value, str):
        errors.append(f'{path}: must be text, got {type(value).__name__}')
        return ''
    if max_length and len(value) > max_length:
        errors.append(f'{path}: longer than {max_length} characters ({len(value)})')
    return value.strip()


def _number(value, path, errors, *, required=True, positive=False):
    if value is None:
        if required:
            errors.append(f'{path}: required')
        return None
    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        errors.append(f'{path}: must be a number, got {value!r}')
        return None
    if positive and number <= 0:
        errors.append(f'{path}: must be greater than zero, got {number}')
    return number


def _choice(value, options, path, errors, *, default=None):
    if value in (None, '') and default is not None:
        return default
    if value not in options:
        errors.append(f'{path}: must be one of {", ".join(options)} — got {value!r}')
        return default
    return value


def _list(value, path, errors, *, required=True):
    if value is None:
        if required:
            errors.append(f'{path}: required')
        return []
    if not isinstance(value, list):
        errors.append(f'{path}: must be a list, got {type(value).__name__}')
        return []
    if required and not value:
        errors.append(f'{path}: must not be empty')
    return value


# ---------------------------------------------------------------------------
# Item validators
# ---------------------------------------------------------------------------
def _validate_study_guide(item, path, errors):
    _text(item.get('title'), f'{path}.title', errors, max_length=200)
    sections = _list(item.get('sections'), f'{path}.sections', errors)
    for i, section in enumerate(sections):
        where = f'{path}.sections[{i}]'
        if not isinstance(section, dict):
            errors.append(f'{where}: must be an object')
            continue
        _text(section.get('heading'), f'{where}.heading', errors, max_length=200)
        _text(section.get('body_html'), f'{where}.body_html', errors)


def _validate_part(part, path, errors):
    """One question part — (a), (b(i)), … — and the marking data behind it."""
    if not isinstance(part, dict):
        errors.append(f'{path}: must be an object')
        return
    _text(part.get('ref'), f'{path}.ref', errors, max_length=12)
    _text(part.get('required'), f'{path}.required', errors)
    marks = _number(part.get('marks'), f'{path}.marks', errors, positive=True)
    mode = _choice(part.get('marking'), MARKING_MODES, f'{path}.marking', errors, default='manual')

    lines = part.get('lines') or []
    rubric = part.get('rubric') or []

    # The mode and the marking data have to agree: an auto-marked part with no
    # figures to compare against would silently score every learner zero.
    if mode == 'auto' and not lines:
        errors.append(f'{path}: marking is "auto" but there are no lines to mark against')
    if mode in ('ai_assisted', 'manual') and not rubric:
        errors.append(f'{path}: marking is "{mode}" but there is no rubric to mark against')
    if lines and rubric:
        errors.append(f'{path}: has both lines and rubric — a part is either a computation '
                      f'or a discussion, not both. Split it into two parts.')

    allocated = Decimal('0')
    for i, line in enumerate(lines):
        where = f'{path}.lines[{i}]'
        if not isinstance(line, dict):
            errors.append(f'{where}: must be an object')
            continue
        _text(line.get('label'), f'{where}.label', errors, max_length=300)
        _text(line.get('authority'), f'{where}.authority', errors, required=False, max_length=120)
        _number(line.get('amount'), f'{where}.amount', errors)
        line_marks = _number(line.get('marks'), f'{where}.marks', errors, positive=True)
        if line.get('tolerance') is not None:
            _number(line.get('tolerance'), f'{where}.tolerance', errors)
        allocated += line_marks or 0

    for i, point in enumerate(rubric):
        where = f'{path}.rubric[{i}]'
        if not isinstance(point, dict):
            errors.append(f'{where}: must be an object')
            continue
        _text(point.get('point'), f'{where}.point', errors)
        _text(point.get('authority'), f'{where}.authority', errors, required=False, max_length=120)
        point_marks = _number(point.get('marks'), f'{where}.marks', errors, positive=True)
        allocated += point_marks or 0

    # The marks on the rows must add up to the marks on the part. This is the
    # check that catches a mis-read solution sheet before it becomes a paper
    # that cannot be marked out of its own total.
    if marks is not None and allocated and allocated != marks:
        errors.append(f'{path}: rows allocate {allocated} mark(s) but the part is worth {marks}. '
                      f'They must agree.')


def _validate_paper(item, path, errors, *, kind):
    _text(item.get('title'), f'{path}.title', errors, max_length=200)
    _text(item.get('scenario_html'), f'{path}.scenario_html', errors)
    total = _number(item.get('total_marks'), f'{path}.total_marks', errors, positive=True)
    _number(item.get('minutes'), f'{path}.minutes', errors, required=False)
    _choice(item.get('release_solution'), RELEASE_MODES,
            f'{path}.release_solution', errors, default='on_submit')

    parts = _list(item.get('parts'), f'{path}.parts', errors)
    refs, part_total = set(), Decimal('0')
    for i, part in enumerate(parts):
        _validate_part(part, f'{path}.parts[{i}]', errors)
        if isinstance(part, dict):
            ref = part.get('ref')
            if ref in refs:
                errors.append(f'{path}.parts[{i}].ref: "{ref}" is used more than once')
            refs.add(ref)
            try:
                part_total += Decimal(str(part.get('marks') or 0))
            except (InvalidOperation, TypeError, ValueError):
                pass

    if total is not None and part_total and part_total != total:
        errors.append(f'{path}: parts add up to {part_total} but total_marks says {total}.')

    if kind == 'challenge':
        _number(item.get('week'), f'{path}.week', errors, positive=True)
        _text(item.get('scenario_key'), f'{path}.scenario_key', errors, max_length=60)


def validate(pack):
    """Return a list of human-readable problems. Empty list = the pack is good.

    Never raises on bad input — a pack that is not even a dict comes back as one
    clear error rather than a ``TypeError`` from somewhere inside.
    """
    errors = []
    if not isinstance(pack, dict):
        return [f'pack: must be a JSON object, got {type(pack).__name__}']

    version = pack.get('pack')
    if version != PACK_VERSION:
        errors.append(f'pack: must be "{PACK_VERSION}", got {version!r}')

    _text(pack.get('module'), 'module', errors, max_length=20)
    _text(pack.get('programme'), 'programme', errors, max_length=40)
    _text(pack.get('cohort'), 'cohort', errors, required=False, max_length=40)

    topic = pack.get('topic')
    if not isinstance(topic, dict):
        errors.append('topic: required — an object with code and title')
    else:
        _text(topic.get('code'), 'topic.code', errors, max_length=20)
        _text(topic.get('title'), 'topic.title', errors, max_length=250)

    # --- Optional placement on the module's year plan -----------------------
    # Absent, the importer puts the topic in the first phase, next week along.
    phase = pack.get('phase')
    if phase is not None:
        if not isinstance(phase, dict):
            errors.append('phase: must be an object with kind and sequence')
        else:
            _choice(phase.get('kind'), PHASE_KINDS, 'phase.kind', errors, default='test')
            _number(phase.get('sequence'), 'phase.sequence', errors,
                    required=False, positive=True)
            _text(phase.get('title'), 'phase.title', errors, required=False, max_length=160)
    _number(pack.get('week'), 'week', errors, required=False, positive=True)

    items = _list(pack.get('items'), 'items', errors)
    for i, item in enumerate(items):
        where = f'items[{i}]'
        if not isinstance(item, dict):
            errors.append(f'{where}: must be an object')
            continue
        kind = _choice(item.get('type'), ITEM_TYPES, f'{where}.type', errors)
        if kind == 'study_guide':
            _validate_study_guide(item, where, errors)
        elif kind in ('mock', 'challenge', 'exam'):
            _validate_paper(item, where, errors, kind=kind)

    return errors


def validate_or_raise(pack):
    """:func:`validate`, but raise :class:`ValidationError` if anything is wrong."""
    errors = validate(pack)
    if errors:
        raise ValidationError(errors)
    return True
