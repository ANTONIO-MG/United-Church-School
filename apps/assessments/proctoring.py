"""Exam integrity — the "focus guard" that watches an assessment attempt.

While a student sits a proctored assessment the browser reports the moments it
loses the student's attention: switching tab, alt-tabbing to another program,
dragging the pointer out of the page, leaving fullscreen, or trying to copy,
paste or print. :func:`record` turns each report into a
:class:`~apps.assessments.models.ProctorEvent`, keeps the running tally on the
attempt and decides what should happen next.

**The count lives here, not in the browser.** The client only says *what
happened*; the tally, the limit and the decision to end an attempt are all
server-side, so editing the JavaScript or replaying requests cannot lower a
student's warning count.

What this can and cannot do — worth being straight about, because it shapes how
you configure it:

* It reliably detects the student leaving *this browser window* — another tab,
  another application, another window, or the pointer leaving the page.
* It cannot see a second device. A phone beside the keyboard is invisible to
  any in-browser check, so treat the report as evidence for a conversation, not
  as proof of cheating.
* Legitimate interruptions (a notification stealing focus, a dropped
  connection) produce events too. That is why the default policy flags the
  attempt for a human rather than ending it.
"""

import logging

from django.utils import timezone

from . import models

logger = logging.getLogger('apps')

# Two reports describing the same interruption (a tab switch fires both a
# window blur and a visibility change) arrive together. Anything within this
# window of the last counted event is recorded as evidence but not counted
# twice against the student.
DEDUPE_SECONDS = 2

# The most events we will store for one attempt. A flapping or hostile client
# cannot bloat the table; the tally keeps rising, only the evidence log stops.
MAX_EVENTS = 300


def is_active(assessment):
    """Whether the focus guard should run for this assessment."""
    return bool(getattr(assessment, 'proctoring_enabled', False))


def client_config(assessment, attempt):
    """The settings the take page hands to exam-guard.js."""
    return {
        'enabled': is_active(assessment),
        'limit': assessment.proctor_warn_limit,
        'action': assessment.proctor_action,
        'blockCopy': assessment.proctor_block_copy,
        'requireFullscreen': assessment.proctor_require_fullscreen,
        'graceSeconds': assessment.proctor_grace_seconds,
        'blurContent': assessment.proctor_blur_content,
        'warnings': attempt.focus_warnings,
    }


def record(attempt, kind, *, seconds_away=0, detail=None):
    """Record one integrity event and return the resulting state.

    Returns ``{'counted', 'warnings', 'limit', 'remaining', 'action',
    'message'}`` where ``action`` is what the client must now do:

    * ``''`` — nothing beyond showing the warning
    * ``'flag'`` — the attempt is flagged for the educator; the student is told
    * ``'autosubmit'`` — the attempt is over and must be submitted now
    """
    assessment = attempt.assessment
    if kind not in dict(models.ProctorEvent.KIND_CHOICES):
        kind = models.ProctorEvent.KIND_BLUR
    seconds_away = max(0, min(3600, int(seconds_away or 0)))

    counted = _should_count(attempt)
    if attempt.proctor_events.count() < MAX_EVENTS:
        models.ProctorEvent.objects.create(
            attempt=attempt, kind=kind, counted=counted,
            seconds_away=seconds_away, detail=detail or {})

    fields = ['away_seconds']
    attempt.away_seconds = min(2 ** 31 - 1, (attempt.away_seconds or 0) + seconds_away)
    if counted:
        attempt.focus_warnings = (attempt.focus_warnings or 0) + 1
        fields.append('focus_warnings')

    limit = assessment.proctor_warn_limit or 0
    over = bool(limit) and attempt.focus_warnings >= limit
    action = ''

    if over and assessment.proctor_action != models.Assessment.ACTION_WARN:
        if not attempt.integrity_flagged:
            attempt.integrity_flagged = True
            attempt.integrity_note = (
                f'Left the assessment window {attempt.focus_warnings} time(s); '
                f'{attempt.away_label} away in total.')[:255]
            fields += ['integrity_flagged', 'integrity_note']
        action = models.Assessment.ACTION_FLAG
        if assessment.proctor_action == models.Assessment.ACTION_AUTOSUBMIT:
            action = models.Assessment.ACTION_AUTOSUBMIT
            if attempt.terminated_at is None:
                attempt.terminated_at = timezone.now()
                fields.append('terminated_at')

    attempt.save(update_fields=fields + ['updated_at'])

    return {
        'counted': counted,
        'warnings': attempt.focus_warnings,
        'limit': limit,
        'remaining': max(0, limit - attempt.focus_warnings) if limit else None,
        'action': action,
        'message': _message(attempt, kind, counted, limit, action),
    }


def _should_count(attempt):
    """False while we are inside the dedupe window of the last counted event."""
    last = (attempt.proctor_events.filter(counted=True)
            .order_by('-created_at').values_list('created_at', flat=True).first())
    if last is None:
        return True
    return (timezone.now() - last).total_seconds() >= DEDUPE_SECONDS


def _message(attempt, kind, counted, limit, action):
    """What the student is told — specific about what was seen and what follows."""
    if action == models.Assessment.ACTION_AUTOSUBMIT:
        return ('You left the assessment window too many times. '
                'The attempt has been ended and your answers submitted.')
    if action == models.Assessment.ACTION_FLAG:
        return ('You have left the assessment window '
                f'{attempt.focus_warnings} times. This attempt has been flagged '
                'for your educator to review.')
    if not counted:
        return 'Stay on this page until you have submitted.'

    seen = {
        models.ProctorEvent.KIND_HIDDEN: 'You switched away from this tab.',
        models.ProctorEvent.KIND_BLUR: 'You moved to another window or program.',
        models.ProctorEvent.KIND_POINTER_OUT: 'Your pointer left the assessment window.',
        models.ProctorEvent.KIND_FULLSCREEN_EXIT: 'You left fullscreen.',
        models.ProctorEvent.KIND_COPY: 'Copying is disabled during this assessment.',
        models.ProctorEvent.KIND_PASTE: 'Pasting is disabled during this assessment.',
        models.ProctorEvent.KIND_CONTEXTMENU: 'The right-click menu is disabled during this assessment.',
        models.ProctorEvent.KIND_PRINT: 'Printing is disabled during this assessment.',
    }.get(kind, 'You left the assessment window.')

    if limit:
        left = max(0, limit - attempt.focus_warnings)
        if left:
            return f'{seen} Warning {attempt.focus_warnings} of {limit} — {left} left.'
        return f'{seen} That was your last warning.'
    return f'{seen} This has been recorded ({attempt.focus_warnings} so far).'


def summary(attempt):
    """The integrity report an educator sees for one attempt."""
    events = list(attempt.proctor_events.all())
    by_kind = {}
    for event in events:
        by_kind.setdefault(event.kind, {'label': event.get_kind_display(),
                                        'icon': event.icon, 'n': 0})
        by_kind[event.kind]['n'] += 1
    return {
        'enabled': is_active(attempt.assessment),
        'events': events,
        'by_kind': sorted(by_kind.values(), key=lambda r: -r['n']),
        'warnings': attempt.focus_warnings,
        'limit': attempt.assessment.proctor_warn_limit,
        'away_seconds': attempt.away_seconds,
        'away_label': attempt.away_label,
        'flagged': attempt.integrity_flagged,
        'note': attempt.integrity_note,
        'terminated': attempt.terminated_at is not None,
    }
