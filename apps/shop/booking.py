"""1-on-1 bookings: when an educator is free, and what happens to a booked slot.

**Free** means free on the *school* calendar. A slot is offered only when all of
these agree:

* it sits inside one of the educator's weekly working windows
  (:class:`EducatorAvailability`) and outside their time off;
* the educator is not hosting (or co-hosting) a live session on the platform then;
* nothing on a calendar feed they connected to the platform (Google / Outlook / Apple,
  :mod:`apps.livesessions.sources`) marks them busy;
* no other booking — paid, or held in someone's cart — overlaps it.

Every one of those busy spans is widened by the service's buffer, so sessions
never run back to back. Slots start on the half hour and must be at least the
service's minimum notice away.

A slot chosen by a student is **held** for :data:`HOLD_MINUTES` while they check
out, and for :data:`CHECKOUT_HOLD_HOURS` once the order is placed (an EFT takes
time). The hold is what stops two students paying for the same hour; it is
taken under a row lock on the educator's rate, so two simultaneous requests for
one slot serialise and the second one sees the first.
"""
import logging
from datetime import datetime, timedelta

from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from .models import Booking, CreditEntry, EducatorAvailability, EducatorRate, EducatorTimeOff, Order, OrderItem

logger = logging.getLogger('apps')

HOLD_MINUTES = 15
CHECKOUT_HOLD_HOURS = 48
SLOT_STEP_MINUTES = 30


class BookingError(Exception):
    """The slot cannot be booked; the message is for the student."""


# ---------------------------------------------------------------------------
# Free / busy
# ---------------------------------------------------------------------------
def _tz():
    return timezone.get_current_timezone()


def _aware(day, clock):
    return timezone.make_aware(datetime.combine(day, clock), _tz())


def _windows(educator, day):
    """The educator's working windows on ``day``, as aware (start, end) pairs."""
    windows = [(_aware(day, w.start_time), _aware(day, w.end_time))
               for w in EducatorAvailability.objects.filter(educator=educator, weekday=day.weekday())
               if w.end_time > w.start_time]
    return sorted(windows)


def busy_spans(educator, start, end, *, exclude_booking=None, include_time_off=True):
    """Everything that occupies ``educator`` between ``start`` and ``end``."""
    from apps.communication.models import MeetingRoom

    spans = []
    user = educator.user
    if user is not None:
        sessions = (MeetingRoom.objects
                    .filter(is_active=True, scheduled_start__lt=end, scheduled_end__gt=start)
                    .filter(Q(host=user) | Q(participants__user=user,
                                             participants__role__in=('host', 'cohost')))
                    .distinct())
        spans += [(m.scheduled_start, m.scheduled_end or m.scheduled_start + timedelta(hours=1))
                  for m in sessions]
        try:
            from apps.livesessions import sources
            spans += [(e.start, e.end or e.start + timedelta(hours=1))
                      for e in sources.entries_for(user, start, end, kinds=('external',))
                      if e.busy and e.start and not e.all_day]
        except Exception:  # pragma: no cover — a feed problem must not hide every slot
            logger.exception('shop: could not read calendar feeds for %s', educator)

    if include_time_off:
        spans += time_off_spans(educator, start, end)

    now = timezone.now()
    bookings = (Booking.objects.filter(educator=educator, start__lt=end, end__gt=start,
                                       status__in=Booking.BLOCKING)
                .filter(Q(status=Booking.STATUS_CONFIRMED) | Q(hold_expires_at__gt=now)))
    if exclude_booking is not None:
        bookings = bookings.exclude(pk=exclude_booking.pk)
    spans += [(b.start, b.end) for b in bookings]
    return spans


def time_off_spans(educator, start, end):
    return [(t.start, t.end) for t in
            EducatorTimeOff.objects.filter(educator=educator, start__lt=end, end__gt=start)]


