"""core/seed_lessons  —  demo lesson content: Term 1, Week 1 for every subject offering.

Three days of lessons ("Day 1", "Day 2", "Day 3") for every grade × subject on the
academic spine (:mod:`core.academic_spine`, 103 offerings), written against the
CAPS Term 1 teaching plans for the start of the 2026 school year. The data is
plain Python; ``python manage.py seed_lessons`` turns it into Topics, Lessons
(sections + blocks), PDF worksheets, quizzes and homework, and places them on
each subject's schedule (Term 1 → Week 1).

The content is generic CAPS teaching material. It says nothing about the school
itself beyond the subject and grade it belongs to.

Data shape
----------
Each content module (``foundation.py``, ``senior_a.py`` …) defines ``LESSONS``::

    LESSONS = {
        (1, 'MATH'): {                       # (grade, subject code on the spine)
            'topic': 'Counting and number recognition to 20',
            'caps': 'Numbers, operations and relationships: count, read and write '
                    'number symbols and names 1–20',          # the CAPS reference
            'summary': 'One or two sentences on what the week covers.',
            'days': [DAY_1, DAY_2, DAY_3],    # exactly three
        },
    }

A **day** is::

    {
        'title': 'Counting objects to 10',     # lesson becomes "Day 1 · Counting objects to 10"
        'minutes': 30,                         # estimated study time
        'objectives': ['…', '…', '…'],         # 2–5 "I can / Learners will" statements
        'notes': '<p>…</p><ul><li>…</li></ul>',  # the explanation (HTML: p, ul, ol, li, strong, em, br)
        'key_terms': [('term', 'meaning'), …], # optional, rendered as a table
        'example': {'title': 'Worked example', 'html': '<p>…</p>'},  # worked example / class activity
        'video': {'id': 'XXXXXXXXXXX',         # a VERIFIED YouTube id (oEmbed 200) …
                  'title': 'Title as on YouTube', 'channel': 'Channel name', 'minutes': 5},
                 # … or, when no verified video fits:  {'search': 'youtube search words'}
        'worksheet': {'instructions': 'Answer all the questions.',
                      'exercises': ['Count the stars: * * * * *', …]},   # 4–8 plain-text lines
        'quiz': [                              # 3–5 auto-marked questions
            ('mcq', 'Question text?', ['option A', 'option B', 'option C'], 1),   # index of correct
            ('tf', 'A statement that is true or false.', True),
        ],
        'homework': {'title': 'Practise counting',   # short title
                     'instructions': 'One or two sentences.',
                     'tasks': ['…', '…'],             # 1–4 tasks
                     'marks': 10},
    }

:func:`validate` checks every module against this shape (pure Python, no Django).
"""
from importlib import import_module

#: The content modules, in phase order. Each defines ``LESSONS``.
MODULES = [
    'foundation',
    'intermediate_a',
    'intermediate_b',
    'senior_a',
    'senior_b',
    'fet_core',
    'fet_maths_sci',
    'fet_humanities',
]

#: Term 1 2026 opens on Wednesday 14 January — Day 1, 2, 3 are 14, 15, 16 January.
TERM_LABEL = 'Term 1'
TOPIC_CODE = 'T1W1'


def load(strict=False):
    """``{(grade, code): spec}`` across every content module that exists."""
    out = {}
    for name in MODULES:
        try:
            module = import_module(f'{__name__}.{name}')
        except ModuleNotFoundError as exc:
            if strict or exc.name != f'{__name__}.{name}':
                raise
            continue
        for key, spec in getattr(module, 'LESSONS', {}).items():
            if key in out:
                raise ValueError(f'{key} defined twice (second time in {name})')
            out[key] = spec
    return out


def _check_day(where, day, problems):
    def need(cond, msg):
        if not cond:
            problems.append(f'{where}: {msg}')

    need(isinstance(day, dict), 'day is not a dict')
    if not isinstance(day, dict):
        return
    for field in ('title', 'objectives', 'notes', 'example', 'video', 'worksheet', 'quiz', 'homework'):
        need(field in day, f'missing {field!r}')
    need(isinstance(day.get('title'), str) and 0 < len(day.get('title', '')) <= 150, 'title 1–150 chars')
    objectives = day.get('objectives') or []
    need(2 <= len(objectives) <= 6, 'objectives: 2–6 items')
    need(isinstance(day.get('notes'), str) and len(day.get('notes', '')) > 40, 'notes too short')
    example = day.get('example') or {}
    need(isinstance(example, dict) and example.get('title') and example.get('html'), 'example needs title + html')
    for term in day.get('key_terms') or []:
        need(isinstance(term, (tuple, list)) and len(term) == 2, f'key term {term!r} is not a pair')
    video = day.get('video') or {}
    if 'id' in video:
        vid = video['id']
        need(isinstance(vid, str) and len(vid) == 11, f'video id {vid!r} is not 11 chars')
        need(video.get('title'), 'video needs its title')
    else:
        need(bool(video.get('search')), 'video needs an id or a search')
    sheet = day.get('worksheet') or {}
    need(sheet.get('instructions') and 3 <= len(sheet.get('exercises') or []) <= 12,
         'worksheet needs instructions + 3–12 exercises')
    quiz = day.get('quiz') or []
    need(3 <= len(quiz) <= 6, f'quiz has {len(quiz)} questions (3–6)')
    for q in quiz:
        if not isinstance(q, (tuple, list)) or not q:
            need(False, f'bad quiz item {q!r}')
            continue
        if q[0] == 'mcq':
            ok = (len(q) == 4 and isinstance(q[2], (list, tuple)) and 2 <= len(q[2]) <= 6
                  and isinstance(q[3], int) and 0 <= q[3] < len(q[2]))
            need(ok, f'bad mcq {q[1:2]!r}')
            if ok:
                need(len(set(q[2])) == len(q[2]), f'duplicate options in {q[1]!r}')
        elif q[0] == 'tf':
            need(len(q) == 3 and isinstance(q[2], bool), f'bad tf {q[1:2]!r}')
        else:
            need(False, f'unknown quiz type {q[0]!r}')
    hw = day.get('homework') or {}
    need(hw.get('title') and hw.get('instructions') and 1 <= len(hw.get('tasks') or []) <= 6,
         'homework needs title, instructions and 1–6 tasks')


def validate(lessons=None):
    """A list of problems (empty = valid)."""
    lessons = load() if lessons is None else lessons
    problems = []
    for key, spec in lessons.items():
        where = f'{key}'
        if not (isinstance(key, tuple) and len(key) == 2 and isinstance(key[0], int)):
            problems.append(f'{where}: key must be (grade, code)')
        for field in ('topic', 'caps', 'days'):
            if not spec.get(field):
                problems.append(f'{where}: missing {field!r}')
        days = spec.get('days') or []
        if len(days) != 3:
            problems.append(f'{where}: needs exactly 3 days, has {len(days)}')
        for index, day in enumerate(days, 1):
            _check_day(f'{where} day {index}', day, problems)
    return problems


def expected_keys():
    """Every (grade, code) the spine offers — what the content must cover."""
    from core import school
    return [(grade, code) for grade in school.GRADES for code, _g, _n in school.subjects_for(grade)]

