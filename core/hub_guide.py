"""The **General course** — how to use the UCS Learning Hub.

Every account on the hub is enrolled here. It is one course with five modules,
each covering one part of the platform, and each module carries a *separate
lesson per audience*: one written for learners, one for educators and staff, and
one for parents. ``Lesson.target_roles`` keeps them apart, so a student opening
"Communication" sees the learner's guide and never the educator's, and vice
versa.

The content lives here rather than in the seed script so it can be read, edited
and reviewed as writing. :func:`build` turns it into real courses, modules,
lessons, sections and blocks via :mod:`core.seed_builders`.

Diagrams are generated locally by :mod:`core.seed_media` — no external image
host, so they keep working offline and ship with the repository.
"""

from __future__ import annotations

from core import seed_builders, seed_media

BRAND = 'UCS Learning Hub'

STUDENT = ['student']
TEAM = ['educator', 'staff', 'admin']
PARENT = ['parent']

# Screencasts have not been recorded for this hub yet. These point at a stable,
# well-known public explainer so the video player is demonstrable out of the
# box — replace the URL with your own recording when you have one.
PLACEHOLDER_VIDEO = 'https://www.youtube.com/watch?v=rfscVS0vtbw'

# ---------------------------------------------------------------------------
# The course
# ---------------------------------------------------------------------------
COURSE = {
    'title': f'Getting Started with the {BRAND}',
    'code': 'HUB-101',
    'subtitle': 'Your guide to everything this hub can do — written for you, whoever you are.',
    'summary': (
        'A short, practical orientation to the UCS Learning Hub. Five modules, '
        'one for each part of the platform, each explained from the ground up.'
    ),
    'description': (
        'Everyone on this platform is enrolled in this course, and everyone gets their own '
        'version of it.\n\n'
        'The UCS Learning Hub brings your classes, your conversations, your live sessions, '
        'your marks and your admin into one place. That is a lot of ground, so rather than hand '
        'you a manual we have broken it into five short modules — Communication, Lessons, '
        'Online Classes, Dashboard & Student Matrix, and Quizzes & Assessments. Work through '
        'them in any order; each one stands on its own and takes about fifteen minutes.\n\n'
        'What you see inside each module depends on who you are. Learners get the guide for '
        'learners. Educators and staff get the version that covers building and running the '
        'thing. Parents get the version about following a learner\'s progress without getting '
        'in the way. Same course, three honest answers to "how does this work?".\n\n'
        'Nothing here is graded and nothing is timed. Come back to it whenever the platform '
        'does something you did not expect.'
    ),
    'duration': 'Self-paced · about 75 minutes in total',
    'level': 'Everyone',
    'language': 'English',
    'fee': 0,
    'certificate_offered': False,
    'learning_outcomes': (
        'Find your way around the hub without hunting for anything\n'
        'Talk to your class, your educator and the wider hub with confidence\n'
        'Open, work through and keep track of a lesson — including your own notes and bookmarks\n'
        'Join, or run, a live online class\n'
        'Read your dashboard, your progress and your marks honestly\n'
        'Sit — or set — a quiz or assessment, and understand how integrity monitoring works'
    ),
    'whats_included': (
        'Five illustrated modules covering every part of the platform\n'
        'A version written specifically for your role\n'
        'Diagrams of every screen you will use\n'
        'Quick-reference handouts you can download and keep\n'
        'A place to leave yourself notes as you go'
    ),
    'requirements': (
        'A device with a modern browser (Chrome, Edge, Firefox or Safari)\n'
        'An internet connection — a phone connection is fine for everything except live video\n'
        'Your sign-in e-mail and password. Nothing else.'
    ),
    'prerequisites': 'None. This is the starting point.',
    'what_you_get': (
        'Permanent access — this course never expires and is never archived\n'
        'A written guide for your exact role, updated as the hub changes\n'
        'Downloadable quick-reference sheets'
    ),
    'min_study_hours': 2,
    'session_schedule': 'No scheduled sessions — work through it whenever suits you.',
}


# ---------------------------------------------------------------------------
# Diagrams
# ---------------------------------------------------------------------------
# Column stops for the student-matrix diagram, as percentages across the row.
_MATRIX_COLUMNS = (0, 26, 42, 57, 71, 88)


def _row(*values):
    """Pair each cell with its column stop, so a diagram row lines up."""
    return list(zip(values, _MATRIX_COLUMNS))


