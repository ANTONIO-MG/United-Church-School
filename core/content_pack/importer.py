"""Turn a validated content pack into database rows.

Three rules this module keeps, because they are what make the pipeline safe to
run twice and safe to hand to a language model later:

**Nothing is published.** Study guides import as ``draft`` lessons; papers as
``draft`` assessments. Publishing stays a deliberate human act through the
existing builder, and the existing ``STATUS_TRANSITIONS`` still refuses to open
a paper with no questions.

**Re-importing updates, it does not duplicate.** Every row created carries a
``source_ref`` derived from the pack, and the importer looks for that first. Fix
a figure in the JSON, run it again, and the same paper is corrected rather than
a second one appearing beside it.

**Nothing lands unless everything validates.** The whole import runs in one
transaction, so a pack that fails half way leaves no partial topic behind.

A pack also lands *in the schedule*, not just in the database. Creating a lesson
and an assessment on a topic is not enough for a candidate to ever meet them:
the module page is built from ``ModulePhase → ModuleWeek → ModuleMaterial``, so
the importer places one material row per item into the week that teaches that
topic. Placement is what makes the teaching sequence in
:mod:`apps.learning.sequence` apply — the guide, then the mock, then the
solution — because that gate reasons over the materials in a week.
"""

import logging
from decimal import Decimal

from django.db import transaction
from django.utils.text import slugify

from .schema import DEFAULT_TOLERANCE, validate_or_raise

logger = logging.getLogger(__name__)

#: Pack item type → the Assessment kind it becomes.
KIND_BY_TYPE = {
    'mock': 'test',
    'challenge': 'assignment',
    'exam': 'mock_exam',
}

#: Pack item type → the ModuleMaterial kind it is scheduled as. This is what
#: decides where it sits in the week's teaching order (apps.learning.sequence).
MATERIAL_KIND_BY_TYPE = {
    'study_guide': 'study_guide',
    'mock': 'questions',
    'challenge': 'assessment',
    'exam': 'mock_exam',
}


class ImportResult:
    """What an import did, in terms a human can check against the source."""

    def __init__(self):
        self.topic = None
        self.week = None
        self.guides_created = self.guides_updated = 0
        self.papers_created = self.papers_updated = 0
        self.questions = 0
        self.scheduled = 0
        self.marks = Decimal('0')
        self.warnings = []

    @property
    def created(self):
        return self.guides_created + self.papers_created

    @property
    def updated(self):
        return self.guides_updated + self.papers_updated

    def __str__(self):
        scheduled = f' · scheduled into {self.week}' if self.week else ''
        return (f'{self.guides_created + self.guides_updated} study guide(s), '
                f'{self.papers_created + self.papers_updated} paper(s), '
                f'{self.questions} question part(s), {self.marks} mark(s) — '
                f'{self.created} created, {self.updated} updated{scheduled}')


class PackImportError(Exception):
    """The pack is valid JSON and valid against the schema, but does not fit the
    database — an unknown module code, a programme that is not installed."""


def _resolve_topic(pack):
    """Find (or create) the syllabus topic this pack belongs to.

    The pack names its module by the institution's own code (``TAX``) and its
    grade by full code (``UCS-GR10``); both must already exist — the
    academic spine is installed by ``.03_admin.py`` and a content
    pack is never allowed to invent one. The *topic* may be created, because a
    new topic is content, not structure.
    """
    from apps.learning.models import ProgrammeModule, Topic

    programme_code = pack['programme']
    module_code = pack['module']
    institution_code, _, prog = programme_code.partition('-')

    offering = (ProgrammeModule.objects
                .filter(programme__institution__code__iexact=institution_code,
                        programme__code__iexact=prog or programme_code,
                        code__iexact=module_code)
                .select_related('programme__institution', 'module')
                .first())
    if offering is None:
        raise PackImportError(
            f'No module "{module_code}" on programme "{programme_code}". '
            f'The academic spine must already have it — content packs do not '
            f'create institutions, programmes or modules.')

    spec = pack['topic']
    topic, created = Topic.objects.get_or_create(
        programme_module=offering, code=spec['code'],
        defaults={'title': spec['title'],
                  'slug': slugify(f"{offering.code}-{spec['code']}-{spec['title']}")[:270],
                  'description': spec.get('description', '')},
    )
    if not created and spec.get('title') and topic.title != spec['title']:
        topic.title = spec['title']
        topic.save(update_fields=['title', 'updated_at'])
    return topic, offering


