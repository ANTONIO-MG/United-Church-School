import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('myhub', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='registered',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='person',
            name='phone',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='person',
            name='enrolled_class',
            field=models.CharField(blank=True, max_length=80, verbose_name='Class'),
        ),
        migrations.AddField(
            model_name='person',
            name='child_name',
            field=models.CharField(blank=True, max_length=160, verbose_name='Child / dependant name'),
        ),
        migrations.AddField(
            model_name='person',
            name='department',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='people', to='myhub.department'),
        ),
        migrations.AddField(
            model_name='person',
            name='course',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='people', to='myhub.course'),
        ),
        migrations.AddField(
            model_name='person',
            name='child_student',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='guardians', to='myhub.student'),
        ),
    ]
