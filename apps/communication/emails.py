"""E-mail delivery helpers.

All outbound mail (notifications, announcements, and the auth/verification/
password e-mails that django-allauth sends) is rendered from templates under
``communication/email/`` that extend the branded layout
``communication/email/base_email.html``. Brand/strings come from the central
catalog (:mod:`core.branding`) so e-mails re-brand and translate with everything
else — they're injected into the context explicitly because context processors
don't run for ``render_to_string``.

Send a branded e-mail directly with :func:`send_branded_email`; the rest of the
app uses the typed wrappers below.
"""

import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from core.branding import strings as _strings

logger = logging.getLogger(__name__)


def _base_context(extra=None):
    catalog = _strings()
    ctx = {
        'brand': catalog.get('brand', {}),
        'strings': catalog,
        'site_url': getattr(settings, 'SITE_URL', ''),
        # Always present so a template that does ``{{ x|default:subject }}``
        # never raises when the caller didn't pass one (a missing *filter
        # argument* is not swallowed by string_if_invalid).
        'subject': '',
    }
    if extra:
        ctx.update(extra)
    return ctx


def _email_inline_map(brand):
    """Branding images to embed inline (CID). Embedding them means they render
    even when SITE_URL isn't publicly reachable (local dev on 127.0.0.1) or the
    recipient's client blocks remote images — which is why they looked broken."""
    return {
        # School branding: the wide crest + wordmark as the header banner, the
        # crest mark beside the help line (both from static/images/brand/, embedded inline).
        # There is deliberately no bottom strip image — it rendered as a bare
        # white bar under the card.
        'header': 'images/brand/ucs-logo.png',
        'logo': brand.get('logo') or 'images/brand/ucs-mark.png',
        'ig': 'email/social-instagram.png',
        'tw': 'email/social-twitter.png',
    }


def _attach_inline_image(msg, static_path, cid):
    """Attach a static image as an inline (Content-ID) part; no-op if missing."""
    import mimetypes
    import os
    from email.mime.image import MIMEImage

    from django.contrib.staticfiles import finders
    abspath = finders.find(static_path)
    if not abspath or not os.path.exists(abspath):
        return False
    try:
        with open(abspath, 'rb') as fh:
            data = fh.read()
        subtype = (mimetypes.guess_type(abspath)[0] or 'image/png').split('/')[-1]
        img = MIMEImage(data, _subtype=subtype)
        img.add_header('Content-ID', f'<{cid}>')
        img.add_header('Content-Disposition', 'inline', filename=os.path.basename(abspath))
        msg.attach(img)
        return True
    except Exception:  # pragma: no cover
        return False


def send_branded_email(subject, recipients, template, context=None, *, from_email=None,
                       reply_to=None, attachments=None):
    """Render ``communication/email/<template>.{html,txt}`` and send it.

    ``recipients`` is a string or an iterable of e-mail addresses. The ``.txt``
    body is optional — if the template is missing, the HTML is stripped to text.
    ``attachments`` is an optional iterable of ``(filename, content, mimetype)``
    tuples (e.g. a PDF invoice). Returns ``True`` on success, ``False`` if
    nothing was sent (no recipients / delivery error). Never raises.
    """
    if isinstance(recipients, str):
        recipients = [recipients]
    recipients = [r for r in recipients if r]
    if not recipients:
        return False

    ctx = _base_context(context)
    ctx.setdefault('subject', subject)
    # Embed branding images inline so they render in every client; the template
    # references them as {{ inline.logo }} etc. (falls back to email_asset URLs).
    inline_map = _email_inline_map(ctx.get('brand') or {})
    ctx['inline'] = {name: f'cid:{name}' for name in inline_map}
    from_email = from_email or getattr(settings, 'DEFAULT_FROM_EMAIL', None)

    try:
        html_body = render_to_string(f'communication/email/{template}.html', ctx)
    except Exception:  # pragma: no cover
        logger.exception('Missing/invalid e-mail template %s.html', template)
        return False

    try:
        text_body = render_to_string(f'communication/email/{template}.txt', ctx)
    except Exception:
        text_body = strip_tags(html_body)

    try:
        msg = EmailMultiAlternatives(subject, text_body, from_email, recipients, reply_to=reply_to)
        msg.attach_alternative(html_body, 'text/html')
        for name, path in inline_map.items():
            _attach_inline_image(msg, path, name)
        for att in (attachments or []):
            if att and att[1]:            # (filename, content, mimetype); skip empty content
                msg.attach(*att)
        msg.send()
        return True
    except Exception:  # pragma: no cover
        logger.exception('Failed to send e-mail %r to %s', subject, recipients)
        return False