def _diagrams():
    """Draw (once) every illustration the guide uses. Returns {key: media path}."""
    base = 'lessons/guide'
    out = {}

    out['navigation'] = seed_media.wireframe(
        f'{base}/navigation.png', 'How the hub is laid out', [
            {'x': 0, 'y': 0, 'w': 22, 'h': 100, 'kind': 'nav', 'label': 'Left menu',
             'note': 'Everything you can reach: your course, lessons, chat, live classes, assessments, your profile.'},
            {'x': 25, 'y': 0, 'w': 75, 'h': 13, 'kind': 'bar', 'label': 'Top bar — search, your course button, the bell, your avatar'},
            {'x': 25, 'y': 17, 'w': 50, 'h': 83, 'kind': 'panel', 'label': 'The page you opened',
             'note': 'Whatever you clicked lands here — a lesson, a chat, your dashboard.'},
            {'x': 78, 'y': 17, 'w': 22, 'h': 83, 'kind': 'accent', 'label': 'Context panel',
             'note': 'Things about the page you are on: your notes, activity, files, members.'},
        ], tone='indigo')

    out['chat'] = seed_media.wireframe(
        f'{base}/chat.png', 'Chat: rooms on the left, the conversation on the right', [
            {'x': 0, 'y': 0, 'w': 30, 'h': 100, 'kind': 'panel', 'label': 'Your rooms'},
            {'x': 2, 'y': 14, 'w': 26, 'h': 13, 'kind': 'row', 'label': 'Your course group'},
            {'x': 2, 'y': 29, 'w': 26, 'h': 13, 'kind': 'row', 'label': 'One per module'},
            {'x': 2, 'y': 44, 'w': 26, 'h': 13, 'kind': 'row', 'label': 'Direct messages'},
            {'x': 33, 'y': 0, 'w': 67, 'h': 12, 'kind': 'bar', 'label': 'Who you are talking to'},
            {'x': 33, 'y': 15, 'w': 67, 'h': 70, 'kind': 'panel', 'label': 'The conversation',
             'note': 'Messages, files, images and replies, newest at the bottom.'},
            {'x': 33, 'y': 88, 'w': 67, 'h': 12, 'kind': 'accent', 'label': 'Write here — attach a file with the clip'},
        ], tone='green')

    out['player'] = seed_media.wireframe(
        f'{base}/lesson-player.png', 'A lesson: sections that open, and your own panel beside them', [
            {'x': 0, 'y': 0, 'w': 70, 'h': 14, 'kind': 'bar', 'label': 'Lesson title, how long it takes, your progress bar'},
            {'x': 0, 'y': 17, 'w': 70, 'h': 15, 'kind': 'row', 'label': 'READING · Section one · 6 min read · done'},
            {'x': 0, 'y': 34, 'w': 70, 'h': 26, 'kind': 'panel', 'label': 'VIDEO · Section two — open',
             'note': 'The content appears when you click the section open. Everything else stays folded away.'},
            {'x': 0, 'y': 62, 'w': 70, 'h': 15, 'kind': 'row', 'label': 'QUIZ · Section three · 20 min · locked'},
            {'x': 0, 'y': 79, 'w': 70, 'h': 15, 'kind': 'row', 'label': 'ASSESSMENT · Section four · locked'},
            {'x': 73, 'y': 0, 'w': 27, 'h': 94, 'kind': 'accent', 'label': 'Your panel',
             'note': 'Progress · your private notes for the open section · bookmarks · your marks · the module\'s messages.'},
        ], tone='cyan')

    out['builder'] = seed_media.wireframe(
        f'{base}/lesson-builder.png', 'Building a lesson: the lesson on the left, your tools on the right', [
            {'x': 0, 'y': 0, 'w': 68, 'h': 12, 'kind': 'bar', 'label': 'Title · saved automatically · Preview as learner'},
            {'x': 0, 'y': 15, 'w': 68, 'h': 20, 'kind': 'panel', 'label': 'Introduction',
             'note': 'Shown above the sections. Keep it short.'},
            {'x': 0, 'y': 38, 'w': 68, 'h': 28, 'kind': 'panel', 'label': 'Section 1 — title, kind, minutes, lock',
             'note': 'Drag content in from the palette. Drag the handle to reorder.'},
            {'x': 0, 'y': 69, 'w': 68, 'h': 25, 'kind': 'panel', 'label': 'Section 2'},
            {'x': 71, 'y': 0, 'w': 29, 'h': 30, 'kind': 'accent', 'label': 'Add content',
             'note': 'Text, image, video, quiz, live session — drag onto a section.'},
            {'x': 71, 'y': 33, 'w': 29, 'h': 22, 'kind': 'panel', 'label': 'Build with AI',
             'note': 'Describe what you want; review the draft.'},
            {'x': 71, 'y': 58, 'w': 29, 'h': 36, 'kind': 'panel', 'label': 'Who gets this',
             'note': 'One student, a whole class, or the module. Then publish.'},
        ], tone='indigo')

    out['live'] = seed_media.wireframe(
        f'{base}/live-class.png', 'A live class', [
            {'x': 0, 'y': 0, 'w': 74, 'h': 74, 'kind': 'nav', 'label': 'Whoever is speaking',
             'note': 'The educator\'s screen or camera fills the stage.'},
            {'x': 0, 'y': 78, 'w': 74, 'h': 22, 'kind': 'accent', 'label': 'Mic · Camera · Share screen · Raise hand · Leave'},
            {'x': 77, 'y': 0, 'w': 23, 'h': 46, 'kind': 'panel', 'label': 'Everyone in the room'},
            {'x': 77, 'y': 50, 'w': 23, 'h': 50, 'kind': 'panel', 'label': 'Class chat',
             'note': 'Ask here without interrupting.'},
        ], tone='green')

    out['dashboard'] = seed_media.wireframe(
        f'{base}/dashboard.png', 'Your dashboard', [
            {'x': 0, 'y': 0, 'w': 24, 'h': 26, 'kind': 'accent', 'label': 'Course progress'},
            {'x': 26, 'y': 0, 'w': 24, 'h': 26, 'kind': 'panel', 'label': 'Lessons done'},
            {'x': 52, 'y': 0, 'w': 24, 'h': 26, 'kind': 'panel', 'label': 'Average mark'},
            {'x': 78, 'y': 0, 'w': 22, 'h': 26, 'kind': 'panel', 'label': 'Attendance'},
            {'x': 0, 'y': 30, 'w': 62, 'h': 40, 'kind': 'panel', 'label': 'What to do next',
             'note': 'The lesson you stopped halfway through, the assessment closing soonest, the next live class.'},
            {'x': 65, 'y': 30, 'w': 35, 'h': 40, 'kind': 'panel', 'label': 'Your timetable'},
            {'x': 0, 'y': 74, 'w': 100, 'h': 26, 'kind': 'panel', 'label': 'Recent activity — everything that happened while you were away'},
        ], tone='cyan')

    out['matrix'] = seed_media.wireframe(
        f'{base}/student-matrix.png', 'The student matrix: everyone, on one screen', [
            {'x': 0, 'y': 0, 'w': 100, 'h': 12, 'kind': 'bar', 'label': 'Filter by course · module · status'},
            {'x': 0, 'y': 15, 'w': 100, 'h': 13, 'kind': 'accent', 'cells': _row(
                'Student', 'Lessons', 'Quizzes', 'Average', 'Attendance', 'Flags')},
            {'x': 0, 'y': 30, 'w': 100, 'h': 13, 'kind': 'row', 'cells': _row(
                'Anesu Dube', '8/12', '82%', '74%', '93%', '—')},
            {'x': 0, 'y': 45, 'w': 100, 'h': 13, 'kind': 'row', 'cells': _row(
                'Rudo Sithole', '12/12', '91%', '88%', '100%', '—')},
            {'x': 0, 'y': 60, 'w': 100, 'h': 13, 'kind': 'row', 'cells': _row(
                'Farai Chirwa', '3/12', '41%', '48%', '52%', 'behind')},
            {'x': 0, 'y': 75, 'w': 100, 'h': 13, 'kind': 'row', 'cells': _row(
                'Tendai Marimo', '11/12', '79%', '71%', '88%', '—')},
        ], tone='amber')

    out['quiz'] = seed_media.wireframe(
        f'{base}/quiz.png', 'Sitting a quiz', [
            {'x': 0, 'y': 0, 'w': 100, 'h': 14, 'kind': 'bar', 'label': 'Quiz title · 20 marks · pass 50%          Time left  14:32'},
            {'x': 0, 'y': 17, 'w': 100, 'h': 12, 'kind': 'accent', 'label': 'This assessment is monitored — stay on this page until you submit'},
            {'x': 0, 'y': 32, 'w': 100, 'h': 24, 'kind': 'panel', 'label': '1. Question text',
             'note': 'Pick one · pick several · type your answer · upload a file.'},
            {'x': 0, 'y': 59, 'w': 100, 'h': 24, 'kind': 'panel', 'label': '2. Question text'},
            {'x': 66, 'y': 87, 'w': 34, 'h': 13, 'kind': 'accent', 'label': 'Submit'},
        ], tone='amber')

    out['guard'] = seed_media.wireframe(
        f'{base}/exam-guard.png', 'What happens if you leave a monitored assessment', [
            {'x': 0, 'y': 0, 'w': 100, 'h': 30, 'kind': 'nav', 'label': 'Return to your assessment',
             'note': 'The questions blur and this covers the page the moment focus leaves the window.'},
            {'x': 0, 'y': 34, 'w': 48, 'h': 28, 'kind': 'panel', 'label': 'What counts',
             'note': 'Switching tab · another program · pointer off the page too long · leaving fullscreen.'},
            {'x': 52, 'y': 34, 'w': 48, 'h': 28, 'kind': 'panel', 'label': 'What is recorded',
             'note': 'Each event, when it happened, and how long you were away.'},
            {'x': 0, 'y': 66, 'w': 100, 'h': 34, 'kind': 'accent', 'label': 'After the limit',
             'note': 'Your educator is shown the report — or, if they chose that setting, the attempt ends and submits.'},
        ], tone='red')

    out['notifications'] = seed_media.wireframe(
        f'{base}/notifications.png', 'The bell, and what is behind it', [
            {'x': 0, 'y': 0, 'w': 100, 'h': 13, 'kind': 'bar', 'label': 'All · Unread · Mentions        Mark all as read'},
            {'x': 0, 'y': 17, 'w': 100, 'h': 17, 'kind': 'row', 'label': 'New lesson published in Communication'},
            {'x': 0, 'y': 37, 'w': 100, 'h': 17, 'kind': 'row', 'label': 'Your quiz has been marked — 82%'},
            {'x': 0, 'y': 57, 'w': 100, 'h': 17, 'kind': 'row', 'label': 'Live class starts in 30 minutes'},
            {'x': 0, 'y': 77, 'w': 100, 'h': 23, 'kind': 'accent', 'label': 'Click any one to read it in full',
             'note': 'Longer notifications open as a proper reading page, not a pop-up.'},
        ], tone='indigo')

    out['parent'] = seed_media.wireframe(
        f'{base}/parent-view.png', 'What a parent sees', [
            {'x': 0, 'y': 0, 'w': 48, 'h': 30, 'kind': 'accent', 'label': 'Your learner',
             'note': 'Name, course, and how far through they are.'},
            {'x': 52, 'y': 0, 'w': 48, 'h': 30, 'kind': 'panel', 'label': 'This week',
             'note': 'Lessons opened, assessments sat, classes attended.'},
            {'x': 0, 'y': 34, 'w': 100, 'h': 30, 'kind': 'panel', 'label': 'Marks and reports',
             'note': 'Published results only — nothing while it is still being marked.'},
            {'x': 0, 'y': 68, 'w': 100, 'h': 32, 'kind': 'panel', 'label': 'Messages from the school',
             'note': 'Announcements, and a direct line to the educator.'},
        ], tone='green')

    out['marking'] = seed_media.wireframe(
        f'{base}/marking.png', 'The marking queue', [
            {'x': 0, 'y': 0, 'w': 100, 'h': 13, 'kind': 'bar', 'label': 'Waiting for you · oldest first'},
            {'x': 0, 'y': 17, 'w': 100, 'h': 15, 'kind': 'row', 'label': 'Rudo Sithole · Essay · 3 questions to mark'},
            {'x': 0, 'y': 35, 'w': 100, 'h': 15, 'kind': 'row', 'label': 'Anesu Dube · Assignment · 2 questions to mark'},
            {'x': 0, 'y': 53, 'w': 100, 'h': 20, 'kind': 'panel', 'label': 'Open one and you get the rubric beside the answer',
             'note': 'Award the marks, write the feedback, move on. The grade recalculates itself.'},
            {'x': 0, 'y': 77, 'w': 100, 'h': 23, 'kind': 'accent', 'label': 'Flagged for integrity review',
             'note': 'Auto-marked quizzes never reach the queue above, so anything the focus guard flagged is listed here separately.'},
        ], tone='amber')

    return {k: v for k, v in out.items() if v}


# ---------------------------------------------------------------------------
# Small helpers that keep the content below readable
# ---------------------------------------------------------------------------
def _p(*paragraphs):
    return ('text', ''.join(f'<p>{p}</p>' for p in paragraphs))


def _ul(intro, items):
    body = f'<p>{intro}</p><ul>' + ''.join(f'<li>{i}</li>' for i in items) + '</ul>'
    return ('text', body)


def _note(variant, title, body):
    return ('callout', variant, f'<p><strong>{title}</strong><br>{body}</p>')


def _pic(diagrams, key, caption):
    path = diagrams.get(key)
    return ('image', path, caption, caption) if path else _p(caption)


# ---------------------------------------------------------------------------
# The five modules
# ---------------------------------------------------------------------------
def module_specs(diagrams):
    """Every module, with one lesson per audience."""
    d = diagrams
    return [
        _communication(d), _lessons(d), _online_classes(d), _dashboard(d), _assessments(d),
    ]


