"""The archive park — where a closed account goes, and how it comes back.

Closing an account is deliberately two-stage, because "delete my account" and
"I've changed my mind" arrive in that order more often than anyone expects:

    close  →  30-day grace (deactivated, reversible in one click)  →  purge

**Grace.** The user row is still there, just ``is_active=False`` with
``UserSettings.is_closing`` set. An administrator reverses it from
``accounts:closed-accounts`` and nothing was lost, because nothing was moved.

**Purge.** ``manage.py purge_closed_accounts`` runs after the 30 days and does
three things in order:

1. **Park it.** Everything that belongs to the account — the user row, the
   profile, settings, consent, the study calendar, and every row that would be
   destroyed by the cascade — is serialised into
   ``backups/archived_accounts/<username>-<id>-<date>/``, together with copies of
   their uploaded files. That directory is the archive park: it is off the
   running database entirely, and it is the only copy left.
2. **Attribute what stays.** Rows that are *someone else's* record of an
   interaction — chat messages, announcements, comments — are not the closing
   user's to delete; a thread with half its bubbles removed rewrites the other
   participant's history. Those FKs are ``SET_NULL``, so they survive the delete
   with no author and render as :data:`~core.utils.DISCONTINUED_USER`.
3. **Delete it.** The live user row goes, and the cascade takes their own content
   with it. From then on the running server holds nothing about them.

**Restore.** :func:`restore_archive` reads a park directory back: it recreates
the user (with an unusable password, so they must reset it), their profile and
settings, and then re-inserts the parked content rows. What cannot come back are
the ``SET_NULL`` links that were dropped in step 2 — the messages are still
there, but they stay attributed to a discontinued account rather than silently
re-acquiring an author.
"""

import json
import logging
import shutil
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import serializers
from django.db import transaction
from django.utils import timezone

logger = logging.getLogger('apps')

#: Models never worth parking: session-ish, log-ish or derived rows that would
#: bloat the archive and mean nothing on the way back.
SKIP_MODELS = {
    'admin.logentry',
    'sessions.session',
    'authtoken.token',
    'account.emailconfirmation',
    'socialaccount.socialtoken',
    'diagnostics.errorevent',
}


def park_root():
    """The archive park directory (created on demand)."""
    return Path(settings.BASE_DIR) / 'backups' / 'archived_accounts'


def _iso(value):
    return value.isoformat() if value else None


# ---------------------------------------------------------------------------
# Collecting
# ---------------------------------------------------------------------------
def owned_querysets(user):
    """Every queryset of rows the cascade would destroy along with ``user``.

    Walked off the model metadata rather than hand-listed, so a model added next
    year is archived without anybody remembering to add it here. Relations whose
    ``on_delete`` is not a cascade are skipped: those rows outlive the user by
    design (that is the "discontinued user" case), so they are not the closing
    account's data to take away.
    """
    from django.db.models import CASCADE

    User = get_user_model()
    out = []
    for relation in User._meta.related_objects:
        field = relation.field
        if getattr(field, 'remote_field', None) is None:
            continue
        if field.remote_field.on_delete is not CASCADE:
            continue
        model = relation.related_model
        label = model._meta.label_lower
        if label in SKIP_MODELS:
            continue
        try:
            rows = model._default_manager.filter(**{field.name: user})
        except Exception:                                # pragma: no cover
            logger.exception('archive: could not read %s', label)
            continue
        out.append((label, rows))
    return out


def snapshot(user):
    """A JSON-serialisable summary of the account (the human-readable half)."""
    person = getattr(user, 'profile', None)
    us = getattr(user, 'account_settings', None)

    data = {
        'schema_version': 2,
        'archived_at': _iso(timezone.now()),
        'user': {
            'id': user.id,
            'username': user.get_username(),
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_active': user.is_active,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'date_joined': _iso(user.date_joined),
            'last_login': _iso(user.last_login),
        },
        'profile': None,
        'settings': None,
        'programme': None,
        'modules': [],
    }

    if person is not None:
        data['profile'] = {
            'first_name': person.first_name,
            'last_name': person.last_name,
            'gender': person.gender,
            'date_of_birth': _iso(person.date_of_birth),
            'phone': person.phone,
            'user_type': person.user_type,
            'profile_status': person.profile_status,
            'registered': person.registered,
        }
        try:
            data['modules'] = [
                enrolment.programme_module.label
                for enrolment in person.module_enrolments.select_related(
                    'programme_module__module', 'programme_module__programme')
            ]
        except Exception:                                # pragma: no cover
            data['modules'] = []

    if us is not None:
        data['settings'] = {
            'profile_visibility': us.profile_visibility,
            'show_email': us.show_email,
            'show_activity': us.show_activity,
            'allow_messages': us.allow_messages,
            'theme': us.theme,
            'language': us.language,
            'closed_at': _iso(us.closed_at),
            'purge_at': _iso(us.purge_at),
        }
    return data


