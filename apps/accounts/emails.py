"""Onboarding e-mails — thin wrappers over the central branded e-mail library
(:mod:`apps.communication.emails`, templates under ``communication/email/``)."""

import logging

from django.conf import settings

logger = logging.getLogger('apps')


def _school():
    """The school's display name, from the brand catalog."""
    from core.branding import BRAND
    return BRAND.get('name') or 'United Church School'


def send_account_invitation(user, password, request=None):
    """E-mail a newly-created team member (admin/staff/educator) their login
    details and first-login steps. Best-effort; failures are logged, not raised."""
    from apps.communication import emails as comm

    login_url = ''
    try:
        from django.urls import reverse
        path = reverse('account_login')
        login_url = request.build_absolute_uri(path) if request is not None else path
    except Exception:  # pragma: no cover - defensive
        login_url = ''
    body = (
        f"An account has been created for you on {_school()}.\n\n"
        "Log in with these details:\n"
        f"    E-mail: {user.email}\n"
        f"    Temporary password: {password}\n\n"
        "On your first login, please:\n"
        "  1. Set your own password — use \"Forgot password?\" on the login page.\n"
        "  2. Complete your profile (a few personal details and consent).\n\n"
        "Welcome to the team."
    )
    try:
        return comm.send_general_email(
            [user.email], f"Your {_school()} account", body,
            action_url=login_url, action_label="Log in", recipient=user)
    except Exception:  # pragma: no cover - e-mail is best-effort
        logger.exception('accounts: account-invitation e-mail failed for %s', user.email)
        return None


def send_registration_summary(person, *, parent_invite_url=None):
    """E-mail the user a summary of what they registered for (+ parent link)."""
    try:
        from apps.communication import emails
        login_url = getattr(settings, 'SITE_URL', '').rstrip('/') + '/myhub/'
        return emails.send_registration_summary_email(
            person, parent_invite_url=parent_invite_url, login_url=login_url)
    except Exception:  # pragma: no cover
        logger.exception('accounts: registration summary e-mail failed')
        return False


def send_invite(invite):
    """E-mail an invitee their single-use registration link (parent or educator)."""
    try:
        from django.urls import reverse

        from apps.communication import emails as ce
        base = (getattr(settings, 'SITE_URL', '') or '').rstrip('/')
        accept_url = base + reverse('accounts:accept-invite', args=[invite.token])
        is_parent = invite.role == 'parent'
        subject = ('You have been invited to join as a parent / guardian'
                   if is_parent else f'You have been invited to teach at {_school()}')
        return ce.send_branded_email(
            subject, invite.email, 'invite-parent' if is_parent else 'invite-educator', {
                'invite': invite, 'accept_url': accept_url,
                'student': invite.student, 'programme': invite.programme,
            })
    except Exception:  # pragma: no cover
        logger.exception('accounts: invite e-mail failed')
        return False


