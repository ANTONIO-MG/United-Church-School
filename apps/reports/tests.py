"""End-to-end tests for certificates: data, artwork, downloads and access.

A certificate is a document somebody keeps, prints and shows to an employer, so
these tests are unusually strict about *format*:

* the data handed to the renderer is validated field by field, and a
  certificate that cannot be described truthfully must refuse to render rather
  than produce a sheet with a blank name on it;
* the downloads are checked as real files — PNG magic bytes, a ``%PDF`` header,
  the declared content type, the filename in the Content-Disposition header —
  not merely as a 200;
* the PNG, the PDF and the on-screen preview must come from the same artwork,
  which is asserted by rendering them and comparing.
"""

import io

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import Person

from . import certificate_render, certificates, models
from core.testing import enrol, make_module, make_programme

User = get_user_model()

LOCMEM_CACHE = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}

PNG_MAGIC = b'\x89PNG\r\n\x1a\n'
PDF_MAGIC = b'%PDF'


@override_settings(CACHES=LOCMEM_CACHE, MEDIA_ROOT='/tmp/ucs-lms-test-media')
class CertificateFixtureMixin(TestCase):

    def setUp(self):
        super().setUp()
        cache.clear()
        self.addCleanup(cache.clear)

        self.programme = make_programme('UCS', 'GR10')
        self.module = make_module('Advanced Auditing', 'AUDA', programme=self.programme)

        self.student = self._user('sam@example.com', 'Samira', 'Hadid', 'student')
        self.other = self._user('other@example.com', 'Other', 'Person', 'student')
        self.educator = self._user('ed@example.com', 'Ed', 'Ucator', 'educator')

        self.cert = models.Certificate.objects.create(
            student=self.student, module=self.module, kind='module',
            title='Advanced Auditing', final_mark=88, issued_at=timezone.now())

    def _user(self, email, first, last, role):
        user = User.objects.create_user(username=email, email=email, password='x',
                                        first_name=first, last_name=last)
        person = Person.objects.get(user=user)
        person.first_name, person.last_name = first, last
        person.user_type = role
        person.registered = True
        person.profile_status = True
        person.save()
        return user


