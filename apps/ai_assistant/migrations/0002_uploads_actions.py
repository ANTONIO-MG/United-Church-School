import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ai_assistant', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AssistantUpload',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('public_id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ('file', models.FileField(blank=True, null=True, upload_to='ai_uploads/')),
                ('kind', models.CharField(choices=[('auto', 'Auto-detect'), ('audio', 'Audio'), ('video', 'Video'), ('pdf', 'PDF / document'), ('text', 'Text')], default='auto', max_length=10)),
                ('original_name', models.CharField(blank=True, max_length=255)),
                ('note', models.TextField(blank=True, help_text='Optional instruction from the user for the crew.')),
                ('status', models.CharField(choices=[('pending', 'Queued'), ('processing', 'Processing'), ('done', 'Done'), ('failed', 'Failed')], db_index=True, default='pending', max_length=12)),
                ('transcript', models.TextField(blank=True)),
                ('summary', models.TextField(blank=True)),
                ('takeaways', models.TextField(blank=True)),
                ('result_json', models.JSONField(blank=True, default=dict)),
                ('error', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ai_uploads', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='AssistantAction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('public_id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ('action_type', models.CharField(choices=[('task', 'Task'), ('reminder', 'Reminder'), ('event', 'Calendar event'), ('meeting', 'Meeting'), ('email', 'Email'), ('invoice', 'Invoice')], db_index=True, default='task', max_length=12)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('payload', models.JSONField(blank=True, default=dict)),
                ('priority', models.CharField(choices=[('low', 'Low'), ('normal', 'Normal'), ('high', 'High')], default='normal', max_length=10)),
                ('due_at', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(choices=[('pending', 'Pending approval'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('applied', 'Applied'), ('failed', 'Failed')], db_index=True, default='pending', max_length=12)),
                ('result_note', models.CharField(blank=True, max_length=255)),
                ('applied_ref', models.CharField(blank=True, max_length=120)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ai_actions', to=settings.AUTH_USER_MODEL)),
                ('session', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='actions', to='ai_assistant.assistantsession')),
                ('upload', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='actions', to='ai_assistant.assistantupload')),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.AddIndex(
            model_name='assistantaction',
            index=models.Index(fields=['status', 'action_type'], name='ai_assist_status_type_idx'),
        ),
    ]
