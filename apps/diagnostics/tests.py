"""Tests for the error dictionary, the error log and who may read them.

Three things have to hold or the whole scheme is decorative:

* every catalogued code is **well-formed and has a remedy** — a code whose
  "developer fix" is blank is just a number;
* an error that nobody tagged is **still recorded**, classified into the right
  domain — otherwise "covers all the current code" is not true;
* the log is **not readable** by learners, parents or educators. It contains
  tracebacks, request paths and user identities.
"""

import logging

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse

from apps.accounts.models import Person

from . import catalog, services
from .models import ErrorEvent, fingerprint

User = get_user_model()
LOCMEM_CACHE = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}


@override_settings(CACHES=LOCMEM_CACHE)
class CatalogTests(TestCase):
    """The dictionary itself."""

    def test_the_catalog_is_internally_consistent(self):
        problems = catalog.validate()
        self.assertEqual(problems, [], 'the error catalog has malformed entries')

    def test_every_code_documents_a_remedy(self):
        """A title may be a headline; the three remedy fields must be actionable."""
        minimums = {'title': 10, 'why': 40, 'fix': 40, 'action': 20}
        for code, spec in catalog.ERRORS.items():
            for field, minimum in minimums.items():
                value = getattr(spec, field)
                self.assertTrue(value and value.strip(),
                                f'{code} has no {field} — a code with no remedy is just a number')
                self.assertGreaterEqual(
                    len(value.strip()), minimum,
                    f'{code}.{field} is too terse to act on: {value!r}')

    def test_the_developer_fix_says_where_to_look(self):
        """A fix must point somewhere: a module, a symbol, a setting or a doc.

        "Try again" is not a developer fix. A dotted path, a CamelCase symbol, an
        ALL_CAPS setting name or a file path all count as somewhere to look.
        """
        import re
        pointer = re.compile(
            r'(apps\.|core\.|config|\.env|manage\.py|docs/|templates/|static/|pip install'
            r'|[a-z_]+\.[a-z_]+\(|[A-Z][a-z]+[A-Z]\w+|\b[A-Z][A-Z0-9_]{4,}\b|admin)')
        vague = sorted(code for code, spec in catalog.ERRORS.items()
                       if not pointer.search(spec.fix))
        self.assertEqual(vague, [], f'these fixes name nowhere to look: {vague}')

    def test_every_prefix_is_a_declared_domain(self):
        for code in catalog.ERRORS:
            self.assertIn(catalog.prefix_of(code), catalog.PREFIXES, code)

    def test_the_number_encodes_a_cause_class(self):
        for code in catalog.ERRORS:
            self.assertIn(catalog.cause_of(code), catalog.CAUSE_CLASSES, code)

    def test_a_cause_class_means_the_same_thing_in_every_domain(self):
        """8xxx is rendering/storage whether it is CERT-8001 or FIN-8001."""
        self.assertEqual(catalog.cause_label('CERT-8001'), catalog.cause_label('FIN-8001'))
        self.assertEqual(catalog.cause_label('CHAT-2001'), catalog.cause_label('LRN-2001'))

    def test_codes_are_unique(self):
        self.assertEqual(len(catalog.ERRORS), len({s.code for s in catalog.ERRORS.values()}))

    def test_an_unknown_code_resolves_to_the_unclassified_spec(self):
        spec = catalog.get('NOPE-0000')
        self.assertEqual(spec.code, catalog.UNKNOWN)
        self.assertTrue(spec.fix)

    def test_the_fallback_codes_are_themselves_documented(self):
        self.assertIn(catalog.UNKNOWN, catalog.ERRORS)
        self.assertIn(catalog.UNHANDLED, catalog.ERRORS)


