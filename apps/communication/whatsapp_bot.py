"""The WhatsApp bot — what happens when a student messages us back.

Notifications already go *out* on WhatsApp (:func:`apps.communication.services.notify`).
This is the other direction: a student replies, and gets a useful answer without
opening the platform. It is deliberately a small, closed set of commands rather
than a conversational assistant — a learner (or parent) on a phone between classes wants
"when is my next test", not a chat.

What it answers
---------------
======================  =====================================================
``help`` / ``menu``     everything below, which is also the reply to anything
                        it does not recognise
``dates`` / ``next``    the next assessment dates from their school's
                        academic calendar
``subjects``            their subjects and whether each one is open
``invoice`` / ``pay``   what is outstanding, and the PDF sent through again
``notices``             their unread notifications
``stop`` / ``mute``     turn WhatsApp notifications off
``start``               turn them back on
======================  =====================================================

Three rules run through all of it:

* **Identify first, answer second.** A reply only ever contains a person's own
  data, and only when the number maps to exactly one account. An unknown number
  — or one shared by two accounts — gets a polite "we can't match this number",
  never a guess. Phone numbers are re-used and re-issued; treating one as proof
  of identity for anything more than "here are your own dates" would be wrong.
* **``stop`` always works.** It is answered before anything else, it needs no
  account, and it is honoured immediately. Somebody asking to be left alone gets
  left alone.
* **Never raise into the webhook.** Meta re-delivers anything that is not
  answered with 200, so an exception here would become an infinite retry loop.
  Failures are logged and turned into an apology.
"""
import logging

from django.utils import timezone

from core import whatsapp

logger = logging.getLogger(__name__)

#: Aliases → command. Kept generous: people type what they think of, and every
#: one of these has been someone's first guess.
COMMANDS = {
    'help': 'help', 'menu': 'help', 'hi': 'help', 'hello': 'help', 'start help': 'help',
    '?': 'help', 'options': 'help', 'commands': 'help',
    'dates': 'dates', 'date': 'dates', 'next': 'dates', 'test': 'dates', 'tests': 'dates',
    'exam': 'dates', 'exams': 'dates', 'calendar': 'dates', 'when': 'dates',
    'modules': 'modules', 'module': 'modules', 'courses': 'modules',
    'subjects': 'modules', 'subject': 'modules',
    'invoice': 'invoice', 'invoices': 'invoice', 'pay': 'invoice', 'payment': 'invoice',
    'balance': 'invoice', 'fees': 'invoice', 'account': 'invoice',
    'notices': 'notices', 'notifications': 'notices', 'unread': 'notices', 'news': 'notices',
    'week': 'week', 'plan': 'week', 'due': 'week', 'todo': 'week', 'this week': 'week',
    'stop': 'stop', 'mute': 'stop', 'unsubscribe': 'stop', 'off': 'stop',
    'start': 'start', 'resume': 'start', 'subscribe': 'start', 'on': 'start',
}

HELP = (
    '*United Church School*\n'
    'Reply with one of these:\n\n'
    '*WEEK* — your week ahead: what is due, open and on\n'
    '*DATES* — your next tests and exams\n'
    '*SUBJECTS* — your subjects and what is open\n'
    '*INVOICE* — what is outstanding, and the PDF again\n'
    '*NOTICES* — your unread notifications\n'
    '*STOP* — no more WhatsApp messages\n\n'
    'Everything else lives on the platform.'
)

UNKNOWN_NUMBER = (
    "We can't match this number to a United Church School account.\n\n"
    'If you are a learner or parent, add this number under *Contact* on your profile and '
    'message us again. Otherwise reply *STOP* and we will not message you again.'
)

AMBIGUOUS_NUMBER = (
    'This number is on more than one account, so we cannot tell who is asking. '
    'Please sign in to the platform instead — or reply *STOP* to stop these messages.'
)


def parse(text):
    """The command in a message, or ``''``.

    Matches the whole message first, then its first word, so "dates please" and
    "DATES" both land on the same place.
    """
    cleaned = (text or '').strip().lower().strip('.!?')
    if not cleaned:
        return ''
    if cleaned in COMMANDS:
        return COMMANDS[cleaned]
    return COMMANDS.get(cleaned.split()[0], '')


