"""School fees — the family's page for paying a grade's monthly fees.

A learner (or a parent, for the child they are viewing) sees the grade, the
monthly fee, how far the fees are paid, what is owing, and the "pay N months
in advance" choices. Choosing one raises (or reuses) a school-fees invoice and
goes to PayFast, or e-mails the invoice for EFT / the school office. Paying
unlocks every subject in the grade for exactly those months
(:mod:`apps.learning.fees`).
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse

from core.roles import role_flags
from core.scoping import children_of, viewing_child


def _learner_for(request):
    """The learner whose fees this page is about: the parent's chosen child,
    or the signed-in learner. ``(person, children)``."""
    flags = role_flags(request)
    if flags.get('is_parent'):
        child = viewing_child(request)
        children = [getattr(u, 'profile', None) for u in children_of(request.user)]
        return (getattr(child, 'profile', None) if child else None), [c for c in children if c]
    return getattr(request.user, 'profile', None), []


@login_required
def school_fees(request):
    from apps.learning import fees

    person, children = _learner_for(request)
    status = fees.fee_status(person) if person is not None else None

    if request.method == 'POST' and status is not None:
        try:
            months = int(request.POST.get('months') or 1)
        except ValueError:
            months = 1
        invoice = fees.raise_fees_invoice(person, status['programme'], months=months)
        if invoice is None:
            messages.info(request, 'This grade has no school fees to pay.')
            return redirect('finance:school-fees')
        if request.POST.get('action') == 'eft':
            try:
                from apps.finance.emails import send_invoice_email
                send_invoice_email(invoice)
            except Exception:  # pragma: no cover - best effort
                pass
            messages.success(
                request, f'Invoice {invoice.number} for {invoice.fee_months} month'
                         f'{"s" if invoice.fee_months != 1 else ""} has been e-mailed. Pay at '
                         "Standard Bank using the learner's name and grade as the reference — the "
                         'subjects open as soon as the payment is recorded.')
            return redirect(reverse('finance:school-fees') + (
                f'?student={person.user_id}' if children else ''))
        return redirect('finance:pay', public_id=invoice.public_id)

    return render(request, 'finance/school-fees.html', {
        'page_title': 'School fees', 'person': person, 'status': status,
        'children': children, 'is_parent': bool(children) or role_flags(request).get('is_parent'),
    })
