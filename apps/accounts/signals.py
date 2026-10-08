"""Signal handlers for the accounts app.

Two responsibilities:

1. Keep a :class:`~apps.accounts.models.Person` profile in sync with every
   ``auth.User`` (one is created automatically when a user is created).
2. Record an :class:`~apps.accounts.models.ActivityLog` row whenever a user is
   created, updated or deleted, or logs in / out.

Connected in :meth:`apps.accounts.apps.AccountsConfig.ready`.
"""

import logging

from django.conf import settings
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch import receiver

from .middleware import get_current_request
from apps.learning.models import ProgrammeModule
from .models import ActivityLog, Person
logger = logging.getLogger(__name__)


def _request_context():
    """Return (actor, ip_address, request_path) safely."""
    request = get_current_request()

    # ALWAYS return a tuple (never None)
    if request is None:
        return None, None, None

    ip = request.META.get('REMOTE_ADDR')
    path = request.path

    actor = None
    if hasattr(request, "user") and request.user.is_authenticated:
        actor = getattr(request.user, 'profile', None)

    return actor, ip, path


def _profile_of(user):
    """Return the ``Person`` linked to ``user``, or ``None`` if there is none."""
    if user is None:
        return None
    try:
        return user.profile
    except Person.DoesNotExist:
        return None


# ---------------------------------------------------------------------------
# Keep a Person profile attached to every User
# ---------------------------------------------------------------------------
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_person_profile(sender, instance, created, raw=False, **kwargs):
    # ``raw`` means the row is being loaded verbatim from a fixture or an
    # account archive, which carries its own Person. Making one here would
    # collide with it on the one-to-one user column, so raw loads are skipped —
    # which is what ``raw`` is for.
    if created and not raw:
        Person.objects.create(user=instance)


# ---------------------------------------------------------------------------
# Enrol a student when their registration invoice is paid (Phase 4)
# ---------------------------------------------------------------------------
def _send_paid_registration_summary(invoice):
    """Welcome + summary + proof of payment, for a *registration* invoice.

    Only fires for an invoice that has module enrolments behind it — an invoice
    for anything else (a shop order, an ad-hoc fee) is not a registration and
    gets its own receipt e-mail from the finance app instead. Never raises: a
    settled payment must stand whatever happens to the e-mail.
    """
    try:
        from apps.learning.models import ModuleEnrolment

        enrolments = list(
            ModuleEnrolment.objects
            .filter(invoice_uid=invoice.public_id)
            .select_related('programme_module__programme__institution', 'person__user'))
        if not enrolments:
            return

        person = enrolments[0].person
        programme = enrolments[0].programme_module.programme
        from . import registration_billing
        registration_billing.send_registration_summary(
            person, invoice, enrolments, paid=True, programme=programme)
    except Exception:  # pragma: no cover
        logger.exception('accounts: registration summary e-mail failed for invoice %s',
                         getattr(invoice, 'number', '?'))


try:
    from apps.finance.dispatch import invoice_paid

    @receiver(invoice_paid)
    def enrol_on_invoice_paid(sender, invoice, **kwargs):
        """An invoice settled →
        (1) unlock any ProgrammeModules it was raised for (module per-month
            billing — the institution→programme→module spine),
        (2) send the registration summary with the proof of payment attached,
            for a registration invoice that was paid by card, and
        (3) clear the onboarding gate for the person whose pending invoice this
            is (a no-op for any other invoice)."""
        from core.errors import capture
        with capture('FIN-6002', reraise=False, context={'invoice': str(invoice.public_id)}):
            from apps.learning.enrolment import activate_modules_for_invoice
            activate_modules_for_invoice(invoice)

        _send_paid_registration_summary(invoice)

        Person.objects.filter(pending_invoice_uid=invoice.public_id).update(
            pending_invoice_uid=None)
except Exception:  # pragma: no cover - finance app always present, defensive only
    logger.exception('accounts: could not connect invoice_paid receiver')


# ---------------------------------------------------------------------------
# Audit logging: user create / update
# ---------------------------------------------------------------------------
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def log_user_save(sender, instance, created, raw=False, **kwargs):
    # A raw load is a restore, not somebody doing something — and the profile it
    # would be logged against has not been inserted yet.
    if raw:
        return
    actor, ip, path = _request_context()
    ActivityLog.objects.create(
        actor=actor,
        target_user=_profile_of(instance),
        action='create' if created else 'update',
        description=f"User {'created' if created else 'updated'}: {instance}",
        ip_address=ip,
        request_path=path,
    )
    logger.info('USER %s | id=%s | email=%s',
                'CREATED' if created else 'UPDATED', instance.pk, instance.email)


# ---------------------------------------------------------------------------
# Audit logging: user delete
# ---------------------------------------------------------------------------
@receiver(post_delete, sender=settings.AUTH_USER_MODEL)
def log_user_delete(sender, instance, **kwargs):
    actor, ip, path = _request_context()
    ActivityLog.objects.create(
        actor=actor,
        target_user=_profile_of(instance),
        action='delete',
        description=f'User deleted: {instance}',
        ip_address=ip,
        request_path=path,
    )
    logger.warning('USER DELETED | id=%s | email=%s', instance.pk, instance.email)


# ---------------------------------------------------------------------------
# Audit logging: login / logout
# ---------------------------------------------------------------------------
@receiver(user_logged_in)
def log_login(sender, request, user, **kwargs):
    person = _profile_of(user)
    ActivityLog.objects.create(
        actor=person,
        target_user=person,
        action='login',
        description='User logged in',
        ip_address=request.META.get('REMOTE_ADDR', None),
        request_path=request.path or None,
    )


@receiver(user_logged_out)
def log_logout(sender, request, user, **kwargs):
    person = _profile_of(user)
    ActivityLog.objects.create(
        actor=person,
        target_user=person,
        action='logout',
        description='User logged out',
        ip_address=request.META.get('REMOTE_ADDR', None),
        request_path=request.path or None,
    )


# ---------------------------------------------------------------------------
# Security: confirm by e-mail when a password is changed or reset (allauth)
# ---------------------------------------------------------------------------
try:  # allauth is always installed, but stay defensive.
    from allauth.account.signals import password_changed as _pw_changed
    from allauth.account.signals import password_reset as _pw_reset

    def _email_password_changed(request, user, **kwargs):
        try:
            from apps.communication.emails import send_password_changed
            login_url = getattr(settings, 'SITE_URL', '').rstrip('/') + '/myhub/page-login/'
            send_password_changed(user, login_url=login_url)
        except Exception:  # pragma: no cover - never break the password flow
            logger.exception('Failed to send password-changed e-mail')

    receiver(_pw_changed)(_email_password_changed)
    receiver(_pw_reset)(_email_password_changed)
except Exception:  # pragma: no cover
    logger.exception('Could not wire allauth password signals')