# ---------------------------------------------------------------------------
# Typed wrappers used by the rest of the app
# ---------------------------------------------------------------------------
def send_notification_email(note):
    """E-mail a single :class:`~apps.communication.models.Notification`."""
    email = getattr(note.recipient, 'email', '')
    if not email:
        return False
    return send_branded_email(
        note.title or note.verb or 'Notification',
        email,
        'notification',
        {'notification': note, 'recipient': note.recipient},
    )


def _email_of(user):
    return getattr(user, 'email', '') if user else ''


def send_general_email(recipients, heading, body, *, action_url=None, action_label=None,
                       subject=None, recipient=None):
    """A general communication / general user e-mail."""
    return send_branded_email(subject or heading, recipients, 'general', {
        'heading': heading, 'body': body, 'action_url': action_url,
        'action_label': action_label, 'recipient': recipient,
    })


def send_event_reminder(user, *, event_title, event_when, event_location='', action_url=''):
    return send_branded_email(f'Upcoming: {event_title}', _email_of(user), 'event-upcoming', {
        'recipient': user, 'event_title': event_title, 'event_when': event_when,
        'event_location': event_location, 'action_url': action_url,
    })


def send_session_scheduled(user, *, session_title, session_when='', join_url=''):
    return send_branded_email(f'Session scheduled: {session_title}', _email_of(user),
                              'session-scheduled', {
        'recipient': user, 'session_title': session_title,
        'session_when': session_when, 'join_url': join_url,
    })


def send_invoice_email(invoice, pay_url):
    return send_branded_email(f'Invoice {invoice.number} — payment requested',
                              _email_of(invoice.customer), 'invoice',
                              {'invoice': invoice, 'pay_url': pay_url})


def send_invoice_reminder(invoice, pay_url, *, stage='manual'):
    """A polite nudge about an unpaid invoice, with the pay link."""
    if stage == 'before_3':
        subject = f'Reminder: invoice {invoice.number} is due in 3 days'
    elif stage == 'due':
        subject = f'Invoice {invoice.number} is due today'
    elif stage == 'after_7':
        subject = f'Invoice {invoice.number} is overdue'
    else:
        subject = f'Reminder: invoice {invoice.number}'
    return send_branded_email(subject, _email_of(invoice.customer), 'invoice-reminder',
                              {'invoice': invoice, 'pay_url': pay_url, 'stage': stage})


def send_estimate_email(estimate, view_url):
    return send_branded_email(f'Estimate {estimate.number} from us',
                              _email_of(estimate.customer), 'estimate',
                              {'estimate': estimate, 'view_url': view_url})


def send_purchase_email(invoice, pay_url=''):
    return send_branded_email(f'Order confirmed — {invoice.number}',
                              _email_of(invoice.customer), 'purchase',
                              {'invoice': invoice, 'pay_url': pay_url})


def send_payment_made(invoice):
    """The receipt, with the receipt PDF attached as the record of payment.

    The PDF is best effort: if it will not render, the e-mail still goes — a
    buyer who paid must hear that they paid.
    """
    attachments = []
    try:
        from apps.finance.pdf import render_receipt_pdf
        pdf = render_receipt_pdf(invoice)
        if pdf:
            attachments.append((f'Receipt-{invoice.number}.pdf', pdf, 'application/pdf'))
    except Exception:  # pragma: no cover
        logger.exception('receipt PDF failed for %s', invoice.number)
    return send_branded_email(f'Receipt — Invoice {invoice.number} paid',
                              _email_of(invoice.customer), 'payment-made', {'invoice': invoice},
                              attachments=attachments)


def send_welcome_to_class(user, *, course=None, modules=None, action_url=''):
    return send_branded_email('Welcome to your course', _email_of(user), 'welcome-class', {
        'recipient': user, 'course': course,
        'modules': modules or [], 'action_url': action_url,
    })


