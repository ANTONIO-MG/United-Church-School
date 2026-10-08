import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    """Personal-reminder support on Event: owner (private events) + category
    (Learning Hub feature 6 — calendar integration)."""

    dependencies = [
        ('myhub', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='calendar_events', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='event',
            name='category',
            field=models.CharField(choices=[('event', 'Event'), ('reminder', 'Reminder')], default='event', max_length=12),
        ),
    ]