# --- 1. Communication -------------------------------------------------------
def _communication(d):
    return {
        'name': 'Communication',
        'code': 'HUB-COM',
        'description': ('Chat, direct messages, discussions, announcements, notifications and '
                        'mail — how people talk to each other on this hub, and how to be heard.'),
        'lessons': [
            {
                'title': 'Talking to your class, your educator and everyone else',
                'subtitle': 'Where every conversation on the hub happens, and which one to use.',
                'minutes': 14, 'roles': STUDENT,
                'intro': [
                    _p('Almost every question you will have is faster to ask than to look up. This '
                       'lesson shows you the four places a conversation can happen here, and which '
                       'one to reach for.'),
                    _pic(d, 'navigation', 'Where things live: the menu on the left, the page in the middle, context on the right.'),
                ],
                'sections': [
                    {'title': 'Group chat — your course and your modules', 'type': 'reading', 'minutes': 4,
                     'summary': 'The rooms you were put in automatically.', 'open': True,
                     'blocks': [
                         _p('The moment you were enrolled, the hub put you in a group chat for your course '
                            'and one for every module in it. You do not have to join anything — open '
                            '<strong>Chat</strong> in the left menu and they are waiting.'),
                         _pic(d, 'chat', 'Rooms on the left, the conversation on the right, the box you type in at the bottom.'),
                         _ul('Use the module room for anything about that module:', [
                             'A question about something in a lesson.',
                             'Checking what was covered in a class you missed.',
                             'Sharing a link or a file — use the paperclip.',
                             'Working through a problem out loud with other people.',
                         ]),
                         _note('tip', 'Ask in the room, not in a DM',
                               'If you are stuck, three other people probably are too. Asking in the '
                               'module room means everybody gets the answer, and your educator only '
                               'has to write it once.'),
                     ]},
                    {'title': 'Direct messages — one person at a time', 'type': 'reading', 'minutes': 2,
                     'summary': 'Private, and best kept for things that really are private.',
                     'blocks': [
                         _p('You can message any person you share a course or module with. Open their '
                            'profile and choose <strong>Message</strong>, or start a new conversation '
                            'from the Chat page.'),
                         _p('Direct messages are private between the two of you — but they are still on '
                            'a school system, and staff can access them if there is a safeguarding '
                            'concern. Say things you would be comfortable having read back to you.'),
                     ]},
                    {'title': 'Discussions — questions that deserve a thread', 'type': 'reading', 'minutes': 3,
                     'summary': 'Slower than chat, and much easier to find again.',
                     'blocks': [
                         _p('Chat scrolls away. A <strong>discussion</strong> does not. When your question '
                            'is bigger than one line — "can someone explain why this works?" — start a '
                            'discussion in the module instead.'),
                         _ul('A discussion gives you things chat cannot:', [
                             'A title, so people know what it is before they open it.',
                             'Threaded replies, so two conversations can happen without tangling.',
                             'An <strong>accepted answer</strong> your educator can mark, so the next '
                             'person to ask finds the right reply first.',
                             'Likes, so the genuinely useful replies rise.',
                         ]),
                         _note('info', 'Tag people with @',
                               'Typing @ and a name notifies that person directly. Use it when you need '
                               'one specific person — not on every post.'),
                     ]},
                    {'title': 'Notifications — the bell, and how to keep it useful', 'type': 'reading', 'minutes': 3,
                     'summary': 'What reaches you, and how to change it.',
                     'blocks': [
                         _pic(d, 'notifications', 'The bell collects everything: new lessons, marks, class reminders, mentions.'),
                         _p('The bell in the top bar collects everything the hub needs to tell you: a new '
                            'lesson published, a mark released, a live class starting, someone mentioning '
                            'you. Click any notification to read it in full — longer ones open as a proper '
                            'reading page.'),
                         _p('Under <strong>Settings › Notifications</strong> you choose what also reaches '
                            'you by e-mail. Our advice: leave marks and live classes on, and turn chat '
                            'e-mails off — otherwise the important ones get buried.'),
                     ]},
                    {'title': 'Announcements and mail', 'type': 'reading', 'minutes': 2,
                     'summary': 'The one-way channels, and why you cannot reply to some of them.',
                     'blocks': [
                         _p('<strong>Announcements</strong> come from staff and go to a whole course or the '
                            'whole hub. They are one-way on purpose — they are for things everyone must '
                            'know, not for discussion. If you need to respond, use the module chat or '
                            'message the sender.'),
                         _p('<strong>Mail</strong> is the hub\'s internal inbox, used for anything formal: '
                            'fee notices, results letters, official correspondence. Treat it like e-mail, '
                            'because that is what it is.'),
                         _note('warning', 'One rule for all of it',
                               'Everything you write here is attached to your name and kept. Be the person '
                               'you would want in your group chat.'),
                     ]},
                ],
                'attachments': [(
                    'Which channel should I use?', 'text/plain',
                    'WHICH CHANNEL SHOULD I USE?\n'
                    '===========================\n\n'
                    'Quick question about a module      -> the module group chat\n'
                    'Something private, one person       -> a direct message\n'
                    'A question worth keeping/finding    -> a discussion in the module\n'
                    'Something formal or official        -> Mail\n'
                    'You are staff and everyone must know-> an Announcement\n\n'
                    'Rule of thumb: if more than one person benefits from the answer,\n'
                    'ask somewhere more than one person can see it.\n'
                )],
            },
            {
                'title': 'Running communication in your modules',
                'subtitle': 'Keeping a class talking, keeping it on topic, and keeping the record.',
                'minutes': 15, 'roles': TEAM,
                'intro': [
                    _p('You have the same chat, discussions and messages your learners do, plus the '
                       'tools to broadcast and to moderate. This is how to use them without drowning.'),
                ],
                'sections': [
                    {'title': 'The rooms you already own', 'type': 'reading', 'minutes': 3,
                     'summary': 'Created for you, and kept in sync automatically.', 'open': True,
                     'blocks': [
                         _pic(d, 'chat', 'Every course and every module has its own room, membership kept in sync with enrolment.'),
                         _p('Every course and module has a chat room, and membership tracks enrolment '
                            'automatically — enrol a student and they appear; move them and they move. '
                            'You never maintain a list.'),
                         _note('tip', 'Post first',
                               'A silent room stays silent. Open each of your module rooms in week one '
                               'and post something — the week ahead, a question, anything. Rooms that '
                               'start empty tend to stay empty.'),
                     ]},
                    {'title': 'Announcements — when everyone must know', 'type': 'reading', 'minutes': 3,
                     'summary': 'Reach a course or the whole hub in one action.',
                     'blocks': [
                         _p('An announcement composes once and delivers to every member of the audience '
                            'you pick — as a notification, and by e-mail for anyone who has that turned '
                            'on. Use it for changes of date, closures, deadlines: things where "I posted '
                            'it in chat" is not good enough.'),
                         _ul('Before you send one, check:', [
                             'Is the <strong>audience</strong> right? A hub-wide announcement about one '
                             'module annoys hundreds of people.',
                             'Does the <strong>title</strong> say the thing? "Friday\'s class moved to 10am" '
                             'beats "Important notice".',
                             'Would a chat message have done? Save announcements for when they matter, '
                             'or people stop reading them.',
                         ]),
                     ]},
                    {'title': 'Discussions — where the good teaching happens', 'type': 'reading', 'minutes': 4,
                     'summary': 'Threads, accepted answers, and building a resource that lasts.',
                     'blocks': [
                         _p('A discussion outlives the class it came from. When a learner asks something '
                            'good in chat, move it: start a discussion, answer it there, and mark the '
                            'answer <strong>accepted</strong>. Do that for a term and you have built a '
                            'genuine reference for next year\'s class.'),
                         _p('You can pin a discussion to the top of a module, and close one when it has '
                            'run its course. Pinning the two or three threads everyone asks about is the '
                            'single cheapest way to cut your own repeat workload.'),
                     ]},
                    {'title': 'Moderation, and the record', 'type': 'reading', 'minutes': 3,
                     'summary': 'What the hub watches, and what you should do about it.',
                     'blocks': [
                         _p('The hub scores content for risk and raises a <strong>violation</strong> when '
                            'something looks wrong. Violations carry a category and a severity, and can '
                            'lead to a penalty — a warning, a mute, a suspension — with an appeal route '
                            'for the learner.'),
                         _note('warning', 'Automated flags are a prompt, not a verdict',
                               'A flag means "a person should look at this". Read the message in its '
                               'context before you act. Learners talk to each other in ways a rule engine '
                               'reads badly.'),
                         _p('Everything — chat, discussions, direct messages — is retained and can be '
                            'produced if there is a safeguarding or conduct concern. Tell your learners '
                            'that plainly at the start. It changes behaviour more than any filter.'),
                     ]},
                    {'title': 'Keeping your own inbox survivable', 'type': 'reading', 'minutes': 2,
                     'summary': 'Notification settings, honestly.',
                     'blocks': [
                         _ul('If you teach several modules, turn these off first under Settings › Notifications:', [
                             'E-mail for every chat message — the bell is enough.',
                             'E-mail for feed posts.',
                         ]),
                         _ul('Keep these on:', [
                             'Mentions of you.',
                             'Assessment submissions waiting to be marked.',
                             'Live class reminders.',
                         ]),
                     ]},
                ],
            },
            {
                'title': 'Staying in touch with the school',
                'subtitle': 'How to reach an educator, and what you will be told without asking.',
                'minutes': 9, 'roles': PARENT,
                'intro': [
                    _p('You do not need to learn the whole platform. You need to know how the school '
                       'reaches you, and how you reach the school. That is this lesson.'),
                ],
                'sections': [
                    {'title': 'What arrives without you asking', 'type': 'reading', 'minutes': 3,
                     'summary': 'Announcements, results and reminders come to you.', 'open': True,
                     'blocks': [
                         _pic(d, 'notifications', 'The bell in the top bar collects everything addressed to you.'),
                         _ul('The bell in the top bar collects everything addressed to you:', [
                             '<strong>Announcements</strong> from the school — closures, dates, notices.',
                             '<strong>Results</strong> once they are published (never while marking is in progress).',
                             '<strong>Reminders</strong> before a live class or a deadline.',
                             '<strong>Messages</strong> from an educator.',
                         ]),
                         _p('Click any notification to read it in full. Under <strong>Settings › '
                            'Notifications</strong> you can have the important ones e-mailed to you as '
                            'well, which is worth doing if you do not sign in often.'),
                     ]},
                    {'title': 'Reaching an educator', 'type': 'reading', 'minutes': 3,
                     'summary': 'Message directly — and what to expect back.',
                     'blocks': [
                         _p('Open your learner\'s module, find the educator listed on it, and choose '
                            '<strong>Message</strong>. That goes straight to them and appears in their '
                            'notifications.'),
                         _ul('A few things that make this work better:', [
                             'Say which learner you are writing about — educators teach many.',
                             'Ask one question at a time.',
                             'Allow a working day or two. Educators teach during the day.',
                             'For anything formal — fees, appeals, records — use <strong>Mail</strong> '
                             'rather than chat, so there is a proper record.',
                         ]),
                     ]},
                    {'title': 'What you can and cannot see', 'type': 'reading', 'minutes': 2,
                     'summary': 'Being straight with you about the boundaries.',
                     'blocks': [
                         _p('You can see your learner\'s progress, their published marks, their attendance '
                            'and anything the school sends you.'),
                         _p('You cannot see their private notes, their direct messages, or their chat with '
                            'classmates. That is deliberate. If you have a concern about something in '
                            'those spaces, raise it with the school and staff can look properly.'),
                         _note('info', 'Marks appear when they are final',
                               'A result you cannot see yet is usually still being marked. Written answers '
                               'are marked by a person, which takes longer than a multiple-choice quiz.'),
                     ]},
                ],
            },
        ],
    }