def free_slots(rate, day, minutes, *, now=None, exclude_booking=None):
    """Start times on ``day`` when ``rate``'s educator can take a ``minutes`` session."""
    product = rate.product
    now = now or timezone.now()
    earliest = now + timedelta(hours=product.min_notice_hours)
    latest = now + timedelta(days=product.booking_window_days)
    windows = _windows(rate.educator, day)
    if not windows:
        return []

    day_start, day_end = windows[0][0], windows[-1][1]
    buffer = timedelta(minutes=product.buffer_minutes)
    # The buffer keeps sessions apart; it does not pad leave, so time off is
    # added as-is.
    busy = [(s - buffer, e + buffer) for s, e in
            busy_spans(rate.educator, day_start - buffer, day_end + buffer,
                       exclude_booking=exclude_booking, include_time_off=False)]
    busy += time_off_spans(rate.educator, day_start, day_end)
    length = timedelta(minutes=minutes)
    step = timedelta(minutes=SLOT_STEP_MINUTES)

    slots = []
    for win_start, win_end in windows:
        # Align to the half hour so the picker reads 14:00, 14:30 …
        cursor = win_start
        if cursor.minute % SLOT_STEP_MINUTES:
            cursor += timedelta(minutes=SLOT_STEP_MINUTES - cursor.minute % SLOT_STEP_MINUTES)
        while cursor + length <= win_end:
            end = cursor + length
            clash = any(s < end and e > cursor for s, e in busy)
            if not clash and earliest <= cursor <= latest:
                slots.append(cursor)
            cursor += step
    return slots


def week_of_slots(rate, minutes, start_day, *, days=14, now=None, exclude_booking=None):
    """``days`` rows of ``{'day', 'slots'}`` for the picker; full days kept."""
    rows = []
    for offset in range(days):
        day = start_day + timedelta(days=offset)
        rows.append({'day': day, 'slots': free_slots(rate, day, minutes, now=now,
                                                     exclude_booking=exclude_booking)})
    return rows


def is_free(rate, start, minutes, *, exclude_booking=None, now=None):
    local = timezone.localtime(start)
    return any(slot == start for slot in
               free_slots(rate, local.date(), minutes, now=now, exclude_booking=exclude_booking))


# ---------------------------------------------------------------------------
# Hold → confirm → reschedule / cancel
# ---------------------------------------------------------------------------
def hold_slot(*, user, rate, start, minutes, note=''):
    """Hold ``start`` for ``user`` and put the session in their cart."""
    if minutes not in rate.product.lengths:
        raise BookingError('That session length is not offered.')
    with transaction.atomic():
        EducatorRate.objects.select_for_update().get(pk=rate.pk)
        if not is_free(rate, start, minutes):
            raise BookingError('Sorry — that time has just been taken. Please pick another.')
        cart = Order.get_cart(user)
        price = rate.price_for(minutes)
        item = OrderItem.objects.create(order=cart, product=rate.product, quantity=1, unit_price=price)
        booking = Booking.objects.create(
            product=rate.product, educator=rate.educator, student=user,
            start=start, end=start + timedelta(minutes=minutes), minutes=minutes, price=price,
            hold_expires_at=timezone.now() + timedelta(minutes=HOLD_MINUTES),
            order_item=item, note=note[:2000])
        cart.recalc_total()
    return booking


def refresh_hold(booking, *, hours=None, minutes=None):
    """Keep a held slot for longer — re-checking it is still free if it lapsed."""
    if booking.status != Booking.STATUS_HELD:
        return booking
    now = timezone.now()
    if booking.hold_expires_at and booking.hold_expires_at <= now:
        rate = EducatorRate.objects.filter(product=booking.product, educator=booking.educator).first()
        if rate is None or not is_free(rate, booking.start, booking.minutes, exclude_booking=booking):
            raise BookingError(f'The {booking.label} slot is no longer available — '
                               'please remove it and choose another time.')
    delta = timedelta(hours=hours) if hours else timedelta(minutes=minutes or HOLD_MINUTES)
    booking.hold_expires_at = now + delta
    booking.save(update_fields=['hold_expires_at', 'updated_at'])
    return booking


def _session_title(booking):
    return f'1-on-1: {booking.product.name}'


