"""Default avatars by gender / title, and fresh URLs for re-uploaded pictures."""

import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from apps.livesessions.tests import make_user
from core.utils import avatar_url

from .models import Person, default_avatar_url, profile_picture_path

MEDIA = tempfile.mkdtemp(prefix='ucs-avatar-test-')
PNG = (b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f'
       b'\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82')


@override_settings(MEDIA_ROOT=MEDIA)
class AvatarTests(TestCase):

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA, ignore_errors=True)

    def person(self, **fields):
        user = make_user(f'u{Person.objects.count()}')
        Person.objects.filter(user=user).update(**fields)
        return Person.objects.get(user=user)

    def test_default_follows_gender_then_title(self):
        self.assertTrue(self.person(gender='male').avatar_url.endswith('default-male.svg'))
        self.assertTrue(self.person(gender='female').avatar_url.endswith('default-female.svg'))
        self.assertTrue(self.person(gender='', title='mrs').avatar_url.endswith('default-female.svg'))
        self.assertTrue(self.person(gender=None, title='mr').avatar_url.endswith('default-male.svg'))
        self.assertTrue(self.person(gender='other', title='dr').avatar_url.endswith('default-neutral.svg'))

    def test_uploaded_picture_wins(self):
        p = self.person(gender='male')
        p.profile_picture = SimpleUploadedFile('me.png', PNG, content_type='image/png')
        p.save()
        self.assertIn('/profile_pics/', p.avatar_url)
        self.assertEqual(avatar_url(p.user), p.avatar_url)

    def test_reuploading_the_same_filename_gets_a_new_url(self):
        p = self.person()
        p.profile_picture = SimpleUploadedFile('photo.jpg', PNG)
        p.save()
        first = p.avatar_url
        p.profile_picture = SimpleUploadedFile('photo.jpg', PNG)
        p.save()
        self.assertNotEqual(first, p.avatar_url)
        self.assertTrue(profile_picture_path(p, 'x.PNG').endswith('.png'))

    def test_no_profile_gets_neutral(self):
        self.assertEqual(avatar_url(None), default_avatar_url())

    def test_sidebar_shows_the_default(self):
        p = self.person(gender='female')
        self.client.force_login(p.user)
        r = self.client.get('/community/settings/')
        self.assertContains(r, 'default-female.svg')
