import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_person_onboarding'),
        ('myhub', '0001_initial'),
    ]

    operations = [
        # A subject now belongs to a Program (the classroom/activity); the
        # myhub.Course link becomes optional.
        migrations.AlterUniqueTogether(
            name='subject',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='subject',
            name='program',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='subjects', to='accounts.program'),
        ),
        migrations.AlterField(
            model_name='subject',
            name='course',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='subjects', to='myhub.course'),
        ),
        migrations.AlterModelOptions(
            name='subject',
            options={'ordering': ['program', 'course', 'name']},
        ),
    ]
