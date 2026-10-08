from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """App config for the accounts app.

    ``ready()`` imports :mod:`apps.accounts.signals` so the profile-creation
    and audit-logging signal handlers are connected at startup.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.accounts'

    def ready(self):
        from . import signals  # noqa: F401  (import for side effects)

        # Delete the old profile picture from disk when it is replaced or the
        # Person is removed (Django leaves the file behind otherwise).
        from core.file_cleanup import register
        register(self.get_model('Person'), ['profile_picture'])

        # People are shown by name, never by login/e-mail (see apps.accounts.names).
        from .names import install
        install(self.get_model('Person'))