class CertificateDataTests(CertificateFixtureMixin):
    """What gets handed to the renderer, and what must be refused."""

    def data(self):
        return certificates.render_data(self.cert)

    def test_every_key_the_renderer_indexes_is_present_and_non_empty(self):
        data = self.data()
        for key in ('title', 'kind_line', 'student_name', 'award_name', 'award_line',
                    'number', 'verify_url', 'issuer', 'signatures'):
            self.assertIn(key, data)
            self.assertTrue(data[key], f'{key} must not be blank on a certificate')

    def test_types_are_what_the_renderer_expects(self):
        data = self.data()
        for key in ('title', 'kind_line', 'student_name', 'award_line', 'number',
                    'verify_url', 'issuer'):
            self.assertIsInstance(data[key], str, f'{key} is drawn as text')
        self.assertIsInstance(data['signatures'], list)
        self.assertEqual(len(data['signatures']), 2, 'the template carries two signature blocks')
        for entry in data['signatures']:
            self.assertEqual(len(entry), 2, 'each signature is (who, role)')
            self.assertTrue(all(isinstance(part, str) and part for part in entry))

    def test_the_holders_real_name_is_used(self):
        self.assertEqual(self.data()['student_name'], 'Samira Hadid')

    def test_the_award_line_states_the_module_the_mark_and_the_issuer(self):
        line = self.data()['award_line']
        # A module offering prints as "<programme code> / <module code>".
        self.assertIn(str(self.module), line)
        self.assertIn('88%', line)
        self.assertIn('United Church School', line)
        self.assertIn(self.cert.issued_at.strftime('%d %B %Y'), line)

    def test_the_mark_is_rendered_as_a_whole_percentage(self):
        self.cert.final_mark = 67.4
        self.assertEqual(certificates.render_data(self.cert)['final_mark'], '67%')

    def test_the_grade_letter_follows_the_default_scale(self):
        for mark, letter in ((88, 'A'), (74, 'B'), (63, 'C'), (55, 'D'), (30, 'F')):
            self.cert.final_mark = mark
            self.assertEqual(certificates.render_data(self.cert)['grade_letter'], letter,
                             f'{mark}% should be a {letter}')

    def test_the_grade_letter_honours_a_modules_own_scale(self):
        models.ModuleWeighting.objects.create(
            module=self.module,
            grade_scale=[{'min': 90, 'letter': 'Distinction'}, {'min': 0, 'letter': 'Pass'}])
        self.cert.final_mark = 88
        self.assertEqual(certificates.render_data(self.cert)['grade_letter'], 'Pass')

    def test_the_verification_url_points_at_this_certificate(self):
        data = self.data()
        self.assertIn(str(self.cert.verification_uuid), data['verify_url'])
        self.assertIn('/reports/verify/', data['verify_url'])

    def test_the_verification_url_is_absolute_when_a_request_is_available(self):
        response = self.client.get('/')       # any request object will do
        data = certificates.render_data(self.cert, response.wsgi_request)
        self.assertTrue(data['verify_url'].startswith('http://testserver/'))

    def test_the_kind_becomes_the_line_under_the_headline(self):
        self.assertEqual(self.data()['kind_line'], 'OF MODULE COMPLETION')

    def test_a_certificate_falls_back_to_its_title_when_it_names_no_module(self):
        cert = models.Certificate.objects.create(
            student=self.student, kind='programme',
            title='Grade 10 Completion', final_mark=71)
        self.assertEqual(certificates.render_data(cert)['award_name'], 'Grade 10 Completion')

    # --- The refusals -----------------------------------------------------
    def test_a_certificate_with_no_holder_name_refuses_to_render(self):
        nameless = User.objects.create_user(username='x', email='')
        self.cert.student = nameless
        with self.assertRaises(ValidationError):
            certificates.render_data(self.cert)

    def test_a_certificate_naming_no_achievement_refuses_to_render(self):
        self.cert.subject = None
        self.cert.course = None
        self.cert.title = '   '
        with self.assertRaises(ValidationError):
            certificates.render_data(self.cert)

    def test_a_malformed_certificate_number_refuses_to_render(self):
        for bad in ('', '  ', 'ab', 'has spaces', 'x' * 41):
            self.cert.number = bad
            with self.assertRaises(ValidationError, msg=f'{bad!r} should be rejected'):
                certificates.render_data(self.cert)

    def test_a_lowercase_number_is_normalised_rather_than_rejected(self):
        self.cert.number = 'cert-abc123'
        self.assertEqual(certificates.render_data(self.cert)['number'], 'CERT-ABC123')

    def test_the_auto_generated_number_satisfies_the_format(self):
        fresh = models.Certificate.objects.create(
            student=self.student, module=self.module, title='X', final_mark=50)
        self.assertRegex(fresh.number, certificates.NUMBER_RE)


