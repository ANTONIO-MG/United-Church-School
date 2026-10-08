"""Profile-context builders — the data layer behind ``templates/profiles/shell.html``.

Every "profile" in the hub (a **person** or a **module**) renders
through one shell. This module assembles that shell's context for the entity:
the header (cover/avatar/title/meta), the tab strip, the right-hand **Activity**
and **Files** panels, and the payload for the currently-active tab.

Keeping it here (rather than in a view) means the person profile can adopt the
exact same shell later with no duplication. Every lookup is defensive so a
missing/optional app never breaks the page.
"""

import logging

from django.urls import reverse
from django.utils import timezone

logger = logging.getLogger('apps')

# Tab definitions (key, label, icon) — the module "sections".
MODULE_TABS = [
    ('feed', 'Feed', 'bi-card-text'),
    ('chat', 'Chat', 'bi-chat-left-text'),
    ('lessons', 'Lessons', 'bi-journal-richtext'),
    ('assessments', 'Assessments', 'bi-ui-checks'),
    ('live', 'Live classes', 'bi-camera-video'),
    ('documents', 'Documents', 'bi-folder2-open'),
    ('events', 'Events', 'bi-calendar-event'),
    ('reminders', 'Reminders', 'bi-bell'),
    ('activity', 'Activity', 'bi-activity'),
]

COURSE_TABS = [
    ('feed', 'Feed', 'bi-card-text'),
    ('overview', 'Overview', 'bi-info-circle'),
    ('modules', 'Subjects', 'bi-diagram-3'),
    ('lessons', 'Lessons', 'bi-journal-richtext'),
    ('assessments', 'Assessments', 'bi-ui-checks'),
    ('documents', 'Documents', 'bi-folder2-open'),
    ('events', 'Events', 'bi-calendar-event'),
    ('activity', 'Activity', 'bi-activity'),
]


# ---------------------------------------------------------------------------
# Shared pieces (Activity + Files panels)
# ---------------------------------------------------------------------------
def activity_for(modules, limit=8, *, user=None):
    """The scope's activity rail — learning records, wall posts (with their
    media) and the notifications raised for these modules.

    Three sources merged newest-first:

      * **xAPI statements** — who passed/completed/answered what.
      * **Wall posts** — what was shared to the scope's feed, carrying any
        attached images/videos so the rail actually shows the media rather than
        just saying a post happened.
      * **Notifications** — the ones addressed to ``user`` that point at this
        module, so a student sees "your assignment was marked" in the
        context it belongs to instead of only in the global bell menu.

    Each item is ``{icon, text, when, url, media}`` where ``media`` is a list of
    ``{url, kind, name}`` the shell renders as a grid.
    """
    items = []
    module_ids = [s.id for s in modules] if modules else []

    # --- xAPI learning records (only when an LRS app is installed) ---
    try:
        from apps.lrs.models import XapiStatement
    except ImportError:
        XapiStatement = None
    if XapiStatement is not None:
        try:
            qs = (XapiStatement.objects.filter(module__in=modules, voided=False)
                  .select_related('local_user')[:limit])
            icons = {'passed': 'bi-check-circle', 'failed': 'bi-x-circle', 'completed': 'bi-flag',
                     'experienced': 'bi-eye', 'answered': 'bi-pencil'}
            for s in qs:
                items.append({
                    'icon': icons.get(s.verb_display, 'bi-dot'),
                    'text': f'{s.actor_name or "Someone"} {s.verb_display}',
                    'when': s.stored, 'url': '', 'media': [],
                })
        except Exception:  # pragma: no cover
            logger.exception('profiles: activity lookup failed')

    # --- Wall posts + their attachments ---
    try:
        from django.db.models import Q as _Q
        from apps.communication.models import Discussion
        scope = _Q(module_id__in=module_ids) if module_ids else _Q(pk__in=[])
        for post in (Discussion.objects.filter(scope)
                     .select_related('author').prefetch_related('attachments')
                     .order_by('-created_at')[:limit]):
            media = []
            for att in post.attachments.all():
                if not att.file:
                    continue
                try:
                    media.append({'url': att.file.url, 'kind': att.kind,
                                  'name': att.original_name or ''})
                except ValueError:      # file recorded but missing on disk
                    continue
            who = (post.author.get_full_name() or post.author.get_username()) if post.author else 'Someone'
            verb = 'shared media' if media else 'posted'
            items.append({
                'icon': 'bi-image' if media else 'bi-chat-square-text',
                'text': f'{who} {verb}: {post.title or post.body[:60]}',
                'when': post.created_at,
                'url': post.get_absolute_url(),
                'media': media[:4],
            })
    except Exception:  # pragma: no cover
        logger.exception('profiles: activity wall lookup failed')

    # --- Notifications raised for these modules ---
    if user is not None and getattr(user, 'is_authenticated', False):
        try:
            from django.db.models import Q as _Q
            from apps.communication.models import Notification
            scope = _Q(announcement__modules__in=module_ids) if module_ids else _Q(pk__in=[])
            levels = {'error': 'bi-exclamation-triangle', 'warning': 'bi-exclamation-circle',
                      'success': 'bi-check-circle'}
            for note in (Notification.objects.filter(scope, recipient=user)
                         .select_related('actor').distinct().order_by('-created_at')[:limit]):
                items.append({
                    'icon': levels.get(note.level, 'bi-bell'),
                    'text': note.title or note.verb or 'Notification',
                    'when': note.created_at,
                    'url': note.url or '',
                    'media': [],
                })
        except Exception:  # pragma: no cover
            logger.exception('profiles: activity notification lookup failed')

    items.sort(key=lambda i: i['when'], reverse=True)
    return items[:limit]


