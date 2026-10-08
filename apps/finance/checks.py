"""Startup guards for the money path.

A misconfiguration here does not raise an error anybody sees — it silently
gives the product away. These checks turn that into a boot failure instead:
``runserver`` runs system checks on start, and ``manage.py check --deploy``
runs them in your release step.

Registered in :meth:`apps.finance.apps.FinanceConfig.ready`.
"""

from django.conf import settings
from django.core.checks import Error, Tags, Warning as CheckWarning, register

from . import payfast


def _not_production():
    """True when these guards should stand down.

    ``DEBUG`` means a developer's machine. ``TESTING`` means the Django test
    runner, which forces ``DEBUG=False`` — without this every deployment guard
    below would fire on every test run and block the suite.

    ``PAYMENTS_ENABLED=False`` means this deployment does not sell anything: the
    pay page refuses instead of building a checkout (see
    :func:`apps.finance.views.pay`), so there is no money path left to
    misconfigure. Without this a site that takes no payments could not be
    deployed at all — the honest fix for that is a flag saying so, not
    placeholder merchant credentials that make the guard pass while checkout
    stays broken.
    """
    return bool(
        settings.DEBUG
        or getattr(settings, 'TESTING', False)
        or not getattr(settings, 'PAYMENTS_ENABLED', True)
    )


@register(Tags.security)
def payfast_sandbox_not_in_production(app_configs, **kwargs):
    """``PAYFAST_SANDBOX=true`` with ``DEBUG=False`` must not start.

    The shipped ``.env`` defaults to sandbox mode with empty merchant keys, and
    ``is_sandbox()`` defaults to ``True`` when the setting is missing entirely —
    so the dangerous combination is the one you reach by *forgetting* to
    configure PayFast, not by choosing anything. In that state checkout either
    settles invoices without payment or points at a sandbox host with no
    credentials. Neither is something to discover from a customer.
    """
    if _not_production() or not payfast.is_sandbox():
        return []
    return [Error(
        'PAYFAST_SANDBOX is true but DEBUG is False.',
        hint='This is a production build wired to PayFast\'s sandbox. Set '
             'PAYFAST_SANDBOX=false and configure PAYFAST_MERCHANT_ID, '
             'PAYFAST_MERCHANT_KEY and PAYFAST_PASSPHRASE for your live '
             'merchant account. Payments taken in this state are not real.',
        id='finance.E001',
    )]


@register(Tags.security)
def payfast_has_credentials(app_configs, **kwargs):
    """Live mode needs a merchant id, key and passphrase to sign with."""
    if _not_production() or payfast.is_sandbox():
        return []
    missing = [name for name in ('PAYFAST_MERCHANT_ID', 'PAYFAST_MERCHANT_KEY',
                                 'PAYFAST_PASSPHRASE')
               if not (getattr(settings, name, '') or '').strip()]
    if not missing:
        return []
    return [Error(
        f'PayFast is in live mode but {", ".join(missing)} '
        f'{"is" if len(missing) == 1 else "are"} not set.',
        hint='Without these the redirect signature cannot be built and the ITN '
             'cannot be verified, so no payment will complete. The passphrase '
             'must match the one set in the PayFast dashboard.',
        id='finance.E002',
    )]


@register(Tags.security)
def payfast_notify_url_is_reachable(app_configs, **kwargs):
    """PayFast has to be able to POST the ITN back to us.

    A localhost or unset ``SITE_BASE_URL`` builds a ``notify_url`` PayFast
    cannot reach, so payments are taken and never recorded — the worst failure
    mode of the three, because the money moves.
    """
    if _not_production() or payfast.is_sandbox():
        return []
    from core.utils import site_base

    base = (site_base() or '').lower()
    if not base or 'localhost' in base or '127.0.0.1' in base:
        return [CheckWarning(
            f'PayFast is live but the site base URL is {base or "unset"}.',
            hint='PayFast POSTs the ITN to a notify_url built from this. If it '
                 'is not publicly reachable, payments will succeed at PayFast '
                 'and never be recorded against the invoice. Set SITE_BASE_URL '
                 '(or the Sites framework entry) to the public https:// host.',
            id='finance.W001',
        )]
    return []