# --- 2. Lessons -------------------------------------------------------------
def _lessons(d):
    return {
        'name': 'Lessons',
        'code': 'HUB-LES',
        'description': ('How a lesson is put together and how to work through one — sections, '
                        'locks, video, your own notes and bookmarks, and how progress is tracked.'),
        'lessons': [
            {
                'title': 'How to work through a lesson',
                'subtitle': 'Sections that open, a panel that is yours, and progress that remembers you.',
                'minutes': 16, 'roles': STUDENT,
                'intro': [
                    _p('A lesson here is not a wall of text. It is a stack of labelled sections you open '
                       'one at a time, with a panel beside it that belongs to you. Once you know how '
                       'those two parts work, every lesson on the hub works the same way.'),
                    _pic(d, 'player', 'A lesson: sections down the middle, your own panel on the right.'),
                ],
                'sections': [
                    {'title': 'Finding a lesson in the first place', 'type': 'reading', 'minutes': 2,
                     'summary': 'Two routes, both two clicks.', 'open': True,
                     'blocks': [
                         _ul('There are two ways in, and both are short:', [
                             'Press your <strong>course</strong> button in the top bar. That opens the '
                             'course overview, which lists every lesson grouped by module with how far '
                             'through each one you are. Click one to open it.',
                             'Or open a <strong>module</strong> and choose its Lessons tab.',
                         ]),
                         _note('tip', 'Start where you stopped',
                               'The course overview shows a progress bar on every lesson and the button '
                               'says <em>Continue</em> rather than <em>Start</em> for anything you have '
                               'already opened. Go to the one that is half-finished first.'),
                     ]},
                    {'title': 'Reading the sections before you open them', 'type': 'reading', 'minutes': 4,
                     'summary': 'Every section tells you what it is and how long it takes.',
                     'blocks': [
                         _p('Each section carries a label, a title and a duration before you open it — so '
                            'you can decide whether you have time for it right now.'),
                         ('table', 'What the labels on a section mean',
                          ['Label', 'What is inside', 'What the time means'],
                          [['Reading', 'Written explanation, tables, images', 'How long to read it'],
                           ['Video', 'A video or audio recording', 'How long the recording runs'],
                           ['Quiz', 'A short set of questions', 'The time limit, if there is one'],
                           ['Assessment', 'A test or assignment that counts', 'How long it is expected to take'],
                           ['Live class', 'A scheduled online session', 'How long the session runs'],
                           ['Interactive', 'An activity you work through', 'Roughly how long it takes'],
                           ['Resources', 'Files to download', 'Time to look through them']]),
                         _p('Click the section header to open it. Only one thing at a time is on your '
                            'screen, which is the point.'),
                     ]},
                    {'title': 'Locked sections', 'type': 'reading', 'minutes': 2,
                     'summary': 'What the padlock means and how to clear it.',
                     'blocks': [
                         _p('A padlock on a section means your educator has put something before it that '
                            'you need to finish first. It is not broken and it is not personal — it is '
                            'there because the next part will not make sense without the previous one.'),
                         _p('Finish every required section above it — read them and press <strong>Mark '
                            'complete</strong>, or submit the quiz if that is what is asked — and the '
                            'padlock opens.'),
                     ]},
                    {'title': 'Video, and how to keep your place', 'type': 'video', 'minutes': 5,
                     'summary': 'The player, and bookmarking a moment you want to come back to.',
                     'blocks': [
                         _p('Video plays inside the lesson — uploaded recordings and YouTube links alike, '
                            'in the same player, with speed control and captions where they exist.'),
                         ('video', PLACEHOLDER_VIDEO,
                          'Video plays inline. Use "Bookmark this moment" to save the exact second you '
                          'want to return to. (Placeholder — your school will replace this with its own '
                          'recordings.)', 5),
                         _note('tip', 'Bookmark the moment, not the video',
                               'Under every video there is <strong>Bookmark this moment</strong>. It saves '
                               'the exact second you were at. Clicking that bookmark later reopens the '
                               'section and jumps the player straight back there.'),
                     ]},
                    {'title': 'The panel on the right is yours', 'type': 'reading', 'minutes': 4,
                     'summary': 'Notes, bookmarks, your marks, and the module conversation.',
                     'blocks': [
                         _ul('Five tabs, all private to you except the last:', [
                             '<strong>Info</strong> — how far through you are, who wrote the lesson, and '
                             'any files attached to it.',
                             '<strong>Notes</strong> — a notebook that changes as you open sections, so '
                             'what you wrote stays attached to the part that prompted it. It saves itself.',
                             '<strong>Bookmarks</strong> — everything you saved. Select any text in a '
                             'lesson and a <em>Bookmark passage</em> button appears; the passage is '
                             'highlighted again when you come back to it.',
                             '<strong>Results</strong> — your score on any quiz in this lesson, with a '
                             'rating and a plain sentence about what to do next.',
                             '<strong>Messages</strong> — what your class is discussing in this module.',
                         ]),
                         _note('info', 'Nobody reads your notes',
                               'Your notes and bookmarks are yours alone. Not your educator, not your '
                               'parent, not other learners. Write what actually helps you.'),
                     ]},
                    {'title': 'Finishing, and what gets recorded', 'type': 'reading', 'minutes': 2,
                     'summary': 'Honest about what the system tracks.',
                     'blocks': [
                         _p('Press <strong>Mark complete</strong> at the foot of a section when you are '
                            'done with it, and <strong>Finish lesson</strong> at the bottom when you have '
                            'worked through the whole thing. That is what fills your progress bar and '
                            'unlocks anything gated behind it.'),
                         _ul('What the hub records about your reading:', [
                             'Which sections you completed, and when.',
                             'Roughly how long you spent on each one.',
                             'Your quiz results.',
                         ]),
                         _p('Your educator can see that. They cannot see your notes or your bookmarks.'),
                     ]},
                ],
                'attachments': [(
                    'Lesson page cheat sheet', 'text/plain',
                    'THE LESSON PAGE — CHEAT SHEET\n'
                    '=============================\n\n'
                    'Sections     Click the header to open one. The label tells you what is\n'
                    '             inside; the time on the right tells you how long it takes.\n'
                    'Padlock      Finish the required sections above it first.\n'
                    'Notes        Right panel, pencil tab. Changes with the open section.\n'
                    '             Saves itself.\n'
                    'Bookmarks    Select text -> "Bookmark passage".\n'
                    '             Under a video -> "Bookmark this moment".\n'
                    '             Both jump you straight back when clicked.\n'
                    'Results      Right panel, award tab. Your marks for this lesson.\n'
                    'Finishing    "Mark complete" per section, "Finish lesson" at the end.\n\n'
                    'Private to you: your notes and your bookmarks.\n'
                    'Visible to your educator: sections completed, time spent, marks.\n'
                )],
            },
            {
                'title': 'Building a lesson worth sitting through',
                'subtitle': 'The builder, the audience buttons, and letting AI do the first draft.',
                'minutes': 18, 'roles': TEAM,
                'intro': [
                    _p('The builder puts the lesson in the middle of your screen and your tools down the '
                       'side. You drag content in, it saves as you go, and you can see exactly what a '
                       'learner will see at any point.'),
                    _pic(d, 'builder', 'The lesson on the left, the toolbox on the right.'),
                ],
                'sections': [
                    {'title': 'Sections first, content second', 'type': 'reading', 'minutes': 4,
                     'summary': 'Why the structure is the lesson.', 'open': True,
                     'blocks': [
                         _p('Start by laying out the sections — the shape of the lesson — before you write '
                            'a word of content. Four to seven sections is the sweet spot. Fewer and each '
                            'one is a wall; more and the lesson feels endless.'),
                         _ul('Each section carries four decisions:', [
                             '<strong>Title</strong> — what the learner sees folded up. Make it specific: '
                             '"Why sampling works" beats "Part 2".',
                             '<strong>Kind</strong> — Reading, Video, Quiz, Assessment, Live, Interactive '
                             'or Resources. Leave it on <em>Auto</em> and it works itself out from what '
                             'you put inside.',
                             '<strong>Minutes</strong> — leave blank and it is estimated from the content '
                             '(reading speed for prose, the time limit for a quiz, the length of a video). '
                             'Override it when you know better.',
                             '<strong>Lock</strong> — hold this section shut until everything required '
                             'above it is done.',
                         ]),
                         _note('warning', 'Use locks sparingly',
                               'A lock is right when the next section genuinely cannot be understood '
                               'without the previous one. Locking everything just teaches learners to '
                               'click through without reading.'),
                     ]},
                    {'title': 'Getting content in', 'type': 'reading', 'minutes': 4,
                     'summary': 'Drag from the palette, or click to add.',
                     'blocks': [
                         _p('The palette on the right holds every kind of block. <strong>Drag</strong> one '
                            'onto a section to drop it exactly where you want it, or click it to add it '
                            'to the last section. Blocks drag between sections by their handle.'),
                         ('table', 'What each block is for',
                          ['Block', 'Use it when'],
                          [['Text', 'Explaining. The toolbar has headings, sizes, colour, alignment and lists.'],
                           ['Callout', 'One thing that must not be missed — a definition, a warning.'],
                           ['Image', 'A diagram or photograph that carries meaning.'],
                           ['Video', 'Uploaded recordings, or a YouTube/Vimeo link — same player either way.'],
                           ['Table', 'Anything genuinely tabular. Not for layout.'],
                           ['Diagram', 'A picture with numbered labels you place by clicking it.'],
                           ['File', 'Something to download and keep.'],
                           ['Embed page', 'An external page, read inside the lesson.'],
                           ['Quiz / test', 'Check understanding, or assess it properly.'],
                           ['Live session', 'A scheduled class, joined from inside the lesson.'],
                           ['Interactive', 'An uploaded H5P activity.']]),
                         _note('tip', 'Set the video length',
                               'On a video block there is a "Length in minutes" field. Fill it in — it is '
                               'what the learner sees on the folded section, and it is how they decide '
                               'whether to start now.'),
                     ]},
                    {'title': 'Letting AI write the first draft', 'type': 'reading', 'minutes': 3,
                     'summary': 'Useful for structure. Never trusted for accuracy.',
                     'blocks': [
                         _p('The <strong>Build with AI</strong> panel takes a written brief and drafts '
                            'sections straight into the lesson you are editing. You can also start a whole '
                            'lesson from a document — upload a chapter or your notes and it comes back as '
                            'a structured draft.'),
                         _ul('It is genuinely good at:', [
                             'Breaking a topic into a sensible sequence of sections.',
                             'Turning your rough notes into readable prose.',
                             'Producing the summary tables you never get round to making.',
                         ]),
                         _ul('It is not to be trusted with:', [
                             'Facts, dates, figures and citations — check every one.',
                             'Anything specific to your school, which it does not know.',
                             'Assessment answers.',
                         ]),
                         _note('warning', 'AI drafts are always drafts',
                               'Nothing generated is ever published automatically. It lands as a draft in '
                               'your editor and stays there until you read it and publish it yourself. '
                               'Read it properly — your name goes on it.'),
                     ]},
                    {'title': 'Choosing who gets it', 'type': 'reading', 'minutes': 3,
                     'summary': 'One student, a class, or the whole module.',
                     'blocks': [
                         _ul('Three buttons under <strong>Who gets this lesson</strong>:', [
                             '<strong>Student</strong> — named individuals. The list only ever contains '
                             'learners in modules you teach. Use it for catch-up work or extension.',
                             '<strong>Class</strong> — everyone enrolled in a course, now and in future.',
                             '<strong>ProgrammeModule</strong> — everyone taking the module. The usual choice.',
                         ]),
                         _p('Set <strong>Status</strong> to Published and press Save & publish. Draft '
                            'lessons are invisible to learners no matter who they are targeted at, so you '
                            'can build in the open without anyone seeing half a lesson.'),
                     ]},
                    {'title': 'Saving, previewing and attachments', 'type': 'reading', 'minutes': 3,
                     'summary': 'Nothing is ever lost.',
                     'blocks': [
                         _p('Everything saves as you type — the chip at the top says so. The '
                            '<strong>Save</strong> button just flushes it immediately if you want the '
                            'reassurance. <strong>Preview as learner</strong> opens the real lesson page '
                            'exactly as a student sees it, with locks open so you can check the whole '
                            'thing.'),
                         _p('Drop PDFs, images or text files into <strong>Attachments</strong> and they '
                            'appear in the learner\'s side panel, downloadable, for the whole lesson.'),
                     ]},
                ],
            },
            {
                'title': 'What your learner is actually doing in a lesson',
                'subtitle': 'So the progress bar you are looking at means something.',
                'minutes': 8, 'roles': PARENT,
                'intro': [
                    _p('You will see percentages and progress bars against your learner\'s name. This is '
                       'what they are counting.'),
                    _pic(d, 'player', 'What a lesson looks like from your learner\'s side.'),
                ],
                'sections': [
                    {'title': 'A lesson is a stack of sections', 'type': 'reading', 'minutes': 3,
                     'summary': 'Not a document — a sequence.', 'open': True,
                     'blocks': [
                         _p('Each lesson is broken into labelled sections — some reading, some video, some '
                            'a quiz. Your learner opens them one at a time and marks each one complete '
                            'when they are done. Some sections are locked until the ones before them are '
                            'finished.'),
                         _p('The percentage you see is simply how many of the required sections they have '
                            'completed. A lesson at 60% has more sections left, not a mark of 60%.'),
                     ]},
                    {'title': 'Progress is not the same as understanding', 'type': 'reading', 'minutes': 3,
                     'summary': 'Worth saying plainly.',
                     'blocks': [
                         _note('info', 'What the bar can and cannot tell you',
                               'It tells you what has been opened and marked done, and roughly how long '
                               'was spent. It cannot tell you whether any of it went in. For that, look '
                               'at the quiz results — or better, ask them to explain something.'),
                         _p('If the bar is stuck, that is worth a conversation. It usually means a locked '
                            'section they got stuck on, or a topic they have quietly avoided.'),
                     ]},
                    {'title': 'Their notes are theirs', 'type': 'reading', 'minutes': 2,
                     'summary': 'And that is deliberate.',
                     'blocks': [
                         _p('Learners can keep private notes and bookmarks inside a lesson. You cannot see '
                            'them and neither can their educator. That is on purpose: a notebook you know '
                            'is being read is not a notebook, it is homework.'),
                     ]},
                ],
            },
        ],
    }


