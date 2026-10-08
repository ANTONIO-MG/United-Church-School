"""Tests for the lessons page: course / subject filters and the when rail.

The filters are the whole point of the page, and they are the easy thing to get
subtly wrong — a filter that silently matches everything looks identical to a
working one until somebody relies on it. So each filter is asserted to *exclude*
what it should, not merely to include what it should.
"""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import Person

from . import authoring, models, player, styles
from core.testing import enrol, make_module, make_programme

User = get_user_model()

LOCMEM_CACHE = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}
LESSONS_URL = reverse('learning:lessons')


@override_settings(CACHES=LOCMEM_CACHE)
class LessonFilterTests(TestCase):
    """Two programmes, three modules, lessons spread across past / today / future."""

    def setUp(self):
        super().setUp()
        cache.clear()
        self.addCleanup(cache.clear)

        self.cta = make_programme('UCS', 'GR10')
        self.law = make_programme('LAWSCH', 'LLB')

        self.audit = make_module('Advanced Auditing', 'AUDA', programme=self.cta)
        self.tax = make_module('Taxation', 'TAXA', programme=self.cta)
        self.contracts = make_module('Contracts', 'CONT', programme=self.law)

        email = 'learner@example.com'
        self.user = User.objects.create_user(username=email, email=email, password='x',
                                             first_name='Lea', last_name='Rner')
        self.person = Person.objects.get(user=self.user)
        self.person.user_type = 'student'
        self.person.registered = True
        self.person.profile_status = True
        self.person.save()
        for module in (self.audit, self.tax, self.contracts):
            enrol(self.person, module)

        now = timezone.localtime()
        self.past = self._lesson('Old auditing lesson', self.audit, now - timedelta(days=9))
        self.today = self._lesson('Today’s auditing lesson', self.audit, now)
        self.soon = self._lesson('Upcoming tax lesson', self.tax, now + timedelta(days=4))
        self.other_programme = self._lesson('Contract basics', self.contracts, now)

        self.client.force_login(self.user)

    def _lesson(self, title, module, publish_at):
        return models.Lesson.objects.create(
            title=title, module=module, status=models.Lesson.STATUS_PUBLISHED,
            publish_at=publish_at)

    def titles(self, **query):
        response = self.client.get(LESSONS_URL, query)
        self.assertEqual(response.status_code, 200)
        return {lesson.title for lesson in response.context['lessons']}

    # --- No filter --------------------------------------------------------
    def test_unfiltered_shows_every_lesson_the_learner_may_see(self):
        self.assertEqual(
            self.titles(),
            {self.past.title, self.today.title, self.soon.title, self.other_programme.title})

    def test_the_page_offers_the_programmes_and_modules_that_actually_have_lessons(self):
        response = self.client.get(LESSONS_URL)
        self.assertEqual({c.pk for c in response.context['programmes']},
                         {self.cta.pk, self.law.pk})
        self.assertEqual({s.pk for s in response.context['modules']},
                         {self.audit.pk, self.tax.pk, self.contracts.pk})

    def test_a_module_with_no_lessons_is_not_offered_as_a_filter(self):
        empty = make_module('Empty Module', 'EMPT', programme=self.cta)
        enrol(self.person, empty)
        response = self.client.get(LESSONS_URL)
        self.assertNotIn(empty.pk, {s.pk for s in response.context['modules']})

    # --- Programme / module -----------------------------------------------
    def test_filtering_by_programme_excludes_the_other_course(self):
        titles = self.titles(programme=self.cta.pk)
        self.assertIn(self.today.title, titles)
        self.assertNotIn(self.other_programme.title, titles,
                         'a Law lesson must not survive a Grade 10 filter')

    def test_filtering_by_programme_narrows_the_module_choices_too(self):
        response = self.client.get(LESSONS_URL, {'programme': self.cta.pk})
        self.assertEqual({s.pk for s in response.context['modules']},
                         {self.audit.pk, self.tax.pk})

    def test_filtering_by_module_excludes_the_other_modules(self):
        titles = self.titles(module=self.audit.pk)
        self.assertEqual(titles, {self.past.title, self.today.title})

    def test_programme_and_module_filters_combine(self):
        self.assertEqual(self.titles(programme=self.cta.pk, module=self.tax.pk),
                         {self.soon.title})

    def test_a_contradictory_combination_returns_nothing_rather_than_everything(self):
        self.assertEqual(self.titles(programme=self.law.pk, module=self.tax.pk), set())

    # --- The when rail ----------------------------------------------------
    def test_past_shows_only_lessons_already_published(self):
        self.assertEqual(self.titles(when='past'), {self.past.title})

    def test_today_shows_only_todays_lessons(self):
        self.assertEqual(self.titles(when='today'),
                         {self.today.title, self.other_programme.title})

    def test_upcoming_shows_only_lessons_not_yet_live(self):
        self.assertEqual(self.titles(when='upcoming'), {self.soon.title})

    def test_the_three_when_buckets_partition_the_lessons(self):
        """Every lesson lands in exactly one bucket — none lost, none doubled."""
        buckets = [self.titles(when=w) for w in ('past', 'today', 'upcoming')]
        combined = set().union(*buckets)
        self.assertEqual(combined, self.titles())
        self.assertEqual(sum(len(b) for b in buckets), len(combined),
                         'a lesson appears in more than one bucket')

    def test_a_lesson_with_no_publish_date_counts_as_already_live(self):
        undated = models.Lesson.objects.create(
            title='Undated', module=self.audit, status=models.Lesson.STATUS_PUBLISHED)
        self.assertNotIn(undated.title, self.titles(when='upcoming'))
        self.assertIn(undated.title, self.titles())

    def test_when_combines_with_the_module_filter(self):
        self.assertEqual(self.titles(when='past', module=self.audit.pk), {self.past.title})
        self.assertEqual(self.titles(when='past', module=self.tax.pk), set())

    def test_a_nonsense_when_value_is_ignored_not_obeyed(self):
        self.assertEqual(self.titles(when='sometime'), self.titles())

    def test_a_nonsense_programme_value_is_ignored(self):
        self.assertEqual(self.titles(programme='drop-table'), self.titles())

    # --- Context the template depends on ----------------------------------
    def test_the_active_filters_come_back_as_integers_for_comparison(self):
        response = self.client.get(LESSONS_URL,
                                   {'programme': self.cta.pk, 'module': self.audit.pk,
                                    'when': 'today'})
        self.assertEqual(response.context['active_programme'], self.cta.pk)
        self.assertEqual(response.context['active_module'], self.audit.pk)
        self.assertEqual(response.context['active_when'], 'today')
        # The template compares `active_programme == p.pk`; a string never matches.
        self.assertIsInstance(response.context['active_programme'], int)
        self.assertIsInstance(response.context['active_module'], int)

    def test_the_page_offers_both_grid_and_list_modes(self):
        html = self.client.get(LESSONS_URL).content.decode()
        self.assertIn('gridModeBtn', html)
        self.assertIn('listModeBtn', html)
        self.assertIn('as-list', html)

    # --- Visibility -------------------------------------------------------
    def test_a_learner_never_sees_a_module_they_are_not_enrolled_in(self):
        stranger = make_module('Not Mine', 'NOTM', programme=self.cta)
        hidden = self._lesson('Secret lesson', stranger, timezone.localtime())
        self.assertNotIn(hidden.title, self.titles())

    def test_a_learner_never_sees_an_unpublished_lesson(self):
        draft = models.Lesson.objects.create(title='Draft lesson', module=self.audit,
                                             status=models.Lesson.STATUS_DRAFT)
        self.assertNotIn(draft.title, self.titles())

    def test_the_lesson_creator_button_is_hidden_from_learners(self):
        html = self.client.get(LESSONS_URL).content.decode()
        self.assertFalse(self.client.get(LESSONS_URL).context['can_teach'])
        self.assertNotIn('Lesson creator', html)

    def test_an_educator_sees_the_lesson_creator(self):
        self.person.user_type = 'educator'
        self.person.save()
        response = self.client.get(LESSONS_URL)
        self.assertTrue(response.context['can_teach'])
        self.assertIn('Lesson creator', response.content.decode())