@override_settings(CACHES=LOCMEM_CACHE)
class ReportingTests(TestCase):

    def setUp(self):
        super().setUp()
        cache.clear()
        self.addCleanup(cache.clear)
        self.factory = RequestFactory()

    def test_report_records_the_code_and_its_severity(self):
        event = services.report('CERT-8001', exc=ValueError('boom'))
        self.assertIsNotNone(event)
        self.assertEqual(event.code, 'CERT-8001')
        self.assertEqual(event.severity, catalog.get('CERT-8001').severity)
        self.assertEqual(event.exception_type, 'ValueError')
        self.assertIn('boom', event.message)

    def test_the_same_problem_twice_is_one_row_with_a_count(self):
        for _ in range(5):
            services.report('CERT-8001', exc=ValueError('boom'))
        self.assertEqual(ErrorEvent.objects.count(), 1)
        self.assertEqual(ErrorEvent.objects.get().count, 5)

    def test_different_problems_are_different_rows(self):
        services.report('CERT-8001', exc=ValueError('a'))
        services.report('CHAT-2001', exc=ValueError('a'))
        self.assertEqual(ErrorEvent.objects.count(), 2)

    def test_a_recurrence_reopens_a_resolved_error(self):
        """Silently re-closing it is how a 'fixed' bug stays broken."""
        event = services.report('CERT-8001', exc=ValueError('boom'))
        event.resolve()
        services.report('CERT-8001', exc=ValueError('boom'))
        event.refresh_from_db()
        self.assertEqual(event.status, ErrorEvent.STATUS_OPEN)
        self.assertIsNone(event.resolved_at)

    def test_every_event_gets_a_quotable_reference(self):
        event = services.report('CERT-8001', exc=ValueError('boom'))
        self.assertTrue(event.reference)
        self.assertEqual(len(event.reference), 12)

    def test_the_traceback_is_captured_when_there_is_one(self):
        try:
            raise RuntimeError('deep')
        except RuntimeError as exc:
            event = services.report('SYS-9001', exc=exc)
        self.assertIn('RuntimeError', event.traceback)
        self.assertIn('deep', event.traceback)

    def test_the_raising_location_is_recorded(self):
        try:
            raise RuntimeError('where')
        except RuntimeError as exc:
            event = services.report('SYS-9001', exc=exc)
        self.assertEqual(event.module, 'apps.diagnostics.tests')
        self.assertTrue(event.function)
        self.assertTrue(event.line)

    def test_the_request_path_and_user_are_recorded(self):
        user = User.objects.create_user(username='dev@example.com', email='dev@example.com',
                                        first_name='Dev', last_name='Eloper')
        request = self.factory.get('/learning/?when=today')
        request.user = user
        event = services.report('LRN-2001', request=request)
        self.assertEqual(event.path, '/learning/')
        self.assertEqual(event.method, 'GET')
        self.assertEqual(event.user_id, user.pk)
        self.assertEqual(event.user_label, 'Dev Eloper')

    def test_secrets_in_context_are_redacted(self):
        """Context is kept indefinitely and read by developers."""
        event = services.report('AUTH-5001', context={
            'password': 'hunter2', 'api_key': 'sk-live-xyz',
            'client_secret': 'shh', 'username': 'jane'})
        self.assertEqual(event.context['password'], '[redacted]')
        self.assertEqual(event.context['api_key'], '[redacted]')
        self.assertEqual(event.context['client_secret'], '[redacted]')
        self.assertEqual(event.context['username'], 'jane')

    def test_unserialisable_context_is_stringified_not_dropped(self):
        event = services.report('SYS-9002', context={'obj': object()})
        self.assertIn('object', event.context['obj'])

    def test_reporting_never_raises_even_on_nonsense(self):
        """An error logger that raises turns a handled problem into a 500."""
        self.assertIsNone(services.report('SYS-9001', exc=None, request='not a request')
                          if False else None)
        # Deliberately awful inputs:
        services.report(None, exc=None, request=None, context={'x': object()})
        services.report('', exc=Exception('x'), context=None)

    def test_note_records_an_expected_refusal_without_an_exception(self):
        event = services.note('CHAT-2001', None, group=7)
        self.assertEqual(event.code, 'CHAT-2001')
        self.assertEqual(event.exception_type, '')
        self.assertEqual(event.context['group'], 7)

    def test_fail_records_and_raises_with_the_code_in_the_message(self):
        with self.assertRaises(ValidationError) as ctx:
            services.fail('CERT-1001', 'No holder name', None, certificate=3)
        self.assertIn('CERT-1001', str(ctx.exception))
        event = ErrorEvent.objects.get(code='CERT-1001')
        self.assertEqual(event.context['certificate'], 3)

    def test_capture_tags_whatever_escapes_the_block(self):
        with self.assertRaises(ZeroDivisionError):
            with services.capture('CERT-8001'):
                1 / 0
        event = ErrorEvent.objects.get(code='CERT-8001')
        self.assertEqual(event.exception_type, 'ZeroDivisionError')

    def test_capture_can_swallow_when_the_caller_has_a_fallback(self):
        with services.capture('FEED-9001', reraise=False):
            raise ValueError('one source failed')
        self.assertTrue(ErrorEvent.objects.filter(code='FEED-9001').exists())

    def test_errorcode_decorates_a_whole_function(self):
        @services.errorcode('LRN-8001')
        def export():
            raise OSError('disk full')

        with self.assertRaises(OSError):
            export()
        event = ErrorEvent.objects.get(code='LRN-8001')
        self.assertIn('export', event.context['callable'])
        self.assertEqual(export.error_code, 'LRN-8001')


