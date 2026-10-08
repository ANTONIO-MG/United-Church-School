"""The PayFast ITN webhook is the platform's only unauthenticated money path.

``/finance/payfast/notify/`` is ``csrf_exempt`` and open to the internet by
necessity — PayFast calls it server-to-server. Everything that stops it being a
"mark any invoice paid" button lives in :func:`apps.finance.payfast.verify_itn`
and the view's amount check, and all of it once failed open:

* the signature test was ``if received and _signature(data) != received`` —
  omit the field and there is nothing to compare, so the check was skipped;
* the server confirmation was ``if 'VALID' not in resp.text.upper()`` — and
  PayFast's *rejection* reply is the literal string ``INVALID``, which contains
  ``VALID``;
* ``amount_gross`` was never compared to the balance, so a genuine small
  payment could close a large invoice.

Every buyer knows their own invoice's ``public_id`` — it is in their pay link —
so these are not theoretical. The network call is stubbed; what is under test is
our own decision-making.
"""

from decimal import Decimal
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings

from . import models, payfast

User = get_user_model()

PASSPHRASE = 'test-passphrase'


def _reply(text):
    """A stand-in for the requests.post() response from PayFast's validator."""
    return mock.Mock(text=text)


@override_settings(PAYFAST_PASSPHRASE=PASSPHRASE, PAYFAST_MERCHANT_ID='10000100',
                   PAYFAST_MERCHANT_KEY='key', PAYFAST_SANDBOX=True)
class PayfastItnTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.customer = User.objects.create_user(
            username='buyer', email='buyer@example.com', password='pw12345!')
        self.invoice = models.Invoice.objects.create(
            customer=self.customer, status=models.Invoice.STATUS_SENT,
            subtotal=Decimal('5000.00'), total=Decimal('5000.00'))

    def _payload(self, *, sign=True, **overrides):
        data = {
            'm_payment_id': str(self.invoice.public_id),
            'pf_payment_id': '1234567',
            'payment_status': 'COMPLETE',
            'amount_gross': '5000.00',
        }
        data.update(overrides)
        data = {k: v for k, v in data.items() if v is not None}
        # An explicit ``signature=`` override is the point of the test — don't
        # overwrite a deliberately forged one with a valid one.
        if sign and 'signature' not in overrides:
            data['signature'] = payfast._signature(data)
        return data

    def _notify(self, payload, confirmation='VALID'):
        with mock.patch('requests.post', return_value=_reply(confirmation)):
            return self.client.post('/finance/payfast/notify/', payload)

    def _status(self):
        self.invoice.refresh_from_db()
        return self.invoice.status

    # --- forged notifications -------------------------------------------------

    def test_notification_without_a_signature_is_rejected(self):
        """The original hole: no signature meant no signature *check*."""
        response = self._notify(self._payload(sign=False))
        self.assertEqual(response.status_code, 400)
        self.assertNotEqual(self._status(), models.Invoice.STATUS_PAID)

    def test_notification_with_a_wrong_signature_is_rejected(self):
        response = self._notify(self._payload(signature='0' * 32))
        self.assertEqual(response.status_code, 400)
        self.assertNotEqual(self._status(), models.Invoice.STATUS_PAID)

    def test_bare_invoice_id_and_complete_status_is_rejected(self):
        """The exact forgery from the report: id + payment_status, nothing else."""
        response = self._notify({'m_payment_id': str(self.invoice.public_id),
                                 'payment_status': 'COMPLETE'})
        self.assertEqual(response.status_code, 400)
        self.assertNotEqual(self._status(), models.Invoice.STATUS_PAID)

    def test_invalid_confirmation_is_not_read_as_valid(self):
        """'INVALID' contains 'VALID' — a substring test accepted every rejection."""
        response = self._notify(self._payload(), confirmation='INVALID')
        self.assertEqual(response.status_code, 400)
        self.assertNotEqual(self._status(), models.Invoice.STATUS_PAID)

    def test_incomplete_payment_is_rejected(self):
        response = self._notify(self._payload(payment_status='CANCELLED'))
        self.assertEqual(response.status_code, 400)
        self.assertNotEqual(self._status(), models.Invoice.STATUS_PAID)

    # --- malformed input ------------------------------------------------------

    def test_malformed_invoice_id_is_acked_not_a_500(self):
        """``public_id`` is a UUIDField: filtering it with junk raises."""
        response = self._notify(self._payload(m_payment_id='not-a-uuid'))
        self.assertEqual(response.status_code, 200)

    def test_unknown_invoice_id_is_acked(self):
        response = self._notify(
            self._payload(m_payment_id='11111111-1111-1111-1111-111111111111'))
        self.assertEqual(response.status_code, 200)

    # --- amount ---------------------------------------------------------------

    def test_underpayment_does_not_close_the_invoice(self):
        """A verified R100 payment must not settle a R5 000 invoice."""
        response = self._notify(self._payload(amount_gross='100.00'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self._status(), models.Invoice.STATUS_PARTIAL)
        self.assertEqual(self.invoice.balance, Decimal('4900.00'))

    def test_overpayment_settles_only_the_balance(self):
        response = self._notify(self._payload(amount_gross='9000.00'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self._status(), models.Invoice.STATUS_PAID)
        self.assertEqual(self.invoice.balance, Decimal('0.00'))

    def test_missing_amount_does_not_settle(self):
        response = self._notify(self._payload(amount_gross=None))
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(self._status(), models.Invoice.STATUS_PAID)

    # --- the genuine article --------------------------------------------------

    def test_a_correctly_signed_confirmed_notification_settles_the_invoice(self):
        response = self._notify(self._payload())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self._status(), models.Invoice.STATUS_PAID)
        self.assertEqual(self.invoice.balance, Decimal('0.00'))

    def test_a_replayed_notification_is_not_charged_twice(self):
        payload = self._payload()
        self._notify(payload)
        self._notify(payload)
        self.assertEqual(self.invoice.payments.count(), 1)


class VerifyItnUnitTests(TestCase):
    """``verify_itn`` in isolation, without the view or the database."""

    @override_settings(PAYFAST_PASSPHRASE=PASSPHRASE)
    def test_confirmation_reply_must_match_exactly(self):
        data = {'payment_status': 'COMPLETE', 'amount_gross': '10.00'}
        data['signature'] = payfast._signature(data)
        for reply, expected in [('VALID', True), ('valid\n', True), (' VALID ', True),
                                ('INVALID', False), ('invalid', False), ('', False)]:
            with self.subTest(reply=reply):
                with mock.patch('requests.post', return_value=_reply(reply)):
                    self.assertIs(payfast.verify_itn(dict(data)), expected)
