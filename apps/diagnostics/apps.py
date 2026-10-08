from django.apps import AppConfig


class DiagnosticsConfig(AppConfig):
    """Diagnostics app.

    ``ready()`` imports :mod:`apps.diagnostics.deploy_checks` so a build that is
    configured to serve publicly with development security refuses to start.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.diagnostics'
    verbose_name = 'Diagnostics & error log'

    def ready(self):
        from . import deploy_checks  # noqa: F401  (imported for side effects)