# --- 3. Online classes ------------------------------------------------------
def _online_classes(d):
    return {
        'name': 'Online Classes',
        'code': 'HUB-LIVE',
        'description': ('Live sessions — joining one, hosting one, what happens to attendance, '
                        'and where the recording goes afterwards.'),
        'lessons': [
            {
                'title': 'Joining a live class',
                'subtitle': 'How to get in, what to check first, and how to be a good participant.',
                'minutes': 11, 'roles': STUDENT,
                'intro': [
                    _p('Live classes happen inside the hub. There is nothing to install and no meeting '
                       'code to type — you click a link and you are in.'),
                    _pic(d, 'live', 'The stage in the middle, everyone in the room and the class chat on the right.'),
                ],
                'sections': [
                    {'title': 'Finding the session', 'type': 'reading', 'minutes': 2,
                     'summary': 'Three places the link appears.', 'open': True,
                     'blocks': [
                         _ul('The join link turns up wherever you are already looking:', [
                             'In the <strong>module</strong>, under its Live classes tab.',
                             'Inside a <strong>lesson</strong>, if the class is part of one.',
                             'On your <strong>dashboard</strong>, under what is coming up.',
                         ]),
                         _p('A reminder notification arrives before it starts. The button goes live a few '
                            'minutes before the scheduled time.'),
                     ]},
                    {'title': 'The two minutes before you join', 'type': 'reading', 'minutes': 3,
                     'summary': 'The checks that save everyone else five minutes.',
                     'blocks': [
                         _ul('Do these before the session, not during it:', [
                             'Use headphones. Without them your speakers feed back into your microphone '
                             'and everyone hears it but you.',
                             'Allow the browser access to your camera and microphone when it asks.',
                             'Close anything streaming or downloading in the background.',
                             'Find somewhere with reasonable light in front of you, not behind you.',
                         ]),
                         _note('tip', 'On a phone or a weak connection?',
                               'Turn your camera off and keep only audio. Video is the first thing to drop '
                               'when a connection is thin — turning it off yourself keeps your sound '
                               'clear, which is the part that matters.'),
                     ]},
                    {'title': 'Being in the room', 'type': 'reading', 'minutes': 3,
                     'summary': 'Mic discipline, hands and chat.',
                     'blocks': [
                         _ul('The controls along the bottom:', [
                             '<strong>Mic</strong> — stay muted unless you are speaking. Every unmuted '
                             'microphone adds background noise to the room.',
                             '<strong>Camera</strong> — on if you can. It changes how a class feels.',
                             '<strong>Share screen</strong> — for when it is your turn to present.',
                             '<strong>Raise hand</strong> — the polite way to say you have something.',
                             '<strong>Leave</strong> — you can rejoin if you drop out.',
                         ]),
                         _p('The <strong>class chat</strong> down the side is the best place for questions '
                            'while somebody is talking. Your educator can pick them up at a natural break '
                            'instead of losing their thread.'),
                     ]},
                    {'title': 'Attendance and recordings', 'type': 'reading', 'minutes': 3,
                     'summary': 'What is recorded, and what happens if you miss one.',
                     'blocks': [
                         _p('Joining through the hub marks your attendance automatically. You do not sign '
                            'anything, and there is nothing to remember.'),
                         _note('warning', 'Sessions may be recorded',
                               'If a session is being recorded you will be told at the start. The '
                               'recording — and often a transcript — appears in the module afterwards, '
                               'so a class you miss is not a class you lose.'),
                         _p('If your connection dies mid-class, rejoin. Your attendance still counts, and '
                            'the recording covers what you missed.'),
                     ]},
                ],
            },
            {
                'title': 'Running a live class',
                'subtitle': 'Scheduling, hosting, attendance and what happens after the session.',
                'minutes': 13, 'roles': TEAM,
                'intro': [
                    _p('Scheduling a live class provisions the room, notifies the class, records '
                       'attendance and files the recording afterwards. You schedule it; the hub does the '
                       'rest.'),
                    _pic(d, 'live', 'What your learners see when they join.'),
                ],
                'sections': [
                    {'title': 'Scheduling one', 'type': 'reading', 'minutes': 3,
                     'summary': 'Two routes, depending on what the class is for.', 'open': True,
                     'blocks': [
                         _ul('Either:', [
                             'From the <strong>module</strong>, under Live classes — for a normal '
                             'timetabled session. This creates a class session, so attendance reconciles '
                             'against the register.',
                             'From inside a <strong>lesson</strong>, by dropping in a Live session block — '
                             'for a session that belongs to a specific piece of content.',
                         ]),
                         _p('Give it a title that says what it is, set the date, time and length, and the '
                            'class is notified automatically.'),
                     ]},
                    {'title': 'Teams or the built-in room', 'type': 'reading', 'minutes': 3,
                     'summary': 'Which one you get, and why you may not have a choice.',
                     'blocks': [
                         _p('If your school has configured Microsoft Teams, sessions are created as '
                            'real Teams meetings hosted under your account — which brings Teams recording, '
                            'transcripts and attendance reporting with it. If it has not, the hub uses its '
                            'own built-in video room.'),
                         _p('Learners never see the difference. They click the same in-app link either '
                            'way, and it resolves to whichever is configured.'),
                         _note('info', 'Only staff and educators host',
                               'Hosting requires a licensed account. Learners always join as participants '
                               'through the hub link — they are never given the raw meeting URL.'),
                     ]},
                    {'title': 'Hosting well', 'type': 'reading', 'minutes': 4,
                     'summary': 'What actually goes wrong, and how to avoid it.',
                     'blocks': [
                         _ul('Before:', [
                             'Join five minutes early. Something is always wrong five minutes early.',
                             'Have the thing you are sharing already open.',
                             'Say at the start whether you are recording.',
                         ]),
                         _ul('During:', [
                             'Watch the chat, or ask someone to. Questions land there because people are '
                             'too polite to interrupt.',
                             'Say people\'s names when you answer them. On video it is the only way they '
                             'know you meant them.',
                             'Stop every ten minutes and ask something. A silent room is not an '
                             'understanding room.',
                         ]),
                         _note('tip', 'Record even the ordinary ones',
                               'The recording is worth more to the learner who was ill than the session '
                               'was to anyone who attended. It costs you nothing.'),
                     ]},
                    {'title': 'Afterwards', 'type': 'reading', 'minutes': 3,
                     'summary': 'Attendance, recordings and the follow-up.',
                     'blocks': [
                         _p('Attendance is captured from who actually joined, and appears against the '
                            'class session. Where Teams is configured, a scheduled sync pulls the '
                            'recording, transcript and attendance report back into the module after the '
                            'session ends.'),
                         _ul('Two minutes of follow-up that pays for itself:', [
                             'Post the recording link in the module chat.',
                             'Post the two or three questions that came up, with your answers.',
                             'Note who was missing and why — the attendance view makes a pattern obvious '
                             'long before a term report does.',
                         ]),
                     ]},
                ],
            },
            {
                'title': 'Live classes, and what attendance means',
                'subtitle': 'When they happen, whether your learner turned up, and what if they cannot.',
                'minutes': 7, 'roles': PARENT,
                'intro': [
                    _p('Live classes are scheduled online sessions with an educator. Here is what you can '
                       'see about them.'),
                ],
                'sections': [
                    {'title': 'When they happen', 'type': 'reading', 'minutes': 2,
                     'summary': 'And how you find out.', 'open': True,
                     'blocks': [
                         _p('Scheduled sessions appear in the module and on your learner\'s dashboard, and '
                            'a reminder notification goes out before each one. If you have e-mail '
                            'notifications on, you get those too.'),
                     ]},
                    {'title': 'Attendance', 'type': 'reading', 'minutes': 3,
                     'summary': 'Recorded automatically, visible to you.',
                     'blocks': [
                         _p('Joining through the hub records attendance automatically — there is no '
                            'register to sign and nothing for your learner to remember. You can see their '
                            'attendance on their profile.'),
                         _note('info', 'A missed class is not a lost class',
                               'Most sessions are recorded and posted to the module afterwards. If your '
                               'learner misses one, they can still watch it. Encourage that rather than '
                               'worrying about the mark on the register.'),
                     ]},
                    {'title': 'If they cannot attend', 'type': 'reading', 'minutes': 2,
                     'summary': 'Tell someone — it is easy and it helps.',
                     'blocks': [
                         _p('Message the educator through the module. A one-line "she is ill today" is '
                            'enough, and it means an absence is understood rather than counted.'),
                         _p('Connection trouble is worth mentioning too. Educators can often provide the '
                            'material another way if they know it is a recurring problem rather than a '
                            'lack of interest.'),
                     ]},
                ],
            },
        ],
    }


