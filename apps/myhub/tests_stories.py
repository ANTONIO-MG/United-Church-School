"""The school's stories — public pages behind the landing page's "Read more"."""

from django.test import TestCase
from django.urls import reverse

from core import stories


class StoryPagesTests(TestCase):
    def test_the_index_is_public_and_lists_every_story(self):
        response = self.client.get('/social/stories/')
        self.assertEqual(response.status_code, 200)
        for story in stories.all_stories():
            self.assertContains(response, reverse('pages:story', args=[story['slug']]))

    def test_every_story_opens_in_full_for_an_anonymous_visitor(self):
        for story in stories.all_stories():
            response = self.client.get(f"/social/stories/{story['slug']}/")
            self.assertEqual(response.status_code, 200, story['slug'])
            self.assertContains(response, story['title'][:20])
            last = [p for p in story['body'] if not p.startswith(('## ', '• '))][-1]
            self.assertContains(response, last[:40].replace('&', '&amp;').replace("'", '&#x27;')
                                .replace('"', '&quot;'))

    def test_an_unknown_story_is_404(self):
        self.assertEqual(self.client.get('/social/stories/no-such-story/').status_code, 404)

    def test_the_landing_page_links_to_our_own_story_pages(self):
        response = self.client.get('/social/landing/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse('pages:stories'))
        for story in stories.recent(4):
            self.assertContains(response, reverse('pages:story', args=[story['slug']]))
        # "Read more" opens our page, not the old site.
        self.assertNotRegex(response.content.decode(), r'class="more small" href="https?://')

    def test_stories_are_newest_first_with_images(self):
        dates = [s['date'] for s in stories.all_stories()]
        self.assertEqual(dates, sorted(dates, reverse=True))
        self.assertTrue(all(s['image'] for s in stories.all_stories()))
