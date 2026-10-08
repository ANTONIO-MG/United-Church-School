"""Render finance documents to PDF (xhtml2pdf / reportlab — pure pip, no system
libraries).

Two documents, one per way a registration can be settled:

* :func:`render_invoice_pdf` — what to pay, attached when the student takes the
  free week and will pay by EFT.
* :func:`render_receipt_pdf` — proof that it was paid, attached when the card
  payment has already cleared.

Both return ``bytes`` or ``None``; a PDF that will not render is never allowed
to take an e-mail (or a registration) down with it.
"""
import io
import logging
import os

from django.template.loader import render_to_string

logger = logging.getLogger('apps')


def _link_callback(uri, rel):
    """Resolve ``/static/…`` and ``/media/…`` URLs to files on disk.

    xhtml2pdf fetches images itself rather than going through Django, so a URL
    path is resolved against the *process working directory* and the image is
    dropped without an error. The invoice carries the logo, so it has to
    resolve; anything that is not ours is handed back untouched.
    """
    from django.conf import settings
    from django.contrib.staticfiles import finders

    static_url, media_url = settings.STATIC_URL or '/static/', settings.MEDIA_URL or '/media/'
    if uri.startswith(static_url):
        found = finders.find(uri[len(static_url):].split('?')[0])
        if found:
            return found[0] if isinstance(found, (list, tuple)) else found
    if uri.startswith(media_url):
        path = os.path.join(settings.MEDIA_ROOT, uri[len(media_url):].split('?')[0])
        if os.path.exists(path):
            return path
    return uri


def _render(template, context, *, invoice, kind):
    """Render ``template`` to PDF bytes, or ``None`` if anything goes wrong."""
    try:
        from xhtml2pdf import pisa

        from django.conf import settings

        from core.branding import strings
        context = dict(context, brand=strings().get('brand', {}),
                       vat_number=getattr(settings, 'VAT_NUMBER', ''))
        if invoice is not None and 'items' in context:
            context.setdefault('gross_subtotal', sum(
                (item.gross_amount for item in context['items']), 0))
        html = render_to_string(template, context)
        buf = io.BytesIO()
        result = pisa.CreatePDF(html, dest=buf, link_callback=_link_callback)
        if result.err:
            from core.errors import note
            note('FIN-8001', invoice=getattr(invoice, 'number', ''))
            logger.warning('finance: xhtml2pdf reported errors for %s %s',
                           kind, getattr(invoice, 'number', '?'))
            return None
        return buf.getvalue()
    except Exception as exc:  # pragma: no cover
        from core.errors import report
        report('FIN-8001', exc, context={'invoice': getattr(invoice, 'number', '?')})
        logger.exception('finance: %s PDF generation failed for %s',
                         kind, getattr(invoice, 'number', '?'))
        return None


def _customer_phone(invoice):
    """The customer's phone for the "bill to" block, or '' when we have none.

    Walked defensively: finance must not assume an accounts Person or a contact
    row exists (staff-raised invoices often have neither), and a missing phone
    is never a reason to fail an invoice.
    """
    person = getattr(invoice.customer, 'profile', None)
    contact = getattr(person, 'contact', None)
    return (getattr(contact, 'primary_phone', '') or '').strip()


def render_invoice_pdf(invoice):
    """Return the invoice as PDF ``bytes``, or ``None`` if generation fails."""
    return _render('finance/invoice_pdf.html', {
        'invoice': invoice,
        'items': list(invoice.items.all()),
        'phone': _customer_phone(invoice),
    }, invoice=invoice, kind='invoice')


def render_receipt_pdf(invoice):
    """Return a proof of payment as PDF ``bytes``, or ``None`` if it fails.

    Lists the payments actually recorded against the invoice, so the document
    stands on its own as evidence rather than just restating the invoice.
    """
    return _render('finance/receipt_pdf.html', {
        'invoice': invoice,
        'items': list(invoice.items.all()),
        'payments': list(invoice.payments.all()),
    }, invoice=invoice, kind='receipt')


def render_estimate_pdf(estimate):
    """The estimate, on the invoice's layout with estimate labels."""
    return _render('finance/invoice_pdf.html', {
        'invoice': estimate, 'kind': 'estimate', 'items': list(estimate.items.all()),
        'phone': _customer_phone(estimate),
    }, invoice=estimate, kind='estimate')


def render_statement_pdf(data):
    """A statement of account (see finance.documents.statement)."""
    return _render('finance/statement_pdf.html', {'s': data}, invoice=None, kind='statement')
