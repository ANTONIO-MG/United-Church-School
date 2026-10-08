"""Shared builders for the two seed scripts.

``.03_admin.py`` (the clean base install) and ``.04_demo_seed.py``
(the populated demonstration) both need to do the same things: turn a written
lesson spec into real ``Lesson``/``LessonSection``/``LessonBlock`` rows, verify
an account's e-mail, give a person a face, and compose a welcome notification.
Keeping that here means the two scripts stay short and can never drift apart.

A **lesson spec** is a plain dict::

    {
      'title': 'Finding your way around',
      'subtitle': 'Where everything lives, and how to get back to it.',
      'minutes': 12,
      'roles': ['student'],            # who may see it ([] = everyone)
      'intro': [ ...blocks... ],       # rendered above the tear-drops
      'sections': [
        {'title': 'The menu', 'summary': '…', 'type': 'reading',
         'minutes': 4, 'lock': False, 'open': True, 'blocks': [ ...blocks... ]},
      ],
      'attachments': [('Quick reference', 'text/plain', b'...')],
    }

A **block** is a tuple whose first item names the kind — see :func:`add_blocks`.
"""

from __future__ import annotations

from django.core.files.base import ContentFile
from django.utils import timezone

from core import seed_media


# ---------------------------------------------------------------------------
# accounts
# ---------------------------------------------------------------------------
def verify_email(user):
    """Mark ``user``'s address verified + primary so they can sign in at once.

    The platform gates login on a verified allauth ``EmailAddress``; a
    freshly-created user has none. No-op when allauth is absent or the user has
    no e-mail.
    """
    if not user or not getattr(user, 'email', ''):
        return False
    try:
        from allauth.account.models import EmailAddress
    except Exception:  # pragma: no cover - allauth optional
        return False
    address = EmailAddress.objects.filter(user=user, email__iexact=user.email).first()
    if address is None:
        EmailAddress.objects.create(user=user, email=user.email, verified=True, primary=True)
    else:
        address.verified = True
        address.primary = True
        address.save(update_fields=['verified', 'primary'])
    EmailAddress.objects.filter(user=user).exclude(email__iexact=user.email).update(primary=False)
    return True


def give_face(person, pool, key=None):
    """Assign a profile picture from ``pool`` (media-relative paths).

    The file is already inside ``MEDIA_ROOT``, so the field only needs its path
    — no re-upload, no duplicate bytes on disk.
    """
    if not pool or person is None:
        return False
    if person.profile_picture and str(person.profile_picture):
        return False
    chosen = seed_media.stable_pick(pool, key or person.pk or person.user_id)
    if not chosen:
        return False
    person.profile_picture = chosen
    person.save(update_fields=['profile_picture'])
    return True


# ---------------------------------------------------------------------------
# lessons
# ---------------------------------------------------------------------------
def add_blocks(lesson, blocks, section=None, start_order=0):
    """Create ``LessonBlock`` rows from a list of block tuples.

    Supported shapes::

        ('heading', level, 'text')
        ('text', '<p>html</p>')
        ('callout', 'info|tip|warning|danger', '<p>html</p>')
        ('image', 'media/relative/path.png', 'caption', 'alt text')
        ('video', 'https://youtu.be/…', 'caption', minutes)
        ('table', 'caption', [headers], [[row cells], …])
        ('file', 'Title', 'description')          # attach media separately
        ('embed', 'https://…', 'Title', height)
        ('reference', 'text', 'authors', 'year', 'url')
        ('divider',)

    Returns the next free ``order``.
    """
    from apps.learning.models import LessonBlock

    order = start_order
    for raw in blocks or []:
        kind = raw[0]
        data, block_type, media_rel = {}, None, ''

        if kind == 'heading':
            block_type, data = LessonBlock.TYPE_HEADING, {'text': raw[2], 'level': raw[1]}
        elif kind == 'text':
            block_type, data = LessonBlock.TYPE_TEXT, {'html': raw[1]}
        elif kind == 'callout':
            block_type, data = LessonBlock.TYPE_CALLOUT, {'variant': raw[1], 'html': raw[2]}
        elif kind == 'image':
            block_type = LessonBlock.TYPE_IMAGE
            media_rel = raw[1]
            data = {'url': seed_media.media_url(raw[1]),
                    'caption': raw[2] if len(raw) > 2 else '',
                    'alt': raw[3] if len(raw) > 3 else (raw[2] if len(raw) > 2 else '')}
        elif kind == 'video':
            block_type = LessonBlock.TYPE_VIDEO
            url = raw[1]
            provider = 'youtube' if ('youtu' in url) else ('vimeo' if 'vimeo' in url else 'url')
            data = {'url': url, 'provider': provider,
                    'caption': raw[2] if len(raw) > 2 else '',
                    'seconds': (raw[3] * 60) if len(raw) > 3 else 0}
        elif kind == 'table':
            block_type = LessonBlock.TYPE_TABLE
            data = {'caption': raw[1], 'has_header': True, 'headers': raw[2], 'rows': raw[3]}
        elif kind == 'file':
            block_type = LessonBlock.TYPE_FILE
            data = {'title': raw[1], 'description': raw[2] if len(raw) > 2 else ''}
        elif kind == 'embed':
            block_type = LessonBlock.TYPE_EMBED
            data = {'url': raw[1], 'title': raw[2] if len(raw) > 2 else '',
                    'height': raw[3] if len(raw) > 3 else 480, 'mode': 'iframe'}
        elif kind == 'reference':
            block_type = LessonBlock.TYPE_REFERENCE
            data = {'text': raw[1], 'authors': raw[2] if len(raw) > 2 else '',
                    'year': raw[3] if len(raw) > 3 else '', 'url': raw[4] if len(raw) > 4 else ''}
        elif kind == 'divider':
            block_type = LessonBlock.TYPE_DIVIDER
        else:
            continue

        block = LessonBlock.objects.create(
            lesson=lesson, section=section, block_type=block_type, order=order, data=data)
        # An image block points at a file already inside MEDIA_ROOT; setting the
        # field keeps ``media_url`` working even if MEDIA_URL later changes.
        if media_rel and block_type == LessonBlock.TYPE_IMAGE:
            block.media.name = media_rel
            block.save(update_fields=['media'])
        order += 1
    return order


