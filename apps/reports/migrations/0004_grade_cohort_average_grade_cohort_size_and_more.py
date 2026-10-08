"""Persist cohort standing on Grade: class position was already a field but was
never written; cohort size + average join it so a report card or dashboard can
render "3rd of 24, class average 61%" from a single row.

The data step backfills every existing grade so the columns are populated the
moment this lands. The ranking logic is duplicated here rather than imported
from ``apps.reports.services`` on purpose — a migration must keep working
against the historical model even if the service later changes.
"""

from decimal import Decimal

from django.db import migrations, models
from django.utils import timezone


def backfill_ranks(apps, schema_editor):
    """Competition-rank (1, 2, 2, 4) every subject that already has grades."""
    Grade = apps.get_model('reports', 'Grade')
    now = timezone.now()

    subject_ids = list(Grade.objects.values_list('subject_id', flat=True).distinct())
    for subject_id in subject_ids:
        rows = list(Grade.objects.filter(subject_id=subject_id).only('id', 'final_pct'))
        if not rows:
            continue
        size = len(rows)
        average = Decimal(str(round(sum(float(g.final_pct) for g in rows) / size, 2)))

        rows.sort(key=lambda g: float(g.final_pct), reverse=True)
        position, previous_mark = 0, None
        for index, grade in enumerate(rows, start=1):
            mark = float(grade.final_pct)
            if mark != previous_mark:
                position, previous_mark = index, mark
            grade.class_position = position
            grade.cohort_size = size
            grade.cohort_average = average
            grade.ranked_at = now

        Grade.objects.bulk_update(
            rows, ['class_position', 'cohort_size', 'cohort_average', 'ranked_at'], batch_size=500)


def clear_ranks(apps, schema_editor):
    """Reverse step — the three new columns go away, so only reset the position
    field that predates this migration."""
    apps.get_model('reports', 'Grade').objects.update(class_position=None)


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0003_remove_certificate_program_certificate_course'),
    ]

    operations = [
        migrations.AddField(
            model_name='grade',
            name='cohort_average',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
        ),
        migrations.AddField(
            model_name='grade',
            name='cohort_size',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='grade',
            name='ranked_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.RunPython(backfill_ranks, clear_ranks),
    ]