def send_registration_summary_email(person, *, institution='', programme='', modules=(),
                                    total=0, currency='R', paid=False, trial_ends=None,
                                    login_url='', attachments=None,
                                    attachment_label='document'):
    """What the student signed up for, with the money document attached.

    Carries no personal detail on purpose — not the e-mail address, not the
    phone number. The figures are not itemised here either: they are in the
    attached PDF (an invoice when they will pay by EFT, a proof of payment when
    the card has already cleared), which is the thing worth keeping.
    """
    user = getattr(person, 'user', None)
    if not _email_of(user):
        return False
    school = (_strings().get('brand', {}).get('name') or 'United Church School')
    subject = (f'Welcome to {school} — your registration summary' if paid else
               f'Welcome to {school} — your registration summary and invoice')
    return send_branded_email(
        subject, _email_of(user), 'registration-summary', {
            'person': person,
            'first_name': person.first_name or user.get_short_name() or user.get_username(),
            'institution': institution, 'programme': programme,
            'modules': list(modules), 'total': total, 'currency': currency,
            'paid': paid, 'trial_ends': trial_ends,
            'attachment_label': attachment_label, 'login_url': login_url,
        }, attachments=attachments)


def send_trial_expiry_reminder(person, invoice, *, days_left=1, trial_ends=None,
                               pay_url='', modules=(), attachments=None):
    """The nudge a day before a free week runs out on an unpaid invoice."""
    user = getattr(person, 'user', None)
    if not _email_of(user):
        return False
    return send_branded_email(
        f'Your free week ends tomorrow — invoice {invoice.number} is still open',
        _email_of(user), 'trial-ending', {
            'person': person,
            'first_name': person.first_name or user.get_short_name() or user.get_username(),
            'invoice': invoice, 'days_left': days_left, 'trial_ends': trial_ends,
            'pay_url': pay_url, 'modules': list(modules),
        }, attachments=attachments)


def send_password_changed(user, *, login_url=''):
    return send_branded_email('Your password was changed', _email_of(user),
                              'password-changed', {'account': user, 'login_url': login_url})


def email_announcement(announcement, recipients):
    """E-mail an :class:`~apps.communication.models.Announcement` to ``recipients``
    (an iterable of users). Sends one message with all addresses in ``Bcc`` via
    the template; here we keep it simple and send per-recipient for personalised
    greetings — callers run this in the background-ish path of ``send_announcement``."""
    sent_any = False
    for user in recipients:
        email = getattr(user, 'email', '')
        if not email:
            continue
        if send_branded_email(
            announcement.title,
            email,
            'announcement',
            {'announcement': announcement, 'recipient': user},
        ):
            sent_any = True
    return sent_any


#: The most a broadcast e-mail carries as real attachments. Above this (or for a
#: video) the e-mail lists the files and links to the notification instead.
ANNOUNCEMENT_ATTACH_LIMIT = 10 * 1024 * 1024


def announcement_email_files(announcement):
    """``(filename, content, mimetype)`` tuples for a broadcast's e-mail copy.

    Read once per broadcast and reused for every recipient. Videos are never
    attached, and nothing is attached if the documents together exceed
    :data:`ANNOUNCEMENT_ATTACH_LIMIT` — mail servers refuse large messages.
    """
    import mimetypes

    docs = [a for a in announcement.attachments.all() if a.kind != a.KIND_VIDEO]
    if not docs or sum(a.size or 0 for a in docs) > ANNOUNCEMENT_ATTACH_LIMIT:
        return []
    files = []
    for att in docs:
        try:
            with att.file.open('rb') as fh:
                content = fh.read()
        except Exception:  # pragma: no cover - a missing file just isn't attached
            logger.warning('Announcement attachment %s could not be read', att.pk)
            continue
        name = att.original_name or att.file.name.rsplit('/', 1)[-1]
        files.append((name, content, mimetypes.guess_type(name)[0] or 'application/octet-stream'))
    return files


def email_announcement_copy(announcement, note, files=None):
    """E-mail one recipient their copy of a broadcast.

    The button opens *their* notification, where the pictures, the video and
    every attachment are shown — the e-mail cannot play a video.
    """
    from django.urls import reverse

    user = note.recipient
    if not _email_of(user):
        return False
    base = getattr(settings, 'SITE_URL', '').rstrip('/')
    open_url = base + reverse('communication:notification-detail', args=[note.pk])
    link_url = announcement.url or ''
    if link_url.startswith('/'):
        link_url = base + link_url
    return send_branded_email(announcement.title, _email_of(user), 'announcement', {
        'announcement': announcement, 'recipient': user, 'open_url': open_url, 'link_url': link_url,
        'attachment_list': list(announcement.attachments.all()),
        'attached': bool(files),
    }, attachments=files)
