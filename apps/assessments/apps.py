from django.apps import AppConfig


class AssessmentsConfig(AppConfig):
    """Unified assessment engine: quizzes, tests, exam sections, assignments —
    with sections, many question types, attempts and auto-marking."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.assessments'
    label = 'assessments'
    verbose_name = 'Assessments'
