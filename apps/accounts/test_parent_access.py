"""A parent sees their child, and nothing else.

Two halves, and both matter:

* **Reach** — :class:`~apps.accounts.middleware.ParentAccessMiddleware` is an
  allow-list, so the test that earns its keep is the one asserting the *blocked*
  side. A deny-list bug looks identical to a working allow-list until you try the
  page nobody thought to list.
* **Data** — every page a parent *can* reach must show their own child and no
  other family's. Each of those is probed by asking for the other parent's child
  directly, not by trusting the default.
"""

from django.contrib.auth import get_user_model
from core.testing import enrol, make_module
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.accounts.models import ParentLink, Person
from core.scoping import children_of, parent_contacts

User = get_user_model()
LOCMEM_CACHE = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}


@override_settings(CACHES=LOCMEM_CACHE)
class ParentFixtureMixin(TestCase):
    """Two families in one course, so "their child" is always testable against
    somebody else's."""

    def setUp(self):
        super().setUp()
        cache.clear()
        self.addCleanup(cache.clear)

        self.module = make_module(name='Advanced Auditing')
        self.other_module = make_module(name='Taxation')

        self.educator = self._user('ed@example.com', 'educator')
        self.module.educators.add(self.educator.profile)
        self.other_educator = self._user('ed2@example.com', 'educator')
        self.other_module.educators.add(self.other_educator.profile)
        self.admin = self._user('boss@example.com', 'admin')

        self.child = self._user('kid@example.com', 'student')
        enrol(self.child.profile, self.module)
        self.other_child = self._user('other-kid@example.com', 'student')
        enrol(self.other_child.profile, self.other_module)

        self.parent = self._user('mum@example.com', 'parent')
        ParentLink.objects.create(parent=self.parent, student=self.child)
        self.other_parent = self._user('dad@example.com', 'parent')
        ParentLink.objects.create(parent=self.other_parent, student=self.other_child)

    def _user(self, email, user_type):
        user = User.objects.create_user(username=email, email=email, password='x')
        person = Person.objects.get(user=user)
        person.user_type = user_type
        person.registered = True
        person.profile_status = True
        person.save()
        # Re-fetch: the creation signal left a stale Person cached on the user.
        return User.objects.get(pk=user.pk)


class ParentReachTests(ParentFixtureMixin):
    """What a parent may open, and what they may not."""

    ALLOWED = [
        '/shop/', '/finance/',
        '/communication/notifications/', '/communication/chat/',
        '/reports/', '/reports/progress/',
        '/assessments/', '/tasks/',
        '/myhub/events/', '/community/profile/', '/community/settings/',
    ]
    # Routes that exist and must bounce a parent back to the hub. The old MyHub
    # course/roster pages are gone, so they are not listed here — a 404 is not a
    # redirect, and a gate cannot be proven against a URL that resolves nowhere.
    BLOCKED = [
        '/learning/', '/learning/modules/', '/learning/lessons/manage/',
        '/analytics/',
        '/communication/discussions/', '/communication/workspaces/',
        '/communication/attendance/', '/communication/meetings/',
        '/communication/mail/', '/communication/announcements/',
        '/community/members/',
    ]

    def setUp(self):
        super().setUp()
        self.client.force_login(self.parent)

    def test_a_parent_can_open_everything_on_their_list(self):
        for url in self.ALLOWED:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, url)

    def test_a_parent_is_turned_away_from_everything_else(self):
        for url in self.BLOCKED:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302, url)
            self.assertIn('myhub', response.url, url)

    def test_a_student_is_unaffected_by_the_parent_gate(self):
        """The allow-list must bite parents only."""
        self.client.force_login(self.child)
        self.assertEqual(self.client.get('/learning/').status_code, 200)

    def test_an_educator_is_unaffected_by_the_parent_gate(self):
        self.client.force_login(self.educator)
        self.assertEqual(self.client.get('/learning/').status_code, 200)


class ParentDataScopeTests(ParentFixtureMixin):
    """Every page a parent reaches shows their own child."""

    def setUp(self):
        super().setUp()
        self.client.force_login(self.parent)

    def test_children_of_finds_only_the_linked_student(self):
        self.assertEqual([u.pk for u in children_of(self.parent)], [self.child.pk])
        self.assertEqual([u.pk for u in children_of(self.other_parent)], [self.other_child.pk])

    def test_an_unlinked_guardian_sees_nobody_rather_than_everybody(self):
        stranger = self._user('nobody@example.com', 'parent')
        self.assertEqual(list(children_of(stranger)), [])

    def test_progress_opens_on_their_child(self):
        response = self.client.get(reverse('reports:my-progress'))
        self.assertEqual(response.context['target'], self.child)

    def test_progress_refuses_another_familys_child(self):
        response = self.client.get(reverse('reports:my-progress'),
                                   {'student': self.other_child.pk})
        self.assertEqual(response.status_code, 404)

    def test_the_tasks_page_is_the_childs_and_is_read_only(self):
        response = self.client.get(reverse('orgtasks:my-tasks'))
        self.assertEqual(response.context['child'], self.child)
        self.assertTrue(response.context['read_only'])

    def test_the_assessments_page_is_the_childs_and_is_read_only(self):
        response = self.client.get(reverse('assessments:index'))
        self.assertEqual(response.context['child'], self.child)
        self.assertTrue(response.context['read_only'])

    def test_reports_show_only_their_childs_grades(self):
        from apps.reports.models import Grade
        Grade.objects.create(student=self.child, module=self.module, final_pct=80)
        Grade.objects.create(student=self.other_child, module=self.other_module, final_pct=90)
        response = self.client.get(reverse('reports:my-reports'))
        owners = {g.student_id for g in response.context['grades']}
        self.assertEqual(owners, {self.child.pk})


class ParentMessagingTests(ParentFixtureMixin):
    """A parent's line of contact is the school — not a directory of families."""

    def setUp(self):
        super().setUp()
        self.client.force_login(self.parent)

    def test_contacts_are_the_school_and_their_childs_educators(self):
        contacts = set(parent_contacts(self.parent).values_list('pk', flat=True))
        self.assertIn(self.admin.pk, contacts)
        self.assertIn(self.educator.pk, contacts, "their child's educator")

    def test_contacts_exclude_students_and_other_parents(self):
        contacts = set(parent_contacts(self.parent).values_list('pk', flat=True))
        self.assertNotIn(self.child.pk, contacts, 'their own child is not a contact')
        self.assertNotIn(self.other_child.pk, contacts)
        self.assertNotIn(self.other_parent.pk, contacts)

    def test_contacts_exclude_an_educator_who_does_not_teach_their_child(self):
        contacts = set(parent_contacts(self.parent).values_list('pk', flat=True))
        self.assertNotIn(self.other_educator.pk, contacts)

    def test_messaging_an_allowed_contact_opens_a_chat(self):
        response = self.client.get(
            reverse('communication:chat-direct', args=[self.educator.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/communication/chat/', response.url)

    def test_messaging_anyone_else_is_a_404(self):
        """The contact list is a convenience; the route is the control."""
        for blocked in (self.other_child, self.other_parent, self.other_educator):
            response = self.client.get(
                reverse('communication:chat-direct', args=[blocked.pk]))
            self.assertEqual(response.status_code, 404, blocked.email)

    def test_a_parent_is_not_put_in_the_platform_wide_group_chat(self):
        response = self.client.get(reverse('communication:chat-home'))
        kinds = {g.kind for g in response.context['groups']}
        self.assertNotIn('custom', kinds, 'a parent must not join the General room')