# ---------------------------------------------------------------------------
# Past / Today / Upcoming grouping (assessments + events)
# ---------------------------------------------------------------------------
#: Rendered in this order; "today" is styled as the one that needs attention.
TIME_GROUPS = [
    ('today', 'Today', 'bi-dot'),
    ('upcoming', 'Upcoming', 'bi-arrow-up-right'),
    ('past', 'Past', 'bi-clock-history'),
]


def _as_date(value):
    """Coerce a date/datetime (aware or naive) to a local ``date``, else None."""
    if value is None:
        return None
    if hasattr(value, 'hour'):
        try:
            return timezone.localtime(value).date() if timezone.is_aware(value) else value.date()
        except (ValueError, OverflowError):
            return None
    return value


def group_by_time(rows, key):
    """Split ``rows`` into Past / Today / Upcoming buckets.

    ``key`` is a callable returning each row's date/datetime. Rows with no date
    fall into ``undated`` so nothing is silently dropped — an assessment with no
    close date is still an assessment. Returns a list of
    ``{key, label, icon, rows, count}`` with empty buckets removed.
    """
    today = timezone.localdate()
    buckets = {'past': [], 'today': [], 'upcoming': [], 'undated': []}
    for row in rows:
        when = _as_date(key(row))
        if when is None:
            buckets['undated'].append(row)
        elif when == today:
            buckets['today'].append(row)
        elif when > today:
            buckets['upcoming'].append(row)
        else:
            buckets['past'].append(row)

    # Soonest first when looking forward, most recent first when looking back.
    buckets['upcoming'].sort(key=lambda r: _as_date(key(r)) or today)
    buckets['past'].sort(key=lambda r: _as_date(key(r)) or today, reverse=True)

    out = [{'key': k, 'label': label, 'icon': icon, 'rows': buckets[k], 'count': len(buckets[k])}
           for k, label, icon in TIME_GROUPS if buckets[k]]
    if buckets['undated']:
        out.append({'key': 'undated', 'label': 'No date set', 'icon': 'bi-dash-circle',
                    'rows': buckets['undated'], 'count': len(buckets['undated'])})
    return out