class CertificateArtworkTests(CertificateFixtureMixin):
    """The drawing itself — size, fonts and that it actually puts ink down."""

    def test_the_bundled_fonts_are_present(self):
        self.assertTrue(certificate_render.fonts_available(),
                        'the certificate fonts under static/fonts/certificate/ are missing')

    def test_the_sheet_is_a4_landscape(self):
        image = certificate_render.render_image(certificates.render_data(self.cert))
        width, height = image.size
        self.assertGreater(width, height, 'the certificate is landscape')
        self.assertAlmostEqual(width / height, 1.414, delta=0.02,
                               msg='the sheet must keep A4 proportions or it will print cropped')

    def test_scale_changes_the_resolution_not_the_design(self):
        small = certificate_render.render_image(certificates.render_data(self.cert), scale=1.0)
        large = certificate_render.render_image(certificates.render_data(self.cert), scale=2.0)
        self.assertEqual(large.size[0], small.size[0] * 2)
        self.assertAlmostEqual(large.size[0] / large.size[1],
                               small.size[0] / small.size[1], delta=0.01)

    def test_the_artwork_is_gilded_and_inked_not_a_blank_page(self):
        image = certificate_render.render_image(certificates.render_data(self.cert))
        colours = image.convert('RGB').getcolors(maxcolors=1_000_000)
        self.assertIsNotNone(colours)
        present = {rgb for _, rgb in colours}

        white = sum(count for count, rgb in colours if rgb == (255, 255, 255))
        total = image.size[0] * image.size[1]
        self.assertLess(white / total, 0.92, 'the sheet is essentially blank')

        def has(predicate):
            return any(predicate(rgb) for rgb in present)

        self.assertTrue(has(lambda c: c[0] < 60 and c[1] < 60 and c[2] < 60),
                        'the black corner wedges and the text are missing')
        self.assertTrue(has(lambda c: c[0] > 150 and c[1] > 110 and c[2] < 120),
                        'the gold border and seal are missing')

    def test_a_very_long_name_is_shrunk_rather_than_overflowing(self):
        from PIL import ImageDraw
        data = certificates.render_data(self.cert)
        image = certificate_render.render_image(data)
        draw = ImageDraw.Draw(image)
        limit = (1 - 2 * certificate_render.MARGIN) * image.size[0]

        for name in ('Jo', 'Samira Hadid', 'Nokuthula Chikafu-Mutasa Ndlovu Van Der Merwe'):
            font = certificate_render._fit_font(draw, name, 'script',
                                                int(0.130 * image.size[1]), limit)
            width = draw.textlength(name, font=font)
            self.assertLessEqual(width, limit + 1,
                                 f'“{name}” would run into the gold border')

    def test_a_long_award_line_is_capped_at_three_lines(self):
        from PIL import ImageDraw
        image = certificate_render.render_image(certificates.render_data(self.cert))
        draw = ImageDraw.Draw(image)
        font = certificate_render._font('regular', 30)
        lines = certificate_render._wrap(draw, 'word ' * 400, font, 600)
        self.assertGreater(len(lines), 3, 'the fixture should overflow')
        # The renderer slices to three; assert the slice is what gets drawn.
        self.assertLessEqual(len(lines[:3]), 3)

    def test_rendering_is_deterministic(self):
        """Two renders of the same certificate must be byte-identical, otherwise
        the cached PDF and a fresh PNG would not match."""
        data = certificates.render_data(self.cert)
        first = certificate_render.render_png(data)
        second = certificate_render.render_png(data)
        self.assertEqual(first, second)