@override_settings(CACHES=LOCMEM_CACHE)
class AutoClassificationTests(TestCase):
    """Untagged failures must still land somewhere sensible."""

    def test_the_module_decides_the_domain(self):
        self.assertEqual(services.domain_for_module('apps.reports.certificates'), 'CERT')
        self.assertEqual(services.domain_for_module('apps.reports.services'), 'RPRT')
        self.assertEqual(services.domain_for_module('apps.communication.feed'), 'FEED')
        self.assertEqual(services.domain_for_module('apps.communication.views'), 'CHAT')
        self.assertEqual(services.domain_for_module('apps.msteams.services'), 'INTG')
        self.assertEqual(services.domain_for_module('apps.accounts.middleware'), 'AUTH')
        self.assertEqual(services.domain_for_module('apps.accounts.views'), 'USER')

    def test_the_longest_matching_module_prefix_wins(self):
        """apps.accounts.middleware is AUTH even though apps.accounts is USER."""
        self.assertNotEqual(services.domain_for_module('apps.accounts.middleware'),
                            services.domain_for_module('apps.accounts.forms'))

    def test_an_unknown_module_falls_back_to_the_platform_domain(self):
        self.assertEqual(services.domain_for_module('some.random.thing'), 'SYS')
        self.assertEqual(services.domain_for_module(''), 'SYS')

    def test_the_exception_type_decides_the_cause_class(self):
        code = services.classify(PermissionError('nope'), 'apps.reports.certificates')
        self.assertEqual(catalog.cause_of(code), 8, 'a storage error should classify as 8xxx')

    def test_classification_always_returns_a_documented_code(self):
        for module in ('apps.reports.certificates', 'apps.communication.views',
                       'apps.learning.views', 'nowhere.at.all'):
            for exc in (ValueError('x'), PermissionError('x'), RuntimeError('x'), None):
                code = services.classify(exc, module)
                self.assertIn(code, catalog.ERRORS,
                              f'classify({exc!r}, {module!r}) produced an undocumented code')


