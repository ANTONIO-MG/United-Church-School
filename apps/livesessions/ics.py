"""Reading and writing iCalendar (RFC 5545), and fetching a feed safely.

Why hand-rolled rather than ``icalendar`` + ``recurring-ical-events``: this
project keeps its dependency list deliberately short (see
docs/PACKAGE_DECISIONS.md), and what the calendar needs from an imported feed is
narrow — *when is this person busy* — not full RFC fidelity. Writing is likewise
a fixed shape we control.

**What the reader supports:** line unfolding, ``VEVENT`` with ``DTSTART`` /
``DTEND`` / ``DURATION``, ``DATE`` and ``DATE-TIME`` values, ``TZID`` and UTC
(``Z``), ``SUMMARY``, ``LOCATION``, ``UID``, ``STATUS``, ``TRANSP``, simple
``RRULE`` (``FREQ`` daily/weekly/monthly/yearly with ``INTERVAL``, ``COUNT``,
``UNTIL``, ``BYDAY``), and ``EXDATE``.

**What it does not:** ``BYSETPOS`` / ``BYMONTHDAY`` and the rarer RRULE parts,
``VTODO`` / ``VJOURNAL``, attachments, alarms, and attendee lists. An event using
an unsupported rule still imports — it simply appears once, at its first
occurrence, rather than repeating. That is the right way to be wrong here: the
overlay shows slightly *less* busy time than reality, never a phantom booking on
a day that is actually free.

Recurrences are expanded **only inside the requested window** and hard-capped, so
a feed containing "every weekday forever" costs the same as any other.
"""

import datetime as dt
import ipaddress
import logging
import re
from urllib.parse import urlparse

logger = logging.getLogger('apps')

#: Never expand more occurrences than this from one rule, whatever it claims.
MAX_OCCURRENCES = 400
#: Refuse a feed bigger than this. A year of a busy calendar is well under 1 MB.
MAX_FEED_BYTES = 4 * 1024 * 1024

_WEEKDAYS = {'MO': 0, 'TU': 1, 'WE': 2, 'TH': 3, 'FR': 4, 'SA': 5, 'SU': 6}


# ---------------------------------------------------------------------------
# Writing
# ---------------------------------------------------------------------------
def serialise(entries, *, name='United Church School', prodid='-//United Church School//Calendar//EN'):
    """Render ``entries`` as an iCalendar document.

    Each entry needs ``uid``, ``title`` and ``start``; ``end``, ``description``,
    ``location``, ``url``, ``all_day`` and ``cancelled`` are optional.
    """
    lines = ['BEGIN:VCALENDAR', 'VERSION:2.0', f'PRODID:{prodid}',
             'CALSCALE:GREGORIAN', 'METHOD:PUBLISH', f'X-WR-CALNAME:{escape(name)}',
             # Tells Google/Outlook how often to re-poll a subscribed feed.
             'REFRESH-INTERVAL;VALUE=DURATION:PT1H', 'X-PUBLISHED-TTL:PT1H']

    for entry in entries:
        start = entry.get('start')
        if not start:
            continue
        end = entry.get('end') or start + dt.timedelta(hours=1)
        lines.append('BEGIN:VEVENT')
        lines.append(f"UID:{entry.get('uid') or 'ucs-lms'}")
        lines.append(f"DTSTAMP:{_utc_stamp(entry.get('updated') or start)}")
        if entry.get('all_day'):
            lines.append(f'DTSTART;VALUE=DATE:{_local_date(start)}')
            lines.append(f'DTEND;VALUE=DATE:{_local_date(end)}')
        else:
            lines.append(f'DTSTART:{_utc_stamp(start)}')
            lines.append(f'DTEND:{_utc_stamp(end)}')
        lines.append(f"SUMMARY:{escape(entry.get('title'))}")
        if entry.get('description'):
            lines.append(f"DESCRIPTION:{escape(entry['description'])}")
        if entry.get('location'):
            lines.append(f"LOCATION:{escape(entry['location'])}")
        if entry.get('url'):
            lines.append(f"URL:{entry['url']}")
        lines.append('STATUS:' + ('CANCELLED' if entry.get('cancelled') else 'CONFIRMED'))
        lines.append('END:VEVENT')

    lines.append('END:VCALENDAR')
    return '\r\n'.join(_fold(line) for line in lines) + '\r\n'


