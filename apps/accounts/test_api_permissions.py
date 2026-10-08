"""``/api/accounts/`` must enforce the same scoping the HTML pages do.

``/api/`` is on ``LoginRequiredMiddleware``'s and ``ManagementAccessMiddleware``'s
exempt lists — DRF endpoints authenticate themselves — so every rule those
middlewares apply to a management page has to be repeated in the viewset. When
it was not, ``PersonViewSet`` was a full ``ModelViewSet`` over every Person
guarded only by ``IsAuthenticated``, with ``fields = '__all__'``: one PATCH set
your own ``user_type`` to ``admin``, and ``role_flags`` then handed you
``can_manage`` over the whole hub.

These tests pin the three properties that closed that hole: non-admins are
scoped to their own row, privileged fields are read-only for them, and
create/destroy are management actions.
"""

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from .models import Person

User = get_user_model()


def _profile(user, **kw):
    """The Person for ``user`` — a post-save signal may already have made one."""
    person, _ = Person.objects.update_or_create(user=user, defaults=kw)
    return person


class PersonApiScopingTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.learner = User.objects.create_user(
            username='learner', email='learner@example.com', password='pw12345!')
        cls.other = User.objects.create_user(
            username='other', email='other@example.com', password='pw12345!')
        cls.manager = User.objects.create_user(
            username='boss', email='boss@example.com', password='pw12345!', is_staff=True)
        cls.p_learner = _profile(cls.learner, user_type='student', first_name='Lea')
        cls.p_other = _profile(cls.other, user_type='student', first_name='Vic')
        _profile(cls.manager, user_type='admin', first_name='Boss')

    def setUp(self):
        self.client = Client()
        self.client.force_login(self.learner)

    def _rows(self, response):
        body = response.json()
        return body['results'] if isinstance(body, dict) and 'results' in body else body

    # --- privilege escalation -------------------------------------------------

    def test_learner_cannot_promote_themselves(self):
        """The defect that made this file necessary: PATCH user_type=admin."""
        self.client.patch(f'/api/accounts/people/{self.p_learner.pk}/',
                          {'user_type': 'admin'}, content_type='application/json')
        self.p_learner.refresh_from_db()
        self.assertEqual(self.p_learner.user_type, 'student')

    def test_learner_cannot_clear_their_own_enrolment_gate(self):
        """``pending_invoice_uid`` is what holds an unpaid account out."""
        self.p_learner.pending_invoice_uid = '00000000-0000-0000-0000-000000000001'
        self.p_learner.save(update_fields=['pending_invoice_uid'])
        self.client.patch(f'/api/accounts/people/{self.p_learner.pk}/',
                          {'pending_invoice_uid': None}, content_type='application/json')
        self.p_learner.refresh_from_db()
        self.assertIsNotNone(self.p_learner.pending_invoice_uid)

    # --- horizontal access ----------------------------------------------------

    def test_another_persons_record_is_out_of_scope(self):
        url = f'/api/accounts/people/{self.p_other.pk}/'
        self.assertEqual(self.client.get(url).status_code, 404)
        self.assertEqual(
            self.client.patch(url, {'first_name': 'hacked'},
                              content_type='application/json').status_code, 404)
        self.assertIn(self.client.delete(url).status_code, (403, 404))

    def test_list_returns_only_the_requesting_user(self):
        rows = self._rows(self.client.get('/api/accounts/people/'))
        self.assertEqual([r['id'] for r in rows], [self.p_learner.pk])

    def test_creating_people_is_management_only(self):
        response = self.client.post('/api/accounts/people/', {'first_name': 'New'},
                                    content_type='application/json')
        self.assertEqual(response.status_code, 403)

    # --- what must keep working ----------------------------------------------

    def test_own_profile_is_readable_and_editable(self):
        url = f'/api/accounts/people/{self.p_learner.pk}/'
        self.assertEqual(self.client.get(url).status_code, 200)
        response = self.client.patch(url, {'first_name': 'Leanne'},
                                     content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.p_learner.refresh_from_db()
        self.assertEqual(self.p_learner.first_name, 'Leanne')

    def test_manager_keeps_full_reach(self):
        self.client.force_login(self.manager)
        rows = self._rows(self.client.get('/api/accounts/people/'))
        self.assertEqual(len(rows), 3)
        response = self.client.patch(f'/api/accounts/people/{self.p_other.pk}/',
                                     {'user_type': 'educator'},
                                     content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.p_other.refresh_from_db()
        self.assertEqual(self.p_other.user_type, 'educator')