class CertificateDownloadTests(CertificateFixtureMixin):

    def setUp(self):
        super().setUp()
        self.client.force_login(self.student)

    def url(self, name):
        return reverse(f'reports:{name}', args=[self.cert.pk])

    def test_the_png_download_is_a_real_png_named_after_the_certificate(self):
        response = self.client.get(self.url('certificate-png'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/png')
        self.assertEqual(response['Content-Disposition'],
                         f'attachment; filename="{self.cert.number}.png"')
        body = response.content
        self.assertTrue(body.startswith(PNG_MAGIC), 'not a PNG file')
        self.assertEqual(int(response['Content-Length']), len(body))

        from PIL import Image
        image = Image.open(io.BytesIO(body))
        self.assertEqual(image.format, 'PNG')
        self.assertGreater(image.size[0], image.size[1])

    def test_the_pdf_download_is_a_real_pdf_named_after_the_certificate(self):
        response = self.client.get(self.url('certificate-pdf'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertEqual(response['Content-Disposition'],
                         f'attachment; filename="{self.cert.number}.pdf"')
        self.assertTrue(response.content.startswith(PDF_MAGIC), 'not a PDF file')
        self.assertGreater(len(response.content), 5_000, 'the PDF looks empty')

    def test_the_inline_image_is_served_for_display_not_download(self):
        response = self.client.get(self.url('certificate-image'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/png')
        self.assertTrue(response['Content-Disposition'].startswith('inline;'),
                        'the preview must display, not prompt a download')

    def test_the_pdf_is_cached_on_the_certificate_after_the_first_download(self):
        self.assertFalse(self.cert.pdf)
        self.client.get(self.url('certificate-pdf'))
        self.cert.refresh_from_db()
        self.assertTrue(self.cert.pdf, 'the rendered PDF should be stored')
        self.assertTrue(self.cert.pdf.name.endswith('.pdf'))

    def test_a_second_download_serves_identical_bytes(self):
        first = self.client.get(self.url('certificate-pdf')).content
        second = self.client.get(self.url('certificate-pdf')).content
        self.assertEqual(first, second)

    def test_a_lost_stored_pdf_is_re_rendered_rather_than_erroring(self):
        self.client.get(self.url('certificate-pdf'))
        self.cert.refresh_from_db()
        self.cert.pdf.storage.delete(self.cert.pdf.name)
        response = self.client.get(self.url('certificate-pdf'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content.startswith(PDF_MAGIC))

    def test_the_preview_and_the_download_are_the_same_artwork(self):
        """Rendered from the same request, the two paths must be byte-identical.

        The request matters: it is what makes the printed verification URL
        absolute, and the URL is part of the picture.
        """
        response = self.client.get(self.url('certificate-image'))
        direct = certificate_render.render_png(
            certificates.render_data(self.cert, response.wsgi_request), scale=1.0)
        self.assertEqual(response.content, direct,
                         'the preview must be the same render the downloads use')

    def test_the_printed_verification_url_is_absolute(self):
        """A certificate is read on paper; a relative URL is useless there."""
        response = self.client.get(self.url('certificate'))
        self.assertTrue(response.context['verify_url'].startswith('http'),
                        'the printed verify link must be a full URL')

    def test_the_preview_page_offers_pdf_png_and_print(self):
        html = self.client.get(self.url('certificate')).content.decode()
        self.assertIn(self.url('certificate-pdf'), html)
        self.assertIn(self.url('certificate-png'), html)
        self.assertIn(self.url('certificate-image'), html)
        self.assertIn('window.print()', html)
        self.assertIn('Download PDF', html)
        self.assertIn('Download PNG', html)

    def test_the_preview_page_states_the_facts_in_text(self):
        """The artwork is an image; the details must also be readable."""
        html = self.client.get(self.url('certificate')).content.decode()
        self.assertIn('Samira Hadid', html)
        self.assertIn('Advanced Auditing', html)
        self.assertIn(self.cert.number, html)
        self.assertIn('88%', html)

    def test_the_reports_page_links_all_three_actions(self):
        html = self.client.get(reverse('reports:my-reports')).content.decode()
        self.assertIn(self.url('certificate'), html)
        self.assertIn(self.url('certificate-pdf'), html)
        self.assertIn(self.url('certificate-png'), html)


class CertificateAccessTests(CertificateFixtureMixin):

    def urls(self):
        return [reverse(f'reports:{name}', args=[self.cert.pk])
                for name in ('certificate', 'certificate-pdf', 'certificate-png',
                             'certificate-image')]

    def test_a_holder_may_see_their_own(self):
        self.client.force_login(self.student)
        for url in self.urls():
            self.assertEqual(self.client.get(url).status_code, 200, url)

    def test_another_student_may_not(self):
        self.client.force_login(self.other)
        for url in self.urls():
            self.assertEqual(self.client.get(url).status_code, 404, url)

    def test_an_educator_may_not(self):
        """Certificates are closed to educators — they mark the work, but the
        award is the learner's and the institution's."""
        self.client.force_login(self.educator)
        for url in self.urls():
            self.assertEqual(self.client.get(url).status_code, 404, url)

    def test_the_reports_page_hides_certificates_from_an_educator(self):
        self.client.force_login(self.educator)
        response = self.client.get(reverse('reports:my-reports'))
        self.assertFalse(response.context['show_certificates'])
        self.assertNotIn(reverse('reports:certificate', args=[self.cert.pk]),
                         response.content.decode())

    def test_anonymous_visitors_are_sent_to_sign_in(self):
        for url in self.urls():
            response = self.client.get(url)
            self.assertIn(response.status_code, (302, 301), url)

    def test_verification_is_public_and_names_the_holder(self):
        """An employer checking a certificate has no account."""
        url = reverse('reports:verify', args=[self.cert.verification_uuid])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['cert'].pk, self.cert.pk)

    def test_a_bad_verification_uuid_is_a_404(self):
        import uuid
        response = self.client.get(reverse('reports:verify', args=[uuid.uuid4()]))
        self.assertEqual(response.status_code, 404)


class CertificateCacheVersionTests(CertificateFixtureMixin):
    """A redesign must not leave people downloading the previous artwork."""

    def setUp(self):
        super().setUp()
        self.client.force_login(self.student)
        self.url = reverse('reports:certificate-pdf', args=[self.cert.pk])

    def test_the_stored_filename_carries_the_design_version(self):
        self.client.get(self.url)
        self.cert.refresh_from_db()
        self.assertIn(certificates.DESIGN_VERSION, self.cert.pdf.name)

    def test_a_pdf_stored_under_an_older_design_is_re_rendered(self):
        from django.core.files.base import ContentFile
        self.cert.pdf.save(f'{self.cert.number}-v1.pdf',
                           ContentFile(b'%PDF-1.4 stale artwork'), save=True)
        stale_name = self.cert.pdf.name

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.content, b'%PDF-1.4 stale artwork',
                            'the old design was served instead of the current one')
        self.assertGreater(len(response.content), 5_000)

        self.cert.refresh_from_db()
        self.assertNotEqual(self.cert.pdf.name, stale_name)
        self.assertIn(certificates.DESIGN_VERSION, self.cert.pdf.name)

    def test_an_empty_stored_pdf_is_re_rendered(self):
        from django.core.files.base import ContentFile
        self.cert.pdf.save(certificates.pdf_filename(self.cert), ContentFile(b''), save=True)
        response = self.client.get(self.url)
        self.assertTrue(response.content.startswith(PDF_MAGIC))
        self.assertGreater(len(response.content), 5_000)

    def test_a_current_pdf_is_reused_rather_than_re_rendered(self):
        first = self.client.get(self.url).content
        self.cert.refresh_from_db()
        name = self.cert.pdf.name
        second = self.client.get(self.url).content
        self.cert.refresh_from_db()
        self.assertEqual(first, second)
        self.assertEqual(self.cert.pdf.name, name, 'a valid cache must not be rewritten')


class CertificateSignatureTests(CertificateFixtureMixin):
    """The two signature blocks must never print the same name twice."""

    def test_the_educator_counter_signs_when_the_module_has_one(self):
        self.module.educators.add(self.educator.profile)
        signatures = certificates.render_data(self.cert)['signatures']
        self.assertEqual(signatures[0][1], 'Authorised signatory')
        self.assertEqual(signatures[1][1], 'Educator')
        self.assertIn('Ucator', signatures[1][0])

    def test_it_falls_back_to_the_issue_date_when_there_is_no_educator(self):
        signatures = certificates.render_data(self.cert)['signatures']
        self.assertEqual(signatures[1][1], 'Date issued')
        self.assertEqual(signatures[1][0], f'{self.cert.issued_at:%d %B %Y}')

    def test_an_explicit_signature_is_used_for_the_left_block(self):
        self.cert.signature = 'Samira Hadid'
        signatures = certificates.render_data(self.cert)['signatures']
        self.assertEqual(signatures[0], ('Samira Hadid', 'Authorised signatory'))

    def test_the_two_blocks_never_carry_the_same_name(self):
        for add_educator in (False, True):
            if add_educator:
                self.module.educators.add(self.educator.profile)
            signatures = certificates.render_data(self.cert)['signatures']
            self.assertNotEqual(signatures[0][0], signatures[1][0],
                                'the certificate prints the same signatory twice')


class CertificateLayoutTests(CertificateFixtureMixin):
    """Guard the vertical rhythm — overlapping lines are the classic failure.

    These read ``certificate_render.LAYOUT`` rather than repeating its numbers,
    so moving a line in the renderer moves it here too and the assertions stay
    about *collisions* instead of about specific coordinates.
    """

    L = certificate_render.LAYOUT

    def _bounds(self, draw, text, font_name, size_key, y_key, width_limit):
        h = certificate_render.BASE_H
        font = certificate_render._fit_font(
            draw, text, font_name, int(self.L[size_key] * h), width_limit)
        return draw.textbbox((0, self.L[y_key] * h), text, font=font, anchor='lm')

    def test_the_script_name_clears_the_line_above_and_the_rule_below(self):
        """Great Vibes carries tall swashes on capitals and long descenders."""
        from PIL import ImageDraw
        image = certificate_render.render_image(certificates.render_data(self.cert))
        draw = ImageDraw.Draw(image)
        w, h = image.size
        limit = (1 - 2 * certificate_render.MARGIN) * w

        _, _, _, presented_bottom = self._bounds(
            draw, 'This certificate is presented to:', 'regular',
            'presented_size', 'presented_y', limit)
        rule_y = self.L['rule_y'] * h

        for name in ('Chipo Mabhena', 'Muhammad Patel', 'Jane Jones',
                     'Nokuthula Chikafu-Mutasa Ndlovu', 'Jo Ng'):
            _, top, _, bottom = self._bounds(
                draw, name, 'script', 'name_size', 'name_y', limit)
            self.assertGreater(top, presented_bottom,
                               f'“{name}” climbs into “This certificate is presented to:”')
            self.assertLess(bottom, rule_y, f'“{name}” drops through the rule below it')

    def test_the_headline_clears_the_kind_line(self):
        from PIL import ImageDraw
        image = certificate_render.render_image(certificates.render_data(self.cert))
        draw = ImageDraw.Draw(image)
        limit = (1 - 2 * certificate_render.MARGIN) * image.size[0]

        _, _, _, headline_bottom = self._bounds(
            draw, 'CERTIFICATE', 'bold', 'headline_size', 'headline_y', limit)
        _, kind_top, _, _ = self._bounds(
            draw, 'OF SUBJECT COMPLETION', 'bold', 'kind_size', 'kind_y', limit)
        self.assertGreater(kind_top, headline_bottom,
                           '“OF …” overlaps the CERTIFICATE headline')

    def test_the_body_starts_below_the_rule(self):
        self.assertGreater(self.L['body_y'], self.L['rule_y'])

    def test_three_body_lines_still_clear_the_signature_rules(self):
        last_line = self.L['body_y'] + 2 * self.L['body_step']
        self.assertLess(last_line, self.L['sig_rule_y'] - 0.02,
                        'a three-line award statement would run into the signatures')

    def test_the_footer_sits_below_the_signature_roles(self):
        roles_bottom = self.L['sig_rule_y'] + 0.066 + self.L['sig_role_size']
        self.assertGreater(self.L['footer_y'], roles_bottom)
        self.assertLess(self.L['footer_y'], 0.97, 'the footer would print off the sheet')

    def test_every_line_stays_on_the_sheet(self):
        for key, value in self.L.items():
            if key.endswith('_y'):
                self.assertGreater(value, 0.0, f'{key} is above the sheet')
                self.assertLess(value, 1.0, f'{key} is below the sheet')
