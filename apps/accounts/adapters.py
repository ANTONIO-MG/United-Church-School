"""django-allauth adapters.

The seam for hub-specific sign-up behaviour. Keeping it here (rather than
scattering rules through views) means the HTML sign-up page, the DRF
registration serializer and Google sign-in all get the same treatment.
"""

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

from core.branding import strings as _brand_strings


class HubAccountAdapter(DefaultAccountAdapter):
    """Keeps ``username`` mirroring the e-mail address.

    The platform is e-mail-only, but Django's default ``User`` still has a
    required, unique ``username`` column. The convention here is that the two
    are the same value — ``apps.myhub.views.page_login`` authenticates on
    ``username=<e-mail>`` first and only falls back to an e-mail lookup for
    legacy rows. allauth would otherwise derive a username from the local part
    ("learner@example.com" -> "learner"), which quietly inverts that: every new
    account would need the fallback, and two people at different domains
    sharing a local part would collide into "learner", "learner2", ...

    It also makes allauth's own e-mails look like the rest of the platform's —
    see :meth:`render_mail`.
    """

    def populate_username(self, request, user):
        # The e-mail is already validated and unique-checked by the form.
        email = user_email(user)
        if email:
            user.username = email[:150]  # username column is max_length=150
        else:
            super().populate_username(request, user)

    def render_mail(self, template_prefix, email, context, headers=None):
        """Build allauth's message the way the rest of the platform builds its own.

        The verification and password-reset templates extend
        ``communication/email/base_email.html``, which references its banner,
        logo and social icons as ``cid:`` parts — that is how
        :func:`apps.communication.emails.send_branded_email` ships them, and why
        those images survive a client that blocks remote content or a SITE_URL
        that is not publicly reachable.

        allauth builds its own ``EmailMultiAlternatives`` and knows nothing about
        any of that: it rendered the same templates but attached no images, so
        every ``cid:`` reference pointed at nothing and the e-mails arrived with
        broken pictures. Here we add the two halves allauth was missing — the
        brand context the layout reads, and the inline image parts the ``cid:``
        URLs resolve to.
        """
        from apps.communication import emails as branded

        catalog = _brand_strings()
        brand = catalog.get('brand', {})
        inline_map = branded._email_inline_map(brand)

        context = dict(context or {})
        context.setdefault('brand', brand)
        context.setdefault('strings', catalog)
        context.setdefault('module', '')
        # What the layout's {{ inline.header }} etc. resolve to.
        context['inline'] = {name: f'cid:{name}' for name in inline_map}

        msg = super().render_mail(template_prefix, email, context, headers=headers)

        for name, static_path in inline_map.items():
            branded._attach_inline_image(msg, static_path, name)
        return msg


class HubSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Same username convention for accounts created via Google sign-in."""

    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        email = data.get('email') or user_email(user)
        if email:
            user.username = email[:150]
        return user


def user_email(user):
    return (getattr(user, 'email', '') or '').strip()