# ===========================================================================
# The lesson body — one flow, styled per element
# ===========================================================================
class BlockStyleTests(TestCase):
    """The Format toolkit writes CSS into the page, so the whitelist in
    apps.learning.styles is a security boundary, not a nicety."""

    def test_recognised_values_survive(self):
        cleaned = styles.clean({
            'align': 'center', 'font_size': '18px', 'color': '#ff0000',
            'font_weight': '700', 'width': '60%',
        })
        self.assertEqual(cleaned['align'], 'center')
        self.assertEqual(cleaned['font_size'], '18px')
        self.assertEqual(cleaned['color'], '#ff0000')
        self.assertEqual(cleaned['width'], '60%')

    def test_an_unknown_key_is_dropped(self):
        self.assertEqual(styles.clean({'position': 'fixed'}), {})

    def test_a_value_outside_its_whitelist_is_dropped(self):
        self.assertEqual(styles.clean({'align': 'nowhere'}), {})
        self.assertEqual(styles.clean({'font_weight': '900'}), {})

    def test_css_injection_cannot_get_through(self):
        """The classic escapes: closing the declaration, url(), expression()."""
        for hostile in ('red; behavior:url(x)', 'expression(alert(1))',
                        '#fff}body{display:none', 'url(javascript:alert(1))'):
            self.assertEqual(styles.clean({'color': hostile}), {}, hostile)
            self.assertEqual(styles.clean({'background': hostile}), {}, hostile)

    def test_to_css_re_cleans_whatever_is_stored(self):
        """Even a row edited straight in the database cannot inject."""
        self.assertEqual(styles.to_css({'color': 'red; behavior:url(x)'}), '')
        self.assertEqual(styles.to_css({'align': 'center'}), 'text-align:center')

    def test_presets_expand_to_full_declarations(self):
        self.assertIn('box-shadow', styles.to_css({'shadow': 'md'}))
        self.assertIn('border', styles.to_css({'border': 'thin'}))
        self.assertEqual(styles.to_css({'shadow': 'none'}), '')


