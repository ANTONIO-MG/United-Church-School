from django.db import migrations, models


class Migration(migrations.Migration):
    """Per-assessment weighting + extra-credit flag (Learning Hub feature 5)."""

    dependencies = [
        ('assessments', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='assessment',
            name='weight',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=5, help_text='Relative weight within its component (quizzes/tests/…).'),
        ),
        migrations.AddField(
            model_name='assessment',
            name='is_extra_credit',
            field=models.BooleanField(default=False, help_text='Score counts as bonus on top of the final mark, not part of a component.'),
        ),
    ]
