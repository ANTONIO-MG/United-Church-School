"""django-import-export resources for bulk student intake and roster export.

The admin surfaces these as Import / Export buttons on the Person changelist, so
an administrator can onboard a whole intake from the spreadsheet a school
already keeps rather than typing people in one at a time.

The import is keyed on **e-mail**, which is this platform's real identity (there
are no usernames people choose). Importing a row for an address that already
exists updates that person; a new address creates the ``User`` *and* its
``Person`` profile. Passwords are never imported — a new account starts unusable
and the person sets their own password through the normal reset flow.
"""

from django.contrib.auth import get_user_model
from import_export import fields, resources


from .models import Person

User = get_user_model()


class PersonResource(resources.ModelResource):
    """Import / export students (and any other Person) by e-mail address."""

    email = fields.Field(column_name='email', attribute='user__email', readonly=True)

    class Meta:
        model = Person
        # ``email`` identifies the row; ``id`` is deliberately absent so a
        # spreadsheet never has to carry internal primary keys.
        import_id_fields = ('email',)
        fields = ('email', 'first_name', 'last_name', 'user_type', 'phone',
                  'gender', 'date_of_birth')
        export_order = fields
        skip_unchanged = True
        report_skipped = True

    def before_import_row(self, row, **kwargs):
        """Normalise the e-mail and make sure a ``User`` exists for it.

        ``Person`` is created by a post-save signal on ``User``, so creating the
        user here means the row that follows updates an existing profile rather
        than trying to build one with no account behind it.
        """
        email = (row.get('email') or '').strip().lower()
        if not email:
            raise ValueError('Every row needs an "email" column — it is how people are identified.')
        row['email'] = email
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email,
                'first_name': (row.get('first_name') or '').strip(),
                'last_name': (row.get('last_name') or '').strip(),
            },
        )
        if created:
            # No password is ever imported: the account cannot be signed into
            # until the person sets one via the password-reset e-mail.
            user.set_unusable_password()
            user.save(update_fields=['password'])

    def get_instance(self, instance_loader, row):
        """Look the profile up through its user's e-mail."""
        email = (row.get('email') or '').strip().lower()
        return Person.objects.filter(user__email=email).first()

    def dehydrate_email(self, person):
        return person.user.email if person.user_id else ''