def _source_ref(pack, item, index):
    """A stable identity for a pack item, so a re-import finds its own row."""
    explicit = item.get('source_ref')
    if explicit:
        return str(explicit)[:120]
    bits = [pack['module'], pack['topic']['code'], item['type']]
    if item.get('week'):
        bits.append(f"w{item['week']}")
    if not item.get('week') and index:
        bits.append(str(index))
    return '/'.join(bits)[:120]


def _import_study_guide(pack, item, topic, actor, ref, result):
    """The guide becomes a draft Lesson on the topic, one section per heading."""
    from apps.learning.models import Lesson, LessonBlock, LessonSection

    lesson = Lesson.objects.filter(topic=topic, title=item['title']).first()
    if lesson is None:
        lesson = Lesson(topic=topic, title=item['title'])
        result.guides_created += 1
    else:
        result.guides_updated += 1

    lesson.status = Lesson.STATUS_DRAFT
    lesson.subtitle = (item.get('subtitle') or '')[:200]
    if not lesson.slug:
        lesson.slug = slugify(f"{topic.code}-{item['title']}")[:220]
    if item.get('author_name'):
        lesson.author_name = item['author_name'][:120]
    lesson.save()

    # Rebuild rather than merge: the pack is the source of truth, and a
    # half-merged guide carrying orphaned old sections is worse than a rebuild.
    lesson.sections.all().delete()
    lesson.blocks.all().delete()
    for order, section in enumerate(item.get('sections') or []):
        row = LessonSection.objects.create(
            lesson=lesson, title=section['heading'][:200], order=order,
            summary=(section.get('summary') or '')[:300],
            open_by_default=(order == 0))
        # A section is a container; its prose is a text block inside it.
        LessonBlock.objects.create(
            lesson=lesson, section=row, order=0,
            block_type=LessonBlock.TYPE_TEXT,
            data={'html': section['body_html']})
    return lesson


def _question_payload(part):
    """Map one pack part onto the fields of a :class:`Question`.

    A part is either a computation (``lines``) or a discussion (``rubric``); the
    schema has already refused anything that is both or neither. The structure
    goes into ``config`` where the marker reads it, and the model answer into
    ``guidance`` where a human marker sees it.
    """
    lines = part.get('lines') or []
    rubric = part.get('rubric') or []
    mode = part.get('marking') or 'manual'

    if lines:
        config = {
            'kind': 'schedule',
            'lines': [
                {
                    'label': line['label'],
                    'authority': line.get('authority', ''),
                    'amount': str(Decimal(str(line['amount']))),
                    'marks': str(Decimal(str(line['marks']))),
                    'tolerance': str(Decimal(str(line.get('tolerance', DEFAULT_TOLERANCE)))),
                }
                for line in lines
            ],
        }
        guidance = '\n'.join(
            f"{line['label']}"
            + (f" [{line['authority']}]" if line.get('authority') else '')
            + f" = {line['amount']}  ({line['marks']} mark(s))"
            for line in lines)
        return 'schedule', config, guidance, 'auto' if mode == 'auto' else 'manual'

    config = {
        'kind': 'rubric',
        # ai_assisted is recorded so the marking queue knows a suggestion can be
        # asked for. Until that lands the part simply marks by hand, which is
        # the safe default rather than a silent zero.
        'marking_intent': mode,
        'rubric': [
            {
                'point': point['point'],
                'authority': point.get('authority', ''),
                'marks': str(Decimal(str(point['marks']))),
                'professional_skill': bool(point.get('professional_skill')),
            }
            for point in rubric
        ],
    }
    guidance = '\n'.join(
        f"({point['marks']}) {point['point']}"
        + (f"  — {point['authority']}" if point.get('authority') else '')
        for point in rubric)
    return 'long', config, guidance, 'manual'