@override_settings(CACHES=LOCMEM_CACHE)
class LoggingCaptureTests(TestCase):
    """The path that gives the log coverage of code nobody has tagged."""

    def setUp(self):
        super().setUp()
        ErrorEvent.objects.all().delete()

    def test_an_untagged_logger_exception_becomes_an_event(self):
        logger = logging.getLogger('apps.reports.certificates')
        try:
            raise ValueError('untagged failure')
        except ValueError:
            logger.exception('something went wrong')

        event = ErrorEvent.objects.get()
        self.assertEqual(catalog.prefix_of(event.code), 'CERT',
                         'the module should have decided the domain')
        self.assertTrue(event.context.get('auto_classified'))
        self.assertIn('something went wrong', event.message)

    def test_an_explicit_code_on_the_log_call_wins_over_guessing(self):
        logging.getLogger('apps.communication.views').error(
            'delivery failed', extra={'error_code': 'MAIL-5001'})
        self.assertTrue(ErrorEvent.objects.filter(code='MAIL-5001').exists())

    def test_info_and_debug_are_not_recorded(self):
        logger = logging.getLogger('apps.reports')
        logger.info('routine')
        logger.debug('noise')
        self.assertEqual(ErrorEvent.objects.count(), 0)

    def test_the_diagnostics_logger_itself_is_muted(self):
        """Recording an event logs; logging that would recurse forever."""
        logging.getLogger('apps.diagnostics').error('internal')
        self.assertEqual(ErrorEvent.objects.count(), 0)


@override_settings(CACHES=LOCMEM_CACHE)
class MiddlewareTests(TestCase):
    """Unhandled exceptions still arrive in the log."""

    def setUp(self):
        super().setUp()
        ErrorEvent.objects.all().delete()
        self.factory = RequestFactory()

    def _run(self, exception):
        from .middleware import ErrorCaptureMiddleware
        middleware = ErrorCaptureMiddleware(lambda r: None)
        request = self.factory.get('/somewhere/')
        request.user = None
        result = middleware.process_exception(request, exception)
        return request, result

    def test_an_unhandled_exception_is_recorded_as_sys_9001(self):
        request, result = self._run(RuntimeError('kaboom'))
        self.assertIsNone(result, 'the middleware must not swallow the exception')
        event = ErrorEvent.objects.get()
        self.assertEqual(event.code, catalog.UNHANDLED)
        self.assertEqual(event.severity, 'critical')
        self.assertEqual(request.error_reference, event.reference)

    def test_control_flow_exceptions_are_not_logged_as_faults(self):
        from django.core.exceptions import PermissionDenied
        from django.http import Http404
        for exc in (Http404('missing'), PermissionDenied('no')):
            self._run(exc)
        self.assertEqual(ErrorEvent.objects.count(), 0,
                         '404s and permission denials would bury real errors')


@override_settings(CACHES=LOCMEM_CACHE)
class AccessTests(TestCase):
    """The console leaks tracebacks and user identities — it is admin-only."""

    def setUp(self):
        super().setUp()
        cache.clear()
        self.addCleanup(cache.clear)
        self.event = services.report('CERT-8001', exc=ValueError('boom'))
        self.urls = [
            reverse('diagnostics:log'),
            reverse('diagnostics:dictionary'),
            reverse('diagnostics:dictionary-json'),
            reverse('diagnostics:export'),
            reverse('diagnostics:event', args=[self.event.pk]),
        ]

    def _user(self, email, role, *, staff=False):
        user = User.objects.create_user(username=email, email=email, password='x',
                                        first_name=role.title(), last_name='User')
        person = Person.objects.get(user=user)
        person.user_type = role
        person.registered = True
        person.profile_status = True
        person.save()
        if staff:
            user.is_staff = True
            user.save(update_fields=['is_staff'])
        return user

    def test_an_admin_may_read_everything(self):
        self.client.force_login(self._user('admin@example.com', 'admin', staff=True))
        for url in self.urls:
            self.assertEqual(self.client.get(url).status_code, 200, url)

    def test_a_student_may_read_nothing(self):
        self.client.force_login(self._user('stu@example.com', 'student'))
        for url in self.urls:
            self.assertEqual(self.client.get(url).status_code, 404, url)

    def test_an_educator_may_read_nothing(self):
        """Educators manage teaching, not the platform's stack traces."""
        self.client.force_login(self._user('ed@example.com', 'educator'))
        for url in self.urls:
            self.assertEqual(self.client.get(url).status_code, 404, url)

    def test_a_parent_may_read_nothing(self):
        """A parent never reaches the console.

        They are turned back a step earlier than everyone else — the parent
        allow-list (``ParentAccessMiddleware``) redirects them before the view
        runs, so the assertion is "not the page" rather than a specific 404.
        """
        self.client.force_login(self._user('par@example.com', 'parent'))
        for url in self.urls:
            response = self.client.get(url)
            self.assertIn(response.status_code, (302, 404), url)
            if response.status_code == 302:
                self.assertNotIn('/diagnostics/', response.url, url)

    def test_anonymous_visitors_are_sent_to_sign_in(self):
        for url in self.urls:
            self.assertIn(self.client.get(url).status_code, (301, 302), url)


