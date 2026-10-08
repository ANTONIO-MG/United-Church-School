"""Tests for the sign-up / verification / password-reset flow.

These cover the rules the sign-up page is *supposed* to enforce. Several of them
failed before sign-up was routed through allauth's ``SignupForm``: the old view
called ``create_user`` directly, so the password validators never ran, and the
Terms checkbox (which had no ``name``) was never posted or checked server-side.
"""

import re

from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.core import mail
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse

User = get_user_model()

# Satisfy AUTH_PASSWORD_VALIDATORS: long enough, not common, not all-numeric.
GOOD_PASSWORD = 'United!WeStand2026'
NEW_PASSWORD = 'Brand!NewPass2026x'

# The suite must not depend on a running Redis: USE_REDIS=true points the real
# cache at a server that may not be up locally or in CI.
LOCMEM_CACHE = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}


class CacheIsolatedTestCase(TestCase):
    """Clears the cache between tests.

    allauth's ACCOUNT_EMAIL_CONFIRMATION_COOLDOWN (3 minutes by default) refuses
    to re-send a confirmation to an address it has just mailed, and records that
    in the cache — which LocMemCache keeps for the whole process, not per test.
    Without this, whichever test mails an address first silently suppresses the
    mail every later test expects.
    """

    def setUp(self):
        super().setUp()
        cache.clear()
        self.addCleanup(cache.clear)


def signup_payload(**overrides):
    data = {
        'email': 'learner@example.com',
        'password1': GOOD_PASSWORD,
        'password2': GOOD_PASSWORD,
        'terms': 'on',
        # Math CAPTCHA in test mode: any hashkey + the literal 'PASSED' answer
        # validates (see CAPTCHA_TEST_MODE on the test class below).
        'captcha_0': 'PASSED',
        'captcha_1': 'PASSED',
    }
    data.update(overrides)
    return data


# locmem keeps the suite off real SMTP; rate limits are cleared so that repeated
# posts in a test class don't trip allauth's throttle instead of the assertion
# under test (throttling itself is covered separately).
#
# CAPTCHA_TEST_MODE makes the math CAPTCHA accept the literal answer 'PASSED'
# for any challenge, so the sign-up assertions below test the code rather than
# whatever arithmetic image happens to be generated (see signup_payload).
@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
                   ACCOUNT_EMAIL_VERIFICATION='mandatory',
                   ACCOUNT_RATE_LIMITS={},
                   CAPTCHA_TEST_MODE=True,
                   CACHES=LOCMEM_CACHE)
class SignupValidationTests(CacheIsolatedTestCase):

    def setUp(self):
        super().setUp()
        self.url = reverse('myhub:page-register')

    def test_valid_signup_creates_unverified_user_and_sends_mail(self):
        resp = self.client.post(self.url, signup_payload())
        # Sign-up renders "check your e-mail" rather than redirecting: the same
        # page is returned whether or not the address already had an account, so
        # the form cannot be used to discover who is registered.
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'myhub/pages/page-register-done.html')
        user = User.objects.get(email='learner@example.com')
        # username mirrors the e-mail — the platform is e-mail-only.
        self.assertEqual(user.username, 'learner@example.com')
        self.assertFalse(EmailAddress.objects.get(user=user).verified)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('learner@example.com', mail.outbox[0].to)

    def test_consent_is_recorded_not_just_ticked(self):
        self.client.post(self.url, signup_payload())
        profile = User.objects.get(email='learner@example.com').profile
        self.assertIsNotNone(profile.terms_accepted_at)
        self.assertTrue(profile.terms_version)

    def test_terms_must_be_accepted(self):
        resp = self.client.post(self.url, signup_payload(terms=''))
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(User.objects.filter(email='learner@example.com').exists())

    def test_weak_password_rejected(self):
        # 'a' was accepted before: create_user() bypasses AUTH_PASSWORD_VALIDATORS.
        resp = self.client.post(self.url, signup_payload(password1='a', password2='a'))
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(User.objects.filter(email='learner@example.com').exists())

    def test_numeric_and_common_passwords_rejected(self):
        for pw in ('12345678', 'password'):
            with self.subTest(password=pw):
                resp = self.client.post(self.url, signup_payload(password1=pw, password2=pw))
                self.assertEqual(resp.status_code, 200)
        self.assertFalse(User.objects.filter(email='learner@example.com').exists())

    def test_mismatched_passwords_rejected(self):
        resp = self.client.post(self.url, signup_payload(password2=GOOD_PASSWORD + 'x'))
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(User.objects.filter(email='learner@example.com').exists())

    def test_malformed_email_rejected(self):
        resp = self.client.post(self.url, signup_payload(email='notanemail'))
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(User.objects.filter(username='notanemail').exists())

    def test_duplicate_email_creates_no_second_account(self):
        """Signing up with a taken address must not create an account — and must
        not *say so* either.

        ACCOUNT_PREVENT_ENUMERATION makes this response deliberately identical
        to a successful sign-up (the "check your e-mail" page); the existing
        owner is e-mailed instead. Asserting a visible "already exists" error
        here would be asserting an account-enumeration hole.
        """
        User.objects.create_user(username='learner@example.com', email='learner@example.com',
                                 password=GOOD_PASSWORD)
        resp = self.client.post(self.url, signup_payload())
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'myhub/pages/page-register-done.html')
        self.assertEqual(User.objects.filter(email__iexact='learner@example.com').count(), 1)
        # The owner is told someone tried to sign up as them, with no new account made.
        self.assertEqual(len(mail.outbox), 1)

    def test_a_taken_address_is_indistinguishable_from_a_free_one(self):
        """The two responses must match byte for byte, or the form leaks."""
        free = self.client.post(self.url, signup_payload(email='nobody@example.com'))
        mail.outbox.clear()
        cache.clear()
        taken = self.client.post(self.url, signup_payload(email='nobody@example.com'))
        self.assertEqual(free.status_code, taken.status_code)
        self.assertEqual(free.content, taken.content,
                         'the sign-up page reveals whether an address is registered')


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
                   ACCOUNT_EMAIL_VERIFICATION='mandatory',
                   ACCOUNT_RATE_LIMITS={},
                   CACHES=LOCMEM_CACHE)
