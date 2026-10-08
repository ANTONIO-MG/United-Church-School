"""Thin Microsoft Graph client for the Teams live classroom.

App-only (client-credentials) auth: the LMS acts on behalf of licensed educators
without them signing in — so meetings are created straight from the LMS. Every
call is best-effort and returns ``None``/``[]`` rather than raising into a view;
the whole thing is **dormant** until ``MS_GRAPH_*`` is configured.

Requires an Entra app registration with *application* Graph permissions and a
Teams *application access policy* (see docs/TEAMS_INTEGRATION.md). ``msal`` is an
optional dependency — absent, the client simply reports "not configured".
"""

import logging
import time

from django.conf import settings

logger = logging.getLogger('apps')

_GRAPH_SCOPE = ['https://graph.microsoft.com/.default']
_token_cache = {'value': None, 'expires_at': 0}


# ---------------------------------------------------------------------------
# configuration / availability
# ---------------------------------------------------------------------------
def is_configured():
    """True only when Teams is switched on AND all Graph credentials are present."""
    return bool(
        getattr(settings, 'MS_TEAMS_ENABLED', False)
        and settings.MS_GRAPH_TENANT_ID
        and settings.MS_GRAPH_CLIENT_ID
        and settings.MS_GRAPH_CLIENT_SECRET
    )


def _msal_app():
    try:
        import msal
    except Exception:  # pragma: no cover - optional dependency
        logger.warning('msteams: msal is not installed; Teams integration is off')
        return None
    authority = f"{settings.MS_GRAPH_AUTHORITY.rstrip('/')}/{settings.MS_GRAPH_TENANT_ID}"
    return msal.ConfidentialClientApplication(
        client_id=settings.MS_GRAPH_CLIENT_ID,
        client_credential=settings.MS_GRAPH_CLIENT_SECRET,
        authority=authority,
    )


def _get_token():
    """A cached app-only bearer token (client credentials), or None."""
    if not is_configured():
        return None
    now = time.time()
    if _token_cache['value'] and _token_cache['expires_at'] - 60 > now:
        return _token_cache['value']
    app = _msal_app()
    if app is None:
        return None
    try:
        result = app.acquire_token_for_client(scopes=_GRAPH_SCOPE)
    except Exception:  # pragma: no cover
        logger.exception('msteams: token acquisition failed')
        return None
    token = result.get('access_token') if result else None
    if not token:
        logger.error('msteams: no access_token (%s)', (result or {}).get('error_description', 'unknown'))
        return None
    _token_cache['value'] = token
    _token_cache['expires_at'] = now + int((result or {}).get('expires_in', 3600))
    return token


# ---------------------------------------------------------------------------
# low-level request helper
# ---------------------------------------------------------------------------
def _request(method, path, *, json=None, params=None):
    """Call Graph. ``path`` is relative to MS_GRAPH_BASE (or absolute). Returns the
    parsed JSON dict, or None on any failure (logged, never raised)."""
    token = _get_token()
    if not token:
        return None
    import requests
    url = path if path.startswith('http') else f"{settings.MS_GRAPH_BASE.rstrip('/')}/{path.lstrip('/')}"
    try:
        resp = requests.request(
            method, url, params=params, json=json, timeout=30,
            headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
        )
    except Exception:  # pragma: no cover
        logger.exception('msteams: request error %s %s', method, url)
        return None
    if resp.status_code == 401:
        _token_cache['value'] = None   # force refresh next call
    if resp.status_code >= 400:
        logger.error('msteams: %s %s → %s %s', method, url, resp.status_code, resp.text[:300])
        return None
    if resp.status_code == 204 or not resp.content:
        return {}
    try:
        return resp.json()
    except ValueError:  # pragma: no cover
        return {}


