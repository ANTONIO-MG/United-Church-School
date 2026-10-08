"""Turn :mod:`core.seed_lessons` data into rows — used by ``manage.py seed_lessons``.

For every subject offering on the UCS spine this creates:

* a **Topic** ``T1W1`` (Term 1, Week 1) carrying the CAPS reference;
* the **schedule** it sits on — the subject's "Term 1" :class:`ModulePhase`
  (``kind='term'``, ``sequence=1``; created if the year plan is not there yet),
  its **Week 1** :class:`ModuleWeek` (Wed 14 – Fri 16 January 2026) and the
  :class:`WeekTopic` link;
* three published **lessons** ("Day 1 · …", "Day 2 · …", "Day 3 · …") built with
  :func:`core.seed_builders.build_lesson`: objectives, notes, key terms, a worked
  example, a YouTube video, the PDF worksheet, the quiz and the homework;
* per day an open **quiz** (auto-marked MCQ / true-false) and **homework** (an
  ``assignment`` the teacher marks), both linked to the lesson;
* per day four :class:`ModuleMaterial` rows on Week 1 (lesson, worksheet, quiz,
  homework), keyed on ``source_ref`` so a re-run finds its own rows.

Idempotent: an offering whose Day lessons already exist is left alone (so a
teacher's edits survive a re-run); ``clear=True`` removes exactly what this seeder
made (by topic code + ``source_ref`` prefix) and rebuilds it.
"""
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from decimal import Decimal
import html as html_lib
import time as clock

from django.core.files.base import ContentFile
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

from core import school
from core import seed_lessons as data
from core.seed_builders import build_lesson

from .pdf import worksheet_pdf

SOURCE = 'seed-lessons'

#: Term 1 2026 opens on Wednesday 14 January; the three days are Wed, Thu, Fri.
DAY_DATES = [date(school.YEAR, 1, 14), date(school.YEAR, 1, 15), date(school.YEAR, 1, 16)]
#: Homework is due the next school day (Friday's on Monday of Week 2).
DUE_DATES = [date(school.YEAR, 1, 15), date(school.YEAR, 1, 16), date(school.YEAR, 1, 19)]


def _term1():
    (m1, d1), (m2, d2) = school.TERMS[0][1], school.TERMS[0][2]
    return date(school.YEAR, m1, d1), date(school.YEAR, m2, d2)


def _label(day):
    return f'{day:%A} {day.day} {day:%B} {day.year}'


@dataclass
class Stats:
    offerings: int = 0
    skipped: int = 0
    missing: list = field(default_factory=list)
    lessons: int = 0
    quizzes: int = 0
    questions: int = 0
    homework: int = 0
    pdfs: int = 0
    videos: int = 0
    video_links: int = 0
    materials: int = 0
    seconds: float = 0.0

    def __str__(self):
        return (f'{self.offerings} offering(s) seeded, {self.skipped} already present · '
                f'{self.lessons} lessons · {self.quizzes} quizzes ({self.questions} questions) · '
                f'{self.homework} homework tasks · {self.pdfs} PDF worksheets · '
                f'{self.videos} embedded videos + {self.video_links} video search links · '
                f'{self.materials} schedule items · {self.seconds:.1f}s')


def _ref(offering, *parts):
    grade = offering.programme.grade or 0
    return '/'.join([SOURCE, f'GR{grade:02d}', offering.code, data.TOPIC_CODE, *map(str, parts)])


def offerings_qs(grades=None, subjects=None):
    from apps.learning.models import ProgrammeModule
    qs = (ProgrammeModule.objects
          .filter(programme__institution__code=school.SCHOOL['code'], is_active=True)
          .select_related('programme', 'module')
          .order_by('programme__grade', 'order', 'id'))
    if grades:
        qs = qs.filter(programme__grade__in=list(grades))
    if subjects:
        qs = qs.filter(code__in=[s.upper() for s in subjects])
    return qs