def confirm(booking):
    """The booking is paid for: create the live session and tell both sides."""
    if booking.status == Booking.STATUS_CONFIRMED:
        return booking
    from apps.communication.services import notify
    from apps.livesessions import services as live

    student_name = booking.student.get_full_name() or booking.student.get_username()
    meeting = None
    try:
        meeting = live.create_session(
            host=booking.educator.user, title=_session_title(booking),
            start=booking.start, end=booking.end, audience='private', session_kind='consult',
            description=f'1-on-1 with {student_name}.' + (f'\n\n{booking.note}' if booking.note else ''),
            invitees=[booking.student], notify=False)
    except Exception:  # pragma: no cover — the money is real; staff can fix the room
        logger.exception('shop: could not create the session for booking %s', booking.pk)

    booking.status = Booking.STATUS_CONFIRMED
    booking.hold_expires_at = None
    booking.meeting = meeting
    booking.save(update_fields=['status', 'hold_expires_at', 'meeting', 'updated_at'])

    url = _bookings_url()
    notify(booking.student, title='Your 1-on-1 is booked',
           body=f'{booking.label} with {booking.educator}. The join link is on My bookings.',
           verb='booking confirmed', level='success', url=url, meeting=meeting)
    if booking.educator.user_id:
        notify(booking.educator.user, title='New 1-on-1 booked',
               body=f'{student_name} booked {booking.product.name} · {booking.label}.',
               verb='booking', level='info', url=url, meeting=meeting, actor=booking.student)
    return booking


def settle_paid(booking):
    """Payment landed for ``booking``: confirm it, unless the slot was lost.

    A hold lapses if payment takes longer than :data:`CHECKOUT_HOLD_HOURS` (an
    EFT over a long weekend). If someone else booked the time meanwhile, the
    student is not double-booked onto it: the money becomes account credit and
    they are asked to choose another time.
    """
    if booking.status in (Booking.STATUS_CONFIRMED, Booking.STATUS_COMPLETED, Booking.STATUS_CANCELLED):
        return booking
    rate = EducatorRate.objects.filter(product=booking.product, educator=booking.educator).first()
    lapsed = booking.status == Booking.STATUS_EXPIRED or (
        booking.hold_expires_at is not None and booking.hold_expires_at <= timezone.now())
    if lapsed and (rate is None or not _slot_still_open(rate, booking)):
        with transaction.atomic():
            booking.status = Booking.STATUS_CANCELLED
            booking.cancelled_reason = 'The time was taken before payment arrived.'
            booking.save(update_fields=['status', 'cancelled_reason', 'updated_at'])
            CreditEntry.objects.create(user=booking.student, amount=booking.price, booking=booking,
                                       reason=f'Payment for {booking.label} arrived after the slot was taken')
        from apps.communication.services import notify
        notify(booking.student, title='Please choose a new time',
               body=(f'Your payment for {booking.product.name} arrived after {booking.label} was booked '
                     f'by someone else. R{booking.price:,.2f} is on your account as credit — book any '
                     'free time and it will be used automatically.'),
               verb='booking needs a time', level='warning',
               url=booking.product.get_absolute_url(), email=True)
        return booking
    return confirm(booking)


def _slot_still_open(rate, booking):
    """Free apart from this booking — notice period ignored, the student paid."""
    past_notice = timezone.localtime(booking.start) - timedelta(hours=booking.product.min_notice_hours)
    return any(slot == booking.start for slot in free_slots(
        rate, timezone.localtime(booking.start).date(), booking.minutes,
        now=min(timezone.now(), past_notice), exclude_booking=booking))


def reschedule(booking, *, start, by):
    """Move a confirmed booking to ``start`` (same educator, same length)."""
    if not booking.can_reschedule() and not _is_staff(by):
        raise BookingError('This session is too close to move. Please contact us.')
    rate = EducatorRate.objects.filter(product=booking.product, educator=booking.educator).first()
    if rate is None:
        raise BookingError('This educator no longer offers this session.')
    with transaction.atomic():
        EducatorRate.objects.select_for_update().get(pk=rate.pk)
        if not is_free(rate, start, booking.minutes, exclude_booking=booking):
            raise BookingError('That time is not free. Please pick another.')
        old_label = booking.label
        booking.start, booking.end = start, start + timedelta(minutes=booking.minutes)
        booking.reschedule_count += 1
        booking.save(update_fields=['start', 'end', 'reschedule_count', 'updated_at'])

    if booking.meeting is not None:
        try:
            from apps.livesessions import services as live
            booking.meeting.scheduled_start, booking.meeting.scheduled_end = booking.start, booking.end
            live.update_session(booking.meeting, fields=['scheduled_start', 'scheduled_end'],
                                reschedule=True)
        except Exception:  # pragma: no cover
            logger.exception('shop: could not move the session for booking %s', booking.pk)

    from apps.communication.services import notify
    for user in {booking.student, booking.educator.user} - {None}:
        notify(user, title='1-on-1 moved', body=f'{old_label} → {booking.label}.',
               verb='booking moved', level='info', url=_bookings_url(), meeting=booking.meeting,
               actor=by)
    return booking


