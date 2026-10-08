"""Make ``myhub.Course`` the one and only course model.

The hub had three things calling themselves a course: ``myhub.Course`` (the real
one — subjects, enrolment, fees), ``learning.Module`` (presented as "Courses" in
the learning app), and standalone SCORM packages shown as their own library.
This migration collapses the second into the first.

``Module`` becomes ``CourseUnit``: a *chapter of a course* rather than a rival to
one. It gains a direct ``course`` FK, back-filled from the subject it already
belonged to, and its subject becomes optional so a unit can span a whole course.

Everything is done with ``RenameModel`` / ``RenameField``, so **no row is copied
and none is destroyed** — every unit, item and per-student progress record keeps
its primary key and its history. That matters: ``CourseItemProgress`` is the
record of work learners have actually done.
"""

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def backfill_course(apps, schema_editor):
    """Point each unit at the course its subject already belonged to."""
    CourseUnit = apps.get_model('learning', 'CourseUnit')
    for unit in CourseUnit.objects.filter(course__isnull=True,
                                          subject__isnull=False).select_related('subject'):
        if unit.subject.course_id:
            unit.course_id = unit.subject.course_id
            unit.save(update_fields=['course'])


def noop(apps, schema_editor):
    """Reversing drops the column anyway, so there is nothing to undo."""


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0013_sections_into_the_body_flow'),
        ('myhub', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # --- 1. rename the models (data preserved in place) ---
        migrations.RenameModel(old_name='Module', new_name='CourseUnit'),
        migrations.RenameModel(old_name='ModuleItem', new_name='CourseItem'),
        migrations.RenameModel(old_name='ModuleItemProgress', new_name='CourseItemProgress'),

        # --- 2. rename the fields that pointed at them ---
        migrations.RenameField(model_name='courseitem', old_name='module', new_name='unit'),
        migrations.RenameField(model_name='lesson', old_name='module', new_name='unit'),

        # --- 3. hang units off the course itself ---
        migrations.AddField(
            model_name='courseunit',
            name='course',
            field=models.ForeignKey(blank=True, null=True,
                                    on_delete=django.db.models.deletion.CASCADE,
                                    related_name='units', to='myhub.course'),
        ),
        migrations.RunPython(backfill_course, noop),
        migrations.AlterField(
            model_name='courseunit',
            name='subject',
            field=models.ForeignKey(blank=True, null=True,
                                    on_delete=django.db.models.deletion.CASCADE,
                                    related_name='units', to='accounts.subject'),
        ),

        # --- 4. related names + ordering follow the rename ---
        migrations.AlterModelOptions(name='courseunit', options={'ordering': ['order', 'title']}),
        migrations.AlterModelOptions(name='courseitem', options={'ordering': ['order', 'id']}),
        migrations.AlterField(
            model_name='courseitem', name='unit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                    related_name='items', to='learning.courseunit'),
        ),
        migrations.AlterField(
            model_name='courseitem', name='lesson',
            field=models.ForeignKey(blank=True, null=True,
                                    on_delete=django.db.models.deletion.CASCADE,
                                    related_name='course_items', to='learning.lesson'),
        ),
        migrations.AlterField(
            model_name='courseitem', name='assessment',
            field=models.ForeignKey(blank=True, null=True,
                                    on_delete=django.db.models.deletion.CASCADE,
                                    related_name='course_items', to='assessments.assessment'),
        ),
        migrations.AlterField(
            model_name='courseitemprogress', name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                    related_name='progress', to='learning.courseitem'),
        ),
        migrations.AlterField(
            model_name='courseitemprogress', name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                    related_name='course_item_progress',
                                    to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='lesson', name='unit',
            field=models.ForeignKey(blank=True, null=True,
                                    on_delete=django.db.models.deletion.SET_NULL,
                                    related_name='lessons', to='learning.courseunit'),
        ),
        migrations.AlterModelOptions(
            name='lesson', options={'ordering': ['subject', 'unit', 'title']}),
        # Same stale-index retirement as the lesson rename above: the column
        # becomes unit_id but the index keeps its module_id name, which a later
        # real `module` FK would collide with on a fresh replay.
        migrations.RunSQL(
            sql='ALTER INDEX IF EXISTS learning_courseitem_module_id_58b40e4f RENAME TO learning_courseitem_unit_id_legacy_idx;',
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