def _copy_files(user, directory):
    """Copy the account's uploaded files into the park, preserving their
    relative media path so a restore can point at them again."""
    from django.db.models import FileField

    copied = []
    media_root = Path(settings.MEDIA_ROOT)
    targets = [user] + [obj for obj in (getattr(user, 'profile', None),) if obj is not None]
    for obj in targets:
        for field in obj._meta.get_fields():
            if not isinstance(field, FileField):
                continue
            value = getattr(obj, field.name, None)
            if not value:
                continue
            try:
                source = Path(value.path)
            except (NotImplementedError, ValueError):    # remote storage
                continue
            if not source.exists():
                continue
            try:
                relative = source.relative_to(media_root)
            except ValueError:
                relative = Path(source.name)
            destination = directory / 'media' / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            copied.append(str(relative))
    return copied


# ---------------------------------------------------------------------------
# Parking + purging
# ---------------------------------------------------------------------------
def park_account(user):
    """Write everything about ``user`` into the archive park.

    Returns ``(directory, summary_dict, content_row_count)``. Does **not** delete
    anything — the caller decides when the live rows go.
    """
    stamp = timezone.now()
    name = f'{user.get_username() or user.pk}-{user.pk}-{stamp:%Y%m%d%H%M%S}'
    directory = park_root() / name
    directory.mkdir(parents=True, exist_ok=True)

    summary = snapshot(user)

    # The restorable half: real serialised rows, natural-key free so primary
    # keys (and therefore the links between the rows) survive the round trip.
    payload, count = [], 0
    payload.append(serializers.serialize('python', [user]))
    for label, rows in owned_querysets(user):
        chunk = list(rows)
        if not chunk:
            continue
        count += len(chunk)
        payload.append(serializers.serialize('python', chunk))

    summary['files'] = _copy_files(user, directory)
    summary['content_rows'] = count

    (directory / 'account.json').write_text(
        json.dumps(summary, indent=2, ensure_ascii=False, default=str), encoding='utf-8')
    (directory / 'content.json').write_text(
        json.dumps([row for group in payload for row in group],
                   indent=2, ensure_ascii=False, default=str), encoding='utf-8')
    (directory / 'README.txt').write_text(
        'Archived account.\n\n'
        'account.json  — human-readable summary of who this was.\n'
        'content.json  — every database row that belonged to them, restorable\n'
        '                via the admin "Closed accounts" page.\n'
        'media/        — their uploaded files, at their original media paths.\n\n'
        'Messages and other rows they merely took part in are NOT here: they\n'
        'stayed on the live system, attributed to a discontinued user.\n',
        encoding='utf-8')

    return directory, summary, count


def purge_account(user):
    """Park the account, then delete it. Returns the created
    :class:`~apps.accounts.models.AccountArchive` row."""
    from . import models

    directory, summary, count = park_account(user)
    user_pk = user.pk
    username = user.get_username()
    email = user.email or ''
    User = get_user_model()

    with transaction.atomic():
        archive = models.AccountArchive.objects.create(
            original_user_id=user_pk,
            username=username,
            email=email,
            data=summary,
            file_path=str(directory / 'account.json'),
            archive_dir=str(directory),
            content_rows=count,
        )
        # Delete via the queryset (not ``user.delete()``) so the audit
        # ``post_delete`` signal receives a freshly-loaded User with no cached
        # profile — otherwise it would try to log a reference to the Person the
        # cascade is deleting in the same transaction.
        User.objects.filter(pk=user_pk).delete()
    return archive


# ---------------------------------------------------------------------------
# Coming back
# ---------------------------------------------------------------------------
def restore_archive(archive):
    """Rebuild a purged account from its park directory.

    Returns the restored user. The password is left unusable: whoever asks for
    the account back proves it is theirs through the normal password-reset
    e-mail, not by an administrator handing them a login.
    """
    from . import models

    directory = Path(archive.archive_dir or '').expanduser()
    content = directory / 'content.json'
    if not content.exists():
        raise FileNotFoundError(f'archive content missing at {content}')

    rows = json.loads(content.read_text(encoding='utf-8'))
    media_root = Path(settings.MEDIA_ROOT)
    user_label = get_user_model()._meta.label_lower

    with transaction.atomic():
        objects = list(serializers.deserialize('python', rows, ignorenonexistent=True))
        user_objects = [o for o in objects if o.object._meta.label_lower == user_label]
        if not user_objects:
            raise ValueError('archive holds no user row')

        # The user has to land first — everything else points at it. The
        # deserializer saves ``raw``, which the profile-creating and audit
        # signals skip, so no stand-in Person is made to collide with the
        # archived one on its way in.
        restored_user = user_objects[0].object
        user_objects[0].save()

        for obj in objects:
            if obj is user_objects[0]:
                continue
            obj.save()

        restored_user.is_active = True
        restored_user.set_unusable_password()
        restored_user.save()

        # An archive written before the profile existed would leave the account
        # with no Person, and every page that renders one would 500.
        models.Person.objects.get_or_create(user=restored_user)

        # The account is live again, so it is no longer closing.
        user_settings = models.UserSettings.for_user(restored_user)
        user_settings.cancel_closing()

    # Put the files back where the restored rows expect to find them.
    parked_media = directory / 'media'
    if parked_media.exists():
        for source in parked_media.rglob('*'):
            if not source.is_file():
                continue
            destination = media_root / source.relative_to(parked_media)
            destination.parent.mkdir(parents=True, exist_ok=True)
            if not destination.exists():
                shutil.copy2(source, destination)

    archive.restored_at = timezone.now()
    archive.save(update_fields=['restored_at'])
    return restored_user