# --- 4. Dashboard & student matrix -----------------------------------------
def _dashboard(d):
    return {
        'name': 'Dashboard and Student Matrix',
        'code': 'HUB-DASH',
        'description': ('Your dashboard, your profile, progress and reports — and, for staff, the '
                        'student matrix that puts a whole class on one screen.'),
        'lessons': [
            {
                'title': 'Reading your own dashboard',
                'subtitle': 'What each number means, and which one to act on first.',
                'minutes': 12, 'roles': STUDENT,
                'intro': [
                    _p('Your dashboard is the first thing you see when you sign in. It is trying to '
                       'answer one question: what should I do next?'),
                    _pic(d, 'dashboard', 'Your numbers along the top, what to do next underneath.'),
                ],
                'sections': [
                    {'title': 'The four numbers at the top', 'type': 'reading', 'minutes': 4,
                     'summary': 'What each one counts — and does not count.', 'open': True,
                     'blocks': [
                         ('table', 'The tiles across the top of your dashboard',
                          ['Tile', 'What it counts', 'What it does not mean'],
                          [['Course progress', 'Required lessons and assessments completed',
                            'Not your mark — a 100% here with poor quiz results still needs work'],
                           ['Lessons done', 'Lessons you marked finished',
                            'Not lessons you understood'],
                           ['Average mark', 'The mean of your published, marked results',
                            'Work still being marked is not in here yet'],
                           ['Attendance', 'Live classes joined against those scheduled',
                            'Watching a recording later does not raise it']]),
                         _note('tip', 'Read them in pairs',
                               'Progress high but average low means you are moving too fast. Average high '
                               'but progress low means you know the early material and have stalled. '
                               'Either one on its own tells you almost nothing.'),
                     ]},
                    {'title': 'What to do next', 'type': 'reading', 'minutes': 3,
                     'summary': 'The most useful panel on the page.',
                     'blocks': [
                         _ul('The middle panel is ordered by what will cost you most if you ignore it:', [
                             'The assessment closing soonest.',
                             'The lesson you started and did not finish.',
                             'The next live class.',
                             'Anything an educator has sent you specifically.',
                         ]),
                         _p('If you only look at one thing when you sign in, look at this.'),
                     ]},
                    {'title': 'Your profile, and keeping it right', 'type': 'reading', 'minutes': 3,
                     'summary': 'It is how people find you and how the school reaches you.',
                     'blocks': [
                         _ul('Under <strong>Settings › Account & profile</strong>, keep these current:', [
                             'A profile picture. It genuinely helps in a class of forty names.',
                             'Your phone number and address — used for anything official.',
                             'Your emergency contact.',
                             'A line or two about yourself, if you want.',
                         ]),
                         _note('warning', 'An out-of-date e-mail is a missed result',
                               'Notifications, results and fee notices all go to the address on your '
                               'profile. If it changes, change it here first.'),
                     ]},
                    {'title': 'Progress, grades and reports', 'type': 'reading', 'minutes': 2,
                     'summary': 'Where the detail lives.',
                     'blocks': [
                         _p('Your profile carries the full picture: every module, your mark in each, your '
                            'attendance and your activity. Reports pull it together per term.'),
                         _p('Your final mark in a module is not a simple average — quizzes, tests, '
                            'assignments and exams each carry a different weight, set by your educator. '
                            'That is why one bad quiz matters less than one bad exam.'),
                     ]},
                ],
            },
            {
                'title': 'The student matrix, grades and reports',
                'subtitle': 'Seeing a whole class at once, and finding the learner who is quietly sinking.',
                'minutes': 15, 'roles': TEAM,
                'intro': [
                    _p('The matrix exists to answer one question quickly: who needs me this week? '
                       'Everything else on this page is detail.'),
                    _pic(d, 'matrix', 'Every learner, every measure, one screen.'),
                ],
                'sections': [
                    {'title': 'Reading the matrix', 'type': 'reading', 'minutes': 4,
                     'summary': 'Columns, filters and what to scan for.', 'open': True,
                     'blocks': [
                         _p('One row per learner, one column per measure — lessons completed, quiz '
                            'average, overall mark, attendance, and any flags. Filter by course, module '
                            'or status; export the view when you need it outside the hub.'),
                         _ul('What to scan for, in this order:', [
                             '<strong>Attendance falling</strong> — almost always the first signal, and it '
                             'appears weeks before marks move.',
                             '<strong>Lessons stalled</strong> — a learner stuck on the same count for two '
                             'weeks is stuck on something specific.',
                             '<strong>A gap between progress and marks</strong> — someone clicking '
                             'through without reading.',
                             '<strong>Flags</strong> — integrity events on assessments.',
                         ]),
                         _note('tip', 'The dangerous row is the middling one',
                               'You already know who your struggling learners are. The matrix earns its '
                               'keep by surfacing the quiet, average-looking learner whose attendance has '
                               'slipped from 95% to 70% without anyone noticing.'),
                     ]},
                    {'title': 'How a final mark is actually calculated', 'type': 'reading', 'minutes': 4,
                     'summary': 'Weightings, components and extra credit.',
                     'blocks': [
                         _p('Every assessment feeds a <strong>component</strong> — assignments, quizzes, '
                            'tests or exams — and each component carries a weight per module. That is '
                            'what turns a pile of marks into one defensible number.'),
                         ('table', 'A typical weighting',
                          ['Component', 'Weight', 'Feeds from'],
                          [['Assignments', '20%', 'Manually-marked assignments'],
                           ['Quizzes', '15%', 'Short auto-marked checks'],
                           ['Tests', '25%', 'Longer in-term assessments'],
                           ['Exams', '40%', 'Final and exam-section assessments']]),
                         _ul('Two things that catch people out:', [
                             'An assessment\'s component can be set independently of its kind — a quiz you '
                             'want counted as a test can be, without renaming anything.',
                             'Extra-credit assessments sit outside the components and add on top, so they '
                             'never dilute an average.',
                         ]),
                     ]},
                    {'title': 'The marking queue', 'type': 'reading', 'minutes': 4,
                     'summary': 'Where written answers wait for you.',
                     'blocks': [
                         _pic(d, 'marking', 'Manual answers waiting, and flagged attempts listed separately.'),
                         _p('Objective questions mark themselves the moment a learner submits. Anything '
                            'written — short answers, essays, assignments — lands in the marking queue '
                            'with your rubric shown beside the response. Award the marks, write the '
                            'feedback, and the attempt re-grades itself and updates the module grade.'),
                         _p('An attempt stays <em>submitted</em> while any manual question is unmarked and '
                            'flips to <em>marked</em> when none remain — which is exactly when the learner '
                            'and their parent can see the result.'),
                         _note('info', 'Flagged attempts are listed separately',
                               'An auto-marked quiz never enters the marking queue, so anything the exam '
                               'focus guard flagged appears in its own section underneath. Otherwise it '
                               'would go unseen.'),
                     ]},
                    {'title': 'Reports', 'type': 'reading', 'minutes': 3,
                     'summary': 'What the hub generates, and what it cannot.',
                     'blocks': [
                         _p('Reports assemble marks, attendance and activity per learner per term, ready '
                            'to export. They are built from data that is already there — you do not '
                            're-enter anything.'),
                         _note('warning', 'The comment is still yours',
                               'The hub can tell a parent that attendance is 71% and the average is 64%. '
                               'It cannot tell them that their child has been quietly brilliant in '
                               'discussions since February. Write the comment.'),
                     ]},
                ],
            },
            {
                'title': 'Following your learner\'s progress',
                'subtitle': 'What you can see, what it means, and when to step in.',
                'minutes': 9, 'roles': PARENT,
                'intro': [
                    _p('You have a view of your learner\'s progress. This lesson is about reading it '
                       'fairly.'),
                    _pic(d, 'parent', 'What a parent account shows.'),
                ],
                'sections': [
                    {'title': 'What you can see', 'type': 'reading', 'minutes': 3,
                     'summary': 'Progress, marks, attendance, messages.', 'open': True,
                     'blocks': [
                         _ul('Your learner\'s profile shows you:', [
                             'How far through each module they are.',
                             'Their published marks, per module.',
                             'Their attendance at live classes.',
                             'Their overall activity — what they have been opening.',
                         ]),
                         _p('You also receive announcements, results notifications and reminders '
                            'directly.'),
                     ]},
                    {'title': 'Reading it fairly', 'type': 'reading', 'minutes': 4,
                     'summary': 'The three mistakes worth avoiding.',
                     'blocks': [
                         _ul('Three things worth knowing before you draw a conclusion:', [
                             '<strong>Progress is not attainment.</strong> The percentage is how many '
                             'sections have been marked done, not how well.',
                             '<strong>A missing mark is usually unmarked, not failed.</strong> Written '
                             'work is marked by a person, and that takes days, not seconds.',
                             '<strong>One bad quiz is one bad quiz.</strong> Final marks are weighted, and '
                             'a short quiz carries far less than an exam.',
                         ]),
                         _note('tip', 'The best signal is attendance',
                               'If you look at one number, look at attendance at live classes. It moves '
                               'before marks do, and it is the earliest honest sign that something has '
                               'gone wrong.'),
                     ]},
                    {'title': 'When to step in', 'type': 'reading', 'minutes': 2,
                     'summary': 'And how.',
                     'blocks': [
                         _ul('Worth a message to the educator:', [
                             'Attendance dropping over two or three weeks.',
                             'Progress that has not moved at all in a fortnight.',
                             'A sharp fall in marks in one module but not others — usually a specific '
                             'topic, not a general problem.',
                         ]),
                         _p('Educators would much rather hear from you early than read it in a term '
                            'report.'),
                     ]},
                ],
            },
        ],
    }


