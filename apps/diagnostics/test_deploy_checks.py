"""The deployment guards must fire on production misconfiguration — and only then.

Production used to run with development settings because the HTTPS block in
``config/settings.py`` was commented out with "enable in production" beside it,
and nobody uncomments a block. Those settings now derive from ``DEBUG``, so the
secure value is the default; these checks catch the remaining case, where an
environment variable explicitly overrides one back.

The half that matters most is the negative: a developer's machine and the test
runner must be completely unaffected, or the guards get switched off.
"""

from django.test import TestCase, override_settings

from . import deploy_checks as dc


def _ids(results):
    return sorted(r.id for r in results)


PROD = dict(TESTING=False, DEBUG=False)


class GuardsStandDownTests(TestCase):
    """Nothing fires in development, or under the test runner."""

    @override_settings(DEBUG=True, ALLOWED_HOSTS=['*'], SESSION_COOKIE_SECURE=False,
                       CSRF_COOKIE_SECURE=False, SECURE_SSL_REDIRECT=False,
                       SECURE_HSTS_SECONDS=0, CORS_ALLOW_ALL_ORIGINS=True,
                       SECRET_KEY='django-insecure-abc')
    def test_development_is_untouched(self):
        for check in (dc.allowed_hosts_is_not_a_wildcard,
                      dc.cookies_and_transport_are_secure,
                      dc.cors_is_not_wide_open,
                      dc.secret_key_is_not_the_shipped_default):
            self.assertEqual(check(None), [], check.__name__)

    @override_settings(TESTING=True, DEBUG=False, ALLOWED_HOSTS=['*'],
                       SESSION_COOKIE_SECURE=False, CORS_ALLOW_ALL_ORIGINS=True,
                       SECRET_KEY='django-insecure-abc')
    def test_the_test_runner_is_untouched(self):
        """The runner forces DEBUG=False; TESTING is what tells them apart."""
        for check in (dc.allowed_hosts_is_not_a_wildcard,
                      dc.cookies_and_transport_are_secure,
                      dc.cors_is_not_wide_open,
                      dc.secret_key_is_not_the_shipped_default):
            self.assertEqual(check(None), [], check.__name__)


class AllowedHostsTests(TestCase):
    @override_settings(**PROD, ALLOWED_HOSTS=['*'])
    def test_wildcard_is_refused(self):
        self.assertEqual(_ids(dc.allowed_hosts_is_not_a_wildcard(None)), ['deploy.E002'])

    @override_settings(**PROD, ALLOWED_HOSTS=[])
    def test_empty_is_refused(self):
        self.assertEqual(_ids(dc.allowed_hosts_is_not_a_wildcard(None)), ['deploy.E001'])

    @override_settings(**PROD, ALLOWED_HOSTS=['ucs.org.za', 'www.ucs.org.za'])
    def test_named_hosts_pass(self):
        self.assertEqual(dc.allowed_hosts_is_not_a_wildcard(None), [])


class CookieAndTransportTests(TestCase):
    @override_settings(**PROD, SESSION_COOKIE_SECURE=False, CSRF_COOKIE_SECURE=False,
                       SECURE_SSL_REDIRECT=False, SECURE_HSTS_SECONDS=0)
    def test_all_insecure_reports_each_one(self):
        self.assertEqual(
            _ids(dc.cookies_and_transport_are_secure(None)),
            ['deploy.E003', 'deploy.E004', 'deploy.E005', 'deploy.W001'])

    @override_settings(**PROD, SESSION_COOKIE_SECURE=True, CSRF_COOKIE_SECURE=True,
                       SECURE_SSL_REDIRECT=True, SECURE_HSTS_SECONDS=31536000)
    def test_secure_config_passes(self):
        self.assertEqual(dc.cookies_and_transport_are_secure(None), [])

    @override_settings(**PROD, SESSION_COOKIE_SECURE=True, CSRF_COOKIE_SECURE=True,
                       SECURE_SSL_REDIRECT=True, SECURE_HSTS_SECONDS=0)
    def test_missing_hsts_is_only_a_warning(self):
        results = dc.cookies_and_transport_are_secure(None)
        self.assertEqual(_ids(results), ['deploy.W001'])


class CorsTests(TestCase):
    @override_settings(**PROD, CORS_ALLOW_ALL_ORIGINS=True)
    def test_wide_open_cors_is_refused(self):
        self.assertEqual(_ids(dc.cors_is_not_wide_open(None)), ['deploy.E006'])

    @override_settings(**PROD, CORS_ALLOW_ALL_ORIGINS=False)
    def test_scoped_cors_passes(self):
        self.assertEqual(dc.cors_is_not_wide_open(None), [])


class SecretKeyTests(TestCase):
    @override_settings(**PROD, SECRET_KEY='django-insecure-bq5ce)%1j-iqh@snbr6')
    def test_the_committed_fallback_is_refused(self):
        self.assertEqual(_ids(dc.secret_key_is_not_the_shipped_default(None)),
                         ['deploy.E007'])

    @override_settings(**PROD, SECRET_KEY='a-genuinely-random-production-value')
    def test_a_real_key_passes(self):
        self.assertEqual(dc.secret_key_is_not_the_shipped_default(None), [])
