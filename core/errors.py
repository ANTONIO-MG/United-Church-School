"""Short import path for error reporting: ``from core.errors import fail, note``.

Every app already imports from ``core``; routing the error helpers through here
means a view does not have to reach across into another app's internals just to
report a problem, and the underlying implementation can move without touching
every call site.

    from core.errors import capture, errorcode, fail, note, report

    note('CHAT-2001', request, group=group.pk)        # expected refusal, logged
    fail('CERT-1001', 'No holder name.', request)     # log it and raise it

    with capture('CERT-8001', request):               # tag whatever escapes
        png = render_png(cert)

    @errorcode('LRN-8001')                            # tag a whole view
    def export_module(request, module_id): ...

See docs/ERROR_CODES.md for the code scheme and apps/diagnostics/catalog.py for
the dictionary itself.
"""

from apps.diagnostics.catalog import ERRORS, cause_label, get, prefix_of  # noqa: F401
from apps.diagnostics.services import (  # noqa: F401
    capture,
    classify,
    errorcode,
    fail,
    note,
    report,
)

__all__ = ['report', 'note', 'fail', 'capture', 'errorcode', 'classify',
           'get', 'ERRORS', 'prefix_of', 'cause_label']