# --- 5. Quizzes & assessments ----------------------------------------------
def _assessments(d):
    return {
        'name': 'Quizzes and Assessments',
        'code': 'HUB-ASS',
        'description': ('Sitting a quiz, understanding monitored assessments, and — for educators '
                        '— building, marking and setting the integrity rules.'),
        'lessons': [
            {
                'title': 'Sitting a quiz or an assessment',
                'subtitle': 'The timer, the rules, monitored assessments, and reading your result.',
                'minutes': 14, 'roles': STUDENT,
                'intro': [
                    _p('Quizzes are short checks. Assessments count. Both work the same way on screen, '
                       'and there are a few things worth knowing before you start one.'),
                    _pic(d, 'quiz', 'The paper, the timer, and — on a monitored assessment — the notice at the top.'),
                ],
                'sections': [
                    {'title': 'Before you press start', 'type': 'reading', 'minutes': 3,
                     'summary': 'The header tells you everything that matters.', 'open': True,
                     'blocks': [
                         _ul('Read the header first. It tells you:', [
                             'How many marks it carries and what counts as a pass.',
                             'Whether there is a <strong>time limit</strong>, and how long.',
                             'How many <strong>attempts</strong> you get.',
                             'Whether it is <strong>monitored</strong>.',
                         ]),
                         _note('warning', 'The clock does not stop',
                               'If there is a time limit, it starts when you open the page and keeps '
                               'running if you close the tab. Do not open an assessment to "have a look" '
                               'unless you are ready to sit it.'),
                     ]},
                    {'title': 'Answering', 'type': 'reading', 'minutes': 3,
                     'summary': 'Question types, and what gets marked how.',
                     'blocks': [
                         ('table', 'What you will be asked, and who marks it',
                          ['Type', 'What to do', 'Marked by'],
                          [['Multiple choice', 'Pick one', 'The system, instantly'],
                           ['Multiple select', 'Pick every correct option', 'The system, instantly'],
                           ['True / false', 'Pick one', 'The system, instantly'],
                           ['Fill in / short answer', 'Type a word or a line', 'Usually the system'],
                           ['Long answer / essay', 'Write properly', 'Your educator'],
                           ['File upload', 'Attach your work', 'Your educator']]),
                         _p('Work that a person marks takes days, not seconds. A missing result usually '
                            'means it is still being marked.'),
                     ]},
                    {'title': 'Monitored assessments', 'type': 'reading', 'minutes': 5,
                     'summary': 'What is watched, what counts, and what happens after.',
                     'blocks': [
                         _p('Some assessments are monitored. You will know, because there is a notice at '
                            'the top of the page before you start. Nothing is hidden from you.'),
                         _pic(d, 'guard', 'What happens the moment focus leaves a monitored assessment.'),
                         _ul('While a monitored assessment is open, the hub watches for:', [
                             'Switching to another tab, or minimising the window.',
                             'Moving to another program or another window.',
                             'Your pointer leaving the page for more than a few seconds.',
                             'Leaving fullscreen, where fullscreen is required.',
                             'Copy, paste, right-click and printing, which are blocked.',
                         ]),
                         _p('The moment focus leaves, the questions blur and a message asks you to come '
                            'back. Each occurrence is counted and shown to your educator, along with how '
                            'long you were away.'),
                         _note('warning', 'When the limit is reached',
                               'Depending on how your educator set it up, going past the warning limit '
                               'either flags your attempt for them to review, or ends it and submits what '
                               'you have. The notice at the top tells you which before you start.'),
                         _ul('None of this should worry you if you are sitting it honestly. But:', [
                             'Close everything else before you start.',
                             'Silence notifications — a pop-up that steals focus counts.',
                             'If something genuinely interrupts you, finish, then message your educator '
                             'and explain. A flag is a prompt for a conversation, not a verdict.',
                         ]),
                     ]},
                    {'title': 'Your result', 'type': 'reading', 'minutes': 3,
                     'summary': 'Where to find it and how to use it.',
                     'blocks': [
                         _p('Auto-marked questions give you a score immediately, with a review of every '
                            'question showing what you chose and what was correct. Anything a person '
                            'marks appears once they have marked it, with their feedback.'),
                         _p('Results also appear in the <strong>Results</strong> tab of the lesson the '
                            'quiz sits in, with a rating and a plain sentence about what to do next.'),
                         _note('tip', 'Read the review, not just the number',
                               'The number tells you where you are. The per-question review tells you what '
                               'to fix. Only one of those is useful.'),
                     ]},
                ],
                'attachments': [(
                    'Before you sit a monitored assessment', 'text/plain',
                    'BEFORE YOU SIT A MONITORED ASSESSMENT\n'
                    '=====================================\n\n'
                    '[ ] Close every other tab and program.\n'
                    '[ ] Silence notifications on your computer and your phone.\n'
                    '[ ] Check the header: marks, pass mark, time limit, attempts.\n'
                    '[ ] Read the monitoring notice so you know what counts.\n'
                    '[ ] Have water and anything permitted already beside you.\n'
                    '[ ] Only press start when you are ready to finish.\n\n'
                    'WHAT COUNTS AS A WARNING\n'
                    '  - switching tab or minimising\n'
                    '  - moving to another program or window\n'
                    '  - pointer off the page for more than a few seconds\n'
                    '  - leaving fullscreen (where required)\n\n'
                    'IF SOMETHING GENUINELY INTERRUPTS YOU\n'
                    '  Finish the paper, then message your educator and explain.\n'
                    '  A flag is a prompt for a conversation, not an accusation.\n'
                )],
            },
            {
                'title': 'Building, marking and safeguarding an assessment',
                'subtitle': 'The question builder, the marking queue, and the exam focus guard.',
                'minutes': 17, 'roles': TEAM,
                'intro': [
                    _p('This covers writing an assessment, deciding what marks itself, marking the rest, '
                       'and setting the integrity rules — including an honest account of what those '
                       'rules can and cannot do.'),
                ],
                'sections': [
                    {'title': 'Building the paper', 'type': 'reading', 'minutes': 4,
                     'summary': 'Question types, and choosing auto or manual per question.', 'open': True,
                     'blocks': [
                         _pic(d, 'quiz', 'What the learner will see.'),
                         _p('Create the assessment, then add questions one at a time. Per question you '
                            'choose the type and whether it is <strong>auto-marked</strong> (you define '
                            'the key) or <strong>manually marked</strong> (you write a rubric and grade it '
                            'later). Total marks stay in sync with the sum of the questions '
                            'automatically.'),
                         _ul('Settings worth thinking about, not defaulting through:', [
                             '<strong>Time limit</strong> — 0 for no limit. A limit changes what you are '
                             'measuring, so choose deliberately.',
                             '<strong>Attempts</strong> — 0 for unlimited. Unlimited attempts on a '
                             'formative quiz is good practice; on a test it is not.',
                             '<strong>Pass mark</strong> and the <strong>component</strong> the result '
                             'feeds.',
                             '<strong>Availability window</strong> — when it opens and closes.',
                         ]),
                         _note('tip', 'Write the rubric while you write the question',
                               'It is the only time you fully remember what you meant. It also appears '
                               'beside the answer when you come to mark, which is when you will thank '
                               'yourself.'),
                     ]},
                    {'title': 'The exam focus guard', 'type': 'reading', 'minutes': 5,
                     'summary': 'What it detects, what it cannot, and how to configure it honestly.',
                     'blocks': [
                         _pic(d, 'guard', 'What a learner sees when focus leaves a monitored assessment.'),
                         _p('Turn on <strong>Exam integrity</strong> in the builder and the assessment '
                            'page watches for the learner leaving the window: another tab, another '
                            'program, the pointer off the page, leaving fullscreen. Copy, paste, '
                            'right-click and printing can be blocked. The questions blur the moment focus '
                            'goes, so the paper cannot be read from a second screen.'),
                         ('table', 'The settings, and what we would choose',
                          ['Setting', 'What it does', 'Suggested'],
                          [['Warnings allowed', 'How many before the action below', '3'],
                           ['Pointer grace', 'Seconds off-page before it counts', '3'],
                           ['When the limit is reached', 'Warn / flag / end the attempt', 'Flag'],
                           ['Block copy & paste', 'Disables copy, paste, right-click, print', 'On'],
                           ['Hide questions when unfocused', 'Blurs the paper while away', 'On'],
                           ['Require fullscreen', 'Counts leaving fullscreen', 'High-stakes only']]),
                         _note('warning', 'Be straight about what this is',
                               'It detects the learner leaving <em>this browser window</em>. It cannot see '
                               'a phone beside the keyboard or a second laptop — no in-browser check can. '
                               'Honest interruptions raise warnings too. Treat the report as evidence for '
                               'a conversation, never as proof on its own. That is exactly why '
                               '<strong>flag for review</strong> is the default rather than ending the '
                               'attempt.'),
                         _p('The count is kept on the server, not in the browser, so editing the page '
                            'cannot lower it. Duplicate reports of the same interruption are logged but '
                            'counted once.'),
                     ]},
                    {'title': 'Marking', 'type': 'reading', 'minutes': 4,
                     'summary': 'The queue, the rubric, and re-grading.',
                     'blocks': [
                         _pic(d, 'marking', 'The queue, with flagged attempts listed separately underneath.'),
                         _p('Submitted attempts with written answers appear in the <strong>marking '
                            'queue</strong>, oldest first. Each response is shown next to the rubric you '
                            'wrote. Award the marks, add feedback, save — the attempt re-grades and the '
                            'module grade updates itself.'),
                         _p('Flagged attempts get their own section underneath, because an auto-marked '
                            'quiz never reaches the queue and would otherwise never be looked at.'),
                         _note('tip', 'Mark one question across everyone, not one learner across everything',
                               'Marking question 3 for the whole class in one pass is faster and far more '
                               'consistent than marking one learner\'s entire paper at a time.'),
                     ]},
                    {'title': 'Reviewing a flagged attempt', 'type': 'reading', 'minutes': 4,
                     'summary': 'What the report shows, and how to handle it.',
                     'blocks': [
                         _ul('Opening a flagged attempt shows you the whole evidence log:', [
                             'Every event, what kind it was and the time it happened.',
                             'How long the learner was away each time.',
                             'The total time out of the window.',
                             'Whether the attempt was ended automatically.',
                         ]),
                         _ul('How to read it:', [
                             'Two brief events in a 40-minute paper is noise. Someone got a phone call.',
                             'Fifteen events with 30 seconds away each time is a pattern worth asking '
                             'about.',
                             'One event lasting eleven minutes is a different conversation entirely.',
                         ]),
                         _note('warning', 'Ask before you conclude',
                               'Start with "I noticed you left the assessment window a few times — what '
                               'happened?" You will be surprised how often the answer is a sibling, a '
                               'power cut or a browser notification. The log tells you what the window '
                               'did; only the learner can tell you why.'),
                     ]},
                ],
            },
            {
                'title': 'Understanding your learner\'s assessments',
                'subtitle': 'What counts, when results appear, and what a flag actually means.',
                'minutes': 8, 'roles': PARENT,
                'intro': [
                    _p('Marks are the part of the hub parents look at most, and the part most easily '
                       'misread. This is what the numbers mean.'),
                ],
                'sections': [
                    {'title': 'Quizzes are not exams', 'type': 'reading', 'minutes': 3,
                     'summary': 'And they are not weighted as though they were.', 'open': True,
                     'blocks': [
                         _p('A <strong>quiz</strong> is a short check on the last piece of learning. It is '
                            'meant to be got wrong sometimes — that is how it does its job. A '
                            '<strong>test</strong> or an <strong>exam</strong> is the one that carries '
                            'weight.'),
                         _p('Final marks are weighted: quizzes, tests, assignments and exams each count '
                            'for a different share. One poor quiz moves a final mark barely at all.'),
                     ]},
                    {'title': 'Why a result is not there yet', 'type': 'reading', 'minutes': 2,
                     'summary': 'Almost always marking, not failure.',
                     'blocks': [
                         _p('Multiple-choice questions mark instantly. Written answers and uploaded work '
                            'are marked by a person, and appear when that is done — usually within a few '
                            'days.'),
                         _note('info', 'You only ever see final results',
                               'Nothing partly-marked is shown to you. If you can see a result, it is '
                               'finished.'),
                     ]},
                    {'title': 'If an assessment was flagged', 'type': 'reading', 'minutes': 3,
                     'summary': 'What that means, and what it does not.',
                     'blocks': [
                         _p('Some assessments are monitored: the hub records when a learner leaves the '
                            'assessment window — another tab, another program, the pointer off the page. '
                            'Learners are told this before they start.'),
                         _note('warning', 'A flag is a prompt, not a finding',
                               'It means the window lost focus a number of times. It does not mean anyone '
                               'cheated. A notification stealing focus, a dropped connection or a sibling '
                               'walking in all produce the same record. An educator looks at every flagged '
                               'attempt before drawing any conclusion.'),
                         _p('If your learner tells you they were flagged, the useful response is to ask '
                            'what happened and encourage them to explain it to their educator. That is '
                            'exactly what the system is designed to prompt.'),
                     ]},
                ],
            },
        ],
    }


