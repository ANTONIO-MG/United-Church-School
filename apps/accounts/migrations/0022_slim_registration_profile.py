"""Slim the registration profile down to About you · Contact · Consent.

Three fields move rather than disappear, so the order here matters:

    1. add ``Person.title`` / ``funding_source`` / ``primary_device``
    2. COPY the existing values across from PersonContact / PersonFunding /
       PersonTech
    3. only then drop the old columns and tables

``makemigrations`` writes the removals first, which would throw the data away
before step 2 could read it. Hence the hand-ordered operations below.

Dropped outright (never asked for again): preferred name, middle name, ID /
passport number, occupation, the separate WhatsApp number, the whole
PersonEducation table, and PersonStudyProfile.study_goals. PersonStudyProfile
itself stays — it holds the academic calendar edited on the settings page.
"""

from django.db import migrations, models


def carry_values_forward(apps, schema_editor):
    """Copy title / funding source / primary device onto Person."""
    Person = apps.get_model('accounts', 'Person')
    PersonContact = apps.get_model('accounts', 'PersonContact')
    PersonFunding = apps.get_model('accounts', 'PersonFunding')
    PersonTech = apps.get_model('accounts', 'PersonTech')

    updates = {}

    for person_id, title in PersonContact.objects.exclude(
            title='').values_list('person_id', 'title'):
        updates.setdefault(person_id, {})['title'] = title

    for person_id, source in PersonFunding.objects.exclude(
            funding_source='').values_list('person_id', 'funding_source'):
        updates.setdefault(person_id, {})['funding_source'] = source

    for person_id, device in PersonTech.objects.exclude(
            primary_device='').values_list('person_id', 'primary_device'):
        updates.setdefault(person_id, {})['primary_device'] = device

    for person_id, values in updates.items():
        Person.objects.filter(pk=person_id).update(**values)


def carry_values_back(apps, schema_editor):
    """Reverse: put the values back on the side-tables being restored."""
    Person = apps.get_model('accounts', 'Person')
    PersonContact = apps.get_model('accounts', 'PersonContact')
    PersonFunding = apps.get_model('accounts', 'PersonFunding')
    PersonTech = apps.get_model('accounts', 'PersonTech')

    for person in Person.objects.all():
        if person.title:
            PersonContact.objects.update_or_create(
                person_id=person.pk, defaults={'title': person.title})
        if person.funding_source:
            PersonFunding.objects.update_or_create(
                person_id=person.pk, defaults={'funding_source': person.funding_source})
        if person.primary_device:
            PersonTech.objects.update_or_create(
                person_id=person.pk, defaults={'primary_device': person.primary_device})


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0021_remove_person_department'),
    ]

    operations = [
        # --- 1. the new home for the three fields that move -------------------
        migrations.AddField(
            model_name='person',
            name='title',
            field=models.CharField(blank=True, max_length=10, choices=[
                ('mr', 'Mr'), ('mrs', 'Mrs'), ('ms', 'Ms'), ('miss', 'Miss'),
                ('dr', 'Dr'), ('prof', 'Prof')]),
        ),
        migrations.AddField(
            model_name='person',
            name='funding_source',
            field=models.CharField(blank=True, max_length=20, verbose_name='Who pays the fees', choices=[
                ('self', 'Self'), ('parent', 'Parent / Guardian'), ('employer', 'Employer'),
                ('nsfas', 'NSFAS'), ('government', 'Government'), ('scholarship', 'Scholarship'),
                ('company', 'Company'), ('other', 'Other')]),
        ),
        migrations.AddField(
            model_name='person',
            name='primary_device',
            field=models.CharField(blank=True, max_length=12, verbose_name='Primary learning device', choices=[
                ('laptop', 'Laptop'), ('desktop', 'Desktop'), ('tablet', 'Tablet'), ('phone', 'Phone')]),
        ),

        # --- 2. move the data, while both sides still exist -------------------
        migrations.RunPython(carry_values_forward, carry_values_back),

        # --- 3. the phone field: one number, tagged with its country ----------
        migrations.AddField(
            model_name='personcontact',
            name='phone_country',
            field=models.CharField(blank=True, default='ZA', max_length=2,
                                   verbose_name='Phone country'),
        ),
        migrations.AlterField(
            model_name='personcontact',
            name='primary_phone',
            field=models.CharField(blank=True, max_length=30,
                                   verbose_name='Phone number (WhatsApp)'),
        ),

        # --- 4. now the old columns can go -----------------------------------
        migrations.RemoveField(model_name='personcontact', name='title'),
        migrations.RemoveField(model_name='personcontact', name='preferred_name'),
        migrations.RemoveField(model_name='personcontact', name='middle_name'),
        migrations.RemoveField(model_name='personcontact', name='id_or_passport'),
        migrations.RemoveField(model_name='personcontact', name='occupation'),
        migrations.RemoveField(model_name='personcontact', name='whatsapp_number'),
        migrations.RemoveField(model_name='personstudyprofile', name='study_goals'),

        # --- 5. ...and the one-field side-tables with them --------------------
        migrations.RemoveField(model_name='personfunding', name='person'),
        migrations.RemoveField(model_name='persontech', name='person'),
        migrations.DeleteModel(name='PersonEducation'),
        migrations.DeleteModel(name='PersonFunding'),
        migrations.DeleteModel(name='PersonTech'),
    ]
