"""Response headers that stop an uploaded file running as script in our origin.

Uploads are served from ``MEDIA_URL`` on the *same host* as the application, so
the browser treats anything served there as same-origin. An uploaded ``.svg`` —
a legitimate image format that may also contain ``<script>`` — or an ``.html``
attachment therefore executes with access to the session cookie and can act as
the signed-in user. Extension validators (see :mod:`core.validators`) alone do
not close this, because ``.svg`` has to remain allowed for logos and avatars.

Two headers do close it:

``X-Content-Type-Options: nosniff``
    Stops the browser second-guessing a declared content type — a ``.png`` whose
    bytes are really HTML stays a broken image instead of becoming a page.

``Content-Disposition: attachment``
    Applied to the extensions in
    :data:`core.validators.NEVER_INLINE_EXTENSIONS`, so those download rather
    than render. An SVG logo still displays through an ``<img>`` tag, which is
    the only way the product uses one; what stops working is *navigating* to it
    directly, which is exactly the attack.

In production media is normally served by nginx / a CDN, which should carry the
same rules — this middleware makes the guarantee hold wherever Django serves the
file itself (the dev server, and any storage backend that streams through a
view).
"""

from django.conf import settings

from core.validators import must_download


class MediaSecurityHeadersMiddleware:
    """Add anti-sniffing / anti-inline headers to responses under ``MEDIA_URL``."""

    def __init__(self, get_response):
        self.get_response = get_response
        self.media_url = getattr(settings, 'MEDIA_URL', '/media/') or '/media/'
        self.files_url = getattr(settings, 'FILES_URL', self.media_url) or self.media_url

    def __call__(self, request):
        response = self.get_response(request)
        path = request.path
        if not (path.startswith(self.media_url) or path.startswith(self.files_url)):
            return response

        response['X-Content-Type-Options'] = 'nosniff'
        # A media file is not a page: nothing on it should be able to fetch, and
        # nothing should be able to frame it.
        response.setdefault('Content-Security-Policy', "sandbox; default-src 'none'")
        response.setdefault('X-Frame-Options', 'DENY')

        if must_download(path):
            # Overwrite rather than setdefault: Django's static serve view (and
            # some storage backends) already set ``Content-Disposition: inline``,
            # and deferring to it left exactly the SVG-executes-in-our-origin
            # case open — the header was present, so it looked handled.
            filename = path.rsplit('/', 1)[-1].replace('"', '')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