# ---------------------------------------------------------------------------
# clearing
# ---------------------------------------------------------------------------
def clear(offerings):
    """Remove what this seeder created on ``offerings`` (files included)."""
    from apps.assessments.models import Assessment
    from apps.learning.models import Lesson, ModuleMaterial, ModuleWeek, Topic

    removed = 0
    for offering in offerings:
        prefix = _ref(offering)
        ModuleMaterial.objects.filter(source_ref__startswith=prefix).delete()
        Assessment.objects.filter(source_ref__startswith=prefix).delete()
        topic = Topic.objects.filter(programme_module=offering, code=data.TOPIC_CODE).first()
        if topic is None:
            continue
        for lesson in Lesson.objects.filter(topic=topic):
            for resource in lesson.resources.all():
                if resource.file:
                    resource.file.delete(save=False)
            lesson.delete()
            removed += 1
        # The week we made for the topic goes too, when nothing else is in it.
        for week in ModuleWeek.objects.filter(topics=topic):
            week.week_topics.filter(topic=topic).delete()
            if not week.week_topics.exists() and not week.materials.exists():
                phase = week.phase
                week.delete()
                # The term phase itself stays: it is the subject's year plan.
        topic.delete()
    return removed


# ---------------------------------------------------------------------------
# building
# ---------------------------------------------------------------------------
def _schedule(offering, topic, spec):
    """The Term 1 phase → Week 1 → topic link for ``offering``."""
    from apps.learning.models import ModulePhase, ModuleWeek, WeekTopic

    start, end = _term1()
    # The school term the week sits in: ModulePhase(kind=term, sequence=1), the
    # first block of the default year plan ("Term 1"), shared by every cohort.
    phase, _ = ModulePhase.objects.get_or_create(
        programme_module=offering, kind=ModulePhase.KIND_TERM, sequence=1,
        defaults={'cohort': None, 'title': data.TERM_LABEL, 'order': 1,
                  'starts_on': start, 'ends_on': end, 'is_published': True,
                  'summary': f'{school.TERMS[0][0]} {school.YEAR}: {_label(start)} to '
                             f'{_label(end)}.'[:300]})
    changed = []
    for name, value in (('starts_on', start), ('ends_on', end)):
        if getattr(phase, name) is None:          # fill blanks only; a teacher's dates win
            setattr(phase, name, value)
            changed.append(name)
    if not phase.is_published:
        phase.is_published = True
        changed.append('is_published')
    if changed:
        phase.save(update_fields=changed + ['updated_at'])

    week, _ = ModuleWeek.objects.get_or_create(
        phase=phase, number=1,
        defaults={'title': f'Week 1 · {topic.title}'[:200], 'order': 1,
                  'starts_on': DAY_DATES[0], 'ends_on': DAY_DATES[-1], 'is_published': True,
                  'summary': spec.get('summary') or spec['caps']})
    WeekTopic.objects.get_or_create(week=week, topic=topic, defaults={'order': 0})
    return phase, week


def _list_html(items):
    return '<ul>' + ''.join(f'<li>{html_lib.escape(str(i))}</li>' for i in items) + '</ul>'


def _video_blocks(video, stats):
    if video.get('id'):
        stats.videos += 1
        url = f'https://www.youtube.com/watch?v={video["id"]}'
        caption = video.get('title', '')
        if video.get('channel'):
            caption = f'{caption} — {video["channel"]}'
        return [('video', url, caption, int(video.get('minutes') or 0))]
    stats.video_links += 1
    query = video.get('search', '')
    from urllib.parse import quote_plus
    url = f'https://www.youtube.com/results?search_query={quote_plus(query)}'
    return [('callout', 'info',
             f'<p><strong>Find a video:</strong> search YouTube for '
             f'<a href="{url}" target="_blank" rel="noopener">{html_lib.escape(query)}</a> '
             f'and watch one short clip with an adult or your teacher.</p>')]