def cancel(booking, *, by, reason=''):
    """Staff / the educator cancel a paid session: the student gets it as credit.

    Students cannot cancel for money back (they may reschedule instead), so this
    is only reachable by staff and the booking's own educator — enforced here as
    well as in the view.
    """
    if not (_is_staff(by) or booking.educator.user_id == getattr(by, 'pk', None)):
        raise BookingError('Only staff or the educator can cancel a session.')
    if booking.status not in Booking.BLOCKING:
        raise BookingError('This session is not active.')
    was_paid = booking.status == Booking.STATUS_CONFIRMED
    with transaction.atomic():
        booking.status = Booking.STATUS_CANCELLED
        booking.cancelled_by = by
        booking.cancelled_reason = reason[:255]
        booking.save(update_fields=['status', 'cancelled_by', 'cancelled_reason', 'updated_at'])
        if was_paid and booking.price > 0:
            CreditEntry.objects.create(
                user=booking.student, amount=booking.price, booking=booking, created_by=by,
                reason=f'Cancelled 1-on-1: {booking.product.name} ({booking.label})')

    if booking.meeting is not None:
        try:
            from apps.livesessions import services as live
            live.cancel_session(booking.meeting, by=by, reason=reason)
        except Exception:  # pragma: no cover
            logger.exception('shop: could not cancel the session for booking %s', booking.pk)

    from apps.communication.services import notify
    body = f'{booking.label} with {booking.educator} has been cancelled.'
    if was_paid and booking.price > 0:
        body += f' R{booking.price:,.2f} has been added to your account credit for your next purchase.'
    if reason:
        body += f' Reason: {reason}'
    notify(booking.student, title='1-on-1 cancelled', body=body, verb='booking cancelled',
           level='warning', url=_bookings_url(), actor=by, email=True)
    return booking


def expire_holds(now=None):
    """Release holds that ran out. Run by the scheduler every few minutes.

    A hold still sitting in an open cart just lapses — the line stays, and
    checkout re-checks the slot. A hold on an order already placed but never
    paid is expired and its line removed from nobody: the invoice stays as a
    record, and paying it later reports the slot as needing a new time.
    """
    now = now or timezone.now()
    lapsed = Booking.objects.filter(status=Booking.STATUS_HELD, hold_expires_at__lte=now)
    placed = lapsed.filter(order_item__order__checked_out=True)
    count = placed.update(status=Booking.STATUS_EXPIRED)
    return f'{count} unpaid booking(s) expired'


def complete_past(now=None):
    now = now or timezone.now()
    return Booking.objects.filter(status=Booking.STATUS_CONFIRMED, end__lt=now).update(
        status=Booking.STATUS_COMPLETED)


def run_housekeeping():
    """Scheduler entry point: expire unpaid holds, close sessions that have ended."""
    message = expire_holds()
    done = complete_past()
    return f'{message}; {done} session(s) completed'


# ---------------------------------------------------------------------------
# Credit
# ---------------------------------------------------------------------------
def apply_credit(invoice, user):
    """Spend the user's account credit on ``invoice``. Returns the amount used."""
    from decimal import Decimal

    from apps.finance import services as finance

    with transaction.atomic():
        balance = CreditEntry.balance_for(user)
        use = min(balance, invoice.balance)
        if use <= 0:
            return Decimal('0')
        CreditEntry.objects.create(user=user, amount=-use, invoice=invoice,
                                   reason=f'Used on invoice {invoice.number}')
    finance.settle_payment(invoice, use, method='credit', reference='Account credit',
                           gateway_ref=f'CREDIT-{invoice.number}')
    return use


def _is_staff(user):
    if user is None:
        return False
    if user.is_staff or user.is_superuser:
        return True
    return getattr(getattr(user, 'profile', None), 'user_type', '') in ('admin', 'staff')


def _bookings_url():
    from django.urls import reverse
    return reverse('shop:my-bookings')
