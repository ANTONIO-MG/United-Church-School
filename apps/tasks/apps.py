from django.apps import AppConfig


class TasksConfig(AppConfig):
    """App config for the tasks app.

    A custom ``label`` ('orgtasks') avoids any clash with other apps/libraries
    that use the generic name "tasks"; the URL namespace and related-query
    names follow this label.

    ``ready()`` imports :mod:`apps.tasks.signals` so assignments are fanned out
    when a task is created and CRUD events are audited, then connects the
    lesson/assessment hooks that keep a delivered task in step with its content.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.tasks'
    label = 'orgtasks'
    verbose_name = 'Tasks'

    def ready(self):
        from . import signals  # noqa: F401  (import for side effects)
        # Connected here rather than at import time: the learning/assessments
        # models must already be loaded, which they are by ``ready()``.
        signals.connect_activity_signals()
