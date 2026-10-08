"""Shared upload validators.

Every ``FileField``/``ImageField`` in the project used to accept anything of any
size: workspace documents, lesson attachments, feed images, profile pictures,
proof-of-payment documents. Two separate problems come from that:

* **Size.** Nothing stopped a multi-gigabyte upload filling the disk.
* **Type.** An uploaded ``.svg`` or ``.html`` is served from the media domain and
  runs as script *in this site's origin* — it can read the session cookie and
  act as the signed-in user. ``.svg`` is the awkward one: it is a legitimate
  image format and an executable document at the same time, so it is allowed
  where images are, and the media response headers
  (:mod:`apps.accounts.middleware`) stop it executing.

The allow-lists are deliberately narrow — an extension not listed is one nobody
has asked for yet. Adding one is a one-line change here rather than a decision
repeated at nineteen call sites.

Validators must be module-level named callables (not lambdas or locals), or
``makemigrations`` cannot serialise them into a migration.
"""

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.template.defaultfilters import filesizeformat
from django.utils.deconstruct import deconstructible

MB = 1024 * 1024

# --- what each kind of field accepts ---------------------------------------
IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'avif']
DOCUMENT_EXTENSIONS = [
    'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
    'txt', 'csv', 'rtf', 'odt', 'ods', 'odp',
]
MEDIA_EXTENSIONS = ['mp3', 'wav', 'm4a', 'ogg', 'mp4', 'webm', 'mov', 'm4v']
ARCHIVE_EXTENSIONS = ['zip']

# An attachment may be any of the above — a learner submitting an assignment or
# a colleague sharing a workspace file should not have to care which bucket it
# falls in.
ATTACHMENT_EXTENSIONS = sorted(
    set(IMAGE_EXTENSIONS + DOCUMENT_EXTENSIONS + MEDIA_EXTENSIONS + ARCHIVE_EXTENSIONS))


@deconstructible
class MaxFileSize:
    """Reject an upload larger than ``max_mb`` megabytes."""

    def __init__(self, max_mb):
        self.max_mb = max_mb

    def __call__(self, value):
        size = getattr(value, 'size', None)
        if size is not None and size > self.max_mb * MB:
            raise ValidationError(
                'That file is %(size)s. The limit is %(limit)s.',
                code='file_too_large',
                params={'size': filesizeformat(size),
                        'limit': filesizeformat(self.max_mb * MB)},
            )

    def __eq__(self, other):
        return isinstance(other, MaxFileSize) and other.max_mb == self.max_mb

    def __hash__(self):
        return hash(('MaxFileSize', self.max_mb))


# --- ready-made validator lists, one per kind of field ----------------------
# Sizes are per-field rather than global: a profile picture has no business
# being 25 MB, and a lecture recording legitimately is.
validate_image = [FileExtensionValidator(IMAGE_EXTENSIONS), MaxFileSize(5)]
validate_avatar = [FileExtensionValidator(IMAGE_EXTENSIONS), MaxFileSize(2)]
validate_document = [FileExtensionValidator(DOCUMENT_EXTENSIONS), MaxFileSize(25)]
validate_attachment = [FileExtensionValidator(ATTACHMENT_EXTENSIONS), MaxFileSize(25)]
validate_media = [FileExtensionValidator(IMAGE_EXTENSIONS + MEDIA_EXTENSIONS),
                  MaxFileSize(100)]
validate_package = [FileExtensionValidator(ARCHIVE_EXTENSIONS), MaxFileSize(200)]
# Sent with a broadcast notification: a poster, a short clip or the document itself.
validate_broadcast = [FileExtensionValidator(ATTACHMENT_EXTENSIONS), MaxFileSize(100)]
# A shop download: a worksheet PDF, the spreadsheet, or the zip of past papers.
validate_download = [FileExtensionValidator(DOCUMENT_EXTENSIONS + ARCHIVE_EXTENSIONS),
                     MaxFileSize(200)]


# --- media response headers -------------------------------------------------
# Extensions that must never be rendered inline by the browser, whatever the
# stored content type says. Serving one of these from the media domain with
# ``Content-Disposition: inline`` runs it in this site's origin.
NEVER_INLINE_EXTENSIONS = frozenset({
    'svg', 'html', 'htm', 'xhtml', 'xml', 'js', 'mjs', 'css', 'swf', 'xht',
})


def must_download(name):
    """True when ``name`` must be served as an attachment rather than inline."""
    _, _, ext = (name or '').rpartition('.')
    return ext.lower() in NEVER_INLINE_EXTENSIONS
