import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def populate_invite_tokens(apps, schema_editor):
    """Give every existing person a distinct token before the unique index."""
    Person = apps.get_model('accounts', 'Person')
    for person in Person.objects.all().only('id'):
        Person.objects.filter(pk=person.pk).update(parent_invite_token=uuid.uuid4())


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    """Parent/guardian links (max 2 per student) + a per-student invite token,
    and an address field (Phase D — registration wizard)."""

    dependencies = [
        ('accounts', '0003_subject_program'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='address',
            field=models.CharField(blank=True, max_length=255),
        ),
        # 1) Add the token column non-unique so existing rows don't collide.
        migrations.AddField(
            model_name='person',
            name='parent_invite_token',
            field=models.UUIDField(default=uuid.uuid4, editable=False, null=True),
        ),
        # 2) Populate distinct values per row.
        migrations.RunPython(populate_invite_tokens, noop),
        # 3) Enforce uniqueness + index, matching the model field.
        migrations.AlterField(
            model_name='person',
            name='parent_invite_token',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True),
        ),
        migrations.CreateModel(
            name='ParentLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='guardian_of', to=settings.AUTH_USER_MODEL)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='guardians', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at'], 'unique_together': {('parent', 'student')}},
        ),
    ]
