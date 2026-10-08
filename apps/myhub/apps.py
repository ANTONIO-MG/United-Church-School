from django.apps import AppConfig


class MyHubConfig(AppConfig):
    """App config for the MyHub dashboard.

    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.myhub'
    verbose_name = 'MyHub Dashboard'

    def ready(self):
        # Register the startup guard that compiles all first-party templates
        # so a broken tag fails `manage.py check` instead of a live request.
        from . import checks  # noqa: F401

        # Nothing to register for on-disk image cleanup any more: the models
        # that carried uploads (Course, LibraryItem, BlogPost, Professor,
        # Student, Staff) went with the old MyHub theme, and Event has no image.
