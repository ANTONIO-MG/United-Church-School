"""Reporting an error: ``report()``, ``capture()`` and ``@errorcode``.

Three ways in, deliberately:

* :func:`report` — you caught something and you know exactly what it means.
* :func:`capture` — a ``with`` block that tags whatever escapes it.
* :func:`errorcode` — a decorator for a whole view or service function.

Plus a fourth that needs no code changes at all: :mod:`apps.diagnostics.logging`
turns existing ``logger.exception`` calls into events, auto-classified by
:func:`classify`. That is what makes the log cover the whole codebase rather than
only the parts that have been tagged by hand.

**Reporting must never be able to break the request it is reporting on.** Every
public function here swallows its own failures — an error logger that raises
turns a handled problem into a 500.
"""

import logging
import traceback as tb_module
import uuid
from contextlib import contextmanager
from functools import wraps

from . import catalog

logger = logging.getLogger('apps.diagnostics')

# Module prefix → catalog domain. Longest match wins, so a submodule can be more
# specific than its package.
MODULE_DOMAINS = (
    ('apps.accounts.middleware', 'AUTH'),
    ('apps.accounts.adapters', 'AUTH'),
    ('apps.accounts.resources', 'RPRT'),
    ('apps.accounts', 'USER'),
    ('apps.communication.broadcast', 'NOTF'),
    ('apps.communication.auto', 'NOTF'),
    ('apps.communication.weekly', 'NOTF'),
    ('apps.communication.feed', 'FEED'),
    ('apps.communication.emails', 'MAIL'),
    ('apps.communication.api', 'CHAT'),
    ('apps.communication.serializers', 'CHAT'),
    ('apps.communication', 'CHAT'),
    ('apps.msteams', 'INTG'),
    ('apps.learning', 'LRN'),
    ('apps.assessments', 'ASMT'),
    ('apps.reports.certificate_render', 'CERT'),
    ('apps.reports.certificates', 'CERT'),
    ('apps.reports', 'RPRT'),
    ('apps.analytics', 'ANLT'),
    ('apps.tasks', 'TASK'),
    ('apps.shop', 'SHOP'),
    ('apps.finance', 'FIN'),
    ('apps.ai_assistant', 'AI'),
    ('apps.scheduler', 'SCHD'),
    ('apps.livesessions', 'MEET'),
    ('apps.staffdesk.backups', 'BKP'),
    ('apps.staffdesk', 'DESK'),
    ('apps.revision', 'REV'),
    ('apps.myhub', 'HUB'),
    ('core.branding', 'SYS'),
    ('core', 'SYS'),
    ('config', 'SYS'),
)

# Exception type name → cause class digit. Anything unlisted is 9 (unexpected),
# which is the honest answer and keeps those visible for triage.
EXCEPTION_CAUSES = {
    'ValidationError': 1,
    'ValueError': 1,
    'TypeError': 1,
    'KeyError': 1,
    'IndexError': 1,
    'InvalidOperation': 1,
    'DecimalException': 1,
    'MultiValueDictKeyError': 1,
    'UnicodeDecodeError': 1,
    'PermissionDenied': 2,
    'SuspiciousOperation': 2,
    'DisallowedHost': 2,
    'DisallowedRedirect': 2,
    'Http404': 3,
    'DoesNotExist': 3,
    'ObjectDoesNotExist': 3,
    'FileNotFoundError': 3,
    'MultipleObjectsReturned': 4,
    'ConnectionError': 5,
    'ConnectTimeout': 5,
    'ReadTimeout': 5,
    'Timeout': 5,
    'HTTPError': 5,
    'RequestException': 5,
    'SMTPException': 5,
    'SMTPAuthenticationError': 5,
    'SSLError': 5,
    'URLError': 5,
    'IntegrityError': 6,
    'DataError': 6,
    'OperationalError': 6,
    'DatabaseError': 6,
    'ImproperlyConfigured': 7,
    'ImportError': 7,
    'ModuleNotFoundError': 7,
    'AttributeError': 9,
    'OSError': 8,
    'IOError': 8,
    'PermissionError': 8,
    'SuspiciousFileOperation': 8,
}


def domain_for_module(module):
    """Catalog prefix for a dotted module path (longest prefix wins)."""
    module = module or ''
    best, best_len = 'SYS', -1
    for candidate, prefix in MODULE_DOMAINS:
        if (module == candidate or module.startswith(candidate + '.')) and len(candidate) > best_len:
            best, best_len = prefix, len(candidate)
    return best