def lessons_with_progress(lessons, user):
    """Decorate lessons with this student's progress + the facts worth showing.

    Adds ``pct``, ``status_label``, ``minutes_spent``, ``estimated_minutes``,
    ``resource_count``, ``assessment_count``, ``section_count`` and
    ``has_locks`` to each row so the lesson list can show a progress bar and
    useful context beside the title without firing a query per lesson.
    """
    rows = list(lessons)
    if not rows:
        return rows
    ids = [lesson.id for lesson in rows]

    sessions, resources, assessments = {}, {}, {}
    sections, locks = {}, set()
    try:
        from django.db.models import Count as _Count, Max as _Max, Sum as _Sum
        from apps.learning.models import LessonResource, LessonSection, StudySession
        if getattr(user, 'is_authenticated', False):
            for row in (StudySession.objects.filter(student=user, lesson_id__in=ids)
                        .values('lesson_id')
                        .annotate(pct=_Max('completion_pct'), secs=_Sum('total_seconds'))):
                sessions[row['lesson_id']] = row
        for row in (LessonResource.objects.filter(lesson_id__in=ids)
                    .values('lesson_id').annotate(n=_Count('id'))):
            resources[row['lesson_id']] = row['n']
        # How many tear-drops each lesson has, and whether any of them gate.
        for row in (LessonSection.objects.filter(lesson_id__in=ids)
                    .values('lesson_id').annotate(n=_Count('id'))):
            sections[row['lesson_id']] = row['n']
        locks = set(LessonSection.objects.filter(lesson_id__in=ids, requires_previous=True)
                    .values_list('lesson_id', flat=True))
    except Exception:  # pragma: no cover
        logger.exception('profiles: lesson progress lookup failed')
    try:
        from django.db.models import Count as _Count
        from apps.assessments.models import Assessment
        for row in (Assessment.objects.filter(lesson_id__in=ids)
                    .values('lesson_id').annotate(n=_Count('id'))):
            assessments[row['lesson_id']] = row['n']
    except Exception:  # pragma: no cover
        pass

    for lesson in rows:
        session = sessions.get(lesson.id) or {}
        pct = int(session.get('pct') or 0)
        lesson.pct = max(0, min(100, pct))
        lesson.minutes_spent = round((session.get('secs') or 0) / 60)
        lesson.resource_count = resources.get(lesson.id, 0)
        lesson.assessment_count = assessments.get(lesson.id, 0)
        lesson.section_count = sections.get(lesson.id, 0)
        lesson.has_locks = lesson.id in locks
        if lesson.pct >= 100:
            lesson.status_label, lesson.status_tone = 'Completed', 'success'
        elif lesson.pct > 0:
            lesson.status_label, lesson.status_tone = 'In progress', 'primary'
        else:
            lesson.status_label, lesson.status_tone = 'Not started', 'muted'
    return rows


def files_for(modules, limit=20):
    """Lesson resources (uploaded files) across ``modules`` → sidebar Files."""
    out = []
    try:
        from apps.learning.models import LessonResource
        # NB: clear the model's default ordering — LessonResource orders by
        # ``lesson``, whose own Meta ordering chains through ProgrammeModule → Course and
        # makes Django raise "Infinite loop caused by ordering".
        qs = (LessonResource.objects.filter(lesson__module__in=modules)
              .exclude(file='').select_related('lesson').order_by('-id')[:limit])
        icons = {'pdf': 'bi-file-earmark-pdf', 'word': 'bi-file-earmark-word',
                 'ppt': 'bi-file-earmark-slides', 'image': 'bi-file-earmark-image',
                 'audio': 'bi-file-earmark-music', 'video': 'bi-file-earmark-play'}
        for r in qs:
            if not r.file:
                continue
            out.append({
                'name': r.title or r.file.name.rsplit('/', 1)[-1],
                'url': r.file.url,
                'meta': r.lesson.title if r.lesson else '',
                'icon': icons.get(r.kind, 'bi-file-earmark'),
            })
    except Exception:  # pragma: no cover
        logger.exception('profiles: files lookup failed')
    return out


