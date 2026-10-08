"""End-to-end tests for chat, the activity feed, notifications and the call page.

The emphasis is on the **shape of the data**, not just on pages returning 200. A
chat that renders fine but serves ``avatar`` under a different key, or omits
``read_by_count``, is a page that silently loses its faces and its read ticks —
the template fails quietly and nobody notices until a user complains. So every
API contract the front end depends on is asserted field by field, including the
type of each value.
"""

import io

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import Person

from . import models, services
from core.testing import enrol, make_module, make_programme

User = get_user_model()

LOCMEM_CACHE = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}


def tiny_png():
    """A real 1×1 PNG — ImageField rejects arbitrary bytes."""
    from PIL import Image
    buf = io.BytesIO()
    Image.new('RGB', (1, 1), (200, 30, 30)).save(buf, format='PNG')
    return SimpleUploadedFile('face.png', buf.getvalue(), content_type='image/png')


@override_settings(CACHES=LOCMEM_CACHE, MEDIA_ROOT='/tmp/ucs-lms-test-media')
class ChatFixtureMixin(TestCase):
    """A programme, a module and two enrolled students who can see each other."""

    def setUp(self):
        super().setUp()
        cache.clear()
        self.addCleanup(cache.clear)

        self.programme = make_programme('UCS', 'GR10')
        self.module = make_module('Advanced Auditing', 'AUD', programme=self.programme)

        self.alice = self._student('alice@example.com', 'Alice', 'Ndlovu', avatar=True)
        self.bob = self._student('bob@example.com', 'Bob', 'Marley', avatar=False)

        self.group = services.get_or_create_direct_chat(self.alice, self.bob)
        self.client.force_login(self.alice)

    def _student(self, email, first, last, *, avatar):
        user = User.objects.create_user(username=email, email=email, password='x',
                                        first_name=first, last_name=last)
        person = Person.objects.get(user=user)
        person.first_name, person.last_name = first, last
        person.user_type = 'student'
        person.registered = True
        person.profile_status = True
        if avatar:
            person.profile_picture = tiny_png()
        person.save()
        enrol(person, self.module)
        return user

    def send(self, body, sender=None, reply_to=None):
        return models.Message.objects.create(
            group=self.group, sender=sender or self.bob, body=body, reply_to=reply_to)

    def connect(self, a, b):
        """Put two students through the accept-a-connection gate."""
        conn, _ = services.request_connection(a, b)
        if conn is not None:
            services.respond_connection(conn, accept=True, by_user=b)
        return conn


