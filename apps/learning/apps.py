from django.apps import AppConfig


class LearningConfig(AppConfig):
    """Study content: modules, lessons (with resources & versioning) and the
    study-session timer that measures actual studying."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.learning'
    label = 'learning'
    verbose_name = 'Learning'

    def ready(self):
        # Clean up lesson media when replaced or deleted.
        from core.file_cleanup import register
        register(self.get_model('LessonResource'), ['file'])
        register(self.get_model('Lesson'), ['cover_image', 'author_avatar'])
        register(self.get_model('LessonBlock'), ['media'])
        register(self.get_model('ModuleMaterial'), ['file'])
        # Keep each offering's chat group in step with who may open the module.
        from . import signals  # noqa: F401
