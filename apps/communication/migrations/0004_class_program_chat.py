import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    """Give classes (accounts.Group) and programs (accounts.Program) their own
    auto-managed chat groups, alongside the existing course/subject ones."""

    dependencies = [
        ('communication', '0003_collaboration'),
        ('accounts', '0003_subject_program'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chatgroup',
            name='kind',
            field=models.CharField(
                choices=[
                    ('direct', 'Direct (1:1)'),
                    ('course', 'Course group'),
                    ('subject', 'Subject group'),
                    ('group', 'Class / group'),
                    ('program', 'Program group'),
                    ('custom', 'Custom group'),
                ],
                default='custom', max_length=10),
        ),
        migrations.AddField(
            model_name='chatgroup',
            name='group',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='chat_group', to='accounts.group'),
        ),
        migrations.AddField(
            model_name='chatgroup',
            name='program',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='chat_group', to='accounts.program'),
        ),
    ]
