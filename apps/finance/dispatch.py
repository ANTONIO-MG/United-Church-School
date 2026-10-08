"""Cross-app signals for the finance domain.

``invoice_paid`` fires once, when an invoice first becomes fully paid. Other
apps (e.g. accounts, for enrolment) listen without finance importing them.

Providing args: ``invoice`` — the paid :class:`apps.finance.models.Invoice`.
"""
from django.dispatch import Signal

invoice_paid = Signal()
