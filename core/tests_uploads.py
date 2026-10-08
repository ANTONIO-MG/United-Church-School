"""Uploads must be checked, and media must not run as script in our origin.

Every FileField/ImageField in the project once accepted anything of any size.
The two consequences are different in kind: an unbounded upload fills the disk,
while an uploaded ``.svg`` or ``.html`` served from the media domain executes
*in this site's origin* with access to the session cookie.

The second is the one extension validators cannot fully close, because ``.svg``
has to stay allowed for logos and avatars — so it is handled by response headers
instead (:mod:`core.media_headers`).
"""

import shutil
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import re_path
from django.views.static import serve

from core import validators as v


class CoverageTests(TestCase):
    def test_every_file_field_in_the_project_has_validators(self):
        """The regression guard: a new FileField added without any fails here."""
        from django.apps import apps

        missing = [
            f'{model._meta.label}.{field.name}'
            for model in apps.get_models()
            for field in model._meta.get_fields()
            if field.__class__.__name__ in ('FileField', 'ImageField')
            and not getattr(field, 'validators', [])
        ]
        self.assertEqual(missing, [], f'file fields with no validators: {missing}')


class MaxFileSizeTests(TestCase):
    def test_a_file_over_the_limit_is_rejected(self):
        check = v.MaxFileSize(1)
        big = SimpleUploadedFile('big.pdf', b'x' * (2 * v.MB))
        with self.assertRaises(ValidationError) as ctx:
            check(big)
        self.assertEqual(ctx.exception.code, 'file_too_large')

    def test_a_file_under_the_limit_passes(self):
        v.MaxFileSize(1)(SimpleUploadedFile('small.pdf', b'x' * 1024))

    def test_it_is_deconstructible_for_migrations(self):
        """Validators must serialise, or makemigrations cannot write them out."""
        path, args, kwargs = v.MaxFileSize(5).deconstruct()
        self.assertEqual(path, 'core.validators.MaxFileSize')
        self.assertEqual(args, (5,))

    def test_equal_instances_compare_equal(self):
        """Unequal instances would make makemigrations detect a change forever."""
        self.assertEqual(v.MaxFileSize(5), v.MaxFileSize(5))
        self.assertNotEqual(v.MaxFileSize(5), v.MaxFileSize(6))


class ExtensionTests(TestCase):
    def _run(self, validators, filename):
        upload = SimpleUploadedFile(filename, b'data')
        for check in validators:
            check(upload)

    def test_an_executable_extension_is_refused_on_a_document_field(self):
        for name in ('payload.html', 'payload.js', 'payload.svg', 'shell.php'):
            with self.subTest(name=name), self.assertRaises(ValidationError):
                self._run(v.validate_document, name)

    def test_ordinary_documents_pass(self):
        for name in ('slip.pdf', 'marks.xlsx', 'notes.docx', 'export.csv'):
            with self.subTest(name=name):
                self._run(v.validate_document, name)

    def test_svg_is_allowed_as_an_image_but_flagged_never_inline(self):
        """It is a real image format and a script vector at the same time."""
        self._run([v.validate_image[0]], 'logo.svg')
        self.assertTrue(v.must_download('logo.svg'))

    def test_must_download_covers_the_dangerous_extensions(self):
        for name in ('a.svg', 'a.html', 'a.htm', 'a.xml', 'a.js', 'a.css'):
            with self.subTest(name=name):
                self.assertTrue(v.must_download(name))
        for name in ('a.png', 'a.pdf', 'a.docx', 'a.mp4', 'noextension'):
            with self.subTest(name=name):
                self.assertFalse(v.must_download(name))

    def test_extension_matching_is_case_insensitive(self):
        self.assertTrue(v.must_download('LOGO.SVG'))
        with self.assertRaises(ValidationError):
            self._run(v.validate_document, 'payload.HTML')


# config/urls.py appends the media route inside ``if settings.DEBUG:``, which is
# evaluated once at import — and the test runner forces DEBUG=False, so
# override_settings(DEBUG=True) comes too late and every /media/ URL 404s. This
# urlconf serves MEDIA_ROOT unconditionally for the header tests below.
urlpatterns = [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]


@override_settings(ROOT_URLCONF='core.tests_uploads')
class MediaHeaderTests(TestCase):
    """Headers are asserted against **real, served files**.

    An earlier version of these tests requested paths that did not exist. Every
    assertion passed against the 404s while the live behaviour was wrong: the
    static serve view sets ``Content-Disposition: inline`` itself, so a
    middleware that only filled in a missing header left SVGs rendering inline —
    the exact case this is meant to stop. A 200 is therefore asserted first.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.media = Path(settings.MEDIA_ROOT) / '_header_probe'
        cls.media.mkdir(parents=True, exist_ok=True)
        (cls.media / 'evil.svg').write_bytes(
            b'<svg xmlns="http://www.w3.org/2000/svg">'
            b'<script>alert(document.cookie)</script></svg>')
        (cls.media / 'evil.html').write_bytes(b'<script>alert(1)</script>')
        (cls.media / 'ok.png').write_bytes(b'\x89PNG\r\n\x1a\n')
        (cls.media / 'notes.pdf').write_bytes(b'%PDF-1.4')

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.media, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.client = Client()

    def _get(self, name):
        response = self.client.get(f'/media/_header_probe/{name}')
        self.assertEqual(response.status_code, 200,
                         f'{name} was not served — the assertions below would be vacuous')
        return response

    def test_svg_is_forced_to_download(self):
        response = self._get('evil.svg')
        self.assertEqual(response.headers.get('X-Content-Type-Options'), 'nosniff')
        self.assertIn('attachment', response.headers.get('Content-Disposition', ''))
        self.assertNotIn('inline', response.headers.get('Content-Disposition', ''))

    def test_html_is_forced_to_download(self):
        response = self._get('evil.html')
        self.assertIn('attachment', response.headers.get('Content-Disposition', ''))

    def test_an_ordinary_image_is_not_forced_to_download(self):
        response = self._get('ok.png')
        self.assertEqual(response.headers.get('X-Content-Type-Options'), 'nosniff')
        self.assertNotIn('attachment', response.headers.get('Content-Disposition', ''))

    def test_a_pdf_still_opens_inline(self):
        response = self._get('notes.pdf')
        self.assertNotIn('attachment', response.headers.get('Content-Disposition', ''))

    def test_media_responses_are_sandboxed(self):
        response = self._get('ok.png')
        self.assertIn('sandbox', response.headers.get('Content-Security-Policy', ''))
        self.assertEqual(response.headers.get('X-Frame-Options'), 'DENY')

    @override_settings(ROOT_URLCONF='config.urls')
    def test_ordinary_pages_are_untouched(self):
        response = self.client.get('/')
        self.assertNotIn('sandbox', response.headers.get('Content-Security-Policy', ''))


class UploadSizeSettingTests(TestCase):
    def test_request_body_is_capped(self):
        from django.conf import settings

        self.assertLessEqual(settings.DATA_UPLOAD_MAX_MEMORY_SIZE, 500 * v.MB)
        self.assertTrue(settings.DATA_UPLOAD_MAX_MEMORY_SIZE > 0)