# ---------------------------------------------------------------------------
# online meetings
# ---------------------------------------------------------------------------
def create_online_meeting(organizer_upn, *, subject, start_iso, end_iso, allow_recording=True):
    """Create a Teams meeting owned by ``organizer_upn`` (their UPN / work e-mail).

    Returns ``{'id', 'join_url'}`` or None. Anonymous attendees are allowed
    (students join by link); the organizer is the sole presenter by default.

    ``recordAutomatically`` is what makes the class record itself the moment the
    host joins — nobody has to remember to press the button, which is the whole
    reason the recording pipeline can be relied on downstream.
    """
    if not is_configured():
        return None
    body = {
        'startDateTime': start_iso,
        'endDateTime': end_iso,
        # Graph names this 'subject'. It is the title Teams shows in the call, in
        # the organiser's calendar, and on the recording it files in OneDrive —
        # which is what the after-class pipeline matches on.
        'subject': subject,
        'allowedPresenters': 'organizer',
        'allowAttendeeToEnableCamera': True,
        'allowAttendeeToEnableMic': True,
        'isEntryExitAnnounced': False,
        'lobbyBypassSettings': {'scope': 'everyone', 'isDialInBypassEnabled': True},
        'recordAutomatically': bool(allow_recording),
    }
    data = _request('POST', f'/users/{organizer_upn}/onlineMeetings', json=body)
    if not data or not data.get('id'):
        return None
    return {'id': data['id'], 'join_url': data.get('joinWebUrl', '')}


def update_online_meeting(organizer_upn, meeting_id, **fields):
    """PATCH an existing meeting (times, subject, recording flag). None on failure."""
    if not is_configured() or not fields:
        return None
    return _request('PATCH', f'/users/{organizer_upn}/onlineMeetings/{meeting_id}', json=fields)


def delete_online_meeting(organizer_upn, meeting_id):
    return _request('DELETE', f'/users/{organizer_upn}/onlineMeetings/{meeting_id}')


def get_online_meeting(organizer_upn, meeting_id):
    return _request('GET', f'/users/{organizer_upn}/onlineMeetings/{meeting_id}')


# ---------------------------------------------------------------------------
# Outlook / Teams calendar events (the staff-side invite)
# ---------------------------------------------------------------------------
def create_calendar_event(organizer_upn, *, subject, start_iso, end_iso, body_html='',
                          attendees=(), join_url='', time_zone='UTC'):
    """Put the session on ``organizer_upn``'s Outlook calendar and invite staff.

    Students are deliberately **not** attendees: they have no Microsoft account
    and join anonymously from the platform's launch page, so adding them would post
    invitations to addresses the tenant cannot resolve. Only licensed staff and
    educators go on the Microsoft invite; everyone else is reached by the
    platform's own notification and e-mail.

    Returns the created event dict (``id`` is what to store), or None.
    """
    if not is_configured():
        return None
    event = {
        'subject': subject,
        'body': {'contentType': 'HTML', 'content': body_html or ''},
        'start': {'dateTime': start_iso, 'timeZone': time_zone},
        'end': {'dateTime': end_iso, 'timeZone': time_zone},
        'attendees': [
            {'emailAddress': {'address': upn, 'name': name or upn}, 'type': 'required'}
            for upn, name in attendees if upn
        ],
        # The Teams meeting already exists; this event points at it rather than
        # asking Graph to mint a second, unrelated one.
        'isOnlineMeeting': bool(join_url),
        'onlineMeetingProvider': 'teamsForBusiness',
    }
    if join_url:
        event['onlineMeeting'] = {'joinUrl': join_url}
    return _request('POST', f'/users/{organizer_upn}/events', json=event)


def update_calendar_event(organizer_upn, event_id, **fields):
    if not is_configured() or not event_id or not fields:
        return None
    return _request('PATCH', f'/users/{organizer_upn}/events/{event_id}', json=fields)


def delete_calendar_event(organizer_upn, event_id):
    if not is_configured() or not event_id:
        return None
    return _request('DELETE', f'/users/{organizer_upn}/events/{event_id}')