def person_for_number(number):
    """``(person, error)`` for a WhatsApp number.

    ``error`` is a ready-to-send reply when the number cannot be resolved to
    exactly one person — nothing is answered on a maybe.
    """
    from apps.accounts.models import Person

    digits = whatsapp.msisdn(number) or (number or '')
    tail = digits[-9:]
    if not tail:
        return None, UNKNOWN_NUMBER

    # Numbers are stored as typed ("+27 82 000 0199"), so match on the last nine
    # digits — the national number, which is what stays the same whether or not
    # somebody typed the country code.
    candidates = [
        person for person in Person.objects.select_related('user', 'contact')
        .filter(contact__primary_phone__isnull=False).exclude(contact__primary_phone='')
        if (whatsapp.msisdn(person.contact.primary_phone) or '').endswith(tail)
    ]
    if not candidates:
        return None, UNKNOWN_NUMBER
    if len(candidates) > 1:
        return None, AMBIGUOUS_NUMBER
    return candidates[0], ''


# ---------------------------------------------------------------------------
# The answers
# ---------------------------------------------------------------------------
def _dates(person):
    """The next few dates from the calendars of the institutions they study at."""
    from apps.learning.models import CalendarEvent

    institution_ids = set(person.programme_enrolments.values_list(
        'programme__institution_id', flat=True))
    if not institution_ids:
        return ('You are not registered for a grade yet, so there are no dates on your '
                'calendar. Finish registering on the platform and they will appear here.')

    events = (CalendarEvent.objects
              .filter(is_published=True, calendar__institution_id__in=institution_ids,
                      start__gte=timezone.now())
              .select_related('programme_module', 'programme', 'calendar__institution')
              .order_by('start')[:6])
    if not events:
        return 'Nothing is on your calendar yet. The school\'s dates go up as they are confirmed.'

    lines = ['*Your next dates*']
    for event in events:
        when = timezone.localtime(event.start).strftime('%a %-d %b')
        days = event.days_away
        countdown = 'today' if days == 0 else ('tomorrow' if days == 1 else f'in {days} days')
        what = event.programme_module.code + ' · ' if event.programme_module_id else ''
        lines.append(f'• {when} — {what}{event.title} ({countdown})')
    return '\n'.join(lines)


def _modules(person):
    """Their modules, and whether each one is open."""
    enrolments = list(person.module_enrolments.select_related(
        'programme_module__programme__institution'))
    if not enrolments:
        return 'You are not registered for any subjects yet.'

    lines = ['*Your subjects*']
    for enrolment in enrolments:
        module = enrolment.programme_module
        if enrolment.is_unlocked:
            if enrolment.status == enrolment.STATUS_TRIAL and enrolment.trial_ends_at:
                days = (timezone.localtime(enrolment.trial_ends_at).date()
                        - timezone.localdate()).days
                state = f'free week, {max(days, 0)} day(s) left'
            else:
                state = 'open'
        else:
            state = 'locked — payment outstanding'
        lines.append(f'• {module.code} — {state}')
    return '\n'.join(lines)


def _invoice(person):
    """What is outstanding, with the PDF sent through again."""
    from apps.finance.models import Invoice

    invoice = (Invoice.objects.filter(customer=person.user)
               .exclude(status=Invoice.STATUS_PAID)
               .order_by('-created_at').first())
    if invoice is None:
        return 'You have nothing outstanding — everything is paid up. 👍'

    reply = (f'*Invoice {invoice.number}*\n'
             f'Total: R{invoice.total:,.2f}\n'
             f'Outstanding: R{invoice.balance:,.2f}\n\n'
             'Sending the PDF now. Pay by EFT using the invoice number as your reference, '
             'or pay online from *Finance* on the platform.')

    # Best effort: if the PDF cannot be produced or sent, they still get the
    # numbers above, which is the part they actually asked for.
    try:
        from apps.finance.pdf import render_invoice_pdf
        pdf = render_invoice_pdf(invoice)
        if hasattr(pdf, 'read'):
            pdf = pdf.read()
        number = whatsapp.number_for(person)
        whatsapp.send_document(number, pdf, f'{invoice.number}.pdf',
                               caption=f'Invoice {invoice.number} — R{invoice.total:,.2f}')
    except Exception:  # pragma: no cover - network / rendering
        logger.exception('whatsapp bot: could not send invoice PDF for %s', invoice.number)
    return reply


