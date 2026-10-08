"""Keeping imported calendars in step.

One job (``calendar-subscriptions``) refreshes every active
:class:`~apps.livesessions.models.CalendarSubscription`. Each refresh fetches the
feed, expands recurrences inside a fixed window and **replaces** that window's
events wholesale — a meeting the person deleted or moved in Google has to
disappear from the platform too, and a diff would be more code for the same result.

A feed that keeps failing is not retried forever: after
:data:`DISABLE_AFTER_FAILURES` consecutive failures the subscription is switched
off and its owner is told, because the usual cause is a link they revoked and
only they can fix it.
"""

import logging

from django.utils import timezone

from . import ics

logger = logging.getLogger('apps')

#: How much of each feed to keep. A term behind, two terms ahead.
WINDOW_BEFORE_DAYS = 60
WINDOW_AFTER_DAYS = 240
#: Consecutive failures before the subscription is switched off.
DISABLE_AFTER_FAILURES = 5


def run(limit=50):
    """Refresh the subscriptions that are due. Returns a short summary."""
    from .models import CalendarSubscription

    due = (CalendarSubscription.objects
           .filter(is_active=True)
           .select_related('user')
           .order_by('last_synced_at')[:limit])

    synced = failed = 0
    for subscription in due:
        ok, _detail = refresh(subscription)
        synced += int(ok)
        failed += int(not ok)
    return f'{synced} calendar(s) synced, {failed} failed'


def refresh(subscription):
    """Re-import one subscription. Returns ``(ok, detail)``."""
    from .models import ExternalEvent

    text, error = ics.fetch(subscription.url)
    if error:
        return _record_failure(subscription, error)

    start, end = _window()
    try:
        events = ics.parse(text, window_start=start, window_end=end)
    except Exception as exc:
        logger.exception('subscriptions: could not parse %s', subscription)
        return _record_failure(subscription, f'Could not read that feed ({exc}).'[:300])

    # Replace the window wholesale — see the module docstring on why.
    ExternalEvent.objects.filter(subscription=subscription).delete()
    ExternalEvent.objects.bulk_create([
        ExternalEvent(
            subscription=subscription,
            uid=(event.get('uid') or '')[:255],
            title=(event.get('title') or 'Busy')[:300],
            start=event['start'],
            end=event.get('end'),
            all_day=bool(event.get('all_day')),
            location=(event.get('location') or '')[:300],
            busy=bool(event.get('busy', True)),
        ) for event in events if event.get('start')
    ], batch_size=500)

    subscription.last_synced_at = timezone.now()
    subscription.last_status = subscription.STATUS_OK
    subscription.last_error = ''
    subscription.event_count = len(events)
    subscription.consecutive_failures = 0
    subscription.save(update_fields=['last_synced_at', 'last_status', 'last_error',
                                     'event_count', 'consecutive_failures', 'updated_at'])
    return True, f'{len(events)} event(s)'


def _record_failure(subscription, error):
    """Note a failure, and give up on a feed that will not come back."""
    subscription.last_status = subscription.STATUS_FAILED
    subscription.last_error = str(error)[:300]
    subscription.last_synced_at = timezone.now()
    subscription.consecutive_failures += 1

    fields = ['last_status', 'last_error', 'last_synced_at', 'consecutive_failures', 'updated_at']
    if subscription.consecutive_failures >= DISABLE_AFTER_FAILURES:
        subscription.is_active = False
        fields.append('is_active')
        _tell_the_owner(subscription)
    subscription.save(update_fields=fields)
    return False, subscription.last_error


def _tell_the_owner(subscription):
    """A revoked or rotated feed link is only the owner's to fix."""
    from apps.communication import services as comm
    try:
        comm.notify(
            subscription.user, category='meetings', level='warning',
            verb='calendar disconnected',
            title=f'Calendar disconnected — {subscription.name}',
            body=(f'We could not read “{subscription.name}” after several attempts '
                  f'({subscription.last_error}). Its events have stopped updating. '
                  f'Reconnect it under Settings → Calendar with a fresh link.'),
            url=_settings_url(), email=True,
        )
    except Exception:   # pragma: no cover
        logger.exception('subscriptions: could not notify %s', subscription.user)


def _settings_url():
    """Where the owner goes to reconnect it."""
    from django.urls import reverse
    try:
        return reverse('accounts:settings') + '?tab=connected'
    except Exception:       # pragma: no cover
        return ''


def _window():
    now = timezone.now()
    from datetime import timedelta
    return now - timedelta(days=WINDOW_BEFORE_DAYS), now + timedelta(days=WINDOW_AFTER_DAYS)
