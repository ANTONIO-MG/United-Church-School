"""Fold existing lesson sections into the single body flow.

Before this migration a lesson was "intro blocks, then an accordion of
sections". After it, the lesson is one ordered list of blocks in which a section
is simply a block of type ``section`` — so an author writes a lesson like a blog
post and drops a dropdown section in wherever they want one.

Nothing is destroyed and nothing is copied: each existing ``LessonSection`` gains
an **anchor block** in the top-level flow that points at it, placed after the
lesson's current intro blocks in the section's existing order. The blocks already
filed under that section keep their ``section`` FK and therefore become its
children automatically, which is why no per-block rewrite is needed and why every
``LessonSectionProgress`` / ``LessonNote`` / ``LessonBookmark`` row stays valid.

Reversing simply deletes the anchor blocks, restoring the old shape.
"""

from django.db import migrations


def sections_to_anchor_blocks(apps, schema_editor):
    Lesson = apps.get_model('learning', 'Lesson')
    LessonBlock = apps.get_model('learning', 'LessonBlock')
    LessonSection = apps.get_model('learning', 'LessonSection')

    lesson_ids = (LessonSection.objects.values_list('lesson_id', flat=True)
                  .distinct())
    for lesson in Lesson.objects.filter(pk__in=list(lesson_ids)).iterator():
        sections = list(LessonSection.objects
                        .filter(lesson=lesson)
                        .order_by('order', 'id'))
        if not sections:
            continue

        # Intro blocks keep the head of the flow; sections follow in their own
        # order, so the reading order a learner sees is unchanged.
        intro = list(LessonBlock.objects
                     .filter(lesson=lesson, section__isnull=True)
                     .order_by('order', 'id'))
        for index, block in enumerate(intro):
            if block.order != index:
                block.order = index
                block.save(update_fields=['order'])

        next_order = len(intro)
        for section in sections:
            if LessonBlock.objects.filter(holds_section=section).exists():
                continue                      # already migrated (re-run safe)
            LessonBlock.objects.create(
                lesson=lesson,
                section=None,                 # the anchor lives in the main flow
                holds_section=section,
                block_type='section',
                order=next_order,
                data={'title': section.title, 'summary': section.summary},
                style={},
            )
            next_order += 1


def drop_anchor_blocks(apps, schema_editor):
    LessonBlock = apps.get_model('learning', 'LessonBlock')
    LessonBlock.objects.filter(block_type='section').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0012_lessonblock_holds_section_lessonblock_scorm_package_and_more'),
    ]

    operations = [
        migrations.RunPython(sections_to_anchor_blocks, drop_anchor_blocks),
    ]
