"""Who may see which shop item.

The catalogue is one table serving several audiences. A Grade 12 past-paper pack
is noise to a Grade 3 parent and a school jersey is for everybody, so an item is
visible when either:

* it is **general** — ``institution`` is blank; or
* it belongs to **the viewer's own institution**, and either carries no
  ``programme`` or carries one the viewer is enrolled on.

``module`` is deliberately *not* a gate. It is a filter facet: a candidate may
well want the Financial Reporting pack for a module they are not registered for,
and hiding it would cost a sale for no benefit.

Everything that lists products goes through :func:`visible_products`, so the rule
lives in exactly one place. Admin and staff see the whole catalogue — they are
the people loading it.
"""
from django.db.models import Q

from .models import Product


def _programmes_for(user):
    """The programmes ``user`` is enrolled on, as a queryset (possibly empty)."""
    person = getattr(user, 'profile', None)
    if person is None:
        return None
    try:
        return person.enrolled_programmes
    except Exception:          # pragma: no cover — a shop page must not 500
        return None


def audience_for(request):
    """Whose catalogue this request should show.

    A parent is shopping for their child, so they see what the child sees — not
    the general-only catalogue their own (module-less) account would otherwise
    get, and not everything.
    """
    from core.roles import role_flags

    flags = role_flags(request)
    if flags.get('is_parent'):
        try:
            from core.scoping import viewing_child
            return viewing_child(request)
        except Exception:      # pragma: no cover
            return None
    return getattr(request, 'user', None)


def visible_products(user, queryset=None):
    """Narrow ``queryset`` (default: all active products) to what ``user`` may see."""
    qs = queryset if queryset is not None else Product.objects.filter(status='active')

    if user is None or not getattr(user, 'is_authenticated', False):
        return qs.filter(institution__isnull=True)

    # The people who load the catalogue have to be able to see all of it.
    if user.is_staff or user.is_superuser:
        return qs

    programmes = _programmes_for(user)
    if programmes is None:
        return qs.filter(institution__isnull=True)

    programme_ids = list(programmes.values_list('id', flat=True))
    institution_ids = list(programmes.values_list('institution_id', flat=True))
    if not institution_ids:
        return qs.filter(institution__isnull=True)

    return qs.filter(
        Q(institution__isnull=True)
        | (Q(institution_id__in=institution_ids)
           & (Q(programme__isnull=True) | Q(programme_id__in=programme_ids)))
    ).distinct()


def visible_for_request(request, queryset=None):
    """:func:`visible_products` for whoever this request is shopping as."""
    return visible_products(audience_for(request), queryset)
