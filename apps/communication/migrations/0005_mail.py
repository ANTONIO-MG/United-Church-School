import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    """In-system e-mail (inbox/compose/read) for admin/staff/educators — Phase F."""

    dependencies = [
        ('communication', '0004_class_program_chat'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MailMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sender_email', models.CharField(blank=True, help_text='Sender registered e-mail (used as reply-to).', max_length=254)),
                ('subject', models.CharField(max_length=255)),
                ('body', models.TextField(blank=True)),
                ('external_to', models.CharField(blank=True, help_text='Comma-separated external addresses (no in-system inbox).', max_length=500)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_mail', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='MailRecipient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_read', models.BooleanField(db_index=True, default=False)),
                ('starred', models.BooleanField(default=False)),
                ('trashed', models.BooleanField(default=False)),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipients', to='communication.mailmessage')),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_mail', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-message__created_at'], 'unique_together': {('message', 'recipient')}},
        ),
    ]
