"""The WhatsApp webhook — Meta's end of the conversation.

Two endpoints on one URL, which is how the Cloud API works:

* **GET** — the subscription handshake. Meta calls it once when you point a
  webhook at us and echoes back ``hub.challenge`` if the verify token matches.
* **POST** — every inbound message and delivery receipt, forever.

This is an unauthenticated, publicly-reachable endpoint, so it is written to be
suspicious of what it receives:

* **Every POST is signature-checked** against ``WHATSAPP_APP_SECRET`` using the
  ``X-Hub-Signature-256`` header, compared in constant time. Without a secret
  configured the endpoint refuses everything rather than trusting the internet —
  a webhook that processes unsigned payloads is a stranger's remote control over
  student data.
* **It always answers 200** once the signature is good. Meta re-delivers
  anything else, so an error we return becomes an infinite retry; failures are
  logged instead and the message is dropped.
* **It does the smallest possible amount of work** before answering, and
  everything it does is idempotent on Meta's message id.
"""
import hashlib
import hmac
import json
import logging

from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from . import whatsapp_bot

logger = logging.getLogger(__name__)


def _valid_signature(request):
    """True when the body really came from Meta.

    ``X-Hub-Signature-256`` is HMAC-SHA256 of the raw body keyed with the app
    secret. No secret configured → nothing is valid, deliberately: the safe
    failure for an unconfigured webhook is to accept nothing at all.
    """
    secret = getattr(settings, 'WHATSAPP_APP_SECRET', '')
    if not secret:
        logger.warning('whatsapp webhook: WHATSAPP_APP_SECRET is not set — rejecting')
        return False

    header = request.headers.get('X-Hub-Signature-256', '')
    if not header.startswith('sha256='):
        return False
    expected = hmac.new(secret.encode(), request.body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, header.split('=', 1)[1])


def _messages(payload):
    """Yield ``(number, text, wa_id, raw)`` for each inbound text message.

    Meta's envelope is deeply nested and carries delivery receipts and status
    updates in the same shape as messages, so everything that is not a text
    message from a person is skipped here rather than confusing the bot.
    """
    for entry in payload.get('entry', []) or []:
        for change in entry.get('changes', []) or []:
            value = change.get('value') or {}
            for message in value.get('messages', []) or []:
                if message.get('type') != 'text':
                    # Images, audio, buttons: acknowledged, not understood. The
                    # sender still gets the menu back.
                    yield (message.get('from', ''), '', message.get('id', ''), message)
                    continue
                yield (message.get('from', ''),
                       (message.get('text') or {}).get('body', ''),
                       message.get('id', ''), message)


@csrf_exempt
@require_http_methods(['GET', 'POST'])
def webhook(request):
    """Meta's WhatsApp Cloud API webhook."""
    if request.method == 'GET':
        # Subscription handshake. Compared in constant time — the token is a
        # shared secret, and a timing oracle on it is free to exploit.
        token = getattr(settings, 'WHATSAPP_VERIFY_TOKEN', '')
        mode = request.GET.get('hub.mode', '')
        given = request.GET.get('hub.verify_token', '')
        if mode == 'subscribe' and token and hmac.compare_digest(token, given):
            return HttpResponse(request.GET.get('hub.challenge', ''), content_type='text/plain')
        logger.warning('whatsapp webhook: verification refused (mode=%r)', mode)
        return HttpResponseForbidden('verification failed')

    if not _valid_signature(request):
        return HttpResponseForbidden('bad signature')

    try:
        payload = json.loads(request.body.decode() or '{}')
    except ValueError:
        logger.warning('whatsapp webhook: body was not JSON')
        return HttpResponse('ok')          # 200, or Meta retries it forever

    for number, text, wa_id, raw in _messages(payload):
        if not number:
            continue
        try:
            whatsapp_bot.handle_inbound(number, text, wa_id=wa_id, payload=raw)
        except Exception:  # pragma: no cover - defensive
            logger.exception('whatsapp webhook: could not handle message from %s', number)

    return HttpResponse('ok')