def _notices(person):
    """Their unread notifications, newest first."""
    from .models import Notification

    unread = (Notification.objects.filter(recipient=person.user, is_read=False)
              .order_by('-created_at')[:5])
    if not unread:
        return 'Nothing unread. 🎉'
    lines = ['*Unread notifications*']
    for note in unread:
        when = timezone.localtime(note.created_at).strftime('%-d %b')
        lines.append(f'• {when} — {(note.title or note.verb or "Notification")[:80]}')
    lines.append('\nRead them in full on the platform.')
    return '\n'.join(lines)


def _week(person):
    """The same list the Monday summary sends, on demand."""
    from .weekly import educator_lines, student_lines

    user = getattr(person, 'user', None)
    if user is None:
        return 'We could not find your account details.'
    now = timezone.now()
    lines = (educator_lines if person.user_type == 'educator' else student_lines)(user, now)
    if not lines:
        return 'Nothing is due in the next seven days. A good week to get ahead.'
    return '*Your week ahead*\n\n' + '\n'.join(lines)


def _set_notifications(person, on):
    """Turn WhatsApp notification copies on or off for this person."""
    from .models import NotificationPreference

    pref = NotificationPreference.for_user(person.user)
    pref.whatsapp_enabled = on
    pref.save(update_fields=['whatsapp_enabled', 'updated_at'])
    if on:
        return ('WhatsApp notifications are back on. Reply *STOP* at any time to turn '
                'them off again.')
    return ('Done — no more WhatsApp notifications from us. You will still see everything '
            'on the platform and by e-mail.\n\nReply *START* if you change your mind.')


# ---------------------------------------------------------------------------
# Routing
# ---------------------------------------------------------------------------
def reply_to(number, text, *, person=None):
    """Work out the answer to an inbound message.

    Returns ``(reply_text, command)``. Never raises: an unexpected failure comes
    back as an apology, because the alternative is Meta retrying the webhook
    forever.
    """
    command = parse(text)

    # STOP is answered before anything else and without needing an account:
    # somebody asking to be left alone is not made to identify themselves first.
    if command == 'stop':
        if person is None:
            person, _error = person_for_number(number)
        if person is not None:
            return _set_notifications(person, False), command
        return ('Done — we will not message this number again.', command)

    if person is None:
        person, error = person_for_number(number)
        if error:
            return error, command or 'unknown-number'

    try:
        if command == 'dates':
            return _dates(person), command
        if command == 'modules':
            return _modules(person), command
        if command == 'invoice':
            return _invoice(person), command
        if command == 'notices':
            return _notices(person), command
        if command == 'week':
            return _week(person), command
        if command == 'start':
            return _set_notifications(person, True), command
    except Exception:  # pragma: no cover - defensive
        logger.exception('whatsapp bot: %r failed for %s', command, number)
        return ('Something went wrong on our side looking that up. Please try again, '
                'or check the platform.'), command

    # Anything unrecognised gets the menu — the most useful possible reply to
    # someone who has just discovered they can message us at all.
    greeting = f'Hi {person.first_name}!\n\n' if getattr(person, 'first_name', '') else ''
    return greeting + HELP, command or 'help'


def handle_inbound(number, text, *, wa_id='', payload=None):
    """Log an inbound message, answer it, and log the answer.

    Idempotent on ``wa_id``: Meta re-delivers a webhook until it gets a 200, and
    a student should not be answered three times because our first 200 was slow.
    Returns the :class:`~apps.communication.models.WhatsAppMessage` sent back, or
    ``None`` if this message had already been handled.
    """
    from .models import WhatsAppMessage

    number = whatsapp.msisdn(number) or number
    if wa_id and WhatsAppMessage.objects.filter(direction=WhatsAppMessage.IN,
                                                wa_id=wa_id).exists():
        return None

    person, _error = person_for_number(number)
    WhatsAppMessage.objects.create(
        direction=WhatsAppMessage.IN, number=number, person=person, body=text or '',
        wa_id=wa_id, payload=payload or {}, command=parse(text))

    reply, command = reply_to(number, text, person=person)
    sent, reason = whatsapp.send_text(number, reply)
    if not sent:
        logger.warning('whatsapp bot: reply to %s not delivered (%s)', number, reason)

    return WhatsAppMessage.objects.create(
        direction=WhatsAppMessage.OUT, number=number, person=person, body=reply,
        command=command, payload={'delivered': sent, 'reason': reason})