class LessonBodyFlowTests(TestCase):
    """A lesson is one ordered body in which a section is just an element."""

    def setUp(self):
        super().setUp()
        cache.clear()
        self.addCleanup(cache.clear)
        self.module = make_module('Audit', 'AUDB')
        self.lesson = models.Lesson.objects.create(title='Sampling', module=self.module)

    def _block(self, order, block_type='text', section=None):
        return models.LessonBlock.objects.create(
            lesson=self.lesson, section=section, block_type=block_type, order=order)

    def _section_block(self, order, title='Part one'):
        section = models.LessonSection.objects.create(lesson=self.lesson, title=title, order=0)
        block = models.LessonBlock.objects.create(
            lesson=self.lesson, holds_section=section,
            block_type=models.LessonBlock.TYPE_SECTION, order=order,
            data={'title': title})
        return block, section

    def test_the_body_is_top_level_blocks_in_order(self):
        first = self._block(0)
        anchor, section = self._section_block(1)
        last = self._block(2)
        inside = self._block(0, section=section)

        body = list(self.lesson.body_blocks())
        self.assertEqual([b.pk for b in body], [first.pk, anchor.pk, last.pk])
        # ...and the nested block belongs to the section, not the body.
        self.assertNotIn(inside.pk, [b.pk for b in body])
        self.assertEqual([b.pk for b in anchor.child_blocks], [inside.pk])

    def test_an_element_can_sit_after_a_section(self):
        """The whole point: content is not forced above the accordion."""
        anchor, _ = self._section_block(0)
        after = self._block(1)
        self.assertEqual([b.pk for b in self.lesson.body_blocks()], [anchor.pk, after.pk])

    def test_only_an_anchored_block_counts_as_a_section(self):
        plain = self._block(0, block_type=models.LessonBlock.TYPE_SECTION)
        self.assertFalse(plain.is_section)
        anchor, _ = self._section_block(1)
        self.assertTrue(anchor.is_section)

    def test_deleting_a_section_block_takes_its_section_with_it(self):
        anchor, section = self._section_block(0)
        self._block(0, section=section)
        anchor.delete()
        self.assertFalse(models.LessonSection.objects.filter(pk=section.pk).exists())
        self.assertEqual(self.lesson.blocks.count(), 0)

    def test_ensure_body_flow_gives_a_stray_section_its_place(self):
        """A section made outside the builder must still reach the page."""
        section = models.LessonSection.objects.create(lesson=self.lesson, title='Orphan')
        self.assertEqual(list(self.lesson.body_blocks()), [])
        added = authoring.ensure_body_flow(self.lesson)
        self.assertEqual(added, 1)
        body = list(self.lesson.body_blocks())
        self.assertEqual(len(body), 1)
        self.assertEqual(body[0].holds_section_id, section.pk)
        # ...and it is idempotent.
        self.assertEqual(authoring.ensure_body_flow(self.lesson), 0)

    def test_the_players_rows_follow_the_authored_order(self):
        self._block(0)
        anchor, _ = self._section_block(1)
        self._block(2)
        rows = player.body_rows(self.lesson, AnonymousUser(), preview=True)
        self.assertEqual([r['kind'] for r in rows], ['block', 'section', 'block'])

    def test_block_css_is_rendered_from_the_whitelist(self):
        block = self._block(0)
        block.style = {'align': 'center', 'evil': 'x'}
        block.save()
        self.assertEqual(block.css, 'text-align:center')
