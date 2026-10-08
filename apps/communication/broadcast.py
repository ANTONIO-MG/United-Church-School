"""Broadcast notifications — who a message reaches, and getting it there.

Two callers share this module:

* the staff composer (:class:`~apps.communication.models.Announcement`), where a
  person picks institutions, programmes, cohorts, modules and named people; and
* the automatic notifications (new material, a lesson going live, a new video),
  which ask the same question — "everyone on this module" — in code.

Keeping one resolver means "the students and educators of FAC188" means the same
thing whether staff typed it or the system worked it out.

**What a scope covers.** An institution, programme or cohort covers the students
enrolled in it and the educators who teach one of its modules. A module covers
its enrolled students — paid, on trial or not yet paid; being told about a class
is not the same as being able to open it — and its educators. Admin and staff are
only reached when picked by role or by name: a module notice is for the module.
"""

import logging
import re
import threading

from django.contrib.auth import get_user_model
from django.db import close_old_connections, transaction
from django.db.models import Count, Q
from django.utils import timezone

from core.errors import report

logger = logging.getLogger('apps')

#: A send this small happens inside the request, so the sender sees the final
#: count straight away. Anything bigger goes to a background thread — one
#: branded e-mail is a fraction of a second, and a request must not wait on 500.
INLINE_SEND_LIMIT = 40


# ---------------------------------------------------------------------------
# Audience
# ---------------------------------------------------------------------------
def _ids(items):
    return [getattr(i, 'pk', i) for i in (items or [])]


def audience_users(*, everyone=False, institutions=(), programmes=(), cohorts=(), modules=(),
                   users=(), roles=(), include_parents=False):
    """Every active ``User`` the described audience reaches, de-duplicated.

    ``roles`` narrows the scoped members to those ``Person.user_type`` values
    (empty means every role). People in ``users`` are always included — naming
    someone is deliberate. Asking for the ``parent`` role on a scoped audience
    means "the parents of the students in it", since parents enrol in nothing.
    """
    from apps.accounts.models import ParentLink

    User = get_user_model()
    active = User.objects.filter(is_active=True)
    institutions, programmes = _ids(institutions), _ids(programmes)
    cohorts, modules, users = _ids(cohorts), _ids(modules), _ids(users)
    roles = [r for r in (roles or []) if r]

    if everyone:
        scope = Q(pk__isnull=False)
    else:
        scope = Q(pk__in=[])
        if institutions:
            scope |= Q(profile__programme_enrolments__programme__institution__in=institutions) | \
                     Q(profile__taught_modules__programme__institution__in=institutions)
        if programmes:
            scope |= Q(profile__programme_enrolments__programme__in=programmes) | \
                     Q(profile__taught_modules__programme__in=programmes)
        if cohorts:
            scope |= Q(profile__programme_enrolments__cohort__in=cohorts) | \
                     Q(profile__taught_modules__programme__cohorts__in=cohorts)
        if modules:
            scope |= Q(profile__module_enrolments__programme_module__in=modules) | \
                     Q(profile__taught_modules__in=modules)
    scoped = active.filter(scope)

    picked = scoped
    if roles:
        role_q = Q(profile__user_type__in=roles)
        if 'admin' in roles:
            # role_of_user treats a Django superuser / is_staff login as admin,
            # including the ones created on the shell without a profile.
            role_q |= Q(is_superuser=True) | Q(is_staff=True, profile__isnull=True)
        picked = scoped.filter(role_q)

    wanted = Q(pk__in=picked.values('pk'))
    if users:
        wanted |= Q(pk__in=users)
    if include_parents or ('parent' in roles and not everyone):
        students = scoped.filter(profile__user_type='student').values('pk')
        wanted |= Q(pk__in=ParentLink.objects.filter(student__in=students).values('parent'))
    return active.filter(wanted).distinct()


