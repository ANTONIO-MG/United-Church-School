import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    """Attendance (class sessions), notification preferences and collaboration
    workspaces — Learning Hub features 2, 3 and 4."""

    dependencies = [
        ('communication', '0002_moderation'),
        ('accounts', '0003_subject_program'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ClassSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=200)),
                ('session_date', models.DateField(db_index=True, default=django.utils.timezone.localdate)),
                ('starts_at', models.DateTimeField(blank=True, null=True)),
                ('ends_at', models.DateTimeField(blank=True, null=True)),
                ('late_after_minutes', models.PositiveIntegerField(default=10, help_text='A check-in this many minutes after the start counts as "late".')),
                ('is_open', models.BooleanField(default=True, help_text='While open, joining or checking-in records attendance.')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='class_sessions_created', to=settings.AUTH_USER_MODEL)),
                ('meeting', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='class_session', to='communication.meetingroom')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='class_sessions', to='accounts.subject')),
            ],
            options={'ordering': ['-session_date', '-starts_at']},
        ),
        migrations.AddIndex(
            model_name='classsession',
            index=models.Index(fields=['subject', 'session_date'], name='comm_session_subj_idx'),
        ),
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('present', 'Present'), ('late', 'Late'), ('absent', 'Absent'), ('excused', 'Excused')], db_index=True, default='present', max_length=10)),
                ('source', models.CharField(choices=[('auto', 'Auto (joined call)'), ('login', 'Check-in'), ('manual', 'Manual')], default='manual', max_length=8)),
                ('check_in_at', models.DateTimeField(blank=True, null=True)),
                ('note', models.CharField(blank=True, max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('marked_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='attendance_marked', to=settings.AUTH_USER_MODEL)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendance', to='communication.classsession')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendance_records', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['session', 'student'], 'unique_together': {('session', 'student')}},
        ),
        migrations.CreateModel(
            name='NotificationPreference',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email_enabled', models.BooleanField(default=True, help_text='Also deliver a copy by e-mail.')),
                ('browser_enabled', models.BooleanField(default=True, help_text='Show desktop / browser notifications.')),
                ('notify_mentions', models.BooleanField(default=True)),
                ('notify_messages', models.BooleanField(default=True)),
                ('notify_announcements', models.BooleanField(default=True)),
                ('notify_deadlines', models.BooleanField(default=True, help_text='Upcoming task / assessment deadlines.')),
                ('notify_meetings', models.BooleanField(default=True, help_text='Live sessions & meeting invites.')),
                ('notify_grades', models.BooleanField(default=True, help_text='New grades & certificates.')),
                ('digest', models.CharField(choices=[('off', 'Send immediately'), ('daily', 'Daily digest'), ('weekly', 'Weekly digest')], default='off', max_length=8)),
                ('quiet_hours_start', models.TimeField(blank=True, null=True)),
                ('quiet_hours_end', models.TimeField(blank=True, null=True)),
                ('reminder_lead_minutes', models.PositiveIntegerField(default=60, help_text='How long before a deadline / session to remind you.')),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='notification_preference', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Workspace',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='workspaces_created', to=settings.AUTH_USER_MODEL)),
                ('group', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='workspaces', to='accounts.group')),
                ('subject', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='workspaces', to='accounts.subject')),
                ('members', models.ManyToManyField(blank=True, related_name='workspaces', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-updated_at']},
        ),
        migrations.CreateModel(
            name='WorkspaceFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='workspaces/%Y/%m/')),
                ('title', models.CharField(blank=True, max_length=200)),
                ('original_name', models.CharField(blank=True, max_length=255)),
                ('size', models.PositiveBigIntegerField(default=0)),
                ('version', models.PositiveIntegerField(default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('uploaded_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='workspace_files', to=settings.AUTH_USER_MODEL)),
                ('workspace', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='communication.workspace')),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='WorkspaceNote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('body', models.TextField(blank=True)),
                ('pinned', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='workspace_notes', to=settings.AUTH_USER_MODEL)),
                ('workspace', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notes', to='communication.workspace')),
            ],
            options={'ordering': ['-pinned', '-updated_at']},
        ),
    ]