def _doc_icon(kind, name=''):
    """Bootstrap-icon for a document row, by media kind then file extension."""
    if kind == 'image':
        return 'bi-file-earmark-image'
    if kind == 'video':
        return 'bi-file-earmark-play'
    ext = (name or '').lower().rsplit('.', 1)[-1] if '.' in (name or '') else ''
    return {
        'pdf': 'bi-file-earmark-pdf', 'doc': 'bi-file-earmark-word', 'docx': 'bi-file-earmark-word',
        'ppt': 'bi-file-earmark-slides', 'pptx': 'bi-file-earmark-slides',
        'xls': 'bi-file-earmark-spreadsheet', 'xlsx': 'bi-file-earmark-spreadsheet', 'csv': 'bi-file-earmark-spreadsheet',
        'zip': 'bi-file-earmark-zip', 'rar': 'bi-file-earmark-zip',
        'mp3': 'bi-file-earmark-music', 'wav': 'bi-file-earmark-music',
    }.get(ext, 'bi-file-earmark-text')


def documents_for(*, modules=None, user=None, include_private=True, limit=120):
    """Everything filed under one scope's **Documents** section.

    Three sources, unified into one list — this is what makes "upload knows where
    it belongs" true: a file surfaces in the Documents tab of exactly the scope it
    was posted to.

      * **Lesson resources** — official materials attached to the scope's lessons.
      * **Wall attachments** — media posted to the scope's feed (Discussion).
      * **Chat attachments** — files shared in the scope's chat group (Message).

    ``modules`` scopes by place; ``user`` scopes to a person (their
    own uploads only — "personal"). Each row carries ``kind`` so the template can
    show media inline and open it in the lightbox rather than a new tab.
    """
    modules = list(modules or [])
    rows = []

    # 1. Lesson resources -----------------------------------------------------
    try:
        from apps.learning.models import LessonResource
        lr_scope = modules
        if lr_scope:
            qs = (LessonResource.objects.filter(lesson__module__in=lr_scope)
                  .exclude(file='').select_related('lesson').order_by('-id')[:limit])
            for r in qs:
                if not r.file:
                    continue
                name = r.title or r.file.name.rsplit('/', 1)[-1]
                kind = 'image' if r.kind == 'image' else 'video' if r.kind == 'video' else 'file'
                rows.append({'name': name, 'url': r.file.url, 'kind': kind,
                             'icon': _doc_icon(kind, name),
                             'meta': f'Lesson · {r.lesson.title}' if r.lesson else 'Lesson material',
                             'sort': r.id})
    except Exception:  # pragma: no cover
        logger.exception('documents: lesson resources failed')

    # 2. Wall attachments (Discussion) ---------------------------------------
    try:
        from apps.communication.models import DiscussionAttachment
        q = DiscussionAttachment.objects.select_related(
            'discussion__author', 'reply__author').filter(file__gt='')
        if modules:
            q = q.filter(discussion__module__in=modules)
        elif user is not None:
            q = q.filter(discussion__author=user)
        else:
            q = q.none()
        for a in q.order_by('-id')[:limit]:
            if not a.file:
                continue
            author = getattr(a.discussion, 'author', None) or getattr(a.reply, 'author', None)
            rows.append({'name': a.original_name or a.file.name.rsplit('/', 1)[-1],
                         'url': a.file.url, 'kind': a.kind, 'icon': _doc_icon(a.kind, a.original_name),
                         'meta': f'Posted by {author}' if author else 'From the feed',
                         'sort': a.id})
    except Exception:  # pragma: no cover
        logger.exception('documents: wall attachments failed')

    # 3. Chat attachments (Message) ------------------------------------------
    try:
        from apps.communication.models import MessageAttachment
        q = MessageAttachment.objects.select_related('message__sender', 'message__group').filter(file__gt='')
        if modules:
            q = q.filter(message__group__programme_module__in=modules)   # the subject's chat
        elif user is not None and include_private:
            # "personal chat only": files the person shared in their direct chats.
            # Gated by include_private — a direct chat is between two people, so
            # these are only shown to the person themselves (or staff).
            q = q.filter(message__sender=user, message__group__kind='direct')
        else:
            q = q.none()
        for a in q.filter(message__is_deleted=False).order_by('-id')[:limit]:
            if not a.file:
                continue
            sender = getattr(a.message, 'sender', None)
            rows.append({'name': a.original_name or a.file.name.rsplit('/', 1)[-1],
                         'url': a.file.url, 'kind': a.kind, 'icon': _doc_icon(a.kind, a.original_name),
                         'meta': f'Shared in chat by {sender}' if sender else 'From chat',
                         'sort': 10_000_000 + a.id})
    except Exception:  # pragma: no cover
        logger.exception('documents: chat attachments failed')

    rows.sort(key=lambda d: d.get('sort', 0), reverse=True)
    for d in rows:
        d.pop('sort', None)
    return rows[:limit]


