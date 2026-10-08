"""WhatsApp — the platform's second channel out.

Everything the LMS sends to a person's phone goes through here: notification
copies (:func:`apps.communication.services.notify`) and the registration invoice
PDF (:mod:`apps.accounts.registration_billing`). One transport, one place to
configure, one place to look when a message did not arrive.

The number is the one the student gave on the contact step of registration
(``PersonContact.primary_phone``) — the form already normalises it to
``+27 82…``, and :func:`msisdn` turns that into the digits-only form the API
wants. WhatsApp is the number people actually answer, which is the whole point
of having it alongside e-mail.

Configuration (all via the environment — see ``.env``)::

    WHATSAPP_ENABLED=True
    WHATSAPP_PHONE_NUMBER_ID=...     # Meta → WhatsApp → API setup
    WHATSAPP_ACCESS_TOKEN=...        # permanent system-user token
    WHATSAPP_API_VERSION=v21.0       # optional
    DEFAULT_DIAL_CODE=27             # assumed when a stored number has no code

**Dormant until configured.** With ``WHATSAPP_ENABLED`` off — the default, and
the case on every dev machine — nothing is sent, nothing raises, and every
function reports why. That is deliberate: an unconfigured integration must never
break a notification, a registration or a request, and a developer's test data
has no business messaging real phone numbers.

**A note on the 24-hour window.** Meta only allows free-form messages to someone
who has messaged you in the last 24 hours; outside that window a business must
send an approved *template*. Notification copies here are sent as free-form text,
so in production set :data:`WHATSAPP_TEMPLATE_NAME` to an approved template and
the sender will use it instead. Without it, messages to people who have not
recently replied will be rejected by Meta — which is logged, not raised.
"""
import json
import logging
import urllib.error
import urllib.request
import uuid

from django.conf import settings

logger = logging.getLogger(__name__)

GRAPH = 'https://graph.facebook.com'


def _setting(name, default=None):
    return getattr(settings, name, default)


def enabled():
    """True when there is enough configuration to actually send something."""
    return bool(_setting('WHATSAPP_ENABLED')
                and _setting('WHATSAPP_PHONE_NUMBER_ID')
                and _setting('WHATSAPP_ACCESS_TOKEN'))


def msisdn(phone):
    """``+27 82 000 0199`` → ``27820000199``; ``''`` when it cannot be dialled.

    A local number (``082…``) carries no country code, so the configured default
    is prepended rather than the number being sent somewhere unpredictable.
    """
    digits = ''.join(ch for ch in (phone or '') if ch.isdigit())
    if not digits:
        return ''
    if digits.startswith('00'):
        digits = digits[2:]
    if digits.startswith('0'):
        digits = str(_setting('DEFAULT_DIAL_CODE', '27')) + digits[1:]
    return digits if len(digits) >= 10 else ''


def number_for(user_or_person):
    """The WhatsApp number on file for a user or a Person, or ``''``.

    Accepts either so callers do not have to care which they are holding — a
    notification has a ``User``, the registration flow has a ``Person``.
    """
    person = getattr(user_or_person, 'profile', None) or user_or_person
    contact = getattr(person, 'contact', None)
    return msisdn(getattr(contact, 'primary_phone', ''))


def _post_json(path, payload):
    version = _setting('WHATSAPP_API_VERSION', 'v21.0')
    request = urllib.request.Request(
        f'{GRAPH}/{version}/{path}', data=json.dumps(payload).encode(), method='POST',
        headers={'Authorization': f"Bearer {_setting('WHATSAPP_ACCESS_TOKEN')}",
                 'Content-Type': 'application/json'})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode() or '{}')


def _send(payload, *, what):
    """POST a message payload, turning every failure into ``(False, reason)``.

    Nothing in this module raises. A phone that cannot be reached is a thing to
    log and carry on from, not a reason to fail whatever the user was doing.
    """
    if not enabled():
        return False, 'WhatsApp is not configured on this installation'
    try:
        _post_json(f"{_setting('WHATSAPP_PHONE_NUMBER_ID')}/messages", payload)
        return True, ''
    except urllib.error.HTTPError as exc:          # pragma: no cover - network
        detail = exc.read().decode(errors='ignore')[:300]
        logger.warning('whatsapp: %s to %s rejected: %s', what, payload.get('to'), detail)
        return False, 'WhatsApp rejected the message'
    except Exception:                              # pragma: no cover - network
        logger.exception('whatsapp: %s to %s could not be sent', what, payload.get('to'))
        return False, 'WhatsApp could not be reached'


def send_text(number, body):
    """Send a plain message. Returns ``(sent, reason)``.

    Where :data:`WHATSAPP_TEMPLATE_NAME` is configured the message goes as that
    approved template (with the body as its single parameter), which is what
    Meta requires outside the 24-hour customer-service window.
    """
    number = msisdn(number) if not str(number).isdigit() else str(number)
    if not number:
        return False, 'no usable WhatsApp number'

    template = _setting('WHATSAPP_TEMPLATE_NAME', '')
    if template:
        payload = {
            'messaging_product': 'whatsapp', 'to': number, 'type': 'template',
            'template': {
                'name': template,
                'language': {'code': _setting('WHATSAPP_TEMPLATE_LANG', 'en')},
                'components': [{'type': 'body',
                                'parameters': [{'type': 'text', 'text': body[:1000]}]}],
            },
        }
    else:
        payload = {'messaging_product': 'whatsapp', 'to': number, 'type': 'text',
                   'text': {'preview_url': False, 'body': body[:4000]}}
    return _send(payload, what='message')


def upload_document(data, filename, mime='application/pdf'):
    """Upload a document and return its media id, or ``None``.

    The Cloud API takes documents by media id rather than by URL, so anything
    being sent has to be uploaded first. This is the only multipart request in
    the codebase, so it is assembled by hand rather than adding a dependency.
    """
    if not enabled():
        return None
    phone_id = _setting('WHATSAPP_PHONE_NUMBER_ID')
    version = _setting('WHATSAPP_API_VERSION', 'v21.0')
    boundary = f'----ucs{uuid.uuid4().hex}'
    parts = []

    def field(name, value):
        parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n'
                     f'{value}\r\n'.encode())

    field('messaging_product', 'whatsapp')
    field('type', mime)
    parts.append(
        f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f'Content-Type: {mime}\r\n\r\n'.encode() + data + b'\r\n')
    parts.append(f'--{boundary}--\r\n'.encode())

    request = urllib.request.Request(
        f'{GRAPH}/{version}/{phone_id}/media', data=b''.join(parts), method='POST',
        headers={'Authorization': f"Bearer {_setting('WHATSAPP_ACCESS_TOKEN')}",
                 'Content-Type': f'multipart/form-data; boundary={boundary}'})
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.loads(response.read().decode() or '{}').get('id')
    except Exception:                              # pragma: no cover - network
        logger.exception('whatsapp: upload of %s failed', filename)
        return None


def send_document(number, data, filename, *, caption='', mime='application/pdf'):
    """Upload a file and send it. Returns ``(sent, reason)``."""
    number = msisdn(number) if not str(number).isdigit() else str(number)
    if not number:
        return False, 'no usable WhatsApp number'
    if not enabled():
        return False, 'WhatsApp is not configured on this installation'

    media_id = upload_document(data, filename, mime)
    if not media_id:
        return False, 'WhatsApp did not accept the file'
    return _send({
        'messaging_product': 'whatsapp', 'to': number, 'type': 'document',
        'document': {'id': media_id, 'filename': filename, 'caption': caption[:1000]},
    }, what='document')