class ChatMessageApiContractTests(ChatFixtureMixin):
    """The exact JSON the chat page's renderMsg() reads."""

    def payload(self):
        response = self.client.get(f'/api/communication/messages/?group={self.group.pk}&ordering=created_at')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'].split(';')[0], 'application/json')
        body = response.json()
        return body['results'] if isinstance(body, dict) and 'results' in body else body

    def test_message_carries_every_field_the_template_indexes(self):
        self.send('Morning!')
        message = self.payload()[0]
        for field in ('id', 'group', 'sender', 'body', 'reply_to', 'reply_preview',
                      'attachments', 'mention_links', 'read_by_count',
                      'other_member_count', 'is_edited', 'created_at'):
            self.assertIn(field, message, f'chat.html reads m.{field}')

    def test_sender_carries_avatar_and_initials_with_the_right_types(self):
        self.send('Morning!')
        sender = self.payload()[0]['sender']
        self.assertEqual(sender['id'], self.bob.pk)
        self.assertEqual(sender['display_name'], 'Bob Marley')
        # Bob has no picture: he gets the default avatar as a real absolute URL,
        # never '' or the string 'None' (which would render <img src="None">).
        self.assertTrue(sender['avatar'].startswith('http'))
        self.assertIn('/static/images/avatar/default-', sender['avatar'])
        self.assertEqual(sender['initials'], 'BM')

    def test_avatar_is_an_absolute_url_when_the_person_has_a_picture(self):
        self.send('Hello', sender=self.alice)
        sender = self.payload()[0]['sender']
        self.assertIsInstance(sender['avatar'], str)
        self.assertTrue(sender['avatar'].startswith('http'),
                        f'avatar must be absolute for <img src>, got {sender["avatar"]!r}')
        self.assertIn('.png', sender['avatar'])
        self.assertEqual(sender['initials'], 'AN')

    def test_initials_fall_back_to_the_email_when_there_is_no_name(self):
        nameless = User.objects.create_user(username='zed@example.com', email='zed@example.com')
        self.group.add_member(nameless)
        self.send('hi', sender=nameless)
        sender = self.payload()[0]['sender']
        self.assertEqual(sender['display_name'], 'zed')
        self.assertEqual(sender['initials'], 'ZE')

    def test_read_by_count_is_zero_until_the_other_member_reads(self):
        self.send('Are you there?', sender=self.alice)
        message = self.payload()[0]
        self.assertEqual(message['read_by_count'], 0)
        self.assertEqual(message['other_member_count'], 1)

    def test_read_by_count_rises_once_the_other_member_marks_read(self):
        self.send('Are you there?', sender=self.alice)
        membership = self.group.memberships.get(user=self.bob)
        membership.last_read_at = timezone.now()
        membership.save(update_fields=['last_read_at'])

        message = self.payload()[0]
        self.assertEqual(message['read_by_count'], 1,
                         'a read message must show the double tick')
        self.assertIsInstance(message['read_by_count'], int)

    def test_a_members_own_read_marker_does_not_tick_their_own_message(self):
        """Otherwise every message you send shows as read the moment you send it."""
        self.send('Mine', sender=self.alice)
        membership = self.group.memberships.get(user=self.alice)
        membership.last_read_at = timezone.now()
        membership.save(update_fields=['last_read_at'])
        self.assertEqual(self.payload()[0]['read_by_count'], 0)

    def test_reply_preview_quotes_the_parent_message(self):
        parent = self.send('What time is the class?', sender=self.bob)
        self.send('Two o’clock.', sender=self.alice, reply_to=parent)

        reply = [m for m in self.payload() if m['reply_to'] == parent.pk][0]
        preview = reply['reply_preview']
        self.assertIsNotNone(preview, 'the quote strip needs reply_preview')
        self.assertEqual(preview['id'], parent.pk)
        self.assertEqual(preview['sender'], 'Bob Marley')
        self.assertEqual(preview['body'], 'What time is the class?')
        self.assertIs(preview['has_attachment'], False)

    def test_reply_preview_is_null_for_an_ordinary_message(self):
        self.send('Standalone')
        self.assertIsNone(self.payload()[0]['reply_preview'])

    def test_reply_preview_body_is_truncated_not_unbounded(self):
        parent = self.send('x' * 500)
        self.send('re', sender=self.alice, reply_to=parent)
        preview = [m for m in self.payload() if m['reply_preview']][0]['reply_preview']
        self.assertLessEqual(len(preview['body']), 140)

    def test_posting_a_reply_through_the_api_links_the_parent(self):
        """The composer posts reply_to as form data — it must be accepted."""
        # Two students may only DM once they are connected; that gate is a
        # separate feature and is asserted on its own below.
        self.connect(self.alice, self.bob)
        parent = self.send('Original')
        response = self.client.post('/api/communication/messages/', {
            'group': self.group.pk, 'body': 'My answer', 'reply_to': parent.pk,
        })
        self.assertEqual(response.status_code, 201, response.content[:400])
        created = models.Message.objects.get(pk=response.json()['id'])
        self.assertEqual(created.reply_to_id, parent.pk)
        self.assertEqual(created.sender_id, self.alice.pk)

    def test_unconnected_students_cannot_message_each_other(self):
        """The reply path must not have opened a hole in the DM gate."""
        response = self.client.post('/api/communication/messages/',
                                    {'group': self.group.pk, 'body': 'hello?'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(models.Message.objects.filter(sender=self.alice).count(), 0)

    def test_a_non_member_cannot_read_a_conversation(self):
        outsider = User.objects.create_user(username='out@example.com', email='out@example.com')
        self.send('private')
        self.client.force_login(outsider)
        response = self.client.get(f'/api/communication/messages/?group={self.group.pk}')
        body = response.json()
        results = body['results'] if isinstance(body, dict) and 'results' in body else body
        self.assertEqual(results, [], 'messages must not leak to non-members')


class ChatPageTests(ChatFixtureMixin):

    def test_the_thread_names_both_sides_of_the_conversation(self):
        html = self.client.get(reverse('communication:chat-room',
                                       args=[self.group.pk])).content.decode()
        self.assertIn('Alice Ndlovu', html, 'the header must name the signed-in user')
        self.assertIn('Bob Marley', html, 'the header must name who you are talking to')

    def test_a_direct_conversation_is_titled_by_the_other_person(self):
        response = self.client.get(reverse('communication:chat-room', args=[self.group.pk]))
        active = response.context['active_group']
        self.assertEqual(active.chat_title, 'Bob Marley')
        self.assertTrue(active.is_direct)
        self.assertEqual([p.pk for p in active.peers], [self.bob.pk])

    def test_the_conversation_row_uses_the_peers_photo_not_an_initial(self):
        """Alice sees Bob (no photo); Bob sees Alice (photo) — so check Bob's view."""
        self.client.force_login(self.bob)
        response = self.client.get(reverse('communication:chat-room', args=[self.group.pk]))
        active = response.context['active_group']
        self.assertIsNotNone(active.avatar, 'Alice has a profile picture; it must be used')
        self.assertIn('/media/', active.avatar)

    def test_a_peer_without_a_photo_gets_the_default_avatar(self):
        """No upload: the default picture (by gender / title), never an empty image.
        Initials stay available for any template that still wants them."""
        response = self.client.get(reverse('communication:chat-room', args=[self.group.pk]))
        active = response.context['active_group']
        self.assertIn('/static/images/avatar/default-', active.avatar)
        self.assertEqual(active.avatar_initials, 'BM')

    def test_member_count_is_precomputed_for_the_template(self):
        response = self.client.get(reverse('communication:chat-room', args=[self.group.pk]))
        self.assertEqual(response.context['active_group'].member_count, 2)

    def test_the_new_chat_button_is_labelled_not_just_an_icon(self):
        html = self.client.get(reverse('communication:chat-home')).content.decode()
        self.assertIn('New chat', html)
        self.assertIn('bi-pencil-square', html, 'the icon stays next to the label')

    def test_the_page_offers_reply_and_read_ticks(self):
        html = self.client.get(reverse('communication:chat-room',
                                       args=[self.group.pk])).content.decode()
        self.assertIn('data-reply=', html, 'each message needs a reply control')
        self.assertIn('ticksHtml', html, 'sent/read ticks must be rendered')
        self.assertIn('dayLabel', html, 'day dividers must be rendered')

    def test_day_labels_cover_today_yesterday_weekday_and_older(self):
        html = self.client.get(reverse('communication:chat-room',
                                       args=[self.group.pk])).content.decode()
        for label in ('Today', 'Yesterday', 'Last week', 'weekday'):
            self.assertIn(label, html, f'the {label} divider case is missing')


class ChatCallTests(ChatFixtureMixin):

    def test_starting_a_call_names_it_after_both_people(self):
        response = self.client.get(reverse('communication:chat-call', args=[self.group.pk]),
                                   {'kind': 'audio'})
        self.assertEqual(response.status_code, 302)
        meeting = models.MeetingRoom.objects.latest('created_at')
        self.assertEqual(meeting.title, 'Alice Ndlovu & Bob Marley')

    def test_the_call_link_carries_the_way_back_to_this_chat(self):
        response = self.client.get(reverse('communication:chat-call', args=[self.group.pk]),
                                   {'kind': 'video'})
        chat_url = reverse('communication:chat-room', args=[self.group.pk])
        self.assertIn(f'return={chat_url}', response['Location'])
        self.assertIn('kind=video', response['Location'])

    def test_the_meeting_page_is_unbranded_and_returns_where_it_came_from(self):
        meeting = models.MeetingRoom.objects.create(title='Alice & Bob', host=self.alice,
                                                    provider=models.MeetingRoom.PROVIDER_JITSI)
        chat_url = reverse('communication:chat-room', args=[self.group.pk])
        html = self.client.get(reverse('communication:meeting-room', args=[meeting.slug]),
                               {'return': chat_url}).content.decode()

        self.assertIn('SHOW_JITSI_WATERMARK', html)
        self.assertIn('"enableClosePage": false'.replace('"', ''), html.replace('"', ''))
        self.assertIn(chat_url, html, 'hanging up must land back in the chat')
        self.assertNotIn('open in meet.jit.si', html, 'the raw Jitsi link is replaced by a button')
        self.assertIn('Open meeting in a new tab', html)
        self.assertIn('Share link', html)

    def test_the_share_message_contains_the_title_and_a_full_url(self):
        meeting = models.MeetingRoom.objects.create(title='Alice & Bob', host=self.alice,
                                                    provider=models.MeetingRoom.PROVIDER_JITSI)
        response = self.client.get(reverse('communication:meeting-room', args=[meeting.slug]))
        share = response.context['share_message']
        self.assertIn('Alice & Bob', share)
        self.assertIn('http', share)
        self.assertIn(meeting.slug, share)
        self.assertEqual(response.context['share_url'],
                         f'http://testserver{meeting.get_join_url()}')

    def test_an_offsite_return_url_is_refused(self):
        """?return= is attacker-controlled; it must never leave the site."""
        meeting = models.MeetingRoom.objects.create(title='X', host=self.alice,
                                                    provider=models.MeetingRoom.PROVIDER_JITSI)
        response = self.client.get(reverse('communication:meeting-room', args=[meeting.slug]),
                                   {'return': 'https://evil.example.com/steal'})
        self.assertNotIn('evil.example.com', response.context['return_url'])
        self.assertEqual(response.context['return_url'], reverse('communication:chat-home'))


class NotificationTests(ChatFixtureMixin):

    def make(self, **kwargs):
        return models.Notification.objects.create(
            recipient=self.alice, actor=self.bob, title='Marks published',
            body='Your auditing mark is up.', level='success', **kwargs)

    def test_the_inbox_names_the_sender_instead_of_a_severity_word(self):
        self.make()
        html = self.client.get(reverse('communication:notifications')).content.decode()
        self.assertIn('Bob Marley', html)
        # "Success" was the old level chip; the sender replaced it.
        self.assertNotIn('>Success<', html)

    def test_a_notification_is_decorated_with_an_icon_colour_and_actor(self):
        self.make()
        note = self.client.get(reverse('communication:notifications')).context['notifications'][0]
        self.assertEqual(note.actor_name, 'Bob Marley')
        self.assertEqual(note.actor_initial, 'BM')
        self.assertTrue(note.icon, 'a notification needs an icon for its badge')
        self.assertIn(note.color, {'primary', 'info', 'success', 'warning', 'danger'})

    def test_favouriting_from_the_inbox_moves_it_into_the_favourites_rail(self):
        note = self.make()
        self.client.post(reverse('communication:notifications'),
                         {'action': 'toggle_favourite', 'pk': note.pk})
        note.refresh_from_db()
        self.assertTrue(note.is_favourite)

        favourites = self.client.get(reverse('communication:notifications')).context['favourites']
        self.assertEqual([n.pk for n in favourites], [note.pk])

    def test_favouriting_is_a_toggle(self):
        note = self.make(is_favourite=True)
        self.client.post(reverse('communication:notifications'),
                         {'action': 'toggle_favourite', 'pk': note.pk})
        note.refresh_from_db()
        self.assertFalse(note.is_favourite)

    def test_you_cannot_favourite_somebody_elses_notification(self):
        theirs = models.Notification.objects.create(recipient=self.bob, title='Private')
        self.client.post(reverse('communication:notifications'),
                         {'action': 'toggle_favourite', 'pk': theirs.pk})
        theirs.refresh_from_db()
        self.assertFalse(theirs.is_favourite)

    def test_opening_a_notification_marks_it_read(self):
        note = self.make()
        self.assertFalse(note.is_read)
        self.client.get(reverse('communication:notification-detail', args=[note.pk]))
        note.refresh_from_db()
        self.assertTrue(note.is_read)

    def test_marking_unread_sticks_and_leaves_the_page(self):
        """Redirecting back to the detail page would immediately re-read it."""
        note = self.make(is_read=True)
        response = self.client.post(reverse('communication:notification-detail', args=[note.pk]),
                                    {'action': 'mark_unread'})
        note.refresh_from_db()
        self.assertFalse(note.is_read, 'mark-as-unread must survive the redirect')
        self.assertEqual(response['Location'], reverse('communication:notifications'))

    def test_the_detail_page_offers_favourite_and_unread_not_mark_as_read(self):
        note = self.make()
        html = self.client.get(reverse('communication:notification-detail',
                                       args=[note.pk])).content.decode()
        self.assertIn('value="toggle_favourite"', html)
        self.assertIn('value="mark_unread"', html)
        self.assertNotIn('value="mark_read"', html,
                         'opening the page already reads it — the button was a no-op')
        self.assertNotIn('nr-hero', html, 'the big level tick was removed')

    def test_another_users_notification_is_not_readable(self):
        theirs = models.Notification.objects.create(recipient=self.bob, title='Private')
        response = self.client.get(reverse('communication:notification-detail', args=[theirs.pk]))
        self.assertEqual(response.status_code, 404)


class FeedTests(ChatFixtureMixin):

    def setUp(self):
        super().setUp()
        # The feed lives under the pages namespace at /social/.
        self.url = reverse('pages:dashboard')

    def post(self, body='Hello world', **extra):
        self.client.post(reverse('communication:feed-create'), {'body': body, **extra})
        return models.Feed.objects.latest('created_at')

    def items(self, **query):
        return self.client.get(self.url, query).context['feed_items']

    def test_every_item_carries_the_keys_the_card_template_reads(self):
        self.post()
        item = self.items()[0]
        for key in ('type', 'when', 'actor', 'title', 'body', 'media', 'icon', 'color',
                    'url', 'label', 'extra', 'open_label', 'can_react',
                    'module_id', 'module_name', 'avatar', 'initials'):
            self.assertIn(key, item, f'_feed.html reads item.{key}')

    def test_a_post_is_reactable_and_a_reminder_is_not(self):
        from apps.communication.feed import TYPE_STYLE
        self.assertTrue(TYPE_STYLE['post'][3])
        for quiet in ('task', 'reminder', 'quiz', 'assessment'):
            self.assertFalse(TYPE_STYLE[quiet][3],
                             f'{quiet} must not offer Like / Comment')

    def test_open_labels_say_what_will_open(self):
        from apps.communication.feed import TYPE_STYLE
        self.assertEqual(TYPE_STYLE['message-direct'][2], 'Open in chats')
        self.assertEqual(TYPE_STYLE['message-group'][2], 'Open in chats')
        self.assertEqual(TYPE_STYLE['reminder'][2], 'Open reminder')
        self.assertEqual(TYPE_STYLE['quiz'][2], 'Open quiz')
        self.assertEqual(TYPE_STYLE['assessment'][2], 'Open assessment')

    def test_every_type_has_a_distinct_icon(self):
        from apps.communication.feed import TYPE_STYLE
        icons = [style[0] for style in TYPE_STYLE.values()]
        self.assertEqual(len(icons), len(set(icons)),
                         'each item type must be recognisable by its own icon')

    def test_the_author_photo_is_carried_on_the_item(self):
        self.post()
        item = [i for i in self.items() if i['type'] == 'post'][0]
        self.assertIsNotNone(item['avatar'], 'Alice has a picture; the card must use it')
        self.assertEqual(item['initials'], 'AN')

    def test_the_filter_offers_general_plus_the_modules_you_are_in(self):
        response = self.client.get(self.url)
        modules = list(response.context['feed_modules'])
        self.assertEqual([m.pk for m in modules], [self.module.pk])
        self.assertIsNone(response.context['active_module_id'])

    def test_choosing_a_module_narrows_the_feed_to_that_module(self):
        general = self.post('A general thought')
        tagged = self.post('About auditing', module=self.module.pk)
        self.assertEqual(tagged.module_id, self.module.pk)
        self.assertIsNone(general.module_id)

        filtered = self.items(module=self.module.pk)
        bodies = [i['body'] for i in filtered if i['type'] == 'post']
        self.assertIn('About auditing', bodies)
        self.assertNotIn('A general thought', bodies)

    def test_general_shows_everything_newest_first(self):
        self.post('older')
        self.post('newer', module=self.module.pk)
        posts = [i for i in self.items() if i['type'] == 'post']
        self.assertEqual([p['body'] for p in posts], ['newer', 'older'])

    def test_a_module_you_are_not_in_cannot_be_used_as_a_filter(self):
        other = make_module('Somebody Else’s Module', 'OTHR', programme=self.programme)
        response = self.client.get(self.url, {'module': other.pk})
        self.assertIsNone(response.context['active_module_id'],
                          'an unenrolled module must fall back to General')

    def test_a_post_cannot_be_filed_under_a_module_you_are_not_in(self):
        other = make_module('Not Mine', 'NOTM', programme=self.programme)
        post = self.post('sneaky', module=other.pk)
        self.assertIsNone(post.module_id)

    def test_liking_returns_a_count_and_does_not_navigate(self):
        post = self.post()
        response = self.client.post(reverse('communication:feed-like', args=[post.pk]),
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload, {'ok': True, 'liked': True, 'likes': 1})

    def test_liking_twice_unlikes(self):
        post = self.post()
        url = reverse('communication:feed-like', args=[post.pk])
        self.client.post(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        second = self.client.post(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest').json()
        self.assertFalse(second['liked'])
        self.assertEqual(second['likes'], 0)

    def test_a_like_is_one_per_person_not_a_counter_anyone_can_pump(self):
        post = self.post()
        url = reverse('communication:feed-like', args=[post.pk])
        for _ in range(5):
            self.client.post(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            self.client.post(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        post.refresh_from_db()
        self.assertEqual(post.like_count, 0)
        self.assertEqual(post.likes.count(), 0)

    def test_commenting_returns_the_rendered_comment_and_a_total(self):
        post = self.post()
        response = self.client.post(reverse('communication:feed-comment', args=[post.pk]),
                                    {'body': 'Well said.'},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload['ok'])
        self.assertEqual(payload['count'], 1)
        self.assertEqual(payload['comment']['author'], 'Alice Ndlovu')
        self.assertEqual(payload['comment']['body'], 'Well said.')
        self.assertIn('avatar', payload['comment'])
        self.assertEqual(models.FeedComment.objects.get().post_id, post.pk)

    def test_an_empty_comment_is_rejected(self):
        post = self.post()
        response = self.client.post(reverse('communication:feed-comment', args=[post.pk]),
                                    {'body': '   '},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(models.FeedComment.objects.count(), 0)

    def test_the_share_button_is_gone_from_the_card(self):
        self.post()
        html = self.client.get(self.url).content.decode()
        self.assertNotIn('flip-horizontal ps-1', html, 'the Share action was removed')
