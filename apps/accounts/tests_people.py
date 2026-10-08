"""People are shown by picture and name; the person card shows nothing private."""

from django.template import Context, Template
from django.test import TestCase
from django.urls import reverse

from apps.learning.models import ModuleEnrolment
from apps.livesessions.tests import make_user
from core.testing import make_module
from core.utils import display_name

from .models import Person, UserSettings


class PeopleTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.fac = make_module('Financial Accounting', 'FAC188')
        cls.ann = make_user('ann', 'student', first_name='Ann', last_name='Mokoena')
        cls.ben = make_user('ben', 'student', first_name='Ben', last_name='Dlamini')
        Person.objects.filter(user=cls.ann).update(phone='0821234567', gender='female')
        for u in (cls.ann, cls.ben):
            ModuleEnrolment.objects.create(person=u.profile, programme_module=cls.fac)
        cls.edu = make_user('eve', 'educator', first_name='Eve', last_name='Naidoo')
        cls.edu.profile.taught_modules.add(cls.fac)

    def card(self, viewer, target, fragment=True):
        self.client.force_login(viewer)
        url = reverse('accounts:person-card', args=[target.profile.pk])
        return self.client.get(url + ('?fragment=1' if fragment else ''))

    def test_display_name_prefers_the_profile_name_over_the_login(self):
        self.assertEqual(display_name(self.ann), 'Ann Mokoena')

    def test_card_shows_name_role_and_shared_modules_but_nothing_private(self):
        r = self.card(self.ben, self.ann)
        self.assertContains(r, 'Ann Mokoena')
        self.assertContains(r, 'FAC188')            # a module they share
        self.assertContains(r, 'default-female.svg')
        for private in (self.ann.email, '0821234567'):
            self.assertNotContains(r, private)

    def test_educator_card_lists_what_they_teach(self):
        r = self.card(self.ben, self.edu)
        self.assertContains(r, 'Teaches')
        self.assertContains(r, 'FAC188')

    def test_private_profile_shows_only_name_and_picture(self):
        s = UserSettings.for_user(self.ann)
        s.profile_visibility = UserSettings.VISIBILITY_PRIVATE
        s.save()
        r = self.card(self.ben, self.ann)
        self.assertContains(r, 'Ann Mokoena')
        self.assertContains(r, 'keeps their profile private')
        self.assertNotContains(r, 'FAC188')

    def test_card_page_and_user_id_route(self):
        self.assertEqual(self.card(self.ben, self.ann, fragment=False).status_code, 200)
        self.client.force_login(self.ben)
        r = self.client.get(reverse('accounts:person-card-user', args=[self.ann.pk]) + '?fragment=1')
        self.assertContains(r, 'Ann Mokoena')

    def test_person_chip_renders_picture_name_and_card_link(self):
        html = Template('{% load people %}{% person_chip who %}').render(Context({'who': self.ann}))
        self.assertIn('Ann Mokoena', html)
        self.assertIn('data-person-card=', html)
        self.assertIn('<img', html)
        self.assertNotIn(self.ann.email, html)
