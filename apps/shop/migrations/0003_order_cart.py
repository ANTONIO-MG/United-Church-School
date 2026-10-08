from django.db import migrations, models


class Migration(migrations.Migration):
    """An order doubles as the buyer's cart until checkout (Phase C)."""

    dependencies = [
        ('shop', '0002_course_shop'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='checked_out',
            field=models.BooleanField(default=False),
        ),
    ]