def escape(text):
    """Escape a value for a content line (RFC 5545 §3.3.11)."""
    return (str(text or '')
            .replace('\\', '\\\\').replace(';', r'\;')
            .replace(',', r'\,').replace('\r\n', r'\n').replace('\n', r'\n'))


def _fold(line, limit=73):
    """Fold a content line to 75 octets, continuation lines starting with a space."""
    if len(line) <= limit:
        return line
    head, rest = line[:limit], line[limit:]
    chunks = [rest[i:i + limit - 1] for i in range(0, len(rest), limit - 1)]
    return head + '\r\n ' + '\r\n '.join(chunks)


def _utc_stamp(moment):
    from django.utils import timezone
    if moment is None:
        moment = timezone.now()
    if isinstance(moment, dt.datetime) and timezone.is_naive(moment):
        moment = timezone.make_aware(moment, timezone.get_current_timezone())
    return moment.astimezone(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')


def _local_date(moment):
    from django.utils import timezone
    if isinstance(moment, dt.datetime):
        return timezone.localtime(moment).strftime('%Y%m%d')
    return moment.strftime('%Y%m%d')


# ---------------------------------------------------------------------------
# Fetching — a user-supplied URL, so treat it as hostile
# ---------------------------------------------------------------------------
def fetch(url, *, timeout=20):
    """Download an ICS feed. Returns ``(text, error)`` — exactly one is truthy.

    The URL comes from a form, so this is a server-side request to wherever a
    user typed. Left unguarded that is an SSRF hole: someone could point it at
    ``http://169.254.169.254/`` (cloud metadata) or an internal admin service and
    read the response back out of the calendar. So the scheme is restricted,
    every resolved address is checked against the private ranges, redirects are
    followed manually with the same check applied each hop, and the body is
    capped.
    """
    import requests

    ok, reason = _url_is_safe(url)
    if not ok:
        return '', reason

    seen = set()
    current = url
    try:
        for _hop in range(5):
            response = requests.get(
                current, timeout=timeout, allow_redirects=False, stream=True,
                headers={'User-Agent': 'UCS-LMS/1.0 (calendar subscription)',
                         'Accept': 'text/calendar, text/plain;q=0.8'})
            if response.status_code in (301, 302, 303, 307, 308):
                target = response.headers.get('Location', '')
                if not target or target in seen:
                    return '', 'The feed redirected in a loop.'
                seen.add(target)
                current = requests.compat.urljoin(current, target)
                ok, reason = _url_is_safe(current)
                if not ok:
                    return '', reason
                continue
            if response.status_code == 404:
                return '', 'The feed URL returned "not found" — check it is still shared.'
            if response.status_code in (401, 403):
                return '', 'The feed URL is private. Use the secret / public address instead.'
            if response.status_code >= 400:
                return '', f'The feed returned HTTP {response.status_code}.'

            body = bytearray()
            for chunk in response.iter_content(chunk_size=64 * 1024):
                body.extend(chunk)
                if len(body) > MAX_FEED_BYTES:
                    return '', 'That calendar is too large to import.'
            text = bytes(body).decode('utf-8', 'replace')
            if 'BEGIN:VCALENDAR' not in text:
                return '', 'That URL is not an iCalendar (.ics) feed.'
            return text, ''
        return '', 'The feed redirected too many times.'
    except Exception as exc:      # pragma: no cover - network
        logger.warning('ics: could not fetch %s (%s)', url, exc)
        return '', 'Could not reach that calendar feed.'


def _url_is_safe(url):
    """``(ok, reason)`` — refuse anything that could reach inside the network."""
    import socket

    try:
        parsed = urlparse(url)
    except Exception:
        return False, 'That does not look like a URL.'

    scheme = (parsed.scheme or '').lower()
    if scheme == 'webcal':
        # Google and Apple hand out webcal:// links; it is https underneath.
        return _url_is_safe('https://' + url.split('://', 1)[-1])
    if scheme not in ('http', 'https'):
        return False, 'Only http:// and https:// calendar links can be imported.'
    if not parsed.hostname:
        return False, 'That URL has no host.'

    try:
        infos = socket.getaddrinfo(parsed.hostname, parsed.port or (443 if scheme == 'https' else 80))
    except Exception:
        return False, 'That host could not be found.'

    for info in infos:
        address = info[4][0]
        try:
            ip = ipaddress.ip_address(address)
        except ValueError:
            continue
        if (ip.is_private or ip.is_loopback or ip.is_link_local
                or ip.is_reserved or ip.is_multicast or ip.is_unspecified):
            return False, 'That address is inside the server network and cannot be imported.'
    return True, ''


# ---------------------------------------------------------------------------
# Reading
# ---------------------------------------------------------------------------
def parse(text, *, window_start=None, window_end=None, default_tz=None):
    """Parse an ICS document into event dicts inside the requested window.

    Returns ``[{'uid', 'title', 'start', 'end', 'all_day', 'location', 'busy'}]``
    with aware datetimes. Recurrences are expanded within the window only.
    """
    from django.utils import timezone

    default_tz = default_tz or timezone.get_current_timezone()
    window_start = window_start or (timezone.now() - dt.timedelta(days=30))
    window_end = window_end or (timezone.now() + dt.timedelta(days=180))

    events = []
    for block in _vevents(text):
        try:
            events.extend(_expand(block, window_start, window_end, default_tz))
        except Exception:       # one malformed event must not lose the feed
            logger.debug('ics: skipped an unparseable VEVENT', exc_info=True)
    return events


def _unfold(text):
    """Join RFC 5545 continuation lines (a line starting with space or tab)."""
    lines = []
    for raw in str(text or '').replace('\r\n', '\n').replace('\r', '\n').split('\n'):
        if raw[:1] in (' ', '\t') and lines:
            lines[-1] += raw[1:]
        else:
            lines.append(raw)
    return lines


def _vevents(text):
    """Every VEVENT as ``{name: [(params, value), ...]}``."""
    blocks, current = [], None
    for line in _unfold(text):
        stripped = line.strip()
        if stripped == 'BEGIN:VEVENT':
            current = {}
            continue
        if stripped == 'END:VEVENT':
            if current is not None:
                blocks.append(current)
            current = None
            continue
        if current is None or ':' not in stripped:
            continue
        head, _, value = stripped.partition(':')
        parts = head.split(';')
        name = parts[0].upper()
        params = {}
        for chunk in parts[1:]:
            key, _, val = chunk.partition('=')
            params[key.upper()] = val.strip('"')
        current.setdefault(name, []).append((params, value))
    return blocks


def _first(block, name):
    rows = block.get(name)
    return rows[0] if rows else (None, None)


def _unescape(value):
    return (str(value or '')
            .replace(r'\n', '\n').replace(r'\N', '\n')
            .replace(r'\,', ',').replace(r'\;', ';').replace('\\\\', '\\'))


def _zone(name, fallback):
    if not name:
        return fallback
    try:
        from zoneinfo import ZoneInfo
        return ZoneInfo(name)
    except Exception:
        return fallback


def _value_to_dt(params, value, default_tz):
    """``(datetime, is_date_only)`` for a DTSTART/DTEND/EXDATE value."""
    value = (value or '').strip()
    if not value:
        return None, False
    if (params or {}).get('VALUE') == 'DATE' or (len(value) == 8 and 'T' not in value):
        parsed = dt.datetime.strptime(value[:8], '%Y%m%d')
        return parsed.replace(tzinfo=default_tz), True
    if value.endswith('Z'):
        parsed = dt.datetime.strptime(value, '%Y%m%dT%H%M%SZ')
        return parsed.replace(tzinfo=dt.timezone.utc), False
    parsed = dt.datetime.strptime(value[:15], '%Y%m%dT%H%M%S')
    return parsed.replace(tzinfo=_zone((params or {}).get('TZID'), default_tz)), False


def _duration(value):
    """A DURATION value (``PT1H30M``, ``P2D``) as a timedelta."""
    match = re.fullmatch(r'([+-])?P(?:(\d+)W)?(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?)?',
                         (value or '').strip().upper())
    if not match:
        return dt.timedelta(hours=1)
    sign, weeks, days, hours, minutes, seconds = match.groups()
    delta = dt.timedelta(weeks=int(weeks or 0), days=int(days or 0), hours=int(hours or 0),
                         minutes=int(minutes or 0), seconds=int(seconds or 0))
    return -delta if sign == '-' else delta


def _expand(block, window_start, window_end, default_tz):
    """One VEVENT → the occurrences of it that fall inside the window."""
    start_params, start_value = _first(block, 'DTSTART')
    if start_value is None:
        return []
    start, all_day = _value_to_dt(start_params, start_value, default_tz)
    if start is None:
        return []

    end_params, end_value = _first(block, 'DTEND')
    if end_value:
        end, _ = _value_to_dt(end_params, end_value, default_tz)
    else:
        _p, duration = _first(block, 'DURATION')
        end = start + (_duration(duration) if duration
                       else dt.timedelta(days=1) if all_day else dt.timedelta(hours=1))
    length = (end - start) if end and end > start else dt.timedelta(hours=1)

    _p, status = _first(block, 'STATUS')
    if (status or '').upper() == 'CANCELLED':
        return []
    _p, transp = _first(block, 'TRANSP')
    busy = (transp or 'OPAQUE').upper() != 'TRANSPARENT'

    _p, uid = _first(block, 'UID')
    _p, summary = _first(block, 'SUMMARY')
    _p, location = _first(block, 'LOCATION')

    excluded = set()
    for params, value in block.get('EXDATE', []):
        for chunk in str(value).split(','):
            moment, _ = _value_to_dt(params, chunk, default_tz)
            if moment:
                excluded.add(moment)

    _p, rrule = _first(block, 'RRULE')
    starts = ([start] if not rrule
              else _occurrences(start, rrule, window_start, window_end))

    out = []
    for moment in starts:
        if moment in excluded:
            continue
        finish = moment + length
        if finish < window_start or moment > window_end:
            continue
        out.append({
            'uid': (uid or '') + ('' if not rrule else f'-{moment:%Y%m%dT%H%M%S}'),
            'title': _unescape(summary) or 'Busy',
            'start': moment,
            'end': finish,
            'all_day': all_day,
            'location': _unescape(location),
            'busy': busy,
        })
    return out


def _occurrences(start, rrule, window_start, window_end):
    """Expand a simple RRULE inside the window. Falls back to ``[start]``.

    Only the parts a real person's calendar actually uses are handled; anything
    else returns the single first occurrence, which under-reports busy time
    rather than inventing it.
    """
    rule = {}
    for chunk in str(rrule).split(';'):
        key, _, value = chunk.partition('=')
        rule[key.strip().upper()] = value.strip()

    freq = rule.get('FREQ', '').upper()
    if freq not in ('DAILY', 'WEEKLY', 'MONTHLY', 'YEARLY'):
        return [start]

    interval = max(1, int(rule.get('INTERVAL') or 1))
    count = int(rule['COUNT']) if (rule.get('COUNT') or '').isdigit() else None
    until = None
    if rule.get('UNTIL'):
        try:
            until, _ = _value_to_dt({}, rule['UNTIL'], start.tzinfo)
        except Exception:
            until = None

    bydays = [_WEEKDAYS[d[-2:].upper()] for d in (rule.get('BYDAY') or '').split(',')
              if d and d[-2:].upper() in _WEEKDAYS]

    out, produced, cursor = [], 0, start
    # Walk forward from the event's own start; stop at the window's end, the
    # rule's own end, or the hard cap — whichever comes first.
    guard = 0
    while cursor <= window_end and guard < MAX_OCCURRENCES * 8:
        guard += 1
        if until and cursor > until:
            break
        if count is not None and produced >= count:
            break

        emit = True
        if freq == 'WEEKLY' and bydays:
            emit = cursor.weekday() in bydays
        elif freq == 'DAILY' and bydays:
            emit = cursor.weekday() in bydays

        if emit:
            produced += 1
            if cursor >= window_start:
                out.append(cursor)
                if len(out) >= MAX_OCCURRENCES:
                    break

        if freq == 'DAILY':
            cursor += dt.timedelta(days=interval)
        elif freq == 'WEEKLY':
            # With BYDAY we step a day at a time so each named weekday is
            # visited; the interval then applies to whole weeks.
            cursor += dt.timedelta(days=1) if bydays else dt.timedelta(weeks=interval)
        elif freq == 'MONTHLY':
            cursor = _add_months(cursor, interval)
        else:
            cursor = _add_months(cursor, 12 * interval)
    return out or [start]


def _add_months(moment, months):
    """Add whole months, clamping to the end of a shorter month."""
    import calendar as _cal
    month_index = moment.month - 1 + months
    year = moment.year + month_index // 12
    month = month_index % 12 + 1
    day = min(moment.day, _cal.monthrange(year, month)[1])
    return moment.replace(year=year, month=month, day=day)