def _quiz(offering, topic, lesson, n, day, author):
    """The day's auto-marked quiz, open, linked to the lesson."""
    from apps.assessments.models import Assessment, Choice, Question, Section

    items = day['quiz']
    quiz = Assessment.objects.create(
        topic=topic, module=offering, lesson=lesson, kind=Assessment.KIND_QUIZ,
        title=f'Day {n} quiz · {day["title"]}'[:200],
        description=f'<p>A quick check of today\'s lesson: {len(items)} questions, '
                    f'marked automatically as soon as you submit.</p>',
        total_marks=Decimal(len(items)), pass_mark_pct=50, attempts_allowed=3,
        release_solution=Assessment.RELEASE_ON_SUBMIT, status=Assessment.STATUS_OPEN,
        source_ref=_ref(offering, f'd{n}', 'quiz'), created_by=author)
    section = Section.objects.create(assessment=quiz, title='Questions', order=0,
                                     instructions='Choose the best answer for each question.')
    for order, item in enumerate(items):
        if item[0] == 'tf':
            question = Question.objects.create(section=section, type='tf', text=item[1],
                                               marks=1, order=order)
            Choice.objects.bulk_create([
                Choice(question=question, text='True', is_correct=item[2] is True, order=0),
                Choice(question=question, text='False', is_correct=item[2] is False, order=1)])
        else:
            _kind, text, options, correct = item
            question = Question.objects.create(section=section, type='mcq', text=text,
                                               marks=1, order=order)
            Choice.objects.bulk_create([
                Choice(question=question, text=str(option)[:400], is_correct=(i == correct),
                       order=i) for i, option in enumerate(options)])
    return quiz, len(items)


def _homework(offering, topic, lesson, n, day, author):
    """The day's homework: an assignment the teacher marks."""
    from apps.assessments.models import Assessment, Question, Section

    grade = offering.programme.grade or 0
    hw = day['homework']
    tasks = list(hw['tasks'])
    total = int(hw.get('marks') or len(tasks) * 5) or len(tasks)
    total = max(total, len(tasks))
    due = DUE_DATES[n - 1]
    instructions = hw['instructions']
    description = (f'<p>{instructions}</p>{_list_html(tasks)}'
                   f'<p><strong>Due:</strong> {_label(due)}.</p>')
    homework = Assessment.objects.create(
        topic=topic, module=offering, lesson=lesson, kind=Assessment.KIND_ASSIGNMENT,
        title=f'Day {n} homework · {hw["title"]}'[:200], description=description,
        total_marks=Decimal(total), pass_mark_pct=50, attempts_allowed=1,
        release_solution=Assessment.RELEASE_MANUAL, status=Assessment.STATUS_OPEN,
        source_ref=_ref(offering, f'd{n}', 'homework'), created_by=author,
        solution_notes={'due': due.isoformat()})
    section = Section.objects.create(
        assessment=homework, title='Homework', order=0,
        instructions=f'{instructions} Due {_label(due)}.')
    base, extra = divmod(total, len(tasks))
    upload = grade <= 3
    for order, task in enumerate(tasks):
        marks = base + (1 if order < extra else 0)
        Question.objects.create(
            section=section, order=order, marks=marks,
            type='file_upload' if upload else 'long',
            text=(f'{task} (Ask an adult to take a photo of your work and upload it.)'
                  if upload else task),
            marking_mode=Question.MARKING_MANUAL,
            guidance='Marked by the teacher against the lesson notes.')
    return homework, due


