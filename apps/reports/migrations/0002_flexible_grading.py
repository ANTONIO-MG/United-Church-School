from django.db import migrations, models


class Migration(migrations.Migration):
    """Flexible grading: extra-credit cap + custom letter scale on SubjectWeighting,
    and letter / extra-credit fields on Grade (Learning Hub feature 5)."""

    dependencies = [
        ('reports', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='subjectweighting',
            name='extra_credit_pct',
            field=models.PositiveIntegerField(default=0, help_text='Maximum bonus % that extra-credit work can add on top of the final mark.'),
        ),
        migrations.AddField(
            model_name='subjectweighting',
            name='grade_scale',
            field=models.JSONField(blank=True, default=list, help_text='Letter-grade bands, e.g. [{"min":80,"letter":"A"}, …]. Blank = default A–F scale.'),
        ),
        migrations.AddField(
            model_name='grade',
            name='letter',
            field=models.CharField(blank=True, max_length=4),
        ),
        migrations.AddField(
            model_name='grade',
            name='extra_credit_pct',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
        ),
    ]
