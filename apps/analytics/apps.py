from django.apps import AppConfig


class AnalyticsConfig(AppConfig):
    """Admin/staff/educator-only academic intelligence: student summaries, course
    popularity, performance analytics, predictive risk monitoring and exports."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.analytics'
    label = 'analytics'
    verbose_name = 'Analytics'