def recipients_for_announcement(announcement):
    """The users ``announcement`` reaches, including its legacy audience kinds."""
    from .models import Announcement as A

    a = announcement
    if a.audience == A.AUDIENCE_USER_TYPE:
        return audience_users(everyone=True, roles=[a.user_type] if a.user_type else [])
    if a.audience == A.AUDIENCE_MODULES:
        return audience_users(modules=a.modules.all(), roles=a.roles,
                              include_parents=a.include_parents)
    if a.audience == A.AUDIENCE_USERS:
        return audience_users(users=a.users.all())
    if a.audience == A.AUDIENCE_ALL:
        return audience_users(everyone=True, roles=a.roles, users=a.users.all())
    return audience_users(
        institutions=a.institutions.all(), programmes=a.programmes.all(),
        cohorts=a.cohorts.all(), modules=a.modules.all(), users=a.users.all(),
        roles=a.roles, include_parents=a.include_parents)


def person_label(user):
    """A person's name as the pickers show it — profile name first, then the login's."""
    from core.utils import display_name
    person = getattr(user, 'profile', None)
    full = ' '.join(filter(None, [getattr(person, 'first_name', ''), getattr(person, 'last_name', '')])).strip()
    return full or display_name(user)


def audience_summary(users_qs, sample=8):
    """Totals by role plus a few names, for the composer's live preview."""
    by_role = {row['profile__user_type'] or 'admin': row['n']
               for row in users_qs.order_by().values('profile__user_type').annotate(n=Count('pk', distinct=True))}
    people = []
    for u in users_qs.select_related('profile').order_by('first_name', 'last_name', 'pk')[:sample]:
        people.append(person_label(u))
    return {'total': sum(by_role.values()), 'by_role': by_role, 'sample': people}


# ---------------------------------------------------------------------------
# Video links
# ---------------------------------------------------------------------------
_YOUTUBE = re.compile(
    r'(?:youtube(?:-nocookie)?\.com/(?:watch\?(?:.*&)?v=|embed/|shorts/|live/|v/)|youtu\.be/)'
    r'([A-Za-z0-9_-]{11})')
_VIMEO = re.compile(r'vimeo\.com/(?:video/)?(\d+)')


def embed_url_for(url):
    """A privacy-friendly player URL for a YouTube / Vimeo link, else ''."""
    if not url:
        return ''
    m = _YOUTUBE.search(url)
    if m:
        return f'https://www.youtube-nocookie.com/embed/{m.group(1)}?rel=0'
    m = _VIMEO.search(url)
    if m:
        return f'https://player.vimeo.com/video/{m.group(1)}'
    return ''


# ---------------------------------------------------------------------------
# Sending
# ---------------------------------------------------------------------------
def send(announcement):
    """Deliver ``announcement`` once: notifications, then e-mail copies.

    Claims the row by flipping its status to ``sending`` in one UPDATE, so a
    double-click, the scheduler and a background thread can all call this and
    only one of them sends. Returns the number of people it reached.
    """
    from .models import Announcement, Notification, NotificationPreference
    from .services import notify

    claimed = Announcement.objects.filter(
        pk=announcement.pk,
        status__in=(Announcement.STATUS_DRAFT, Announcement.STATUS_SCHEDULED, Announcement.STATUS_FAILED),
    ).update(status=Announcement.STATUS_SENDING, failure='')
    if not claimed:
        announcement.refresh_from_db()
        return announcement.recipient_count
    announcement.refresh_from_db()

    category = None if announcement.is_important else 'announcements'
    # A retry after a failure carries on where it stopped — nobody is told twice.
    already = Notification.objects.filter(announcement=announcement)
    reached_before = already.count()
    delivered = []
    try:
        people = recipients_for_announcement(announcement).exclude(pk__in=already.values('recipient'))
        for user in people.select_related('profile').iterator():
            note = notify(
                user,
                actor=announcement.sender,
                verb='sent an announcement',
                title=announcement.title,
                body=announcement.body,
                level=announcement.level,
                url=announcement.url,
                announcement=announcement,
                email=False,        # e-mailed below with the attachments and the video
                category=category,
            )
            if note is not None:
                delivered.append(note)

        if announcement.send_email:
            from .emails import announcement_email_files, email_announcement_copy
            files = announcement_email_files(announcement)
            for note in delivered:
                try:
                    if not NotificationPreference.for_user(note.recipient).allows_email(category):
                        continue
                    if email_announcement_copy(announcement, note, files):
                        note.emailed = True
                        note.save(update_fields=['emailed'])
                except Exception as exc:   # pragma: no cover - one bad address never stops the rest
                    logger.exception('broadcast: e-mail failed for notification #%s', note.pk)
                    report('NOTF-5002', exc, context={'announcement': announcement.pk,
                                                      'notification': note.pk})
    except Exception as exc:
        logger.exception('broadcast: announcement #%s failed', announcement.pk)
        report('NOTF-9002', exc, context={'announcement': announcement.pk,
                                          'reached_so_far': reached_before + len(delivered)})
        Announcement.objects.filter(pk=announcement.pk).update(
            status=Announcement.STATUS_FAILED, failure=str(exc)[:2000],
            recipient_count=reached_before + len(delivered))
        announcement.refresh_from_db()
        return announcement.recipient_count

    Announcement.objects.filter(pk=announcement.pk).update(
        status=Announcement.STATUS_SENT, sent_at=timezone.now(),
        recipient_count=reached_before + len(delivered))
    announcement.refresh_from_db()
    return announcement.recipient_count