class LoginVerificationGateTests(CacheIsolatedTestCase):

    def setUp(self):
        super().setUp()
        self.login_url = reverse('myhub:page-login')
        self.user = User.objects.create_user(username='learner@example.com',
                                             email='learner@example.com',
                                             password=GOOD_PASSWORD)
        EmailAddress.objects.create(user=self.user, email=self.user.email,
                                    primary=True, verified=False)

    def test_unverified_user_cannot_log_in(self):
        resp = self.client.post(self.login_url,
                                {'email': 'learner@example.com', 'password': GOOD_PASSWORD})
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.wsgi_request.user.is_authenticated)

    def test_unverified_login_attempt_resends_link(self):
        mail.outbox.clear()
        self.client.post(self.login_url,
                         {'email': 'learner@example.com', 'password': GOOD_PASSWORD})
        self.assertEqual(len(mail.outbox), 1)

    def test_verified_user_can_log_in(self):
        EmailAddress.objects.filter(user=self.user).update(verified=True)
        resp = self.client.post(self.login_url,
                                {'email': 'learner@example.com', 'password': GOOD_PASSWORD})
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.wsgi_request.user.is_authenticated)

    def test_wrong_password_does_not_authenticate(self):
        EmailAddress.objects.filter(user=self.user).update(verified=True)
        resp = self.client.post(self.login_url,
                                {'email': 'learner@example.com', 'password': 'wrong-password'})
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.wsgi_request.user.is_authenticated)


# NB: no ACCOUNT_RATE_LIMITS={} here — this class is exercising the real limits.
@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
                   CACHES=LOCMEM_CACHE)
class LoginRateLimitTests(CacheIsolatedTestCase):
    """The sign-in page authenticates directly instead of using allauth's
    LoginView, so it has to consume allauth's limiter itself. Without that it is
    an unthrottled credential-stuffing target."""

    def setUp(self):
        super().setUp()
        self.login_url = reverse('myhub:page-login')
        self.user = User.objects.create_user(username='learner@example.com',
                                             email='learner@example.com',
                                             password=GOOD_PASSWORD)
        EmailAddress.objects.create(user=self.user, email=self.user.email,
                                    primary=True, verified=True)

    def _attempt(self, password):
        return self.client.post(self.login_url,
                                {'email': 'learner@example.com', 'password': password}).status_code

    def test_repeated_failures_are_throttled(self):
        codes = [self._attempt('wrong-password') for _ in range(9)]
        self.assertIn(429, codes, f'brute force was not throttled: {codes}')

    def test_a_few_fumbles_do_not_lock_out_a_real_user(self):
        for _ in range(3):
            self._attempt('wrong-password')
        self.assertEqual(self._attempt(GOOD_PASSWORD), 302)

    def test_success_clears_the_failure_budget(self):
        for _ in range(3):
            self._attempt('wrong-password')
        self._attempt(GOOD_PASSWORD)      # success must reset the counter
        self.client.logout()
        self.assertNotIn(429, [self._attempt('wrong-password') for _ in range(3)])


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
                   ACCOUNT_RATE_LIMITS={},
                   CACHES=LOCMEM_CACHE)
