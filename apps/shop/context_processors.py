"""Context processor exposing shop summary stats to every template
(badge counts in the sidebar, dashboard widgets, etc.).

Scoped by role: admin/staff see all orders & revenue; everyone else sees only
their own orders. The product/service catalogue counts are public to all."""

from django.db.models import Sum

from core.roles import role_flags

from . import models
from core.request_cache import cached_per_request


def _build_shop_stats(request):
    # Guarded so a missing table (e.g. before `migrate`) or any DB error never
    # takes down every page that renders through this context processor.
    try:
        flags = role_flags(request)
        user = getattr(request, 'user', None)
        orders = models.Order.objects.all()
        completed = models.Payment.objects.filter(status=models.Payment.STATUS_COMPLETED)
        if not flags['is_admin_staff'] and user is not None and user.is_authenticated:
            # Non-admins only see their own orders/spend.
            orders = orders.filter(buyer=user)
            completed = completed.filter(order__buyer=user)

        # Live count of items in the current user's cart (for the navbar badge).
        cart_count = 0
        if user is not None and user.is_authenticated:
            cart = (models.Order.objects.filter(buyer=user, checked_out=False)
                    .order_by('-created_at').first())
            if cart:
                cart_count = sum(item.quantity for item in cart.items.all())

        return {
            'shop_stats': {
                'products': models.Product.objects.filter(kind=models.Product.KIND_PRODUCT).count(),
                'services': models.Product.objects.filter(kind=models.Product.KIND_SERVICE).count(),
                'active_products': models.Product.objects.filter(status='active').count(),
                'orders': orders.count(),
                'pending_orders': orders.filter(status=models.Order.STATUS_PENDING).count(),
                'paid_orders': orders.filter(status=models.Order.STATUS_PAID).count(),
                'total_revenue': completed.aggregate(total=Sum('amount'))['total'] or 0,
                'cart_count': cart_count,
                'recent_products': models.Product.objects.order_by('-created_at')[:5],
            }
        }
    except Exception:
        return {'shop_stats': {}}


def shop_stats(request):
    """Cached for the life of the request — these are nav badges, and this
    processor runs once per template rendered in a response, not once per
    response."""
    return cached_per_request(request, 'shop_stats', lambda: _build_shop_stats(request))