def _import_paper(pack, item, topic, actor, ref, result):
    """A mock, challenge or exam becomes a draft Assessment with one question
    per REQUIRED part — which is exactly how the source papers are written."""
    from apps.assessments.models import Assessment, Question, Section

    kind = KIND_BY_TYPE[item['type']]
    paper = Assessment.objects.filter(source_ref=ref).first()
    if paper is None:
        paper = Assessment(source_ref=ref)
        result.papers_created += 1
    else:
        result.papers_updated += 1

    paper.topic = topic
    # A topic belongs to exactly one offering, and every access check in the
    # assessments app is written against ``module``. Setting only ``topic`` left
    # imported papers unreachable — ``assessment.module`` was None and the take
    # page raised rather than refusing.
    paper.module = topic.programme_module
    paper.title = item['title']
    paper.kind = kind
    paper.description = item.get('scenario_html', '')
    paper.total_marks = Decimal(str(item['total_marks']))
    paper.time_limit_minutes = int(item.get('minutes') or 0)
    paper.release_solution = item.get('release_solution') or Assessment.RELEASE_ON_SUBMIT
    paper.solution_notes = item.get('solution_notes') or {}
    paper.status = Assessment.STATUS_DRAFT      # never published by an import
    paper.save()

    # One section holding the REQUIRED parts, rebuilt from the pack.
    paper.sections.all().delete()
    section = Section.objects.create(
        assessment=paper, title='Required',
        instructions=item.get('instructions', ''), order=0)

    for order, part in enumerate(item.get('parts') or []):
        qtype, config, guidance, marking_mode = _question_payload(part)
        Question.objects.create(
            section=section, type=qtype, order=order,
            text=f"({part['ref']})  {part['required']}",
            marks=Decimal(str(part['marks'])),
            config=config, guidance=guidance, marking_mode=marking_mode,
        )
        result.questions += 1
        result.marks += Decimal(str(part['marks']))

    if item['type'] == 'challenge':
        # The challenge is one evolving scenario released a week at a time, so
        # the week and the scenario it belongs to travel with the paper.
        paper.solution_notes = dict(paper.solution_notes or {},
                                    scenario_key=item.get('scenario_key', ''),
                                    week=item.get('week'))
        paper.save(update_fields=['solution_notes', 'updated_at'])
    return paper


# ---------------------------------------------------------------------------
# Placing a pack in the schedule
# ---------------------------------------------------------------------------
def _resolve_cohort(pack, offering):
    """The intake this pack targets, from ``pack['cohort']`` (a cohort code) on
    the offering's programme — or None (a shared template) when blank/unknown."""
    code = (pack.get('cohort') or '').strip()
    if not code:
        return None
    from apps.learning.models import Cohort
    return Cohort.objects.filter(programme=offering.programme, code__iexact=code).first()


def _resolve_week(pack, topic, offering):
    """The :class:`ModuleWeek` this pack's material belongs in.

    Found in the order that respects what a human has already set up:

    1. A week already pointing at this topic — the schedule was built first and
       the pack is filling it in. This is the normal case and nothing is created.
    2. ``pack["week"]`` naming a week number in a phase — an explicit placement.
    3. Otherwise a new week is appended to the offering's first phase, carrying
       the topic's title, so imported content is never stranded off-schedule.

    A module with no year planned yet gets the block the pack names (or a first
    test block) created for it, unpublished and undated — the content is never
    left stranded off-schedule, but *when* the test sits stays the teacher's call.
    """
    from django.db.models import Q

    from apps.learning.models import ModulePhase, ModuleWeek

    # Which intake this content is for (Option B per-cohort content). A blank/
    # unknown cohort → shared template (cohort=None), visible to every intake.
    # The cohort lives on ModulePhase, so ModuleWeek is scoped via ``phase__``.
    cohort = _resolve_cohort(pack, offering)
    week_scope = Q(phase__cohort=cohort) | Q(phase__cohort__isnull=True)
    phase_scope = Q(cohort=cohort) | Q(cohort__isnull=True)

    # A week already working through this topic — re-import fills it in; nothing new.
    existing = (ModuleWeek.objects
                .filter(phase__programme_module=offering, topics=topic)
                .filter(week_scope).order_by('phase__cohort').first())
    if existing is not None:
        _link_week_topic(existing, topic)
        return existing, False

    spec = pack.get('phase') or {}
    kind = spec.get('kind') or ModulePhase.KIND_TEST
    sequence = spec.get('sequence') or 1

    phase = None
    if spec:
        phase = (ModulePhase.objects
                 .filter(programme_module=offering, sequence=sequence, kind=kind)
                 .filter(phase_scope).order_by('cohort').first())   # this intake before shared
    if phase is None:
        phase = (ModulePhase.objects.filter(programme_module=offering)
                 .filter(phase_scope).order_by('cohort', 'order', 'id').first())
    if phase is None:
        # No year planned for this module + intake yet. Create the block the pack
        # names (or the default first test block), tagged to this intake, rather
        # than leaving the content stranded — but UNPUBLISHED and undated, because
        # when the test actually sits is the teacher's call, not a pack's.
        phase = ModulePhase.objects.create(
            programme_module=offering, kind=kind, sequence=sequence,
            title=spec.get('title', ''), order=sequence, is_published=False,
            cohort=cohort)

    number = pack.get('week')
    if not number:
        last = ModuleWeek.objects.filter(phase=phase).order_by('-number').first()
        number = (last.number + 1) if last else 1

    week, created = ModuleWeek.objects.get_or_create(
        phase=phase, number=number,
        defaults={'order': number, 'is_published': False},
    )
    _link_week_topic(week, topic)
    return week, created


