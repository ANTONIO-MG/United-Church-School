"""Formatting for the shop and finance pages: ``{% load commerce %}``."""
from decimal import Decimal, InvalidOperation

from django import template

register = template.Library()

_FILE_ICONS = {
    'pdf': 'bi-file-earmark-pdf', 'zip': 'bi-file-earmark-zip',
    'doc': 'bi-file-earmark-word', 'docx': 'bi-file-earmark-word', 'odt': 'bi-file-earmark-word',
    'xls': 'bi-file-earmark-excel', 'xlsx': 'bi-file-earmark-excel', 'ods': 'bi-file-earmark-excel',
    'csv': 'bi-file-earmark-spreadsheet',
    'ppt': 'bi-file-earmark-slides', 'pptx': 'bi-file-earmark-slides', 'odp': 'bi-file-earmark-slides',
}

_FULFILMENT_ICONS = {
    'digital': 'bi-file-earmark-arrow-down', 'booking': 'bi-person-video3',
    'shipped': 'bi-box-seam', 'none': 'bi-receipt',
}


def _decimal(value):
    try:
        return Decimal(str(value if value not in (None, '') else 0))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal('0')


@register.filter
def rand(value):
    """``1234.5`` → ``R1,234.50``; negatives as ``−R12.00``."""
    amount = _decimal(value).quantize(Decimal('0.01'))
    sign = '−' if amount < 0 else ''
    return f'{sign}R{abs(amount):,.2f}'


@register.filter
def pct(value):
    """``20.00`` → ``20%``; ``12.50`` → ``12.5%``."""
    return f'{_decimal(value).normalize():f}%'


@register.filter
def file_icon(name):
    ext = str(name or '').rsplit('.', 1)[-1].lower()
    return _FILE_ICONS.get(ext, 'bi-file-earmark')


@register.filter
def fulfilment_icon(value):
    return _FULFILMENT_ICONS.get(str(value), 'bi-bag')


@register.filter
def when(value):
    """An ISO timestamp from a courier/event log → ``3 Oct, 14:05`` local time."""
    from django.utils import timezone
    from django.utils.dateparse import parse_datetime
    moment = parse_datetime(str(value or ''))
    if moment is None:
        return str(value or '')[:10]
    if timezone.is_aware(moment):
        moment = timezone.localtime(moment)
    return moment.strftime('%-d %b, %H:%M')