# ---------------------------------------------------------------------------
# OneDrive / SharePoint drive items
# ---------------------------------------------------------------------------
def get_drive_id(owner_upn):
    """The id of ``owner_upn``'s OneDrive, or None."""
    data = _request('GET', f'/users/{owner_upn}/drive')
    return (data or {}).get('id')


def get_drive_item(drive_id, item_id):
    return _request('GET', f'/drives/{drive_id}/items/{item_id}')


def get_item_by_path(drive_id, path):
    """Look a drive item up by its path relative to the drive root. None if absent."""
    if not path:
        return _request('GET', f'/drives/{drive_id}/root')
    return _request('GET', f'/drives/{drive_id}/root:/{_quote_path(path)}')


def list_children(drive_id, parent_item_id):
    """The immediate children of a folder. Always a list."""
    data = _request('GET', f'/drives/{drive_id}/items/{parent_item_id}/children',
                    params={'$select': 'id,name,size,webUrl,file,folder'})
    return (data or {}).get('value', []) or []


def create_folder(drive_id, parent_item_id, name):
    """Create ``name`` under ``parent_item_id``; return the existing one if it is there.

    ``conflictBehavior: replace`` would delete a folder that already holds last
    week's recording, so this asks Graph to fail on conflict and then reads the
    existing child back. That makes the whole tree-building step idempotent,
    which matters because the pipeline re-runs it on every retry.
    """
    body = {'name': name, 'folder': {}, '@microsoft.graph.conflictBehavior': 'fail'}
    created = _request('POST', f'/drives/{drive_id}/items/{parent_item_id}/children', json=body)
    if created and created.get('id'):
        return created
    listing = _request('GET', f'/drives/{drive_id}/items/{parent_item_id}/children',
                       params={'$filter': f"name eq '{str(name).replace(chr(39), chr(39) * 2)}'",
                               '$select': 'id,name,folder,webUrl'})
    for child in (listing or {}).get('value', []):
        if child.get('name') == name and 'folder' in child:
            return child
    return None


def move_item(drive_id, item_id, *, parent_item_id, new_name=None):
    """Move (and optionally rename) a drive item. Returns the updated item or None."""
    body = {'parentReference': {'id': parent_item_id},
            '@microsoft.graph.conflictBehavior': 'rename'}
    if new_name:
        body['name'] = new_name
    return _request('PATCH', f'/drives/{drive_id}/items/{item_id}', json=body)


def copy_item(drive_id, item_id, *, parent_item_id, new_name=None):
    """Server-side copy. Graph does this asynchronously and returns 202, so this
    reports only whether the copy was *accepted*, not that it has finished."""
    body = {'parentReference': {'driveId': drive_id, 'id': parent_item_id}}
    if new_name:
        body['name'] = new_name
    return _request('POST', f'/drives/{drive_id}/items/{item_id}/copy', json=body) is not None


def upload_small_file(drive_id, parent_item_id, name, content, content_type='text/plain'):
    """Upload up to ~4 MB in one PUT. Returns the drive item, or None.

    Used for the transcript, the summary and the thumbnail — all small. The
    recording is never uploaded: it is already in OneDrive, and gets *moved*.
    """
    token = _get_token()
    if not token:
        return None
    import requests
    if isinstance(content, str):
        content = content.encode('utf-8')
    url = (f"{settings.MS_GRAPH_BASE.rstrip('/')}/drives/{drive_id}/items/"
           f"{parent_item_id}:/{_quote_path(name)}:/content")
    try:
        resp = requests.put(url, data=content, timeout=120,
                            headers={'Authorization': f'Bearer {token}',
                                     'Content-Type': content_type})
    except Exception:  # pragma: no cover
        logger.exception('msteams: upload failed for %s', name)
        return None
    if resp.status_code >= 400:
        logger.error('msteams: upload %s → %s %s', name, resp.status_code, resp.text[:300])
        return None
    try:
        return resp.json()
    except ValueError:  # pragma: no cover
        return None


