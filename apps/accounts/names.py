"""One name for one person, wherever it is read.

People type their name into their profile (accounts.Person) — registration and
the settings page both write it there. Django's login account (auth.User) has
first/last name fields of its own that were only sometimes filled, so pages that
asked the login for a name (``get_full_name|default:email``) fell back to the
e-mail address. Two fixes, both here:

* :func:`sync_login_name` copies the profile's name onto the login whenever a
  Person is saved (migration 0030 did the same once for everyone already here);
* :func:`install_user_str` makes a login print as the person's name rather than
  its username — which on this platform *is* the e-mail address — so a form
  option or ``{{ user }}`` in a template reads "Ann Mokoena", not an address.
"""

from django.db.models.signals import post_save


def sync_login_name(sender, instance, raw=False, **kwargs):
    if raw or not instance.user_id:
        return
    first, last = (instance.first_name or '').strip()[:150], (instance.last_name or '').strip()[:150]
    if not (first or last):
        return      # never blank out a name the login already had
    from django.contrib.auth import get_user_model
    try:
        # A queryset update, not user.save(): no signals, no audit-log noise, no recursion.
        get_user_model().objects.filter(pk=instance.user_id).exclude(first_name=first, last_name=last) \
            .update(first_name=first, last_name=last)
    except Exception as exc:    # never let a name copy break the profile save
        from core.errors import report
        report('USER-9002', exc, context={'person': instance.pk})


def _user_str(self):
    from core.utils import display_name
    return display_name(self)


def install(person_model):
    from django.contrib.auth import get_user_model
    post_save.connect(sync_login_name, sender=person_model, dispatch_uid='accounts.sync_login_name',
                      weak=False)
    get_user_model().__str__ = _user_str