def _lesson_spec(offering, spec, n, day, stats):
    grade = offering.programme.grade or 0
    when = DAY_DATES[n - 1]
    objectives = day['objectives']
    learn = [('text', day['notes'])]
    if day.get('key_terms'):
        learn.append(('table', 'Key terms', ['Term', 'Meaning'],
                      [[t, m] for t, m in day['key_terms']]))
    example = day['example']
    hw = day['homework']
    return {
        'title': f'Day {n} · {day["title"]}'[:200],
        'subtitle': (f'{offering.programme.display_name} {offering.display_name} · '
                     f'{data.TERM_LABEL}, Week 1 · {_label(when)}')[:300],
        'minutes': int(day.get('minutes') or (25 if grade <= 3 else 45)),
        'roles': [],
        'author_role': f'{offering.display_name} · Grade {grade}'[:160],
        'references': [{'text': f'CAPS {offering.module.name}: {spec["caps"]}',
                        'authors': 'Department of Basic Education', 'year': str(school.YEAR),
                        'url': ''}],
        'intro': [
            ('callout', 'info', '<p><strong>Today you will:</strong></p>' + _list_html(objectives)),
        ],
        'sections': [
            {'title': 'Learn', 'summary': day['title'][:300], 'type': 'reading',
             'minutes': 0, 'open': True, 'blocks': learn},
            {'title': example['title'][:200], 'summary': 'Work through it step by step.',
             'type': 'interactive', 'open': False, 'blocks': [('text', example['html'])]},
            {'title': 'Watch', 'summary': (day['video'].get('title') or 'A short video')[:300],
             'type': 'video', 'minutes': int(day['video'].get('minutes') or 0),
             'open': False, 'required': bool(day['video'].get('id')),
             'blocks': _video_blocks(day['video'], stats)},
            {'title': 'Worksheet', 'summary': 'Print or copy it into your book.',
             'type': 'resources', 'open': False,
             'blocks': [('text', f'<p>{html_lib.escape(day["worksheet"]["instructions"])}</p>')]},
            {'title': 'Quick quiz', 'summary': f'{len(day["quiz"])} questions, marked instantly.',
             'type': 'quiz', 'open': False, 'blocks': []},
            {'title': 'Homework', 'summary': hw['title'][:300], 'type': 'assessment',
             'open': False,
             'blocks': [('text', f'<p>{hw["instructions"]}</p>{_list_html(hw["tasks"])}'
                                 f'<p><strong>Due:</strong> {_label(DUE_DATES[n - 1])}.</p>')]},
        ],
    }


def _material(offering, phase, week, topic, n, key, kind, title, order, author, **links):
    from apps.learning.models import ModuleMaterial

    ref = _ref(offering, f'd{n}', key, 'material')
    material = ModuleMaterial.objects.filter(source_ref=ref).first() or ModuleMaterial(source_ref=ref)
    material.phase, material.week, material.topic = phase, week, topic
    material.kind, material.title, material.order = kind, title[:200], order
    material.is_published = True
    material.created_by = material.created_by or author
    for name, value in links.items():
        setattr(material, name, value)
    material.save()
    return material