# ---------------------------------------------------------------------------
# The welcome notification
# ---------------------------------------------------------------------------
# What each role is told the five modules will give them.
_WELCOME_SUBJECTS = {
    'student': [
        ('Communication', 'Where to ask a question so it actually gets answered — group chat, '
                          'discussions, direct messages and the bell.'),
        ('Lessons', 'How a lesson works: sections you open one at a time, your own private notes '
                    'and bookmarks, and what your progress bar is counting.'),
        ('Online Classes', 'Joining a live session, the two-minute check that saves everyone time, '
                           'and how attendance is recorded.'),
        ('Dashboard and Student Matrix', 'Reading your own numbers honestly, and which one to act '
                                         'on first.'),
        ('Quizzes and Assessments', 'Sitting a paper, what a monitored assessment watches for, and '
                                    'how to read your result.'),
    ],
    'educator': [
        ('Communication', 'Running the conversation in your modules — announcements, discussions '
                          'worth keeping, moderation, and keeping your own inbox survivable.'),
        ('Lessons', 'The builder: sections first, drag-and-drop content, the three audience buttons, '
                    'and using AI for a first draft you then check.'),
        ('Online Classes', 'Scheduling, hosting well, and what happens to attendance and recordings '
                           'afterwards.'),
        ('Dashboard and Student Matrix', 'Reading a whole class on one screen, how a final mark is '
                                         'actually weighted, and the marking queue.'),
        ('Quizzes and Assessments', 'Building a paper, the exam focus guard and what it honestly '
                                    'can and cannot detect, and reviewing a flagged attempt.'),
    ],
    'parent': [
        ('Communication', 'What reaches you without asking, and how to reach an educator.'),
        ('Lessons', 'What your learner is actually doing, and what a progress bar does not tell you.'),
        ('Online Classes', 'When sessions happen, how attendance works, and what to do if one is '
                           'missed.'),
        ('Dashboard and Student Matrix', 'Reading progress fairly — and the one number worth '
                                         'watching most.'),
        ('Quizzes and Assessments', 'Why a result is not there yet, and what a flagged assessment '
                                    'does and does not mean.'),
    ],
}

_WELCOME_OPENER = {
    'student': (
        'You are enrolled, your account is live, and everything you need is already waiting for '
        'you. Before you start on your actual coursework, we would like fifteen minutes of your '
        'time — spread over five short guides — to make sure the platform never gets in your way.'),
    'educator': (
        'Your account is live and you have been given the run of the place. Before term gets '
        'loud, there are five short guides waiting for you covering the parts of the hub you will '
        'live in — written for educators, not adapted from the learner version.'),
    'staff': (
        'Your account is live with staff access. Five short guides are waiting for you covering '
        'every part of the platform from the running-it side — the same guides your educators '
        'have.'),
    'admin': (
        'Your administrator account is live. Five short guides cover every part of the platform '
        'from the running-it side; the learner and parent versions of each are visible from the '
        'lesson manager if you want to see what they are being told.'),
    'parent': (
        'Your account is live. You do not need to learn this whole platform — you need to know '
        'how to follow your learner\'s progress and how to reach the school. Five short guides '
        'cover exactly that and nothing more.'),
}

_WELCOME_CLOSER = {
    'student': (
        '<h2>Three things worth doing today</h2>'
        '<ol>'
        '<li><strong>Put a picture on your profile.</strong> Settings › Account &amp; profile. In a '
        'class of forty names it genuinely helps.</li>'
        '<li><strong>Say hello in your module chat.</strong> The rooms that stay useful all term '
        'are the ones somebody talked in during week one.</li>'
        '<li><strong>Open one guide below.</strong> Start with <em>Lessons</em> — it is the one '
        'you will use every single day.</li>'
        '</ol>'
        '<div class="note note--tip"><strong>One promise from us</strong>'
        'Your private notes and your bookmarks inside a lesson are yours. Not your educator\'s, '
        'not your parent\'s. Write what actually helps you.</div>'),
    'educator': (
        '<h2>Three things worth doing today</h2>'
        '<ol>'
        '<li><strong>Post in each of your module rooms.</strong> A room that starts empty stays '
        'empty.</li>'
        '<li><strong>Check your notification settings.</strong> Turn off e-mail for every chat '
        'message before term starts, or the important ones will be buried by week three.</li>'
        '<li><strong>Build one lesson end to end.</strong> Even a short one. The builder makes far '
        'more sense after you have shipped something than after you have read about it.</li>'
        '</ol>'
        '<div class="note note--warn"><strong>One thing we want to be straight about</strong>'
        'The AI drafting tools are good at structure and bad at facts. Nothing they produce is ever '
        'published automatically — it lands as a draft and waits for you. Read it properly before '
        'you publish; your name goes on it.</div>'),
    'staff': (
        '<h2>Where to start</h2>'
        '<p>Read <em>Dashboard and Student Matrix</em> first — it is the screen you will use most, '
        'and it is the fastest way to see who needs attention this week. Then '
        '<em>Communication</em> for announcements and moderation.</p>'
        '<div class="note note--warn"><strong>One thing we want to be straight about</strong>'
        'The exam focus guard tells you when a learner left the assessment window. It cannot see a '
        'phone on the desk, and honest interruptions look identical to dishonest ones. Treat every '
        'flag as a prompt for a conversation, never as a finding.</div>'),
    'parent': (
        '<h2>Two things worth doing today</h2>'
        '<ol>'
        '<li><strong>Check your notification settings.</strong> If you do not sign in often, turn '
        'on e-mail for announcements and results so nothing is missed.</li>'
        '<li><strong>Open <em>Dashboard and Student Matrix</em>.</strong> Ten minutes there will '
        'stop you misreading a progress bar later.</li>'
        '</ol>'
        '<div class="note"><strong>What you can and cannot see</strong>'
        'You can see progress, published marks, attendance and anything the school sends you. You '
        'cannot see your learner\'s private notes or their conversations with classmates. That is '
        'deliberate — but if you have a concern about something in those spaces, raise it with the '
        'school and staff can look properly.</div>'),
}


def welcome_html(person, modules=None):
    """The body of the welcome notification, written for ``person``'s role."""
    role = getattr(person, 'user_type', 'student') or 'student'
    guide_role = role if role in _WELCOME_SUBJECTS else ('educator' if role in ('educator', 'staff', 'admin') else 'student')
    opener = _WELCOME_OPENER.get(role) or _WELCOME_OPENER['student']
    closer = _WELCOME_CLOSER.get(role) or _WELCOME_CLOSER.get(guide_role) or _WELCOME_CLOSER['student']

    rows = ''.join(
        f'<li><strong>{name}</strong> — {blurb}</li>'
        for name, blurb in _WELCOME_SUBJECTS[guide_role]
    )

    enrolled = ''
    if modules:
        names = ', '.join(modules)
        enrolled = (f'<p>You have been added to <strong>{names}</strong>. Each one has its own '
                    f'group chat, its own lessons and its own assessments.</p>')

    return (
        f'<p>{opener}</p>'
        f'<h2>Your five guides</h2>'
        f'<p>Every account on this hub is enrolled in <strong>{COURSE["title"]}</strong>. It has '
        f'five modules, one for each part of the platform:</p>'
        f'<ul>{rows}</ul>'
        f'{enrolled}'
        f'<div class="note"><strong>Each one is written for you</strong>'
        f'The same five modules exist for learners, for educators and staff, and for parents — but '
        f'each role only ever sees its own version. You will not stumble into somebody else\'s '
        f'instructions.</div>'
        f'<h2>How the hub is put together</h2>'
        f'<p>Three ideas explain almost everything:</p>'
        f'<ul>'
        f'<li>A <strong>course</strong> is what you are enrolled in. Its button in the top bar is '
        f'your way home — it opens an overview listing every lesson.</li>'
        f'<li>A <strong>module</strong> is one part of a course. It has its own chat, lessons, '
        f'assessments, live classes and files.</li>'
        f'<li>A <strong>lesson</strong> is a stack of sections you open one at a time, with a panel '
        f'beside it that is yours.</li>'
        f'</ul>'
        f'<p>Everything else — the bell, your dashboard, your profile — hangs off those three.</p>'
        f'{closer}'
        f'<hr>'
        f'<p>Welcome aboard. If the platform ever does something you did not expect, the answer is '
        f'almost certainly in one of the five guides — and if it is not, tell us, because that means '
        f'we wrote them badly.</p>'
    )


def welcome_title(person):
    role = getattr(person, 'user_type', 'student') or 'student'
    return {
        'student': f'Welcome to the {BRAND} — start here',
        'educator': f'Welcome to the {BRAND} — your educator guide',
        'staff': f'Welcome to the {BRAND} — your staff guide',
        'admin': f'Welcome to the {BRAND} — your administrator guide',
        'parent': f'Welcome to the {BRAND} — a short guide for parents',
    }.get(role, f'Welcome to the {BRAND} — start here')


def welcome_summary(person):
    role = getattr(person, 'user_type', 'student') or 'student'
    return {
        'student': 'Five short guides covering everything you will use — and three things worth doing today.',
        'educator': 'Five short guides written for educators, covering the parts of the hub you will live in.',
        'staff': 'Five short guides covering the platform from the running-it side.',
        'admin': 'Five short guides covering the platform from the running-it side.',
        'parent': 'What you can see, how to reach the school, and how to read your learner’s progress fairly.',
    }.get(role, 'Five short guides covering everything you will use.')


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build(*, author, professor=None):
    """Create the onboarding guide — one lesson per audience, per area.

    The guide used to be a Course with five Subjects hanging off it. Courses and
    subjects are gone: a candidate registers for a programme and its modules, and
    the guide is not one of those — it is orientation material that belongs to
    nobody's syllabus.

    So it is now simply a set of lessons with no module, published and separated
    by ``target_roles`` so each audience sees only its own version. Idempotent.
    Returns ``(None, [], lesson_count)`` — the first two are kept so the callers
    that unpack a triple keep working.
    """
    diagrams = _diagrams()
    lessons_made = 0

    for spec in module_specs(diagrams):
        for lesson_spec in spec['lessons']:
            seed_builders.build_lesson(
                lesson_spec, module=None, author=author,
                status='published', visibility='public')
            lessons_made += 1

    return None, [], lessons_made
