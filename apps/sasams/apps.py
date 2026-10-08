from django.apps import AppConfig


class SasamsConfig(AppConfig):
    """SA-SAMS / LURITS export for the Department: learner register, parents,
    mark schedules, attendance and a data-quality report (no models)."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.sasams'
    verbose_name = 'SA-SAMS export'
