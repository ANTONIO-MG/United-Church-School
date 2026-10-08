"""A logging handler that turns log records into error events.

This is what gives the log full coverage without touching all ~300 existing
``except`` blocks: every ``logger.exception(...)`` and ``logger.error(...)``
already in the codebase becomes a catalogued, deduplicated event, classified
from the module it came from and the exception that caused it.

Explicitly tagged sites still win — pass ``extra={'error_code': 'CERT-8001'}``
to any log call and this handler uses it instead of guessing.

The handler is deliberately defensive: logging must not raise, and it must not
recurse (writing an event can itself log).
"""

import logging
import threading

_local = threading.local()


class ErrorLogHandler(logging.Handler):
    """Persist WARNING-and-above records as :class:`~apps.diagnostics.models.ErrorEvent`."""

    #: Loggers whose records are ignored — writing an event logs, and logging
    #: that write would call this handler again.
    MUTED_LOGGERS = ('apps.diagnostics', 'django.db.backends', 'django.utils.autoreload')

    def emit(self, record):
        if getattr(_local, 'busy', False):
            return
        if record.name.startswith(self.MUTED_LOGGERS):
            return
        if record.levelno < logging.WARNING:
            return

        _local.busy = True
        try:
            self._store(record)
        except Exception:               # pragma: no cover - never break logging
            pass
        finally:
            _local.busy = False

    def _store(self, record):
        # Imported lazily: handlers are constructed while settings are still
        # loading, long before the app registry is ready.
        from django.apps import apps as django_apps
        if not django_apps.ready:
            return

        from . import services

        exc = record.exc_info[1] if record.exc_info else None
        code = getattr(record, 'error_code', None)
        severity = {
            logging.WARNING: 'warning',
            logging.ERROR: 'error',
            logging.CRITICAL: 'critical',
        }.get(record.levelno, 'error')

        context = dict(getattr(record, 'error_context', None) or {})
        context.setdefault('logger', record.name)
        if not code:
            context.setdefault('auto_classified', True)

        services.report(
            code,
            exc=exc,
            request=getattr(record, 'request', None),
            message=record.getMessage(),
            context=context,
            severity=severity,
            module=record.name if not exc else '',
            function=record.funcName,
            line=record.lineno,
            # Used only when the raising frame is in a module the domain map does
            # not recognise — see services._report.
            domain_hint=record.name,
        )
