"""Context processor exposing finance summary stats to every template.

Scoped by role: admin/staff see all invoices; everyone else sees only the
invoices billed to them (``customer``)."""

from django.db.models import Sum

from core.roles import role_flags

from . import models
from core.request_cache import cached_per_request


def _build_finance_stats(request):
    try:
        flags = role_flags(request)
        user = getattr(request, 'user', None)
        invoices = models.Invoice.objects.all()
        payments = models.InvoicePayment.objects.all()
        if not flags['is_admin_staff'] and user is not None and user.is_authenticated:
            invoices = invoices.filter(customer=user)
            payments = payments.filter(invoice__customer=user)
        total_invoiced = invoices.aggregate(total=Sum('total'))['total'] or 0
        total_received = payments.aggregate(total=Sum('amount'))['total'] or 0
        return {
            'finance_stats': {
                'invoices_count': invoices.count(),
                'draft_count': invoices.filter(status=models.Invoice.STATUS_DRAFT).count(),
                'paid_count': invoices.filter(status=models.Invoice.STATUS_PAID).count(),
                'overdue_count': invoices.filter(status=models.Invoice.STATUS_OVERDUE).count(),
                'total_invoiced': total_invoiced,
                'total_received': total_received,
                'total_due': (total_invoiced or 0) - (total_received or 0),
            }
        }
    except Exception:
        return {'finance_stats': {}}


def finance_stats(request):
    """Cached for the life of the request — these are nav badges, and this
    processor runs once per template rendered in a response, not once per
    response."""
    return cached_per_request(request, 'finance_stats', lambda: _build_finance_stats(request))
