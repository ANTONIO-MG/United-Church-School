"""Turn a :class:`~apps.reports.models.Certificate` into a downloadable artifact.

:func:`render_data` flattens a certificate into the plain dict the drawing code
in :mod:`apps.reports.certificate_render` consumes, and **validates it** — the
holder's name, the award line, the certificate number and the verification URL
all have to be present and the right shape before anything is drawn. A
certificate is a document someone will keep; issuing one with a blank name or a
broken verification link is worse than failing to issue it, so the checks raise
rather than paper over the gap.

PNG and PDF are both produced from the same rendered image, and the PDF is
cached onto ``Certificate.pdf`` the first time it is asked for.
"""

import logging
import re

from django.conf import settings
from django.core.exceptions import ValidationError
from django.urls import reverse

from core.branding import strings
from core.errors import capture, fail, note

from . import certificate_render

logger = logging.getLogger('apps')

# A certificate number is machine-checkable; keep it that way.
NUMBER_RE = re.compile(r'^[A-Z0-9][A-Z0-9-]{3,39}$')

# ``core.utils.display_name`` never returns blank — an account with no name and
# no e-mail falls back to "User 41". That is a fine label for a debug page and a
# disgrace on a certificate, so it is treated here as "no name at all".
PLACEHOLDER_NAME_RE = re.compile(r'^User \d+$')


def _kind_line(cert):
    """The "OF …" line under the headline, e.g. ``OF COMPLETION``."""
    label = (cert.get_kind_display() or '').strip()
    # The stored kinds name the *thing* (module, programme); on the certificate
    # itself what reads correctly is what was achieved.
    return f'OF {label.upper()} COMPLETION' if label else 'OF COMPLETION'


def _award_line(cert, award_name, grade_letter, issuer):
    mark = f'{float(cert.final_mark):.0f}%'
    grade = f' (grade {grade_letter})' if grade_letter else ''
    return (f'for successfully completing {award_name} with a final mark of '
            f'{mark}{grade}, awarded by {issuer} on '
            f'{cert.issued_at:%d %B %Y}.')


def render_data(cert, request=None):
    """Flatten and validate ``cert`` into the dict the renderer draws from.

    Raises :class:`~django.core.exceptions.ValidationError` when the certificate
    could not be rendered truthfully.
    """
    from core.utils import display_name

    from . import models

    brand = strings().get('brand', {}) or {}
    issuer = (brand.get('legal_name') or brand.get('name') or 'United Church School').strip()

    student_name = (display_name(cert.student) or '').strip()
    if not student_name or PLACEHOLDER_NAME_RE.match(student_name):
        fail('CERT-1001',
             'This certificate has no holder name — add the recipient’s name to '
             'their profile before issuing it',
             certificate=cert.pk, student=cert.student_id)

    award = cert.module
    award_name = (str(award) if award else (cert.title or '')).strip()
    if not award_name:
        fail('CERT-1001', 'This certificate names nothing that was achieved',
             certificate=cert.pk)

    number = (cert.number or '').strip().upper()
    if not NUMBER_RE.match(number):
        fail('CERT-1001',
             f'“{number or "(blank)"}” is not a usable certificate number — '
             f'it must be 4–40 characters of A–Z, 0–9 or "-"',
             certificate=cert.pk, number=number)

    # The letter grade, using the module's own scale when it defines one.
    scale = None
    if cert.module_id:
        weighting = getattr(cert.module, 'weighting', None)
        scale = weighting.scale() if weighting else None
    grade_letter = models.letter_for(cert.final_mark, scale)

    verify_path = reverse('reports:verify', args=[cert.verification_uuid])
    if request is not None:
        verify_url = request.build_absolute_uri(verify_path)
    else:
        verify_url = f"{(getattr(settings, 'SITE_URL', '') or '').rstrip('/')}{verify_path}"
    if not verify_url.endswith(verify_path):
        fail('CERT-1001', 'The certificate verification link could not be built',
             certificate=cert.pk)

    # Two signature blocks, as on the printed template — and they must say
    # different things. The left is whoever signs for the organisation; the
    # right names the educator who taught the module when there is one, so the
    # certificate credits a person rather than printing the same name twice.
    signatory = (cert.signature or '').strip() or issuer
    educator_name = ''
    if cert.module_id:
        educator = cert.module.educators.select_related('user').first()
        if educator is not None:
            educator_name = (str(educator) or '').strip()
    if educator_name and educator_name != signatory:
        counter_signature = (educator_name, 'Educator')
    else:
        # No educator to credit. Repeating the organisation's name in both
        # blocks looks like a rendering fault, so the second block carries the
        # date instead — which keeps the template's two-column footer honest.
        counter_signature = (f'{cert.issued_at:%d %B %Y}', 'Date issued')

    data = {
        'title': (cert.title or award_name).strip(),
        'kind_line': _kind_line(cert),
        'student_name': student_name,
        'award_name': award_name,
        'award_line': _award_line(cert, award_name, grade_letter, issuer),
        'grade_letter': grade_letter,
        'final_mark': f'{float(cert.final_mark):.0f}%',
        'issued_at': cert.issued_at,
        'number': number,
        'verify_url': verify_url,
        'issuer': issuer,
        'signatures': [
            (signatory, 'Authorised signatory'),
            counter_signature,
        ],
    }

    # Cheap contract check: the renderer indexes every one of these, and a
    # KeyError halfway through drawing would leave a half-painted download.
    missing = [k for k in ('title', 'kind_line', 'student_name', 'award_line',
                           'number', 'verify_url', 'issuer', 'signatures') if not data.get(k)]
    if missing:
        fail('CERT-1001', f'Certificate data is incomplete: {", ".join(missing)}',
             certificate=cert.pk, missing=missing)
    return data


