import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('communication', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Violation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source', models.CharField(choices=[('chat', 'Chat'), ('dm', 'Direct message'), ('forum', 'Forum'), ('comment', 'Comment'), ('assignment', 'Assignment'), ('upload', 'Upload'), ('announcement', 'Announcement'), ('profile', 'Profile')], default='chat', max_length=12)),
                ('text', models.TextField(blank=True, help_text='Snapshot of the offending content (evidence).')),
                ('category', models.CharField(blank=True, max_length=40)),
                ('score', models.PositiveSmallIntegerField(default=0)),
                ('detected_by', models.CharField(choices=[('rule', 'Rule'), ('ai', 'AI'), ('report', 'User report')], default='rule', max_length=8)),
                ('evidence', models.JSONField(blank=True, default=dict)),
                ('handled', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('message', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='violations', to='communication.message')),
                ('reporter', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reported_violations', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='violations', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='Penalty',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kind', models.CharField(choices=[('warning', 'Warning'), ('delete', 'Message deletion'), ('mute', 'Temporary mute'), ('chat_suspend', 'Chat suspension'), ('class_suspend', 'Class suspension'), ('platform_suspend', 'Platform suspension'), ('escalate', 'Escalated to staff')], default='warning', max_length=18)),
                ('reason', models.CharField(blank=True, max_length=255)),
                ('starts_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('ends_at', models.DateTimeField(blank=True, help_text='Blank = indefinite.', null=True)),
                ('active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('issued_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='penalties_issued', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='penalties', to=settings.AUTH_USER_MODEL)),
                ('violation', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='penalties', to='communication.violation')),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='Appeal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='pending', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('penalty', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='appeals', to='communication.penalty')),
                ('reviewed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='appeals_reviewed', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='appeals', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='ReputationScore',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.PositiveSmallIntegerField(default=100)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='reputation', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddIndex(
            model_name='violation',
            index=models.Index(fields=['user', 'handled'], name='comm_violation_user_idx'),
        ),
        migrations.AddIndex(
            model_name='penalty',
            index=models.Index(fields=['user', 'active'], name='comm_penalty_user_idx'),
        ),
    ]
