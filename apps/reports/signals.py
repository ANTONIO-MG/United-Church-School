"""When a student's assessment is submitted/marked, recompute their module
grade, re-rank the module's cohort and auto-issue a certificate if they have
now passed the module.

One student's new mark can move everyone else's class position, so the whole
module is re-ranked — not just the row that changed."""

import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


@receiver(post_save, sender='assessments.AssessmentAttempt')
def recompute_grade_on_attempt(sender, instance, **kwargs):
    if instance.status not in ('submitted', 'marked'):
        return
    _refresh(instance.student, instance.assessment.module)


@receiver(post_save, sender='assessments.AssignmentSubmission')
def recompute_grade_on_assignment(sender, instance, **kwargs):
    if instance.status not in ('marked', 'completed'):
        return
    _refresh(instance.student, instance.assessment.module)


def _refresh(student, module):
    from . import services
    try:
        grade = services.compute_grade(student, module)
        # A new mark reorders the cohort, so positions are rewritten module-wide.
        # Guarded separately: a ranking failure must not block the certificate.
        try:
            services.rank_module(module)
        except Exception:  # pragma: no cover
            logger.exception('Class ranking failed for %s', module)
        if grade.passed:
            services.issue_certificate(
                student, module=module, kind='module',
                title=f'Subject Completion — {module}', final_mark=grade.final_pct,
            )
    except Exception:  # pragma: no cover - never let grading break a save
        logger.exception('Grade/certificate refresh failed for %s / %s', student, module)