# ---------------------------------------------------------------------------
# Outputs
# ---------------------------------------------------------------------------
def render_png(cert, request=None, scale=1.0):
    """The certificate as PNG bytes. Raises ValidationError on bad data."""
    data = render_data(cert, request)
    if not certificate_render.fonts_available():
        note('CERT-7001', request, certificate=cert.pk,
             font_dir=certificate_render.FONT_DIR)
    with capture('CERT-8001', request, context={'certificate': cert.pk, 'format': 'png'}):
        return certificate_render.render_png(data, scale=scale)


def render_pdf(cert, request=None):
    """The certificate as PDF bytes. Raises ValidationError on bad data."""
    data = render_data(cert, request)
    if not certificate_render.fonts_available():
        note('CERT-7001', request, certificate=cert.pk,
             font_dir=certificate_render.FONT_DIR)
    with capture('CERT-8001', request, context={'certificate': cert.pk, 'format': 'pdf'}):
        return certificate_render.render_pdf(data)


# Bumped whenever the artwork changes. It is baked into the stored filename so
# that certificates cached under an older design re-render themselves on the
# next download instead of serving a sheet that no longer matches the preview.
DESIGN_VERSION = 'v2'


def pdf_filename(cert):
    return f'{cert.number}-{DESIGN_VERSION}.pdf'


def ensure_pdf(cert, request=None):
    """Return the certificate PDF, rendering and storing it on first request.

    Re-renders when the stored file predates the current design, has gone
    missing from the media backend, or is empty — so neither a redesign nor a
    wiped media folder can leave someone downloading the wrong thing.
    """
    wanted = pdf_filename(cert)
    if cert.pdf and cert.pdf.name.endswith(wanted):
        try:
            with cert.pdf.open('rb') as fh:
                data = fh.read()
            if data:
                return data
            logger.warning('reports: stored PDF for %s is empty, re-rendering', cert.number)
        except (OSError, ValueError):
            logger.warning('reports: stored PDF for %s is unreadable, re-rendering', cert.number)
    elif cert.pdf:
        logger.info('reports: certificate %s was rendered under an older design, refreshing',
                    cert.number)

    data = render_pdf(cert, request)
    from django.core.files.base import ContentFile
    with capture('CERT-8002', request, context={'certificate': cert.pk, 'filename': wanted}):
        cert.pdf.save(wanted, ContentFile(data), save=True)
    return data


def certificate_context(cert, request=None):
    """Template context for the on-screen certificate page."""
    data = render_data(cert, request)
    return {'cert': cert, **data, 'brand': strings().get('brand', {})}
