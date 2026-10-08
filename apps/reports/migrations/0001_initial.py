import uuid

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0003_subject_program'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SubjectWeighting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assignments_pct', models.PositiveIntegerField(default=20)),
                ('quizzes_pct', models.PositiveIntegerField(default=10)),
                ('tests_pct', models.PositiveIntegerField(default=20)),
                ('exams_pct', models.PositiveIntegerField(default=40)),
                ('tasks_pct', models.PositiveIntegerField(default=10)),
                ('pass_mark_pct', models.PositiveIntegerField(default=50)),
                ('subject', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='weighting', to='accounts.subject')),
            ],
        ),
        migrations.CreateModel(
            name='Grade',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('components', models.JSONField(blank=True, default=dict)),
                ('final_pct', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('passed', models.BooleanField(default=False)),
                ('class_position', models.PositiveIntegerField(blank=True, null=True)),
                ('attendance_pct', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('study_hours', models.DecimalField(decimal_places=2, default=0, max_digits=7)),
                ('computed_at', models.DateTimeField(auto_now=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='grades', to=settings.AUTH_USER_MODEL)),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='grades', to='accounts.subject')),
            ],
            options={'ordering': ['subject', '-final_pct'], 'unique_together': {('student', 'subject')}},
        ),
        migrations.CreateModel(
            name='Certificate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kind', models.CharField(choices=[('subject', 'Subject'), ('module', 'Module'), ('class', 'Class'), ('program', 'Program'), ('course', 'Course')], default='subject', max_length=10)),
                ('title', models.CharField(max_length=200)),
                ('final_mark', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('number', models.CharField(blank=True, max_length=40, unique=True)),
                ('verification_uuid', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ('signature', models.CharField(blank=True, max_length=200)),
                ('pdf', models.FileField(blank=True, null=True, upload_to='certificates/')),
                ('issued_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('program', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='certificates', to='accounts.program')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='certificates', to=settings.AUTH_USER_MODEL)),
                ('subject', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='certificates', to='accounts.subject')),
            ],
            options={'ordering': ['-issued_at']},
        ),
    ]
