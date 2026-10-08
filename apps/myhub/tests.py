"""Tests for the public landing page and the shared navbar.

The landing page's navigation is data, not markup: the jump links and the footer
"Programmes" column are read from ``strings.landing`` in ``.strings.json``, and
the CTAs from ``brand.contact`` / ``brand.links``. That keeps the page
re-brandable — and makes it possible to point a link at a section that doesn't
exist, which is what these tests guard against.
"""

import pathlib
import re

from django.conf import settings
from django.test import TestCase, override_settings
from django.urls import reverse

from core.branding import strings

# The suite must not depend on a running Redis (USE_REDIS=true in .env).
LOCMEM_CACHE = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}

LANDING_URL = reverse('pages:landing')


@override_settings(CACHES=LOCMEM_CACHE)
class LandingPageTests(TestCase):

    def setUp(self):
        self.html = self.client.get(LANDING_URL).content.decode()

    def test_landing_is_public(self):
        self.assertEqual(self.client.get(LANDING_URL).status_code, 200)

    def test_uses_the_shared_floating_navbar(self):
        """Not a page-local copy: the same partials/navbar.html every page uses.

        The old bespoke header also left ~90px of dead space, because
        base.html's `body.su-shell` reserves room for a floating navbar that the
        landing page then didn't render.
        """
        self.assertIn('su-navbar', self.html)
        self.assertIn('su-brand', self.html)
        self.assertNotIn('header-static', self.html)

    def test_navbar_shows_the_configured_jump_links(self):
        for item in strings().get('landing', {}).get('nav', []):
            with self.subTest(link=item['label']):
                self.assertIn(item['label'], self.html)
                self.assertIn(f'href="{item["href"]}"', self.html)

    def test_every_in_page_link_points_at_a_real_section(self):
        """No dead anchors.

        `#coaching` and `#pricing` were both linked from the navbar and footer
        after their sections were removed, so the links silently scrolled
        nowhere. Fail loudly instead.
        """
        targets = set(re.findall(r'href="(#[\w-]+)"', self.html))
        targets.discard('#')
        section_ids = {'#' + i for i in re.findall(r'id="([\w-]+)"', self.html)}
        dead = targets - section_ids
        self.assertFalse(dead, f'landing page links to non-existent sections: {sorted(dead)}')

    def test_cta_links_come_from_the_branding_catalog(self):
        from django.templatetags.static import static
        brand = strings()['brand']
        self.assertIn(brand['links']['website_stories'], self.html)
        self.assertIn(static(brand['links']['application_form']), self.html)
        self.assertIn(static(brand['links']['fees_pdf']), self.html)
        self.assertIn(brand['contact']['phone'], self.html)
        self.assertIn(brand['contact']['email'], self.html)

    def test_apply_online_points_at_sign_up(self):
        self.assertIn('Apply online', self.html)
        self.assertIn(f'href="{reverse("myhub:page-register")}"', self.html)

    def test_fees_come_from_core_school(self):
        """The fee table is core.school.FEE_BANDS, formatted as rand — no DB needed."""
        from core.school import FEE_BANDS
        for band in FEE_BANDS:
            with self.subTest(band=band['label']):
                self.assertIn(band['label'], self.html)
        # Grade 1 – 3: R1 900 levy + 12 × R1 200 = R16 300; + R550 registration = R16 850.
        self.assertIn('R\u00a016\u00a0300', self.html)
        self.assertIn('R\u00a016\u00a0850', self.html)

    def test_subjects_and_school_facts_are_shown(self):
        for text in ('isiZulu First Additional Language', 'Coding and Robotics',
                     'Physical Sciences', 'Term 1', 'United We Stand',
                     strings()['school']['principal']):
            with self.subTest(text=text):
                self.assertIn(text, self.html)

    def test_no_thrive_leftovers(self):
        for text in ('Blueprint', 'Thrive', 'Payhip', 'PGDA', 'past-paper', 'Talk to David'):
            with self.subTest(text=text):
                self.assertNotIn(text, self.html)

    def test_no_hardcoded_contact_details_in_the_template(self):
        """Re-branding must be a .strings.json edit, not a template hunt."""
        from pathlib import Path
        from django.conf import settings
        source = (Path(settings.BASE_DIR) / 'templates' / 'pages' / 'landing.html').read_text()
        body = '\n'.join(line for line in source.splitlines()
                         if not line.strip().startswith(('{#', '#', '<!--')))
        for literal in ('wa.me/', 'payhip.com/'):
            self.assertNotIn(literal, body,
                             f'{literal!r} is hard-coded — move it to .strings.json')

    def test_internal_links_do_not_open_a_new_tab(self):
        """Sign in is an internal page; only outbound CTAs get target=_blank."""
        sign_in = re.search(r'<a[^>]*href="' + re.escape(reverse('myhub:page-login')) + r'"[^>]*>',
                            self.html)
        self.assertIsNotNone(sign_in, 'no sign-in link on the landing page')
        self.assertNotIn('target="_blank"', sign_in.group(0))

    def test_footer_contact_column_is_present_and_centred(self):
        self.assertIn('Contact us', self.html)
        self.assertIn('Programmes', self.html)
        self.assertIn('justify-content-center text-center', self.html)

    def test_terms_and_privacy_are_linked(self):
        self.assertIn(reverse('pages:privacy-and-terms'),
                      self.html)