def _link_week_topic(week, topic):
    """Attach ``topic`` to ``week`` (idempotent), appended after existing topics.

    A week works through a *series* of topics; each pack contributes its one topic
    to that series, in import order. Re-importing the same pack is a no-op.
    """
    from apps.learning.models import WeekTopic
    if WeekTopic.objects.filter(week=week, topic=topic).exists():
        return
    last = WeekTopic.objects.filter(week=week).order_by('-order').first()
    order = (last.order + 1) if last else 0
    WeekTopic.objects.create(week=week, topic=topic, order=order)


def _schedule_material(week, item, ref, lesson=None, paper=None, actor=None, order=0, topic=None):
    """Put one imported item on the week's plan, once.

    Keyed on ``source_ref`` exactly as the content rows are, so re-importing a
    pack moves and corrects the same material row rather than stacking a second
    copy beside it.

    Imported material lands **unpublished**. The content is a draft; its place on
    the schedule is a draft too, and both become visible in the one deliberate
    act of publishing.
    """
    from apps.learning.models import ModuleMaterial

    kind = MATERIAL_KIND_BY_TYPE.get(item['type'], ModuleMaterial.KIND_DOCUMENT)
    material = ModuleMaterial.objects.filter(source_ref=ref).first()
    created = material is None
    if created:
        material = ModuleMaterial(source_ref=ref)

    material.phase = week.phase
    material.week = week
    material.topic = topic
    material.kind = kind
    material.title = item['title'][:200]
    material.lesson = lesson
    material.assessment = paper
    material.order = order
    material.is_published = False
    material.created_by = material.created_by or actor
    material.save()
    return material, created


@transaction.atomic
def import_pack(pack, *, actor=None, validate=True):
    """Import ``pack``. Returns an :class:`ImportResult`.

    ``actor`` is the admin/staff user doing the import — recorded as the author
    where the model has somewhere to put it. Permission is the caller's job:
    this function is the mechanism, and the view or command in front of it is
    where "admin and staff only" is enforced.
    """
    if validate:
        validate_or_raise(pack)

    result = ImportResult()
    topic, offering = _resolve_topic(pack)
    result.topic = topic

    week, week_created = _resolve_week(pack, topic, offering)
    result.week = week
    if week is not None and week_created:
        result.warnings.append(
            f'Created week {week.number} on "{week.phase}" to hold this topic. '
            f'It is unpublished and undated — set its dates on the module '
            f'schedule before learners see it.')

    for index, item in enumerate(pack['items']):
        ref = _source_ref(pack, item, index)
        if item['type'] == 'study_guide':
            row = _import_study_guide(pack, item, topic, actor, ref, result)
            lesson, paper = row, None
        else:
            row = _import_paper(pack, item, topic, actor, ref, result)
            lesson, paper = None, row

        if week is not None:
            _schedule_material(week, item, f'{ref}/material', lesson=lesson,
                               paper=paper, actor=actor, order=index, topic=topic)
            result.scheduled += 1

    logger.info('content pack imported: %s · %s — %s',
                offering.label, topic.code, result)
    return result
