"""One parent account, several children: invitations are accepted, and the
parent switches between children."""
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.accounts.models import Invitation, ParentLink

User = get_user_model()


def make(email, kind):
    user = User.objects.create_user(username=email, email=email, password='x-Pass-1234')
    p = user.profile
    p.user_type, p.registered, p.profile_status = kind, True, True
    p.first_name = email.split('@')[0].title()
    p.save()
    return p


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class MultiChildParentTests(TestCase):

    def setUp(self):
        self.parent = make('mom@example.com', 'parent')
        self.first = make('thandi@example.com', 'student')
        self.second = make('sipho@example.com', 'student')
        ParentLink.objects.create(parent=self.parent.user, student=self.first.user, relationship='Mother')

    def test_an_existing_parent_is_asked_to_sign_in_then_accepts(self):
        invite = Invitation.objects.create(role='parent', email='mom@example.com', student=self.second)
        response = self.client.get(reverse('accounts:accept-invite', args=[invite.token]))
        self.assertIn(reverse('myhub:page-login'), response['Location'])
        self.client.force_login(self.parent.user)
        response = self.client.get(reverse('accounts:accept-invite', args=[invite.token]))
        confirm = reverse('accounts:invite-confirm', args=[invite.token])
        self.assertRedirects(response, confirm, fetch_redirect_response=False)
        self.assertContains(self.client.get(confirm), 'Sipho')
        self.client.post(confirm, {'action': 'accept', 'relationship': 'Mother'})
        self.assertEqual(ParentLink.objects.filter(parent=self.parent.user).count(), 2)
        invite.refresh_from_db()
        self.assertEqual(invite.status, Invitation.STATUS_ACCEPTED)

    def test_declining_links_nothing(self):
        invite = Invitation.objects.create(role='parent', email='mom@example.com', student=self.second)
        self.client.force_login(self.parent.user)
        self.client.post(reverse('accounts:invite-confirm', args=[invite.token]), {'action': 'decline'})
        self.assertEqual(ParentLink.objects.filter(parent=self.parent.user).count(), 1)

    def test_someone_else_cannot_use_the_invitation(self):
        invite = Invitation.objects.create(role='parent', email='mom@example.com', student=self.second)
        stranger = make('dad@example.com', 'parent')
        self.client.force_login(stranger.user)
        self.client.post(reverse('accounts:invite-confirm', args=[invite.token]), {'action': 'accept'})
        self.assertFalse(ParentLink.objects.filter(parent=stranger.user).exists())

    def test_the_dashboard_lists_every_child_and_the_choice_is_remembered(self):
        ParentLink.objects.create(parent=self.parent.user, student=self.second.user)
        self.client.force_login(self.parent.user)
        response = self.client.get(reverse('myhub:index'))
        self.assertContains(response, 'Thandi')
        self.assertContains(response, 'Sipho')
        self.client.get(reverse('myhub:index') + f'?student={self.second.user.pk}')
        self.assertEqual(self.client.session['viewing_child'], self.second.user.pk)
        response = self.client.get(reverse('finance:school-fees'))
        self.assertEqual(response.context['person'].pk, self.second.pk)
