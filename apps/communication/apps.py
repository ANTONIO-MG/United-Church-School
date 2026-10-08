from django.apps import AppConfig


class CommunicationConfig(AppConfig):
    """App config for the communication app.

    ``ready()`` connects the signal handlers in :mod:`apps.communication.signals`
    (auto-build chat groups for courses/modules, keep their membership in sync
    with enrolment, and turn @mentions into notifications).
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.communication'
    label = 'communication'
    verbose_name = 'Communication'

    def ready(self):
        from . import signals  # noqa: F401  (import for side effects)
        from . import auto_signals  # noqa: F401  (queue automatic notifications)

        # Remove uploaded files from disk when their attachment/feed row is
        # replaced or deleted (chat files, wall media, feed media, workspace files).
        from core.file_cleanup import register
        register(self.get_model('MessageAttachment'), ['file'])
        register(self.get_model('DiscussionAttachment'), ['file'])
        register(self.get_model('Feed'), ['media'])
        register(self.get_model('WorkspaceFile'), ['file'])
