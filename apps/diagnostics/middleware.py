"""Catch what nothing else did.

``process_exception`` sees every exception that escapes a view. Recording it
here means an unhandled 500 still arrives in the log with a code (``SYS-9001``)
and a **reference** the user can quote — which turns "the site broke" into a
row a developer can open.

The middleware never suppresses the exception: Django's own handling still runs,
so DEBUG still shows the technical page and production still returns the 500.
"""

import logging

logger = logging.getLogger('apps.diagnostics')

#: Exceptions that are normal control flow rather than faults. Logging these
#: would bury real errors under 404s and redirects.
IGNORED = (
    'Http404',
    'PermissionDenied',
    'SuspiciousOperation',
    'DisallowedHost',
    'ImmediateHttpResponse',        # allauth's redirect-by-exception
)


class ErrorCaptureMiddleware:
    """Record unhandled exceptions, and expose the reference on the request."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        if type(exception).__name__ in IGNORED:
            return None
        try:
            from . import catalog, services
            event = services.report(catalog.UNHANDLED, exc=exception, request=request)
            if event is not None:
                # Templates and error pages can show this so the user has
                # something concrete to quote to support.
                request.error_reference = event.reference
        except Exception:               # pragma: no cover
            logger.exception('diagnostics: failed to record an unhandled exception')
        return None                     # let Django handle the response
