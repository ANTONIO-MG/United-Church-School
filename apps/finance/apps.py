from django.apps import AppConfig


class FinanceConfig(AppConfig):
    """App config for the finance app.

    ``ready()`` imports :mod:`apps.finance.signals` so invoice totals/status
    stay in sync and CRUD events are audited, and :mod:`apps.finance.checks` so
    a production build cannot boot pointed at PayFast's sandbox.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.finance'
    verbose_name = 'Finance'

    def ready(self):
        from . import checks, signals  # noqa: F401  (imported for side effects)
