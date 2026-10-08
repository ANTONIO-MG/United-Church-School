"""Who may download which purchased file.

A digital item is delivered twice over, because the two ways of paying finish at
different times:

* **Paid online (PayFast)** — the order flips to paid during checkout and the
  download button appears immediately.
* **Paid by EFT** — accounts marks the invoice paid days later, so the buyer is
  not on the site to see anything. :func:`deliver_order` e-mails them then.

Both paths end in the same place: :func:`can_download`. It is the only thing
that decides, so a download URL cannot be shared into access.
"""
import logging

from .models import Order, OrderItem

logger = logging.getLogger('apps')

#: Attach anything up to this size; above it the e-mail carries a link instead.
#: Mail servers routinely bounce past ~10 MB, and a bounced delivery is worse
#: than a link.
MAX_EMAIL_ATTACHMENT_BYTES = 8 * 1024 * 1024


def download_url(product, file_id=None):
    from django.urls import reverse
    if file_id:
        return reverse('shop:download-file', args=[product.pk, file_id])
    return reverse('shop:download-product', args=[product.pk])


def paid_orders_for(user):
    """Orders of ``user`` that have actually been paid for."""
    return Order.objects.filter(buyer=user, status=Order.STATUS_PAID)


def can_download(user, product):
    """True when ``user`` is entitled to ``product``'s file.

    Staff and admin always may — they load the catalogue and have to be able to
    check what a buyer receives.
    """
    if not product.is_digital:
        return False
    if not getattr(user, 'is_authenticated', False):
        return False
    if user.is_staff or user.is_superuser:
        return True
    return OrderItem.objects.filter(
        order__buyer=user, order__status=Order.STATUS_PAID, product=product).exists()


def downloadable_items(order):
    """The lines of ``order`` that have a file waiting, once it is paid."""
    if order.status != Order.STATUS_PAID:
        return []
    return [item for item in order.items.select_related('product') if item.product.is_digital]


def deliver_order(order):
    """E-mail the buyer their files for a freshly-paid ``order``.

    Small files ride along as attachments; anything larger is linked, because a
    message the mail server rejects delivers nothing at all. Never raises — a
    delivery problem must not roll back a payment that really happened.
    """
    from django.core.mail import EmailMessage
    from django.conf import settings

    from core.branding import strings
    from core.utils import absolute_url

    items = downloadable_items(order)
    buyer_email = (getattr(order.buyer, 'email', '') or '').strip()
    if not items or not buyer_email:
        return False

    brand = strings().get('brand', {})
    brand_name = brand.get('invoice_name') or brand.get('name') or 'United Church School'

    lines, attachments = [], []
    attached_bytes = 0
    for item in items:
        product = item.product
        for label, fieldfile, file_id in product.deliverables():
            try:
                size = fieldfile.size
            except Exception:                  # pragma: no cover — missing file on disk
                logger.warning('shop: %s has no readable file %s for order %s',
                               product.sku, label, order.order_no)
                continue
            # The limit is on the whole message, not each file: five 5 MB
            # attachments bounce just as surely as one 25 MB one.
            if attached_bytes + size <= MAX_EMAIL_ATTACHMENT_BYTES:
                try:
                    fieldfile.open('rb')
                    attachments.append((fieldfile.name.rsplit('/', 1)[-1], fieldfile.read(), None))
                    attached_bytes += size
                finally:
                    fieldfile.close()
                lines.append(f'• {product.name} — {label} (attached)')
            else:
                url = absolute_url(download_url(product, file_id))
                lines.append(f'• {product.name} — {label}: {url}')

    if not lines:
        return False

    body = (
        f'Hello {order.buyer.get_full_name() or order.buyer.get_username()},\n\n'
        f'Payment received for order {order.order_no}. Here is what you bought:\n\n'
        + '\n'.join(lines)
        + '\n\nYou can also download these any time from Shop → My orders while '
          'you are signed in.\n\n'
        f'{brand_name}\n'
    )
    message = EmailMessage(
        subject=f'Your download — order {order.order_no}',
        body=body,
        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
        to=[buyer_email],
    )
    for name, content, mimetype in attachments:
        message.attach(name, content, mimetype)
    try:
        message.send(fail_silently=False)
        return True
    except Exception:                          # pragma: no cover
        logger.exception('shop: could not e-mail downloads for order %s', order.order_no)
        return False