def dispatch(announcement):
    """Send now: inline for a small audience, otherwise on a background thread.

    Returns ``(sent_inline, count)`` — ``count`` is final when inline, and the
    estimated audience size when it was handed to the thread.
    """
    estimate = recipients_for_announcement(announcement).count()
    if estimate <= INLINE_SEND_LIMIT:
        return True, send(announcement)

    pk = announcement.pk

    def _run():
        try:
            from .models import Announcement
            send(Announcement.objects.get(pk=pk))
        except Exception as exc:   # pragma: no cover
            logger.exception('broadcast: background send of #%s crashed', pk)
            report('NOTF-9003', exc, context={'announcement': pk})
        finally:
            close_old_connections()

    transaction.on_commit(lambda: threading.Thread(target=_run, daemon=True,
                                                   name=f'broadcast-{pk}').start())
    return False, estimate


def send_due():
    """Scheduler job: send every scheduled announcement whose time has come."""
    from .models import Announcement

    due = Announcement.objects.filter(status=Announcement.STATUS_SCHEDULED,
                                      scheduled_for__lte=timezone.now()).order_by('scheduled_for')
    sent = []
    for announcement in due:
        sent.append(f'#{announcement.pk}→{send(announcement)}')
    return f'sent {len(sent)} scheduled broadcast(s) {" ".join(sent)}'.strip()


def read_stats(announcement):
    """How many of its notifications were read / e-mailed, for the sender's view."""
    from .models import Notification

    agg = Notification.objects.filter(announcement=announcement).aggregate(
        total=Count('pk'), read=Count('pk', filter=Q(is_read=True)),
        emailed=Count('pk', filter=Q(emailed=True)), whatsapped=Count('pk', filter=Q(whatsapped=True)))
    total = agg['total'] or 0
    agg['read_pct'] = round(100 * agg['read'] / total) if total else 0
    return agg


def scheduler_is_running():
    """True when the background scheduler has ticked recently.

    The quick tick runs every 15 minutes from 06:00 to 22:45 SAST, so outside
    those hours silence is expected; inside them, 20 minutes of silence means the
    timers have stopped, which is logged as SCHD-7001 for the error log.
    """
    try:
        from apps.scheduler.models import JobRun
        now = timezone.now()
        if JobRun.objects.filter(last_started_at__gte=now - timezone.timedelta(minutes=20)).exists():
            return True
        sast_hour = (now + timezone.timedelta(hours=2)).hour
        if 6 <= sast_hour <= 22:
            from core.errors import note
            note('SCHD-7001')
            return False
        return True     # overnight: nothing is meant to be running
    except Exception:   # pragma: no cover
        return False