def create_share_link(drive_id, item_id, *, link_type='view', scope='anonymous'):
    """Mint a sharing link for a drive item and return its URL, or ''.

    ``scope='anonymous'`` is what lets a student who has no Microsoft account
    watch the recording. Tenants can forbid anonymous links; when they do, Graph
    returns 403 and the caller falls back to the organisation-scoped link.
    """
    body = {'type': link_type, 'scope': scope}
    data = _request('POST', f'/drives/{drive_id}/items/{item_id}/createLink', json=body)
    if not data and scope == 'anonymous':
        data = _request('POST', f'/drives/{drive_id}/items/{item_id}/createLink',
                        json={'type': link_type, 'scope': 'organization'})
    return ((data or {}).get('link') or {}).get('webUrl', '')


def download_item(drive_id, item_id):
    """Fetch a drive item's bytes. Returns ``bytes`` or None.

    Only used when something has to leave Microsoft — the YouTube upload. Files
    can be gigabytes, so this streams into memory in chunks rather than letting
    ``requests`` buffer the whole body twice.
    """
    token = _get_token()
    if not token:
        return None
    import requests
    url = f"{settings.MS_GRAPH_BASE.rstrip('/')}/drives/{drive_id}/items/{item_id}/content"
    try:
        with requests.get(url, stream=True, timeout=(30, 600),
                          headers={'Authorization': f'Bearer {token}'}) as resp:
            if resp.status_code >= 400:
                logger.error('msteams: download %s → %s', item_id, resp.status_code)
                return None
            chunks = bytearray()
            for chunk in resp.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    chunks.extend(chunk)
            return bytes(chunks)
    except Exception:  # pragma: no cover
        logger.exception('msteams: download error for %s', item_id)
        return None


def _quote_path(path):
    """Percent-encode a drive path, keeping the ``/`` separators intact."""
    from urllib.parse import quote
    return quote(str(path).strip('/'), safe='/')


# ---------------------------------------------------------------------------
# after-class artifacts
# ---------------------------------------------------------------------------
def list_transcripts(organizer_upn, meeting_id):
    data = _request('GET', f'/users/{organizer_upn}/onlineMeetings/{meeting_id}/transcripts')
    return (data or {}).get('value', []) or []


def get_transcript_content(organizer_upn, meeting_id, transcript_id, fmt='text/vtt'):
    """Raw transcript content (VTT). Returns text or None."""
    token = _get_token()
    if not token:
        return None
    import requests
    url = (f"{settings.MS_GRAPH_BASE.rstrip('/')}"
           f"/users/{organizer_upn}/onlineMeetings/{meeting_id}/transcripts/{transcript_id}/content")
    try:
        resp = requests.get(url, params={'$format': fmt}, timeout=60,
                            headers={'Authorization': f'Bearer {token}'})
    except Exception:  # pragma: no cover
        logger.exception('msteams: transcript content error')
        return None
    if resp.status_code >= 400:
        logger.error('msteams: transcript content → %s', resp.status_code)
        return None
    return resp.text


def list_recordings(organizer_upn, meeting_id):
    data = _request('GET', f'/users/{organizer_upn}/onlineMeetings/{meeting_id}/recordings')
    return (data or {}).get('value', []) or []


def list_attendance_reports(organizer_upn, meeting_id):
    data = _request('GET', f'/users/{organizer_upn}/onlineMeetings/{meeting_id}/attendanceReports')
    return (data or {}).get('value', []) or []


def get_attendance_records(organizer_upn, meeting_id, report_id):
    data = _request(
        'GET',
        f'/users/{organizer_upn}/onlineMeetings/{meeting_id}/attendanceReports/{report_id}/attendanceRecords',
    )
    return (data or {}).get('value', []) or []