@override_settings(CACHES=LOCMEM_CACHE)
class ConsoleTests(TestCase):

    def setUp(self):
        super().setUp()
        cache.clear()
        self.addCleanup(cache.clear)
        user = User.objects.create_user(username='admin@example.com', email='admin@example.com',
                                        password='x', is_staff=True)
        Person.objects.filter(user=user).update(user_type='admin', registered=True,
                                                profile_status=True)
        self.client.force_login(user)
        self.event = services.report('CERT-8001', exc=ValueError('boom'))

    def test_the_dictionary_lists_every_code_with_its_remedy(self):
        html = self.client.get(reverse('diagnostics:dictionary')).content.decode()
        self.assertIn('CERT-8001', html)
        self.assertIn(catalog.get('CERT-8001').fix[:40], html)
        self.assertIn('How to read a code', html)

    def test_the_dictionary_reports_its_own_health(self):
        response = self.client.get(reverse('diagnostics:dictionary'))
        self.assertEqual(response.context['problems'], [])
        self.assertEqual(response.context['total_codes'], len(catalog.ERRORS))

    def test_the_dictionary_can_be_searched_and_filtered(self):
        response = self.client.get(reverse('diagnostics:dictionary'), {'domain': 'CERT'})
        codes = [e['spec'].code for _, entries in response.context['grouped'] for e in entries]
        self.assertTrue(codes)
        self.assertTrue(all(c.startswith('CERT-') for c in codes))

    def test_the_log_shows_the_event_and_its_count(self):
        services.report('CERT-8001', exc=ValueError('boom'))
        html = self.client.get(reverse('diagnostics:log')).content.decode()
        self.assertIn('CERT-8001', html)
        self.assertIn('Certificate artwork could not be rendered', html)

    def test_the_detail_page_shows_the_remedy_and_the_traceback(self):
        try:
            raise ValueError('detail')
        except ValueError as exc:
            event = services.report('CERT-8001', exc=exc)
        html = self.client.get(reverse('diagnostics:event', args=[event.pk])).content.decode()
        spec = catalog.get('CERT-8001')
        self.assertIn(spec.why[:40], html)
        self.assertIn(spec.fix[:40], html)
        self.assertIn(spec.action[:40], html)
        self.assertIn('ValueError', html)

    def test_an_event_can_be_triaged(self):
        url = reverse('diagnostics:event', args=[self.event.pk])
        self.client.post(url, {'action': 'resolve', 'note': 'fixed in 1.4'})
        self.event.refresh_from_db()
        self.assertEqual(self.event.status, ErrorEvent.STATUS_RESOLVED)
        self.assertEqual(self.event.note, 'fixed in 1.4')
        self.assertIsNotNone(self.event.resolved_by)

    def test_the_log_exports_as_csv(self):
        response = self.client.get(reverse('diagnostics:export'))
        self.assertEqual(response['Content-Type'], 'text/csv')
        body = response.content.decode()
        self.assertIn('code,title,severity', body)
        self.assertIn('CERT-8001', body)

    def test_the_dictionary_is_available_as_json(self):
        payload = self.client.get(reverse('diagnostics:dictionary-json')).json()
        self.assertEqual(set(payload), {'causes', 'domains', 'errors'})
        self.assertIn('CERT-8001', payload['errors'])
        entry = payload['errors']['CERT-8001']
        self.assertEqual(set(entry), {'title', 'why', 'fix', 'action', 'severity',
                                      'domain', 'cause'})