def _attach_grid(post, attachments):
    """Decorate a wall post with the fields ``_wall_post.html`` reads to lay its
    attachments out in the shared media grid: up to 4 tiles, a "+N" badge beyond
    that, and the ``data-count`` bucket (1 / 2 / 3 / 4 / more)."""
    n = len(attachments)
    post.grid_attachments = attachments[:4]
    post.grid_extra = max(0, n - 4)
    post.grid_count = str(n) if n <= 4 else 'more'


def wall_for(request, *, author=None, module=None, limit=25):
    """The social wall shown on a profile's **Feed** tab (templates/profiles/_wall.html).

    One implementation for all three profile kinds — the only difference is the
    scope: a **person**'s wall is what they wrote; a **module** wall is
    what was posted to it. Posts are :class:`Discussion` rows (they already carry
    likes, threaded replies and attachments).

    Returns ``posts`` (each decorated with ``liker_ids`` + ``top_comments`` so the
    template needs no queries per row), ``wall_scope`` (where a new post lands)
    and ``can_post``.
    """
    posts, scope = [], {}
    try:
        from apps.communication.models import Discussion

        qs = Discussion.objects.select_related('author__profile', 'module')
        if module is not None:
            qs = qs.filter(module=module)
            scope = {'module': module.pk}
        elif author is not None:
            qs = qs.filter(author=author)
        else:
            return {'posts': [], 'wall_scope': {}, 'can_post': False}

        posts = list(
            qs.prefetch_related(
                'attachments', 'likes',
                'replies__author__profile', 'replies__likes',
                'replies__child_replies__author__profile', 'replies__child_replies__likes',
            ).order_by('-is_pinned', '-created_at')[:limit]
        )
        for p in posts:
            # Precomputed in Python so the card template stays query-free.
            p.liker_ids = {u.pk for u in p.likes.all()}
            p.top_comments = [r for r in p.replies.all() if r.reply_to_id is None]
            _attach_grid(p, list(p.attachments.all()))
    except Exception:  # pragma: no cover
        logger.exception('profiles: wall lookup failed')

    return {
        'posts': posts,
        'wall_scope': scope,
        'can_post': bool(request.user.is_authenticated),
    }


def _tabs(defs, url_for, active, counts=None):
    counts = counts or {}
    return [{'key': k, 'label': label, 'icon': icon, 'url': url_for(k),
             'badge': counts.get(k), 'active': k == active}
            for k, label, icon in defs]


# The <div id="…"> the profile shell wraps its tab content in, and that the tab
# links target with hx-target/hx-select. Kept here so the fragment guard and the
# templates agree on the one id.
PROFILE_CONTENT_ID = 'profContent'