def build_lesson(spec, *, module=None, author=None, status='published',
                 visibility='module', cover=''):
    """Create one fully-authored lesson (sections, blocks, attachments) from a spec.

    Idempotent on ``(module, title)`` — re-running a seed updates the shell
    rather than piling up duplicates. ``module`` may be None for material that
    belongs to no syllabus (the onboarding guide).
    """
    from apps.learning.models import Lesson, LessonResource, LessonSection

    lesson, created = Lesson.objects.get_or_create(
        module=module, title=spec['title'],
        defaults={
            'subtitle': spec.get('subtitle', ''),
            'status': status,
            'visibility': visibility,
            'estimated_minutes': spec.get('minutes', 15),
            'target_roles': spec.get('roles', []),
            'created_by': author,
            'author_name': (author.get_full_name() or author.get_username()) if author else '',
            'author_role': spec.get('author_role', ''),
            'author_bio': spec.get('author_bio', ''),
            'references': spec.get('references', []),
        },
    )
    if not created and lesson.blocks.exists():
        return lesson  # already built — leave the author's edits alone

    lesson.subtitle = spec.get('subtitle', '')
    lesson.status = status
    lesson.visibility = visibility
    lesson.estimated_minutes = spec.get('minutes', 15)
    lesson.target_roles = spec.get('roles', [])
    lesson.references = spec.get('references', [])
    if cover:
        lesson.cover_image.name = cover
    lesson.save()

    order = add_blocks(lesson, spec.get('intro'), section=None, start_order=0)

    for index, raw in enumerate(spec.get('sections', [])):
        section = LessonSection.objects.create(
            lesson=lesson, order=index,
            title=raw['title'],
            summary=raw.get('summary', ''),
            section_type=raw.get('type', LessonSection.TYPE_AUTO),
            duration_minutes=raw.get('minutes', 0),
            is_required=raw.get('required', True),
            requires_previous=raw.get('lock', False),
            open_by_default=raw.get('open', index == 0),
        )
        order = add_blocks(lesson, raw.get('blocks'), section=section, start_order=order)

    for title, content_type, payload in spec.get('attachments', []):
        if lesson.resources.filter(title=title).exists():
            continue
        suffix = {'text/plain': '.txt', 'text/markdown': '.md', 'text/csv': '.csv'}.get(content_type, '.txt')
        resource = LessonResource(lesson=lesson, kind='text', title=title,
                                  order=lesson.resources.count())
        resource.file.save(f"{_slug(title)}{suffix}",
                           ContentFile(payload if isinstance(payload, bytes) else payload.encode()),
                           save=False)
        resource.save()

    return lesson


def _slug(text):
    from django.utils.text import slugify
    return slugify(text)[:60] or 'file'


# ---------------------------------------------------------------------------
# notifications
# ---------------------------------------------------------------------------
def send_welcome(user, *, title, summary, body_html, level='success', url='/myhub/', actor=None):
    """Send one rich, long-form welcome notification (rendered as a reading page)."""
    from apps.communication.models import Notification

    if Notification.objects.filter(recipient=user, verb='welcome').exists():
        return None
    return Notification.objects.create(
        recipient=user, actor=actor, verb='welcome',
        title=title, summary=summary, body=body_html,
        body_format=Notification.FORMAT_HTML,
        level=level, url=url, created_at=timezone.now(),
    )
