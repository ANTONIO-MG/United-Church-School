"""``/api/myhub/`` must not answer anonymous callers.

The site is private — ``LoginRequiredMiddleware`` redirects logged-out visitors
everywhere — but ``/api/`` is on that middleware's exempt list, because DRF
authenticates itself and has to answer in JSON rather than redirect. That made
``IsAuthenticatedOrReadOnly`` on the myhub viewsets the one anonymous read path
into the site. It once exposed learner and staff records; after the clean sweep
only the calendar is left, which still carries titles, locations and
descriptions. This test keeps the gate shut as viewsets are added back.
"""

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.utils import timezone

from . import models

User = get_user_model()


class EventApiRequiresAuthTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='member', email='member@example.com', password='pw12345!')
        now = timezone.now()
        cls.event = models.Event.objects.create(
            title='Staff briefing', location='Boardroom', start=now, end=now)

    def test_anonymous_cannot_list_events(self):
        response = Client().get('/api/myhub/events/')
        self.assertIn(response.status_code, (401, 403))

    def test_anonymous_cannot_retrieve_an_event(self):
        response = Client().get(f'/api/myhub/events/{self.event.pk}/')
        self.assertIn(response.status_code, (401, 403))

    def test_anonymous_cannot_write(self):
        client = Client()
        self.assertIn(
            client.post('/api/myhub/events/', {'title': 'x'},
                        content_type='application/json').status_code, (401, 403))
        self.assertIn(
            client.delete(f'/api/myhub/events/{self.event.pk}/').status_code, (401, 403))

    def test_signed_in_user_can_still_read(self):
        client = Client()
        client.force_login(self.user)
        response = client.get('/api/myhub/events/')
        self.assertEqual(response.status_code, 200)