def seed_offering(offering, spec, stats, author=None):
    from apps.learning.models import (Lesson, LessonBlock, LessonResource, ModuleMaterial,
                                      Topic)
    from apps.learning.authoring import ensure_body_flow

    grade = offering.programme.grade or 0
    topic, created = Topic.objects.get_or_create(
        programme_module=offering, code=data.TOPIC_CODE,
        defaults={'title': spec['topic'][:250], 'order': 0,
                  'reference': f'CAPS {data.TERM_LABEL}'[:160],
                  'description': spec.get('summary') or spec['caps'],
                  'notes': spec['caps'],
                  'slug': slugify(f'{offering.code}-{data.TOPIC_CODE}-{spec["topic"]}')[:270]})
    if Lesson.objects.filter(topic=topic, title__startswith='Day ').count() >= 3:
        stats.skipped += 1
        return False

    phase, week = _schedule(offering, topic, spec)
    start = timezone.make_aware(datetime.combine(DAY_DATES[0], time(7, 30)))

    for n, day in enumerate(spec['days'], 1):
        lesson_spec = _lesson_spec(offering, spec, n, day, stats)
        lesson = build_lesson(lesson_spec, module=offering, author=author, status='published')
        lesson.topic = topic
        lesson.publish_at = None
        lesson.save(update_fields=['topic', 'publish_at', 'updated_at'])
        ensure_body_flow(lesson)
        stats.lessons += 1

        # Learn, example, Watch, Worksheet, Quick quiz, Homework — by position, since
        # the example's title is the author's.
        ordered = list(lesson.sections.order_by('order', 'id'))
        sections = {'Worksheet': ordered[3], 'Quick quiz': ordered[4], 'Homework': ordered[5]}

        # --- worksheet PDF: an attachment + a download card in the section ---
        pdf = worksheet_pdf(grade=grade, subject=offering.display_name, day_number=n, day=day,
                            topic=spec['topic'], date_label=_label(DAY_DATES[n - 1]))
        resource = LessonResource(lesson=lesson, kind='pdf',
                                  title=f'Day {n} worksheet (PDF)', order=0)
        resource.file.save(f'ucs-gr{grade:02d}-{offering.code.lower()}-t1w1-day{n}-worksheet.pdf',
                           ContentFile(pdf), save=False)
        resource.save()
        stats.pdfs += 1
        sheet_section = sections.get('Worksheet')
        block = LessonBlock.objects.create(
            lesson=lesson, section=sheet_section, block_type=LessonBlock.TYPE_FILE,
            order=lesson.blocks.count(),
            data={'title': f'Day {n} worksheet — {day["title"]}'[:200],
                  'description': f'PDF · {len(day["worksheet"]["exercises"])} exercises'})
        block.media.name = resource.file.name          # same stored file, no copy
        block.save(update_fields=['media'])

        # --- quiz + homework, inside their sections ---
        quiz, count = _quiz(offering, topic, lesson, n, day, author)
        stats.quizzes += 1
        stats.questions += count
        LessonBlock.objects.create(
            lesson=lesson, section=sections.get('Quick quiz'), block_type=LessonBlock.TYPE_QUIZ,
            order=lesson.blocks.count(), assessment=quiz, data={'title': quiz.title})
        homework, _due = _homework(offering, topic, lesson, n, day, author)
        stats.homework += 1
        LessonBlock.objects.create(
            lesson=lesson, section=sections.get('Homework'), block_type=LessonBlock.TYPE_QUIZ,
            order=lesson.blocks.count(), assessment=homework, data={'title': homework.title})

        # --- the schedule: Week 1 lists the day's four items in order ---
        base = (n - 1) * 10
        released = start + timedelta(days=n - 1)
        for k, (key, kind, title, links) in enumerate((
                ('lesson', ModuleMaterial.KIND_STUDY_GUIDE, lesson.title, {'lesson': lesson}),
                ('worksheet', ModuleMaterial.KIND_DOCUMENT, f'Day {n} worksheet (PDF)',
                 {'file': resource.file.name}),
                ('quiz', ModuleMaterial.KIND_QUESTIONS, quiz.title, {'assessment': quiz}),
                ('homework', ModuleMaterial.KIND_ASSESSMENT, homework.title,
                 {'assessment': homework}))):
            material = _material(offering, phase, week, topic, n, key, kind, title,
                                 base + k, author, **links)
            if material.available_from is None:
                material.available_from = released
                material.save(update_fields=['available_from'])
            stats.materials += 1
    stats.offerings += 1
    return True


def seed(*, grades=None, subjects=None, clear_first=False, author=None, log=None):
    """Seed every matching offering. Returns :class:`Stats`."""
    began = clock.monotonic()
    stats = Stats()
    lessons = data.load()
    offerings = list(offerings_qs(grades, subjects))
    if clear_first:
        with transaction.atomic():
            clear(offerings)
    for offering in offerings:
        key = (offering.programme.grade, offering.code)
        spec = lessons.get(key)
        if spec is None:
            stats.missing.append(key)
            continue
        with transaction.atomic():
            made = seed_offering(offering, spec, stats, author=author)
        if log:
            log(f'  {"+" if made else "="} Grade {key[0]:>2} {offering.code:<14} {spec["topic"]}')
    stats.seconds = clock.monotonic() - began
    return stats