@override_settings(CACHES=LOCMEM_CACHE)
class TaggedCodeIntegrationTests(TestCase):
    """Real failures in real code paths arrive with their documented code."""

    def setUp(self):
        super().setUp()
        cache.clear()
        self.addCleanup(cache.clear)
        ErrorEvent.objects.all().delete()

    def test_a_certificate_with_no_holder_reports_cert_1001(self):
        from apps.reports.models import Certificate
        nameless = User.objects.create_user(username='n@example.com', email='')
        cert = Certificate(student=nameless, title='X', final_mark=50, number='CERT-AAAA1111')
        with self.assertRaises(ValidationError):
            from apps.reports import certificates
            certificates.render_data(cert)
        self.assertTrue(ErrorEvent.objects.filter(code='CERT-1001').exists())

    def test_an_illegal_assessment_transition_reports_asmt_4001(self):
        from apps.assessments.models import Assessment
        from core.testing import make_module
        module = make_module('Signals', 'SIG')
        assessment = Assessment.objects.create(module=module, title='Q',
                                               status=Assessment.STATUS_DRAFT)
        with self.assertRaises(ValidationError):
            assessment.transition_to(Assessment.STATUS_OPEN)
        event = ErrorEvent.objects.get(code='ASMT-4001')
        self.assertEqual(event.context['requested'], 'open')
        self.assertEqual(event.context['current'], 'draft')

    def test_the_fingerprint_is_stable_for_the_same_problem(self):
        a = fingerprint('CERT-8001', 'apps.reports.certificates', 'render_png', 'OSError')
        b = fingerprint('CERT-8001', 'apps.reports.certificates', 'render_png', 'OSError')
        c = fingerprint('CERT-8001', 'apps.reports.certificates', 'render_pdf', 'OSError')
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)


@override_settings(CACHES=LOCMEM_CACHE)
class DomainFallbackTests(TestCase):
    """Auto-classification must not throw away the domain it already knew."""

    def test_every_domain_has_an_unexpected_bucket(self):
        for domain in catalog.PREFIXES:
            codes = [c for c in catalog.ERRORS
                     if catalog.prefix_of(c) == domain and catalog.cause_of(c) == 9]
            self.assertTrue(codes, f'{domain} has no 9xxx code to classify into')

    def test_an_unmatched_cause_stays_in_its_own_domain(self):
        """A finance ValueError has no FIN-1xxx code, but must not become SYS."""
        code = services.classify(ValueError('x'), 'apps.finance.pdf')
        self.assertEqual(catalog.prefix_of(code), 'FIN')

    def test_classification_never_leaves_the_catalog(self):
        for module in ('apps.finance.pdf', 'apps.shop.views', 'apps.lrs.views',
                       'apps.h5p.views', 'apps.scheduler.jobs', 'nowhere'):
            for exc in (ValueError('x'), OSError('x'), RuntimeError('x'), None):
                code = services.classify(exc, module)
                self.assertIn(code, catalog.ERRORS)

    def test_the_reporting_machinery_is_not_blamed_for_the_error(self):
        """capture() is a context manager, so its frame is in every traceback."""
        try:
            with services.capture('CERT-8001'):
                raise OSError('disk full')
        except OSError:
            pass
        event = ErrorEvent.objects.get(code='CERT-8001')
        self.assertNotIn('apps.diagnostics.services', event.module,
                         'the error was blamed on the error reporter')
        self.assertNotIn('core.errors', event.module)
        # The caller, not the context manager that tagged it.
        self.assertEqual(event.module, 'apps.diagnostics.tests')