def shell_base(request):
    """Which base template a profile-shell page should extend for THIS request.

    Phase 4 (HTMX): a tab click sends ``HX-Request`` and targets ``#profContent``.
    For that request we render only the content fragment — ``base_template`` points
    at ``profiles/_content_fragment.html``, so the child's ``profile_content`` block
    renders alone inside the same ``#profContent`` div htmx swaps, and the whole
    shell (header, tab strip, rail) is never built server-side just to be discarded.

    Every other request — a full page load, or a *boosted* nav that swaps
    ``#appContentCol`` and therefore needs the entire shell — gets the normal
    ``profiles/shell.html``. Guarding on the target id (not just ``HX-Request``) is
    what keeps boosted navigation to a profile page rendering the full shell.

    Views pass the result as ``base_template`` in the context; the child templates
    extend ``base_template|default:'profiles/shell.html'``.
    """
    hx = request.headers.get('HX-Request') == 'true'
    targets_content = request.headers.get('HX-Target') == PROFILE_CONTENT_ID
    if hx and targets_content:
        return 'profiles/_content_fragment.html'
    return 'profiles/shell.html'


# ---------------------------------------------------------------------------
# PERSON profile — same shell as a module profile.
# ---------------------------------------------------------------------------
PERSON_TABS = [
    ('feed', 'Feed', 'bi-card-text'),
    ('about', 'About', 'bi-info-circle'),
    ('modules', 'Subjects', 'bi-journal-bookmark'),
    ('progress', 'Progress', 'bi-graph-up'),
    ('documents', 'Documents', 'bi-folder2-open'),
    ('activity', 'Activity', 'bi-activity'),
]


def activity_for_user(user, limit=8):
    """That person's recent work → Activity panel.

    Read from their own marked attempts. This used to read the xAPI statement
    log; with the LRS gone, the attempts *are* the record — and they were always
    the more legible one, since a statement said "experienced <IRI>" where an
    attempt says "Scored 68% on Test 2".
    """
    items = []
    if user is None:
        return items
    try:
        from apps.assessments.models import AssessmentAttempt

        attempts = (AssessmentAttempt.objects
                    .filter(student=user)
                    .exclude(status='in_progress')
                    .select_related('assessment')
                    .order_by('-submitted_at', '-id')[:limit])
        for attempt in attempts:
            title = getattr(attempt.assessment, 'title', 'an assessment')
            if attempt.status == 'marked':
                total = attempt.assessment.total_marks or 0
                pct = round(float(attempt.score) / float(total) * 100) if total else None
                icon = 'bi-check-circle' if attempt.passed else 'bi-x-circle'
                text = f'Scored {pct}% on {title}' if pct is not None else f'Marked: {title}'
            else:
                icon, text = 'bi-pencil', f'Submitted {title}'
            items.append({'icon': icon, 'text': text,
                          'when': attempt.submitted_at or attempt.started_at})
    except Exception:  # pragma: no cover
        logger.exception('profiles: user activity lookup failed')
    return items


