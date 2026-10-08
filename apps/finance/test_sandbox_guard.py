"""The sandbox shortcut must not survive into production.

``payfast_return()`` settles the invoice on a bare GET when running without
PayFast credentials — a deliberate development convenience, because PayFast's
ITN cannot reach localhost and there is otherwise no way to exercise checkout.
It was keyed on ``PAYFAST_SANDBOX`` alone, which defaults to *true* and is true
in the shipped ``.env``. Every buyer knows their own invoice's ``public_id`` —
it is in their pay link — so shipping in that state made every module free to
anyone who opened their own return URL.

Two independent guards now stand in the way: the simulation additionally
requires ``DEBUG``, and :mod:`apps.finance.checks` refuses to start a
``DEBUG=False`` build that is still pointed at the sandbox.
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.checks import Error
from django.test import Client, TestCase, override_settings

from . import checks, models, payfast

User = get_user_model()


class SandboxSettlementTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.customer = User.objects.create_user(
            username='sbuyer', email='sbuyer@example.com', password='pw12345!')
        self.invoice = models.Invoice.objects.create(
            customer=self.customer, status=models.Invoice.STATUS_SENT,
            subtotal=Decimal('5000.00'), total=Decimal('5000.00'))

    def _return(self):
        return self.client.get(f'/finance/payfast/return/?inv={self.invoice.public_id}')

    def _status(self):
        self.invoice.refresh_from_db()
        return self.invoice.status

    @override_settings(DEBUG=True, PAYFAST_SANDBOX=True,
                       PAYFAST_MERCHANT_ID='', PAYFAST_MERCHANT_KEY='')
    def test_development_still_settles_so_checkout_stays_testable(self):
        self._return()
        self.assertEqual(self._status(), models.Invoice.STATUS_PAID)

    @override_settings(DEBUG=False, PAYFAST_SANDBOX=True,
                       PAYFAST_MERCHANT_ID='', PAYFAST_MERCHANT_KEY='')
    def test_production_build_does_not_settle_on_a_bare_get(self):
        """The free-enrolment hole: sandbox flag on, but this is not a dev box."""
        self._return()
        self.assertNotEqual(self._status(), models.Invoice.STATUS_PAID)
        self.assertEqual(self.invoice.balance, Decimal('5000.00'))

    @override_settings(DEBUG=True, PAYFAST_SANDBOX=True,
                       PAYFAST_MERCHANT_ID='10000100', PAYFAST_MERCHANT_KEY='key')
    def test_real_credentials_mean_payfast_is_authoritative(self):
        """With credentials configured the ITN settles, not the return URL."""
        self._return()
        self.assertNotEqual(self._status(), models.Invoice.STATUS_PAID)

    @override_settings(DEBUG=False, PAYFAST_SANDBOX=False)
    def test_live_mode_never_settles_on_return(self):
        self._return()
        self.assertNotEqual(self._status(), models.Invoice.STATUS_PAID)


class SimulateInSandboxTests(TestCase):
    @override_settings(DEBUG=True, PAYFAST_SANDBOX=True,
                       PAYFAST_MERCHANT_ID='', PAYFAST_MERCHANT_KEY='')
    def test_true_only_in_zero_config_development(self):
        self.assertTrue(payfast.simulate_in_sandbox())

    @override_settings(DEBUG=False, PAYFAST_SANDBOX=True,
                       PAYFAST_MERCHANT_ID='', PAYFAST_MERCHANT_KEY='')
    def test_debug_is_required(self):
        self.assertFalse(payfast.simulate_in_sandbox())


class StartupCheckTests(TestCase):
    """A misconfigured money path should fail at boot, not at the till.

    Every case sets ``TESTING=False`` as well as ``DEBUG``: the guards stand
    down under the test runner (which forces ``DEBUG=False``), so without it
    these would be asserting against a disarmed check.
    """

    def _ids(self, results):
        return [r.id for r in results]

    @override_settings(TESTING=False, DEBUG=False, PAYFAST_SANDBOX=True)
    def test_sandbox_with_debug_off_is_an_error(self):
        results = checks.payfast_sandbox_not_in_production(None)
        self.assertEqual(self._ids(results), ['finance.E001'])
        self.assertIsInstance(results[0], Error)

    @override_settings(TESTING=False, DEBUG=True, PAYFAST_SANDBOX=True)
    def test_sandbox_in_development_is_fine(self):
        self.assertEqual(checks.payfast_sandbox_not_in_production(None), [])

    @override_settings(TESTING=False, DEBUG=False, PAYFAST_SANDBOX=False)
    def test_live_mode_is_fine(self):
        self.assertEqual(checks.payfast_sandbox_not_in_production(None), [])

    @override_settings(TESTING=False, DEBUG=False, PAYFAST_SANDBOX=False, PAYFAST_MERCHANT_ID='',
                       PAYFAST_MERCHANT_KEY='', PAYFAST_PASSPHRASE='')
    def test_live_mode_without_credentials_is_an_error(self):
        self.assertEqual(self._ids(checks.payfast_has_credentials(None)), ['finance.E002'])

    @override_settings(TESTING=False, DEBUG=False, PAYFAST_SANDBOX=False, PAYFAST_MERCHANT_ID='id',
                       PAYFAST_MERCHANT_KEY='key', PAYFAST_PASSPHRASE='phrase')
    def test_live_mode_with_credentials_passes(self):
        self.assertEqual(checks.payfast_has_credentials(None), [])
