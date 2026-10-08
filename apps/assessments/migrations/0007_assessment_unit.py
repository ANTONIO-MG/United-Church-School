"""Follow the ``Module`` → ``CourseUnit`` rename in ``learning``.

``Assessment.module`` becomes ``Assessment.unit``. A rename, not a rebuild — the
column and every value in it stay exactly where they are.
"""

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('assessments', '0006_alter_assessment_status'),
        # The model must already be renamed before this FK can point at it.
        ('learning', '0014_one_course_model'),
    ]

    operations = [
        migrations.RenameField(model_name='assessment', old_name='module', new_name='unit'),
        migrations.AlterField(
            model_name='assessment',
            name='unit',
            field=models.ForeignKey(blank=True, null=True,
                                    on_delete=django.db.models.deletion.SET_NULL,
                                    related_name='assessments', to='learning.courseunit'),
        ),
        migrations.RunSQL(
            # The RenameField above renames the COLUMN, but Postgres keeps the
            # index under its original `..._module_id_...` name. Anything that
            # later adds a real `module` FK to this table wants that exact name
            # back and collides on a fresh replay. Retire it here, at the source.
            sql='ALTER INDEX IF EXISTS assessments_assessment_module_id_c2bb2e26 RENAME TO assessments_assessment_unit_id_legacy_idx;',
            reverse_sql='ALTER INDEX IF EXISTS assessments_assessment_unit_id_legacy_idx RENAME TO assessments_assessment_module_id_c2bb2e26;',
        ),
    ]
