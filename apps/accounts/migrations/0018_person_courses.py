from django.db import migrations, models


def backfill_courses(apps, schema_editor):
    """Seed the new ``courses`` M2M from each person's existing single course."""
    Person = apps.get_model('accounts', 'Person')
    for person in Person.objects.filter(course__isnull=False).iterator():
        person.courses.add(person.course_id)


def unbackfill(apps, schema_editor):
    Person = apps.get_model('accounts', 'Person')
    for person in Person.objects.iterator():
        person.courses.clear()


class Migration(migrations.Migration):

    dependencies = [
        ('myhub', '0003_course_additional_materials_cost_and_more'),
        ('accounts', '0017_remove_personcontact_additional_languages_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='courses',
            field=models.ManyToManyField(
                blank=True, related_name='enrolled_people', to='myhub.course',
            ),
        ),
        migrations.RunPython(backfill_courses, unbackfill),
    ]