def person_context(request, person, tab='feed'):
    """Shell context for a Person profile.

    Visibility is layered:

    * ``is_self`` / staff → ``can_see_private``: contact details, DOB, grades and
      the Edit action.
    * everyone else falls back to the owner's :class:`UserSettings` — ``show_email``
      and ``show_activity`` — so members control what the rest of the hub sees.

    The hard gate (``profile_visibility`` = private / members-only) lives in the
    view, because it has to redirect.
    """
    user = getattr(person, 'user', None)
    viewer = request.user
    is_self = bool(user and viewer.is_authenticated and viewer.pk == user.pk)
    vp = getattr(viewer, 'profile', None)
    is_staff = bool(viewer.is_staff or viewer.is_superuser
                    or (vp and vp.user_type in ('admin', 'staff')))
    # An educator sees the details of the learners they actually teach — they mark
    # this person's work — but not those of learners in someone else's class.
    can_see_private = is_self or is_staff or _teaches(vp, person)

    prefs = _settings_for(user)
    show_email = can_see_private or bool(getattr(prefs, 'show_email', False))
    show_activity = can_see_private or bool(getattr(prefs, 'show_activity', True))
    allow_messages = bool(getattr(prefs, 'allow_messages', True))

    enrolled = list(person.selected_modules.all())
    teaching = list(person.taught_modules.all())
    modules = enrolled + teaching

    meta = [{'icon': 'bi-person-badge', 'text': person.get_user_type_display()}]
    if person.programme:
        meta.append({'icon': 'bi-journal-bookmark', 'text': str(person.programme)})
    if show_email and user and user.email:
        meta.append({'icon': 'bi-envelope', 'text': user.email})
    if can_see_private and person.phone:
        meta.append({'icon': 'bi-telephone', 'text': person.phone})
    if user:
        meta.append({'icon': 'bi-calendar2-plus', 'text': f'Joined {user.date_joined:%b %Y}'})

    if is_self:
        actions = [{'label': 'Edit profile', 'url': reverse('accounts:complete-profile'),
                    'icon': 'bi-pencil-fill', 'style': 'danger-soft'}]
    elif allow_messages and user:
        # chat_direct opens (or creates) the 1-to-1 group — and enforces the
        # student↔student connection gate itself.
        actions = [{'label': 'Message', 'url': reverse('communication:chat-direct', args=[user.pk]),
                    'icon': 'bi-chat-left-text-fill', 'style': 'primary'}]
    else:
        actions = []

    def url_for(key):
        return reverse('accounts:profile', args=[person.pk, key])

    ctx = {
        'person': person, 'is_self': is_self, 'can_see_private': can_see_private,
        'show_email': show_email, 'show_activity': show_activity,
        'profile': {
            'kind': 'person',
            'title': str(person),
            'subtitle': person.get_user_type_display(),
            'verified': person.onboarding_complete,
            'avatar': person.profile_picture.url if person.profile_picture else None,
            'meta': meta,
            'actions': actions,
        },
        'tabs': _tabs(PERSON_TABS, url_for, tab, {'modules': len(modules)}),
        'active_tab': tab,
        'activity_items': activity_for_user(user) if show_activity else [],
        'files': files_for(modules),
        'selected_modules': enrolled, 'taught_modules': teaching,
    }

    if tab == 'progress':
        ctx['grades'] = _grades_for(user) if can_see_private else []
    elif tab == 'documents':
        # A person's own uploads — their wall media (public) plus, only for the
        # person themselves or staff, files they shared in direct chats.
        ctx['documents'] = documents_for(user=user, include_private=can_see_private)
    elif tab == 'activity':
        ctx['activity'] = activity_for_user(user, limit=50) if show_activity else []
    elif tab == 'feed':
        # This person's wall. Only they can post to it.
        ctx.update(wall_for(request, author=user))
        ctx['can_post'] = is_self
    return ctx


def _teaches(viewer_person, person):
    """True if ``viewer_person`` is an educator of a module ``person`` is enrolled in."""
    if not viewer_person or viewer_person.pk == person.pk:
        return False
    try:
        return person.selected_modules.filter(
            pk__in=viewer_person.taught_modules.values_list('pk', flat=True)).exists()
    except Exception:  # pragma: no cover
        return False


def _settings_for(user):
    """The profile owner's :class:`UserSettings` (never raises)."""
    if user is None:
        return None
    try:
        from apps.accounts.models import UserSettings
        return UserSettings.for_user(user)
    except Exception:  # pragma: no cover
        return None


def _grades_for(user):
    if user is None:
        return []
    try:
        from apps.reports.models import Grade
        # order_by('-final_pct') clears Grade's default ordering, which starts at
        # ``module`` and would chain through ProgrammeModule → Course (Django then raises
        # "Infinite loop caused by ordering").
        return list(Grade.objects.filter(student=user)
                    .select_related('module').order_by('-final_pct'))
    except Exception:  # pragma: no cover
        logger.exception('profiles: grades lookup failed')
        return []