class ServerErrorTemplateTests(TestCase):
    """500.html must render with no request and no context processors.

    `django.views.defaults.server_error` calls `template.render()` without a
    request, so `dz_array` / `brand` / `strings` / `request` are all undefined.
    The theme's original 500.html looped over `…|getdata:request.path`, which
    raised while handling the error — turning every 500 into a second 500 and
    hiding the real traceback.
    """

    def test_renders_without_a_request(self):
        from django.template import loader
        html = loader.get_template('500.html').render()   # exactly as Django calls it
        self.assertIn('500', html)

    def test_does_not_depend_on_context_processors(self):
        from pathlib import Path

        from django.conf import settings
        source = (Path(settings.BASE_DIR) / 'templates' / '500.html').read_text()
        body = source.split('{% endcomment %}', 1)[-1]
        for forbidden in ('dz_array', 'request.', '{% static', '{% extends', '{% url'):
            self.assertNotIn(forbidden, body,
                             f'500.html must stay self-contained — {forbidden!r} needs a context '
                             f'that handler500 does not provide')


@override_settings(CACHES=LOCMEM_CACHE)
class SharedNavbarTests(TestCase):
    """The landing CTAs are opt-in — they must not leak onto other pages."""

    def test_marketing_ctas_only_on_landing(self):
        html = self.client.get(reverse('myhub:page-login')).content.decode()
        self.assertNotIn('Get the Blueprint', html)

    def test_other_anonymous_pages_still_offer_signup(self):
        html = self.client.get(reverse('myhub:page-login')).content.decode()
        self.assertIn('Sign up', html)


@override_settings(CACHES=LOCMEM_CACHE)
class AuthPageArtworkTests(TestCase):
    """Sign-in and sign-up must show *different* photographs beside the form.

    Both pages extend the same base, so a regression here is silent: the pages
    still render, they just quietly go back to sharing one stock image.
    """

    IMAGE_RE = re.compile(r"oblique-image[^>]*background-image:url\('([^']+)'\)")
    FOLDER = pathlib.Path(settings.BASE_DIR) / 'static' / 'images' / 'auth'
    FILES = ('sign-in.jpg', 'sign-up.jpg')

    def _install_placeholders(self):
        """Stand in for the real photographs so the wiring can be asserted.

        The artwork is supplied per deployment, so the suite must not depend on
        it being present — but it must still prove that each page asks for its
        own file when one is there.
        """
        from PIL import Image
        self.FOLDER.mkdir(parents=True, exist_ok=True)
        created = []
        for name in self.FILES:
            path = self.FOLDER / name
            if not path.exists():
                Image.new('RGB', (8, 8), (210, 210, 210)).save(path)
                created.append(path)
        self.addCleanup(lambda: [p.unlink(missing_ok=True) for p in created])

    def _side_image(self, url):
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, url)
        match = self.IMAGE_RE.search(response.content.decode())
        self.assertIsNotNone(match, f'{url} has no side artwork at all')
        return match.group(1)

    def test_each_auth_page_asks_for_its_own_image(self):
        self._install_placeholders()
        sign_in = self._side_image(reverse('myhub:page-login'))
        sign_up = self._side_image(reverse('myhub:page-register'))
        self.assertNotEqual(sign_in, sign_up,
                            'sign-in and sign-up are showing the same picture again')

    def test_the_expected_filenames_are_what_the_pages_look_for(self):
        """Pins the names the artwork has to be dropped in as."""
        self._install_placeholders()
        self.assertIn('images/auth/sign-in.jpg', self._side_image(reverse('myhub:page-login')))
        self.assertIn('images/auth/sign-up.jpg', self._side_image(reverse('myhub:page-register')))

    def test_a_missing_photo_falls_back_instead_of_going_blank(self):
        """Until the real files are added the panel shows the theme's own image."""
        if (self.FOLDER / 'sign-in.jpg').exists():
            self.skipTest('the real artwork is installed; nothing to fall back to')
        self.assertIn('curved-images', self._side_image(reverse('myhub:page-login')))
