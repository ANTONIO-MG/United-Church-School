"""The Support / Help centre — a searchable user manual for the whole platform.

Content lives here as data (no database, no migration): each article has an
``audience`` so it is only shown to the people it is for —

  * ``all``      — everyone
  * ``student``  — students **and** parents/guardians
  * ``educator`` — educators
  * ``staff``    — admin **and** staff

The page (:func:`support`) filters the corpus by the viewer's role and by a
free-text search across the title, keywords and body, then groups what remains
by section. Add an article by appending a dict to :data:`HELP_ARTICLES`.
"""
import re

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from core.roles import role_flags

# audience → the human label shown as a little chip on the article.
AUDIENCE_LABEL = {
    'all': 'Everyone', 'student': 'Learners & parents',
    'educator': 'Teachers', 'staff': 'Admin & staff',
}

# The section order the page renders in.
SECTION_ORDER = [
    'Getting started', 'Your studies', 'Fees & subjects',
    'Teaching', 'Administration', 'Help & troubleshooting',
]


def _a(id, title, section, audience, icon, keywords, body):
    return {'id': id, 'title': title, 'section': section, 'audience': audience,
            'icon': icon, 'keywords': keywords, 'body': body.strip()}


HELP_ARTICLES = [
    # ---------------- Getting started (everyone) ----------------
    _a('navigating', 'Finding your way around', 'Getting started', 'all', 'bi-compass',
       'navigation sidebar menu dashboard where is home layout',
       """
<p>Everything hangs off the <strong>sidebar</strong> on the left and the <strong>top bar</strong>.</p>
<ul>
  <li><strong>Dashboard</strong> — your home feed: what's new, your tasks, and what's due next.</li>
  <li><strong>My Subjects / My Grade</strong> — everything you're registered for. Open a subject to reach its <em>Schedule</em>.</li>
  <li><strong>Messages</strong> and <strong>Notifications</strong> — conversations with your teachers and class, and alerts.</li>
  <li><strong>Support &amp; help</strong> — this page, at the bottom of the sidebar.</li>
</ul>
<p>On a phone, tap the menu icon to open the sidebar.</p>
"""),
    _a('first-login', 'Your first login & completing your profile', 'Getting started', 'all', 'bi-person-check',
       'first login profile complete password change forgot verify email onboarding',
       """
<p>The first time you sign in you'll be asked to complete a short profile — your name, date of birth,
area, preferred device, a photo, and your POPIA consent. This unlocks the rest of the platform.</p>
<p>If your account was created for you (staff/educator), your e-mail is already verified. Use
<strong>“Forgot password?”</strong> on the login page to set your own password on first login.</p>
"""),
    _a('messages', 'Messages, notifications & staying in the loop', 'Getting started', 'all', 'bi-chat-left-text',
       'chat message notification announcement bell inbox reply group',
       """
<p><strong>Messages</strong> holds your conversations — 1:1 chats and your subject/class groups.
<strong>Notifications</strong> (the bell) collects alerts: deadlines, results, announcements and welcome guides.</p>
<p>You can tune what you get e-mailed under <em>Settings → Notifications</em>.</p>
"""),

    # ---------------- Your studies (students + parents) ----------------
    _a('register-modules', 'Registering: your grade, subjects & class', 'Your studies', 'student', 'bi-ui-checks',
       'register registration enrol enrolment grade subject class year group choose select application admission',
       """
<p>Registration is three steps:</p>
<ol>
  <li><strong>Your details</strong> — a short profile + consent.</li>
  <li><strong>Grade &amp; subjects</strong> — pick the learner's <strong>grade</strong> (Grade 1 to Grade 12),
      the <strong>class/year group</strong>, and the CAPS subjects they take. The fees are shown with a live total.</li>
  <li><strong>Finish</strong> — pay now (PayFast), start a 7-day free trial, or get an invoice to pay by EFT.</li>
</ol>
<p>If your grade has no named classes, the current school year stands in as your year group.</p>
"""),
    _a('unlock-modules', 'Paying fees & unlocking a subject', 'Fees & subjects', 'student', 'bi-unlock',
       'pay payment fees unlock locked subject module payfast eft invoice trial price monthly lock',
       """
<p>A subject is <strong>locked</strong> until its fees are paid or it is on a free trial. On <em>My Subjects</em> each subject
shows <em>Active</em>, <em>Trial</em> or <em>Locked</em>.</p>
<p>To open a locked subject, click <strong>Unlock</strong> → choose:</p>
<ul>
  <li><strong>Pay now (PayFast)</strong> — card / instant EFT; it unlocks the moment payment clears.</li>
  <li><strong>EFT / pay later</strong> — we e-mail you an invoice; the subject unlocks when the EFT clears.</li>
</ul>
<p>Free subjects are never locked.</p>
"""),
    _a('schedule', 'The subject schedule: terms, weeks, tests & exams', 'Your studies', 'student', 'bi-calendar3-week',
       'schedule term overview study guide week test exam final documents pdf topic teardrop worksheet homework',
       """
<p>Open a subject and choose <strong>Schedule</strong>. It's a set of drop-downs, top to bottom:</p>
<ul>
  <li><strong>Overview &amp; study guide</strong> — what the term covers and how it's assessed.</li>
  <li><strong>The weeks of the term</strong> — each week's topic, with the written material on the left and its
      <strong>documents (PDFs) on the side</strong>.</li>
  <li><strong>Tests</strong> and <strong>examinations</strong>.</li>
</ul>
<p>Work a week in order: read the lesson, try the exercises, then the answers unlock. That order is deliberate —
attempting before you read the answer is where the learning comes from.</p>
"""),
    _a('assessments', 'Sitting a quiz, test or assessment', 'Your studies', 'student', 'bi-pencil-square',
       'assessment quiz test exam take attempt result marks pass submit timer',
       """
<p>Open the assessment from the schedule or your tasks and click <strong>Start</strong>. Watch the timer and
attempt limit. Objective questions mark on submit; written answers are marked by your teacher and appear
under <em>My results</em> with feedback.</p>
"""),
    _a('progress-reports', 'Your progress, results & certificates', 'Your studies', 'student', 'bi-graph-up',
       'progress report card certificate results grades marks award',
       """
<p><em>My Progress</em> shows how you're tracking; <em>Reports &amp; Certificates</em> holds your report cards
and any certificates you've earned. Grades roll up from your marked assessments automatically.</p>
"""),
    _a('parent-view', 'For parents & guardians', 'Your studies', 'student', 'bi-people',
       'parent guardian child link view payment invoice',
       """
<p>As a parent/guardian you see your child's progress, marks and school notices, and can view and pay their
school-fee invoices. A learner can invite up to two parents from their profile.</p>
"""),

    # ---------------- Teaching (educators) ----------------
    _a('build-schedule', 'Building a subject schedule (weeks & materials)', 'Teaching', 'educator', 'bi-tools',
       'build schedule phase week material worksheet study guide upload publish document scaffold',
       """
<p>Open a subject → <strong>Build</strong>. Use <em>Scaffold</em> to create the standard school year (one block per
term, with its weeks), then add <strong>materials</strong> to a block or week: overviews, study guides, worksheets,
answers, past papers and document PDFs. Publish a material to make it visible to learners.</p>
<p>The teaching order (guide → questions → answers) is enforced automatically, so a solution only opens after
the learner submits their attempt.</p>
"""),
    _a('lessons', 'Writing lessons & the lesson player', 'Teaching', 'educator', 'bi-journal-richtext',
       'lesson create editor block heading text image video quiz publish author',
       """
<p><em>Lessons → Lesson creator</em> builds a lesson from blocks — headings, rich text, images, audio/video,
tables, callouts, embedded quizzes and live sessions. Set the author details and <strong>publish</strong> to a
subject/class/individuals. Learners read it in the tear-drop lesson player.</p>
"""),
    _a('marking', 'Marking written answers', 'Teaching', 'educator', 'bi-clipboard-check',
       'mark marking queue rubric grade feedback assessment attempt',
       """
<p>Manually-marked answers land in the <em>Marking queue</em> (under Learning Hub). Each shows the rubric and the
learner's response; award marks + feedback and the attempt re-grades. Auto-marked questions score on submit.</p>
"""),

    # ---------------- Administration (admin + staff) ----------------
    _a('academic-structure', 'Managing the academic structure', 'Administration', 'staff', 'bi-diagram-3',
       'school grade subject class year group academic structure add edit calendar manage caps',
       """
<p><em>Learning Hub → Academic structure</em> is the admin CRUD for the spine:</p>
<ul>
  <li><strong>The school</strong> — United Church School, with its school calendar (terms, tests and exams).</li>
  <li>The school → its <strong>Grades</strong> (Grade 1 to Grade 12); each grade → its CAPS <strong>Subjects</strong>
      (with fees) and its <strong>Classes/year groups</strong>.</li>
</ul>
"""),
    _a('team-accounts', 'Creating admin / staff / educator accounts', 'Administration', 'staff', 'bi-person-plus',
       'create account staff educator admin team invite password superuser verify',
       """
<p>A <strong>superuser</strong> creates team accounts under <em>Administration → Create team account</em>.
The account is made with a verified e-mail and a random password, and an invitation with the login details is
e-mailed to the person. They set their own password (via “Forgot password?”) and complete a short profile on
first login — no grade to pick, since staff aren't enrolled.</p>
"""),
    _a('finance', 'Invoices, payments & receipts', 'Administration', 'staff', 'bi-receipt',
       'invoice payment receipt payfast eft finance pending paid refund history',
       """
<p><em>Finance</em> lists invoices and their status. Registrations and subject unlocks raise school-fee invoices;
paying (PayFast) marks them paid and unlocks the subject; EFT invoices sit as <em>Sent/pending</em> until settled.
Receipts are e-mailed to the payer.</p>
"""),

    # ---------------- Help & troubleshooting (everyone) ----------------
    _a('errors', 'Something went wrong — reading an error', 'Help & troubleshooting', 'all', 'bi-bug',
       'error code problem fix bug broken message support reference',
       """
<p>Most errors show a short <strong>code</strong> like <code>USER-1002</code> or <code>FIN-8002</code>. The prefix
says which part of the system (USER = accounts, FIN = payments, LRN = lessons/subjects) and the wording tells you
what to do. If a code keeps appearing, note it and contact the school office with it — it points them straight to
the cause.</p>
"""),
    _a('locked', 'Why is something locked?', 'Help & troubleshooting', 'all', 'bi-lock',
       'locked lock cant open access subject module week solution test paid fees',
       """
<p>Two different locks read differently:</p>
<ul>
  <li><strong>A padlock</strong> — the fees for the subject haven't been paid yet. Click <em>Unlock</em> to open it.</li>
  <li><strong>An hourglass</strong> — you have it, but haven't reached it in the week's order yet (e.g. try the
      exercises before the answers open). It's a teaching step, not a paywall.</li>
</ul>
"""),
    _a('contact', 'Who to contact for what', 'Help & troubleshooting', 'all', 'bi-headset',
       'contact support help who academic technical educator staff admin',
       """
<p><strong>Academics</strong> — a topic, a mark, a lesson, the schedule: message your <strong>teacher</strong> or
the academic <strong>staff</strong> from Messages.</p>
<p><strong>Technical</strong> — logging in, school fees, or anything about the platform itself: contact the
<strong>school office</strong> (uchs@unitedcs.co.za · 011 648 4727).</p>
"""),

    # ---------------- New feature guides ----------------
    _a('the-bell', 'The bell: notifications, messages & sounds', 'Getting started', 'all', 'bi-bell',
       'bell notification sound chime alert badge dot unread real-time live mention tagged read',
       """
<p>The <strong>bell</strong> in the top bar is your live inbox. A red dot means something new is waiting.
Open it to see the newest <strong>notifications</strong> and the <strong>messages aimed at you</strong> —
every direct (1:1) message, and any group message where someone <strong>@-mentioned</strong> you.</p>
<h4>Sounds</h4>
<p>While you're signed in, a soft chime plays the moment a new notification or message arrives —
a two-tone chime for notifications, a single tone for messages. Your browser may stay silent until
you've clicked somewhere on the page (a one-time browser rule); after that, sounds play on their own.</p>
<h4>Reading &amp; clearing</h4>
<ul>
  <li>Click a <strong>notification</strong> to open it <em>in full</em> on its own page — it's marked read and drops off the bell.</li>
  <li>Click a <strong>message</strong> to jump into that conversation; opening the chat clears it from the bell.</li>
  <li>Read items disappear from the bell automatically — it only ever shows what still needs you.</li>
</ul>
<p>Separately, the <strong>Messages</strong> item in the sidebar counts <em>all</em> unread chat messages,
while the bell is only the things addressed to you.</p>
"""),

    _a('social-feed', 'The community feed: posting, photos & documents', 'Getting started', 'all', 'bi-chat-square-text',
       'social feed post share photo video document file attachment gallery community wall who sees',
       """
<p><strong>Community</strong> (the social feed) is where you share updates with your classmates, teachers and the school community.</p>
<h4>Writing a post</h4>
<ul>
  <li>Type in the <strong>“Share your thoughts…”</strong> box — it starts small and grows as you type.</li>
  <li>Attach <strong>one or more</strong> photos, videos or documents with the <em>Photo / Video</em> and
      <em>Document</em> buttons. Each picked file shows a thumbnail you can remove before posting.</li>
  <li>Pick a subject to file it under (or leave it on <em>General</em>). The note by the button shows who can see it.</li>
</ul>
<h4>Viewing attachments</h4>
<p>Attachments show as a neat tile grid (two side-by-side, a 2×2 for three or four, and a “+N” on the
last tile when there are more). Click any of them to open the <strong>full-screen viewer</strong>:</p>
<ul>
  <li>Images and videos open at real size over a blurred background.</li>
  <li>Use the <strong>‹ ›</strong> arrows (or the ← → keys) to move between a post's attachments, and <strong>Esc</strong> or the ✕ to close.</li>
  <li>Documents open in a scrollable viewer; a <strong>Save</strong> button downloads any file to your device.</li>
</ul>
<p>A poster's <strong>name and photo</strong> link to their profile — click to see who shared something.</p>
"""),

    _a('live-lessons', 'Live lessons: who is here & raising your hand', 'Your studies', 'all', 'bi-broadcast',
       'live lesson presence who is here online raise hand hand-raising classroom together real-time',
       """
<p>When you open a lesson, the rail on the right shows a live <strong>“who's here now”</strong> panel —
the photos of everyone currently viewing that lesson, updating as people arrive and leave.</p>
<h4>Raising your hand</h4>
<p>Tap the <strong>hand</strong> button in that panel to raise your hand — everyone in the lesson sees your
avatar ringed in amber, and a <strong>“N hands up”</strong> line names who has a question. Tap it again to
lower your hand. It's the quiet way to signal your teacher during a shared session.</p>
<p>The live class <em>video</em> itself runs in Microsoft Teams from the session's join link; this panel is the
platform-side presence around it.</p>
"""),

    _a('free-trial', 'Your free trial & how many days are left', 'Fees & subjects', 'student', 'bi-hourglass-split',
       'trial free week seven days left countdown expires unlock pay lapse',
       """
<p>You can start most subjects on a <strong>7-day free trial</strong> — the whole subject opens on trust while
you pay by EFT. Everywhere the subject appears you'll see how long is left:</p>
<ul>
  <li>On <strong>My Subjects</strong>, the subject's badge reads <em>“Trial · N days left”</em>.</li>
  <li>Inside the subject's <strong>Schedule</strong>, a banner shows the days remaining with an <em>Unlock</em> button.</li>
</ul>
<p>When the trial ends, an unpaid subject <strong>closes</strong> until your payment is recorded — nothing is lost,
it simply locks again. Pay any time from the subject to keep your access open. See also
<em>“Paying fees &amp; unlocking a subject”</em>.</p>
"""),

    _a('help-centre', 'Using this help centre', 'Help & troubleshooting', 'all', 'bi-life-preserver',
       'help support search guide manual how to find article this page',
       """
<p>This <strong>Support &amp; help</strong> page (bottom of the sidebar) is your manual. Use the
<strong>search box</strong> at the top to find a topic by name or keyword — results filter as you type.</p>
<p>Articles are grouped by area and are <strong>tailored to you</strong>: learners and parents see the study
guides, teachers see the teaching guides, and admins/staff see the administration guides — plus the
general ones everyone gets. If you can't find something, use <em>“Who to contact for what”</em>.</p>
"""),
]


_TAG = re.compile(r'<[^>]+>')


def _plain(html):
    return _TAG.sub(' ', html)


def _audience_for(request):
    flags = role_flags(request)
    if flags.get('is_admin_staff'):
        return 'staff'
    if flags.get('is_educator'):
        return 'educator'
    return 'student'   # students and parents share the same manual


@login_required
def support(request):
    """The searchable, role-scoped help centre."""
    query = (request.GET.get('q') or '').strip()
    audience = _audience_for(request)

    visible = [a for a in HELP_ARTICLES if a['audience'] in ('all', audience)]
    if query:
        needle = query.lower()
        visible = [a for a in visible
                   if needle in a['title'].lower()
                   or needle in a['keywords'].lower()
                   or needle in _plain(a['body']).lower()]

    # Group into sections in the defined order.
    by_section = {}
    for article in visible:
        by_section.setdefault(article['section'], []).append(article)
    sections = [{'name': name, 'articles': by_section[name]}
                for name in SECTION_ORDER if name in by_section]

    return render(request, 'communication/support.html', {
        'page_title': 'Support & help', 'query': query, 'sections': sections,
        'total': len(visible), 'audience_label': AUDIENCE_LABEL.get(audience, ''),
    })