class PasswordResetTests(CacheIsolatedTestCase):

    def setUp(self):
        super().setUp()
        self.url = reverse('myhub:page-forgot-password')
        self.user = User.objects.create_user(username='learner@example.com',
                                             email='learner@example.com',
                                             password=GOOD_PASSWORD)
        EmailAddress.objects.create(user=self.user, email=self.user.email,
                                    primary=True, verified=True)

    def test_reset_email_is_sent_for_known_address(self):
        self.client.post(self.url, {'email': 'learner@example.com'})
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('learner@example.com', mail.outbox[0].to)

    def _open_reset_form(self):
        """Request a reset, follow the emailed link, return the set-password URL."""
        mail.outbox.clear()
        self.client.post(self.url, {'email': self.user.email})
        link = re.search(r'https?://[^\s"<>]*password/reset/key/[^\s"<>]+', mail.outbox[0].body)
        self.assertIsNotNone(link, 'no reset link in the e-mail')
        path = re.sub(r'^https?://[^/]+', '', link.group(0))
        resp = self.client.get(path, follow=True)
        return resp.redirect_chain[-1][0] if resp.redirect_chain else path

    def test_mismatched_new_passwords_do_not_change_it(self):
        url = self._open_reset_form()
        self.client.post(url, {'password1': NEW_PASSWORD, 'password2': 'something-else'})
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(GOOD_PASSWORD))

    def test_cannot_reset_to_the_current_password(self):
        """allauth permits this by default — UCSResetPasswordKeyForm must not."""
        url = self._open_reset_form()
        resp = self.client.post(url, {'password1': GOOD_PASSWORD, 'password2': GOOD_PASSWORD})
        self.assertEqual(resp.status_code, 200)
        self.assertIn('already your current password', resp.content.decode())

    def test_successful_reset_changes_password_mails_and_returns_to_login(self):
        url = self._open_reset_form()
        mail.outbox.clear()
        resp = self.client.post(url, {'password1': NEW_PASSWORD, 'password2': NEW_PASSWORD},
                                follow=True)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(NEW_PASSWORD))
        self.assertFalse(self.user.check_password(GOOD_PASSWORD), 'old password still works')
        self.assertEqual(resp.redirect_chain[-1][0], reverse('myhub:page-login'))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('password', mail.outbox[0].subject.lower())

    def test_unknown_address_is_indistinguishable(self):
        """No account enumeration.

        allauth's ACCOUNT_PREVENT_ENUMERATION deliberately e-mails an
        "unknown account" notice rather than staying silent, so that neither the
        page nor the presence of a mail reveals whether the address is
        registered. Assert that the *reset key* is what's withheld.
        """
        resp = self.client.post(self.url, {'email': 'stranger@example.com'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertNotIn('password/reset/key', mail.outbox[0].body)


# ---------------------------------------------------------------------------
# Brute-force lockout (django-axes) and the sign-in view that feeds it
# ---------------------------------------------------------------------------
@override_settings(CACHES=LOCMEM_CACHE, ACCOUNT_RATE_LIMITS={},
                   AXES_FAILURE_LIMIT=5, AXES_RESET_ON_SUCCESS=True)
class BruteForceLockoutTests(CacheIsolatedTestCase):
    """django-axes locks an account/IP pair after repeated failures.

    The sign-in page authenticates directly rather than going through allauth's
    LoginView, so it has to cooperate with axes by hand — which is exactly where
    this went wrong once already: the view called ``authenticate()`` twice per
    attempt (once with the e-mail, once with a legacy username), so every honest
    fumble spent *two* of the account's six-attempt budget and users were locked
    out in three tries.
    """

    def setUp(self):
        super().setUp()
        from axes.models import AccessAttempt
        AccessAttempt.objects.all().delete()
        self.addCleanup(AccessAttempt.objects.all().delete)

        self.login_url = reverse('myhub:page-login')
        self.user = User.objects.create_user(username='learner@example.com',
                                             email='learner@example.com',
                                             password=GOOD_PASSWORD)
        EmailAddress.objects.create(user=self.user, email=self.user.email,
                                    primary=True, verified=True)

    def _attempt(self, password):
        return self.client.post(self.login_url,
                                {'email': self.user.email, 'password': password}).status_code

    def _failures(self):
        from axes.models import AccessAttempt
        row = AccessAttempt.objects.filter(username=self.user.email).first()
        return row.failures_since_start if row else 0

    def test_one_wrong_password_records_exactly_one_failure(self):
        """Two per attempt is what halved everyone's lockout budget."""
        self._attempt('wrong-password')
        self.assertEqual(self._failures(), 1,
                         'a single sign-in attempt must cost a single failure')

    def test_three_fumbles_still_leave_the_account_usable(self):
        for _ in range(3):
            self._attempt('wrong-password')
        self.assertEqual(self._attempt(GOOD_PASSWORD), 302,
                         'three mistakes must not lock a real user out')

    def test_a_successful_sign_in_clears_the_failure_record(self):
        for _ in range(3):
            self._attempt('wrong-password')
        self._attempt(GOOD_PASSWORD)
        self.assertEqual(self._failures(), 0)

    def test_sustained_guessing_locks_the_account_out(self):
        codes = [self._attempt('wrong-password') for _ in range(8)]
        self.assertIn(429, codes, f'brute force was never stopped: {codes}')

    def test_even_the_right_password_is_refused_once_locked_out(self):
        """The security property: a lockout is not bypassed by guessing correctly."""
        for _ in range(8):
            self._attempt('wrong-password')
        response = self.client.post(self.login_url,
                                    {'email': self.user.email, 'password': GOOD_PASSWORD})
        self.assertEqual(response.status_code, 429)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_axes_considers_the_account_locked_after_the_failure_limit(self):
        from axes.handlers.proxy import AxesProxyHandler
        for _ in range(8):
            self._attempt('wrong-password')
        request = self.client.post(self.login_url,
                                   {'email': self.user.email, 'password': 'x'}).wsgi_request
        self.assertFalse(AxesProxyHandler.is_allowed(request, {'username': self.user.email}),
                         'axes should be holding this account/IP pair locked')

    def test_the_lockout_page_explains_itself_without_naming_the_account(self):
        """Shown when axes stops a sign-in. It must not confirm the account exists."""
        response = self.client.get(reverse('myhub:page-login'))
        from django.template.loader import render_to_string
        html = render_to_string('account/lockout.html', request=response.wsgi_request)
        self.assertIn('Too many attempts', html)
        self.assertIn('Reset my password', html)
        self.assertNotIn(self.user.email, html)

    def test_the_attempted_password_is_never_written_to_the_log(self):
        secret = 'Hunter2!SuperSecret'
        self._attempt(secret)
        from axes.models import AccessAttempt
        for row in AccessAttempt.objects.all():
            self.assertNotIn(secret, row.post_data or '',
                             'the attempted password must never be stored')


# ---------------------------------------------------------------------------
# My Courses — the events-style listing with a grid / list toggle
# ---------------------------------------------------------------------------
@override_settings(CACHES=LOCMEM_CACHE)
class MyProgrammesTests(CacheIsolatedTestCase):
    """The "My Programme(s)" nav target, off the academic spine.

    Courses are gone: a learner registers for a school's
    programme and its modules, so this page lists ProgrammeEnrolments.
    """

    def setUp(self):
        super().setUp()
        from apps.accounts.models import Person
        from apps.learning.models import (
            Institution, Module, Programme, ProgrammeEnrolment, ProgrammeModule,
        )

        self.url = reverse('accounts:my-programmes')
        institution = Institution.objects.create(name='United Church School', code='UCS')
        self.first = Programme.objects.create(
            institution=institution, name='Grade 10', code='GR10')
        self.second = Programme.objects.create(
            institution=institution, name='Grade 11', code='GR11')
        module = Module.objects.create(name='Financial Reporting', code='FREP')
        ProgrammeModule.objects.create(programme=self.first, module=module, code='FREP')

        email = 'learner@example.com'
        self.user = User.objects.create_user(username=email, email=email,
                                             password=GOOD_PASSWORD,
                                             first_name='Lea', last_name='Rner')
        self.person = Person.objects.get(user=self.user)
        self.person.user_type = 'student'
        self.person.registered = True
        self.person.profile_status = True
        self.person.save()
        for programme in (self.first, self.second):
            ProgrammeEnrolment.objects.create(person=self.person, programme=programme)
        self.client.force_login(self.user)

    def test_the_listing_shows_every_registered_programme(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        names = {p.name for p in response.context['programmes']}
        self.assertEqual(names, {self.first.name, self.second.name})

    def test_each_card_offers_the_modules_behind_it(self):
        html = self.client.get(self.url).content.decode()
        self.assertIn(reverse('learning:my-modules'), html)
        for programme in (self.first, self.second):
            self.assertIn(programme.full_code, html)

    def test_one_programme_goes_straight_to_its_modules(self):
        """Nobody wants a list of one — a single registration opens the modules."""
        from apps.learning.models import ProgrammeEnrolment
        ProgrammeEnrolment.objects.filter(person=self.person, programme=self.second).delete()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('learning:my-modules'))

    def test_a_learner_with_no_programme_is_sent_to_register(self):
        from apps.learning.models import ProgrammeEnrolment
        ProgrammeEnrolment.objects.filter(person=self.person).delete()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('accounts:register-course'))