def classify(exc=None, module=''):
    """Best-effort code for an untagged failure: ``<DOMAIN>-9xxx``-style.

    Returns a *real* catalog code when one covers the situation, otherwise the
    generic unclassified code — never a code the dictionary cannot explain.
    """
    domain = domain_for_module(module)
    cause = EXCEPTION_CAUSES.get(type(exc).__name__, 9) if exc is not None else 9

    def in_domain(wanted_cause):
        return sorted(code for code in catalog.ERRORS
                      if catalog.prefix_of(code) == domain
                      and catalog.cause_of(code) == wanted_cause)

    # Best: a documented code in the right domain AND the right cause class.
    exact = in_domain(cause)
    if exact:
        return exact[0]
    # Next best: the domain's "unexpected" bucket. Staying in the domain keeps
    # the one thing we did know — which part of the platform failed — instead of
    # throwing it away and falling all the way back to SYS.
    fallback = in_domain(9)
    if fallback:
        return fallback[0]
    return catalog.UNKNOWN


def _describe_user(request):
    user = getattr(request, 'user', None) if request is not None else None
    if user is None or not getattr(user, 'is_authenticated', False):
        return None, ''
    try:
        from core.utils import display_name
        return user, (display_name(user) or '')[:200]
    except Exception:
        return user, ''


def _client_ip(request):
    if request is None:
        return None
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if forwarded:
        return forwarded.split(',')[0].strip()[:45] or None
    return request.META.get('REMOTE_ADDR') or None


def _frame_of(exc):
    """(module, function, line) of the deepest frame in this project's code.

    The reporting machinery itself is skipped: ``capture()`` is a context
    manager, so its own frame is in the traceback of everything it tags, and
    reporting every error against apps.diagnostics would make the log useless.
    """
    tb = getattr(exc, '__traceback__', None)
    module = function = ''
    line = None
    while tb is not None:
        frame = tb.tb_frame
        name = frame.f_globals.get('__name__', '')
        if name.startswith(('apps.', 'core.', 'config.')) and not name.startswith(
                ('apps.diagnostics.services', 'core.errors')):
            module, function, line = name, frame.f_code.co_name, tb.tb_lineno
        tb = tb.tb_next
    return module, function, line


def report(code=None, exc=None, request=None, *, message='', context=None,
           severity=None, module='', function='', line=None, domain_hint=''):
    """Record an error against ``code`` and return the stored event (or ``None``).

    Safe to call from anywhere, including an ``except`` block that is about to
    re-raise. Never raises.
    """
    try:
        return _report(code, exc, request, message, context, severity,
                       module, function, line, domain_hint)
    except Exception:                                   # pragma: no cover
        # Last line of defence: the error logger must not become the error.
        logger.exception('diagnostics: could not record an error event')
        return None


def _report(code, exc, request, message, context, severity, module, function, line,
            domain_hint=''):
    from django.utils import timezone

    from .models import ErrorEvent, fingerprint

    frame_module, frame_function, frame_line = _frame_of(exc) if exc is not None else ('', '', None)
    module = module or frame_module
    function = function or frame_function
    line = line or frame_line

    if not code:
        code = classify(exc, module)
        # The deepest project frame is usually the right module — but a helper
        # raising inside a shared utility (or a test) lands in one the domain map
        # does not recognise. The logger's own name is the second-best signal.
        if catalog.prefix_of(code) == 'SYS' and domain_hint:
            hinted = classify(exc, domain_hint)
            if catalog.prefix_of(hinted) != 'SYS':
                code = hinted
    spec = catalog.get(code)
    severity = severity or spec.severity

    exception_type = type(exc).__name__ if exc is not None else ''
    text = (message or (str(exc) if exc is not None else '') or spec.title)[:4000]

    trace = ''
    if exc is not None and getattr(exc, '__traceback__', None) is not None:
        trace = ''.join(tb_module.format_exception(type(exc), exc, exc.__traceback__))[-16000:]

    user, user_label = _describe_user(request)
    view_name = ''
    if request is not None:
        match = getattr(request, 'resolver_match', None)
        if match is not None and match.url_name:
            view_name = f'{match.namespace}:{match.url_name}' if match.namespace else match.url_name

    key = fingerprint(code, module, function, exception_type)
    now = timezone.now()

    event, created = ErrorEvent.objects.get_or_create(
        fingerprint=key,
        defaults={
            'code': code, 'severity': severity, 'message': text,
            'exception_type': exception_type, 'traceback': trace,
            'context': _safe_context(context), 'module': module, 'function': function,
            'line': line, 'path': (getattr(request, 'path', '') or '')[:500],
            'method': (getattr(request, 'method', '') or '')[:10],
            'view_name': view_name[:200], 'user': user, 'user_label': user_label,
            'ip_address': _client_ip(request),
            'first_seen': now, 'last_seen': now,
            'reference': uuid.uuid4().hex[:12].upper(),
        },
    )
    if not created:
        # Same problem again: bump the counter and keep the newest detail.
        # A resolved error that recurs is reopened — silently re-closing it is
        # how a "fixed" bug stays broken in production.
        event.count = models_f_increment(event)
        event.last_seen = now
        event.message = text
        event.traceback = trace or event.traceback
        event.severity = severity
        if context:
            merged = dict(event.context or {})
            merged.update(_safe_context(context))
            event.context = merged
        if request is not None:
            event.path = (getattr(request, 'path', '') or '')[:500]
            event.method = (getattr(request, 'method', '') or '')[:10]
            event.user = user or event.user
            event.user_label = user_label or event.user_label
            event.ip_address = _client_ip(request) or event.ip_address
        if event.status == ErrorEvent.STATUS_RESOLVED:
            event.status = ErrorEvent.STATUS_OPEN
            event.resolved_at = None
        event.save()
    return event


