"""The OneDrive filing cabinet: one folder per session, under a stable tree.

Teams drops a recording wherever it likes — ``Recordings/`` in the organiser's
own OneDrive, named after the meeting and the timestamp. That is fine for the
organiser and useless for everybody else: nobody can find last term's Financial
Reporting Test 2 review in a flat list of two hundred files.

So the pipeline builds a tree and moves things into it:

    <root>/<INSTITUTION>/<PROGRAMME>/<MODULE>/<YYYY-MM-DD Session title>/
        recording.mp4
        transcript.vtt
        summary.md
        thumbnail.jpg

Every function here is idempotent and returns ``None``/``''`` rather than
raising, because each one is a step in a state machine that will be retried.
Nothing is *deleted*: the worst case is a duplicate folder, never a lost class.
"""

import logging

from django.conf import settings

from . import graph

logger = logging.getLogger('apps')


def owner_upn_for(meeting):
    """Whose OneDrive holds this session's folder.

    A single configured drive keeps the whole archive in one place (and one
    backup, and one retention policy). Left blank, each session is filed in its
    own organiser's drive, which is where Teams put the recording anyway and so
    needs no cross-drive copy.
    """
    from apps.livesessions.models import LiveSessionSettings
    configured = (LiveSessionSettings.load().onedrive_owner_upn or '').strip()
    if configured:
        return configured
    return (meeting.organizer_upn or getattr(settings, 'MS_GRAPH_DEFAULT_ORGANIZER', '') or '').strip()


def ensure_session_folder(meeting):
    """Create (or find) this session's folder and return its details.

    Returns ``{'drive_id', 'folder_id', 'path', 'web_url', 'owner_upn'}``, or
    None if Graph is unavailable or the tree could not be built.
    """
    from apps.livesessions.models import LiveSessionSettings

    if not graph.is_configured():
        return None
    owner = owner_upn_for(meeting)
    if not owner:
        logger.warning('onedrive: no drive owner for %s — cannot file artifacts', meeting)
        return None

    drive_id = graph.get_drive_id(owner)
    if not drive_id:
        logger.error('onedrive: could not resolve the drive for %s', owner)
        return None

    conf = LiveSessionSettings.load()
    parts = [conf.onedrive_root.strip() or 'UCS Sessions'] + list(meeting.storage_path_parts)

    root = graph.get_item_by_path(drive_id, '')
    parent_id = (root or {}).get('id')
    if not parent_id:
        return None

    walked = []
    node = None
    for part in parts:
        node = graph.create_folder(drive_id, parent_id, part)
        if not node or not node.get('id'):
            logger.error('onedrive: could not create folder %r under %s', part, '/'.join(walked) or 'root')
            return None
        parent_id = node['id']
        walked.append(part)

    return {
        'drive_id': drive_id,
        'folder_id': parent_id,
        'path': '/'.join(walked),
        'web_url': (node or {}).get('webUrl', ''),
        'owner_upn': owner,
    }


def file_recording(meeting, folder, recording):
    """Move the Teams recording into the session folder; return the drive item.

    ``recording`` is one entry from ``graph.list_recordings``. Its content lives
    in the organiser's drive, so when the archive drive *is* the organiser's
    drive this is a metadata-only move — no bytes travel. When they differ, the
    file is copied server-side (still no bytes through this process), and the
    copy is asynchronous, so the caller polls for it on a later tick.
    """
    from apps.livesessions.models import LiveSessionSettings

    item_id, source_drive = _recording_item_ref(recording)
    if not item_id:
        return None

    target_name = f'{artifact_stem(meeting)}.mp4'
    same_drive = (not source_drive) or source_drive == folder['drive_id']
    keep_original = LiveSessionSettings.load().keep_teams_copy

    if same_drive and not keep_original:
        moved = graph.move_item(folder['drive_id'], item_id,
                                parent_item_id=folder['folder_id'], new_name=target_name)
        if moved:
            return moved
        logger.warning('onedrive: move failed for %s — falling back to a copy', meeting)

    accepted = graph.copy_item(source_drive or folder['drive_id'], item_id,
                               parent_item_id=folder['folder_id'], new_name=target_name)
    if not accepted:
        return None
    # Graph copies asynchronously: the item will not be in the folder yet. The
    # caller re-runs on the next tick and finds it by name.
    return find_child(folder['drive_id'], folder['folder_id'], target_name)


def ensure_subfolder(folder, name):
    """Ensure a named subfolder under a resolved session folder; return a folder dict.

    Used to drop a session's artifacts into the week's ``Recordings`` /
    ``Session summaries`` buckets (the tree ``provision_onedrive`` builds). Returns
    None on failure so the caller can fall back to the base folder.
    """
    if not folder:
        return None
    node = graph.create_folder(folder['drive_id'], folder['folder_id'], name)
    if not node or not node.get('id'):
        return None
    return {
        'drive_id': folder['drive_id'],
        'folder_id': node['id'],
        'path': f"{folder['path']}/{name}",
        'web_url': node.get('webUrl', ''),
        'owner_upn': folder['owner_upn'],
    }


def find_child(drive_id, folder_id, name):
    """The child of ``folder_id`` called ``name``, or None."""
    for child in graph.list_children(drive_id, folder_id):
        if child.get('name') == name:
            return child
    return None


def put_text(folder, name, text, content_type='text/plain'):
    """Write a small text file into the session folder. Returns the item or None."""
    if not text:
        return None
    return graph.upload_small_file(folder['drive_id'], folder['folder_id'], name, text, content_type)


def put_bytes(folder, name, blob, content_type='application/octet-stream'):
    if not blob:
        return None
    return graph.upload_small_file(folder['drive_id'], folder['folder_id'], name, blob, content_type)


def anonymous_link(folder, item_id):
    """A view link a student with no Microsoft account can open, or ''."""
    if not item_id:
        return ''
    return graph.create_share_link(folder['drive_id'], item_id, link_type='view', scope='anonymous')


def _recording_item_ref(recording):
    """``(item_id, drive_id)`` for a Graph ``callRecording``.

    Graph reports the recording's location inconsistently between the beta and
    v1.0 shapes, so this checks each known spelling rather than assuming one.
    """
    if not recording:
        return None, None
    ref = recording.get('driveItem') or recording.get('recordingDriveItem') or {}
    item_id = ref.get('id') or recording.get('driveItemId') or ''
    drive_id = (ref.get('parentReference') or {}).get('driveId') or recording.get('driveId') or ''
    return (item_id or None), (drive_id or None)


def artifact_stem(meeting):
    """The base filename every artifact of this session shares.

    ``2026-03-04 Deferred tax workshop`` → the recording, the transcript, the
    summary, the pack and the thumbnail all hang off it with a suffix, so the
    folder sorts sensibly and a file dragged out of it still says what it is.
    Public because the livesessions pipeline names its own uploads with it.
    """
    from apps.communication.models import _safe_folder_name
    from django.utils import timezone as tz
    when = meeting.scheduled_start or meeting.created_at or tz.now()
    return _safe_folder_name(f'{tz.localtime(when):%Y-%m-%d} {meeting.title}', limit=100)
