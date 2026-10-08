from django.apps import AppConfig


class AdmissionsConfig(AppConfig):
    """United Church School's application for admission — the online version of
    the *UCS Application Form 2026* (learner, family, medical, documents,
    declarations) and the office's checklist for processing it."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.admissions'
    verbose_name = 'Admissions'

    def ready(self):
        from . import signals  # noqa: F401  (connect the invoice_paid receiver)