def models_f_increment(event):
    """Increment in Python but from the freshly-read value.

    An F() expression would be race-safe but leaves ``count`` as a deferred
    object on the instance, which the caller then has to refresh before reading.
    Errors are not a hot write path, so clarity wins here.
    """
    return (event.count or 0) + 1


def _safe_context(context):
    """JSON-safe context, with obvious secrets removed.

    Error context is read by developers and stored indefinitely; a password or
    token that lands here has effectively been written to a permanent log.
    """
    if not context:
        return {}
    redact = ('password', 'token', 'secret', 'authorization', 'cookie', 'csrf',
              'api_key', 'apikey', 'client_secret', 'private')
    clean = {}
    for key, value in dict(context).items():
        name = str(key)[:60]
        if any(word in name.lower() for word in redact):
            clean[name] = '[redacted]'
            continue
        try:
            import json
            json.dumps(value)
            clean[name] = value
        except (TypeError, ValueError):
            clean[name] = str(value)[:500]
    return clean


# ---------------------------------------------------------------------------
# Ergonomics
# ---------------------------------------------------------------------------
@contextmanager
def capture(code, request=None, *, reraise=True, context=None, message=''):
    """Tag anything raised inside the block with ``code``.

        with capture('CERT-8001', request, reraise=False):
            data = render_png(cert)

    ``reraise=False`` swallows the exception once it is recorded — use it only
    where the caller genuinely has a fallback.
    """
    try:
        yield
    except Exception as exc:
        report(code, exc, request, context=context, message=message)
        if reraise:
            raise


def note(code, request=None, **context):
    """Record an expected, handled condition — no exception, nothing raised.

    For the many refusals that are *correct* behaviour (not a member of that
    chat, assessment is closed, upload rejected). They are not bugs, but a spike
    in one of them is exactly the signal that something upstream has broken, so
    they belong in the log at their catalogued severity.
    """
    return report(code, request=request, context=context or None)


def fail(code, message='', request=None, *, exc_class=None, **context):
    """Record the error and raise it, with the code attached to the exception.

        fail('CERT-1001', 'This certificate has no holder name.', request)

    The raised message ends with the code in brackets so that whatever renders
    it — a form error, a toast, an API body — gives the user something exact to
    quote to support without the developer having to remember to add it.
    """
    from django.core.exceptions import ValidationError

    spec = catalog.get(code)
    text = f'{(message or spec.title).rstrip(".")} ({code})'
    exc = (exc_class or ValidationError)(text)
    exc.error_code = code
    report(code, exc=exc, request=request, message=text, context=context or None)
    raise exc


def errorcode(code, *, reraise=True, context=None):
    """Decorator form of :func:`capture` for a view or service function.

        @errorcode('LRN-8001')
        def export_module(request, module_id):
            ...

    The request is picked up automatically when the wrapped function is a view
    whose first argument is an ``HttpRequest``.
    """
    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as exc:
                request = args[0] if args and hasattr(args[0], 'META') else None
                report(code, exc, request,
                       context=dict(context or {}, callable=func.__qualname__))
                if reraise:
                    raise
                return None
        wrapper.error_code = code          # readable by the coverage checker
        return wrapper
    return decorate
