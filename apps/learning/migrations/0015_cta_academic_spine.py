"""The CTA Thrive Coach academic spine: institution-first.

    Institution → Programme → ProgrammeModule → Topic → CourseItem
                              (the offering)

``Module`` is the canonical catalogue (FR, TX, GA, MA, plus the APC's seven
competency areas) and is the one shared level — it is what lets the platform ask
"how is Financial Reporting going across every institution?". ``ProgrammeModule``
is a module as offered on one programme, under the institution's own code:
Milpark ``TAXA``/``MACF``, UNISA and IAS ``TAX``/``MAF``. An offering is unique
per programme by **code**, not by module, because UNISA runs the same Financial
Accounting module as both ``FAC188`` and ``FAC179``.

Every offering owns its topics outright, so the exact content of each institution
is controllable without touching any other. Milpark PGDA FREP's ``FR-01`` and
UNISA PGDA FREP's ``FR-01`` are two rows with their own wording, ordering, depth,
past-paper frequency and mark weighting. The topic **code** is the shared
vocabulary that still reports them together, and the weighting columns stay blank
until that institution's own papers have actually been analysed.

**Nothing is dropped and no row is touched.** ``CourseItem.unit`` and
``Lesson.subject`` merely become nullable, and both models gain a nullable
``topic``, so the legacy course spine keeps working while content is moved
across. The reverse migration is clean.
"""

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0019_person_ms_upn'),
        ('learning', '0014_one_course_model'),
    ]

    operations = [
        migrations.CreateModel(
            name='Institution',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('code', models.CharField(help_text='Institution code used throughout — "MILPARK", "UNISA", "IAS", "SAICA".', max_length=20, unique=True)),
                ('name', models.CharField(max_length=160, unique=True)),
                ('slug', models.SlugField(blank=True, max_length=180, unique=True)),
                ('accent_colour', models.CharField(blank=True, default='#1F3864', help_text='Hex colour used for this institution across the LMS.', max_length=9)),
                ('accent_name', models.CharField(blank=True, help_text='e.g. "Steel Blue".', max_length=40)),
                ('logo', models.ImageField(blank=True, null=True, upload_to='institutions/')),
                ('website', models.URLField(blank=True, max_length=300)),
                ('description', models.TextField(blank=True)),
                ('order', models.PositiveIntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['order', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Module',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('code', models.CharField(help_text='Canonical code, e.g. "FR" or "APC-FR".', max_length=20, unique=True)),
                ('name', models.CharField(max_length=160, unique=True)),
                ('slug', models.SlugField(blank=True, max_length=180, unique=True)),
                ('is_competency_area', models.BooleanField(default=False, help_text='A SAICA competency area rather than an examined module.')),
                ('description', models.TextField(blank=True, help_text='Scope of technical content covered.')),
                ('order', models.PositiveIntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['order', 'name'],
            },
        ),
        migrations.AlterField(
            model_name='courseitem',
            name='unit',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='items', to='learning.courseunit'),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='subject',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='lessons', to='accounts.subject'),
        ),
        migrations.CreateModel(
            name='Programme',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('code', models.CharField(help_text='Short code, e.g. "PGDA". Prefixed with the institution code to give the full code, "MILPARK-PGDA".', max_length=30)),
                ('name', models.CharField(help_text='Short display name, e.g. "PGDA".', max_length=160)),
                ('full_name', models.CharField(blank=True, help_text='e.g. "Postgraduate Diploma in Accounting".', max_length=250)),
                ('slug', models.SlugField(blank=True, max_length=180)),
                ('level', models.CharField(choices=[('cta', 'CTA'), ('bridging', 'Pre-CTA bridging'), ('apc', 'Final qualifying assessment'), ('postgraduate', 'Postgraduate'), ('undergraduate', 'Undergraduate')], db_index=True, default='cta', max_length=16)),
                ('depth_default', models.CharField(choices=[('FND', 'Foundational — bridging level: principle and basic application'), ('ADV', 'Advanced — CTA/PGDA level: full complexity, integrated scenarios'), ('INT', 'Integrated — APC level: cross-discipline judgement, no topic silos'), ('UG', 'Undergraduate — below bridging level')], default='ADV', help_text='Depth this programme is normally pitched at.', max_length=4)),
                ('is_competency_based', models.BooleanField(default=False, help_text='Structured around competency areas rather than examined modules (APC).')),
                ('description', models.TextField(blank=True)),
                ('order', models.PositiveIntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('institution', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='programmes', to='learning.institution')),
            ],
            options={
                'ordering': ['institution', 'order', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Cohort',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('code', models.CharField(help_text='e.g. "P25F".', max_length=30)),
                ('name', models.CharField(blank=True, help_text='e.g. "2025 first intake".', max_length=120)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('programme', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cohorts', to='learning.programme')),
            ],
            options={
                'ordering': ['programme', '-start_date', 'code'],
            },
        ),
        migrations.AddField(
            model_name='lesson',
            name='target_programmes',
            field=models.ManyToManyField(blank=True, related_name='targeted_lessons', to='learning.programme'),
        ),
        migrations.CreateModel(
            name='ProgrammeModule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('code', models.CharField(help_text='This institution\'s code for the module, e.g. "FREP" or "TAXA".', max_length=20)),
                ('name', models.CharField(blank=True, help_text='Overrides the canonical module name when this programme names it differently — Milpark\'s "…and Financial Management" vs "…and Finance".', max_length=160)),
                ('depth_level', models.CharField(blank=True, choices=[('FND', 'Foundational — bridging level: principle and basic application'), ('ADV', 'Advanced — CTA/PGDA level: full complexity, integrated scenarios'), ('INT', 'Integrated — APC level: cross-discipline judgement, no topic silos'), ('UG', 'Undergraduate — below bridging level')], help_text="Blank = inherit the programme's default depth.", max_length=4)),
                ('description', models.TextField(blank=True, help_text='Coverage of this offering.')),
                ('order', models.PositiveIntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('module', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='offerings', to='learning.module')),
                ('programme', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='modules', to='learning.programme')),
            ],
            options={
                'verbose_name': 'Programme module',
                'ordering': ['programme', 'order', 'id'],
            },
        ),
        migrations.CreateModel(
            name='ProgrammePhase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(help_text='e.g. "Foundation".', max_length=120)),
                ('period', models.CharField(blank=True, help_text='e.g. "March – May".', max_length=120)),
                ('focus', models.TextField(blank=True)),
                ('order', models.PositiveIntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('programme', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='phases', to='learning.programme')),
            ],
            options={
                'ordering': ['order', 'id'],
            },
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('code', models.CharField(db_index=True, help_text='Topic code from the curriculum reference, e.g. "FR-01". Shared with the same topic on other institutions — that is how they are reported together.', max_length=20)),
                ('title', models.CharField(max_length=250)),
                ('slug', models.SlugField(blank=True, max_length=270)),
                ('reference', models.CharField(blank=True, help_text='Standard / legislation behind the topic — "IAS 12", "VAT Act s16(3)".', max_length=160)),
                ('description', models.TextField(blank=True)),
                ('depth', models.CharField(blank=True, choices=[('FND', 'Foundational — bridging level: principle and basic application'), ('ADV', 'Advanced — CTA/PGDA level: full complexity, integrated scenarios'), ('INT', 'Integrated — APC level: cross-discipline judgement, no topic silos'), ('UG', 'Undergraduate — below bridging level')], help_text="Blank = inherit the offering's depth.", max_length=4)),
                ('frequency', models.CharField(blank=True, choices=[('every_sitting', 'Every sitting'), ('most_sittings', 'Most sittings'), ('recurring', 'Recurring'), ('periodic', 'Periodic'), ('rare', 'Rarely tested')], db_index=True, help_text="How often the topic appears in this institution's papers. Blank = not yet analysed.", max_length=16)),
                ('avg_marks', models.DecimalField(blank=True, decimal_places=1, help_text="🎯 Average marks the topic carries in this institution's papers.", max_digits=5, null=True)),
                ('is_non_negotiable', models.BooleanField(default=False, help_text='📌 Non-negotiable — prepare this every time.')),
                ('notes', models.TextField(blank=True, help_text='How this offering treats the topic.')),
                ('order', models.PositiveIntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('programme_module', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='topics', to='learning.programmemodule')),
            ],
            options={
                'ordering': ['order', 'id'],
            },
        ),
        migrations.AddField(
            model_name='courseitem',
            name='topic',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='items', to='learning.topic'),
        ),
        migrations.AddField(
            model_name='lesson',
            name='topic',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='lessons', to='learning.topic'),
        ),
        migrations.AddConstraint(
            model_name='programme',
            constraint=models.UniqueConstraint(fields=('institution', 'code'), name='uniq_programme_code_per_institution'),
        ),
        migrations.AddConstraint(
            model_name='cohort',
            constraint=models.UniqueConstraint(fields=('programme', 'code'), name='uniq_cohort_code_per_programme'),
        ),
        migrations.AddConstraint(
            model_name='programmemodule',
            constraint=models.UniqueConstraint(fields=('programme', 'code'), name='uniq_module_code_per_programme'),
        ),
        migrations.AddConstraint(
            model_name='programmephase',
            constraint=models.UniqueConstraint(fields=('programme', 'name'), name='uniq_phase_name_per_programme'),
        ),
        migrations.AddIndex(
            model_name='topic',
            index=models.Index(fields=['programme_module', 'order'], name='learning_to_program_e90379_idx'),
        ),
        migrations.AddConstraint(
            model_name='topic',
            constraint=models.UniqueConstraint(fields=('programme_module', 'code'), name='uniq_topic_code_per_programme_module'),
        ),
    ]