# ---------------------------------------------------------------------------
# SUBJECT profile
# ---------------------------------------------------------------------------
def module_context(request, module, tab='feed'):
    """Shell context + active-tab payload for a ProgrammeModule profile."""
    # ``for_role`` keeps each audience's copy of a lesson to itself — a learner
    # never sees the educator's version of the same topic, and vice versa.
    lessons = module.lessons.for_role(request.user).order_by('-created_at')
    assessments = module.assessments.order_by('-created_at')
    students = module.students.select_related('user').all()
    educators = module.educators.select_related('user').all()

    counts = {'lessons': lessons.count(), 'assessments': assessments.count(),
              'live': module.class_sessions.count()}

    def url_for(key):
        return reverse('learning:module-profile', args=[module.pk, key])

    ctx = {
        'module': module,
        'profile': {
            'kind': 'module',
            'title': module.name,
            'subtitle': ' · '.join(p for p in [module.code, str(module.programme) if module.programme_id else ''] if p),
            'verified': True,
            'avatar': None,
            'meta': [
                {'icon': 'bi-people', 'text': f'{students.count()} learner{"s" if students.count() != 1 else ""}'},
                {'icon': 'bi-person-badge', 'text': f'{educators.count()} educator{"s" if educators.count() != 1 else ""}'},
                {'icon': 'bi-journal-richtext', 'text': f'{counts["lessons"]} lessons'},
            ],
            'actions': [],
        },
        'tabs': _tabs(MODULE_TABS, url_for, tab, counts),
        'active_tab': tab,
        'activity_items': activity_for([module], user=request.user),
        'files': files_for([module]),
        'students': students, 'educators': educators,
    }
    ctx.update(_module_tab_payload(request, module, tab, lessons, assessments))
    return ctx


def _module_tab_payload(request, module, tab, lessons, assessments):
    data = {}
    if tab == 'lessons':
        data['lessons'] = lessons_with_progress(lessons[:50], request.user)
    elif tab == 'assessments':
        data['assessment_groups'] = group_by_time(
            assessments[:100], lambda a: a.available_to or a.available_from)
    elif tab == 'live':
        person = getattr(request.user, 'profile', None)
        data['can_host_live'] = bool(
            request.user.is_staff
            or (person and (person.user_type in ('admin', 'staff')
                            or module.educators.filter(pk=person.pk).exists())))
        data['live_sessions'] = module.class_sessions.select_related('meeting', 'created_by')[:50]
    elif tab == 'documents':
        data['documents'] = documents_for(modules=[module])
    elif tab == 'events':
        data['event_groups'] = group_by_time(_events_for([module]), lambda e: e.session_date)
    elif tab == 'reminders':
        data['reminders'] = _reminders_for(module)
    elif tab == 'activity':
        data['activity'] = activity_for([module], limit=50, user=request.user)
    elif tab == 'chat':
        data['chat_group'] = _chat_group_for(module)
    else:  # feed — the class wall (same component as a person's)
        data.update(wall_for(request, module=module))
    return data


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def _lessons_by_module(rows, modules):
    """Group decorated lesson rows under their module, modules in programme order.

    Returns ``[{'module': …, 'lessons': [...], 'done': n}]`` — only modules
    that actually have lessons, so an empty module does not clutter the page.
    """
    by_id = {}
    for lesson in rows:
        by_id.setdefault(lesson.module_id, []).append(lesson)
    groups = []
    for module in modules:
        items = by_id.pop(module.id, [])
        if items:
            groups.append({'module': module, 'lessons': items,
                           'done': sum(1 for l in items if l.pct >= 100)})
    # Anything whose module is not in this programme's list (shouldn't happen, but
    # never silently drop a lesson).
    for items in by_id.values():
        groups.append({'module': items[0].module, 'lessons': items,
                       'done': sum(1 for l in items if l.pct >= 100)})
    return groups


def _events_for(modules):
    try:
        from apps.communication.models import ClassSession
        return list(ClassSession.objects.filter(module__in=modules)
                    .select_related('module').order_by('-session_date')[:30])
    except Exception:  # pragma: no cover
        return []


def _reminders_for(module):
    try:
        from apps.tasks.models import Task
        return list(Task.objects.filter(module=module).order_by('-created_at')[:30])
    except Exception:  # pragma: no cover
        return []


def _chat_group_for(module):
    try:
        from apps.communication.models import ChatGroup
        return ChatGroup.objects.filter(module=module).first()
    except Exception:  # pragma: no cover
        return None
