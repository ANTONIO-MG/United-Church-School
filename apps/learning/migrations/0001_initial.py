import uuid

import django.db.models.deletion
import django.utils.text
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
            name='Module',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('order', models.PositiveIntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='modules', to='accounts.subject')),
            ],
            options={'ordering': ['subject', 'order', 'title']},
        ),
        migrations.CreateModel(
            name='Lesson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=200)),
                ('slug', models.SlugField(blank=True, max_length=220)),
                ('body', models.TextField(blank=True, help_text='Rich-text lesson content.')),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('published', 'Published'), ('archived', 'Archived'), ('scheduled', 'Scheduled'), ('expired', 'Expired')], db_index=True, default='draft', max_length=12)),
                ('visibility', models.CharField(choices=[('institution', 'Entire institution'), ('program', 'Specific program'), ('class', 'Specific class'), ('subject', 'Specific subject'), ('group', 'Study group'), ('individual', 'Individual students')], default='subject', max_length=12)),
                ('publish_at', models.DateTimeField(blank=True, null=True)),
                ('expire_at', models.DateTimeField(blank=True, null=True)),
                ('estimated_minutes', models.PositiveIntegerField(default=30, help_text='Estimated study time.')),
                ('version', models.PositiveIntegerField(default=1)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='lessons_created', to=settings.AUTH_USER_MODEL)),
                ('module', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='lessons', to='learning.module')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lessons', to='accounts.subject')),
                ('target_groups', models.ManyToManyField(blank=True, related_name='lessons', to='accounts.group')),
                ('target_programs', models.ManyToManyField(blank=True, related_name='lessons', to='accounts.program')),
                ('target_subjects', models.ManyToManyField(blank=True, related_name='targeted_lessons', to='accounts.subject')),
                ('target_users', models.ManyToManyField(blank=True, related_name='targeted_lessons', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['subject', 'module', 'title']},
        ),
        migrations.CreateModel(
            name='LessonResource',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kind', models.CharField(choices=[('text', 'Text'), ('pdf', 'PDF'), ('word', 'Word'), ('ppt', 'PowerPoint'), ('image', 'Image'), ('audio', 'Audio'), ('video', 'Video'), ('youtube', 'YouTube'), ('link', 'External link'), ('embed', 'Embed'), ('download', 'Download')], default='pdf', max_length=10)),
                ('title', models.CharField(blank=True, max_length=200)),
                ('file', models.FileField(blank=True, null=True, upload_to='lessons/')),
                ('url', models.URLField(blank=True, max_length=500)),
                ('order', models.PositiveIntegerField(default=0)),
                ('lesson', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='resources', to='learning.lesson')),
            ],
            options={'ordering': ['lesson', 'order']},
        ),
        migrations.CreateModel(
            name='LessonVersion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version', models.PositiveIntegerField(default=1)),
                ('body', models.TextField(blank=True)),
                ('resources_json', models.JSONField(blank=True, default=list)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='lesson_versions', to=settings.AUTH_USER_MODEL)),
                ('lesson', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='versions', to='learning.lesson')),
            ],
            options={'ordering': ['lesson', '-version'], 'unique_together': {('lesson', 'version')}},
        ),
        migrations.CreateModel(
            name='StudySession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('public_id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ('status', models.CharField(choices=[('not_started', 'Not started'), ('in_progress', 'In progress'), ('paused', 'Paused'), ('submitted', 'Submitted'), ('completed', 'Completed'), ('overdue', 'Overdue'), ('cancelled', 'Cancelled')], db_index=True, default='not_started', max_length=12)),
                ('start_time', models.DateTimeField(blank=True, null=True)),
                ('end_time', models.DateTimeField(blank=True, null=True)),
                ('last_resumed_at', models.DateTimeField(blank=True, null=True)),
                ('total_seconds', models.PositiveIntegerField(default=0)),
                ('completion_pct', models.PositiveIntegerField(default=0)),
                ('lesson', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='study_sessions', to='learning.lesson')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='study_sessions', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]
