from django.apps import AppConfig


class AttendanceConfig(AppConfig):
    """The daily school register: one register per class per school day, every
    learner pre-marked present, the class teacher marks who is absent."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.attendance'
    verbose_name = 'Daily attendance'
