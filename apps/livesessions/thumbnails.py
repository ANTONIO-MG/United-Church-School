"""Draw a session thumbnail: the details, laid over a background image.

One background picture is configured once (``LiveSessionSettings.thumbnail_background``);
every session gets its own card by having its title, programme, module, week or
test, and its date and time drawn on top. The same 1280×720 image is used in
three places — the session card on the platform, the schedule row, and the
YouTube thumbnail — so a student recognises the class before reading anything.

Pillow is already a hard dependency (ImageFields), so there is nothing new to
install. If the background is missing or unreadable the card is drawn on a flat
brand panel instead: a plain thumbnail is a much smaller problem than a session
that could not be created because an image was.
"""

import io
import logging

from django.conf import settings

logger = logging.getLogger('apps')

#: YouTube's thumbnail size, and a clean 16:9 for the platform card.
SIZE = (1280, 720)
#: Left/right gutter and the bottom edge the text block sits on.
MARGIN = 72


def render(meeting, *, conf=None):
    """Return the thumbnail as JPEG ``bytes``, or None if it could not be drawn."""
    try:
        from PIL import Image, ImageDraw
    except Exception:       # pragma: no cover - Pillow is a hard dep, but never crash a session
        logger.warning('thumbnails: Pillow unavailable — skipping')
        return None

    from .models import LiveSessionSettings
    conf = conf or LiveSessionSettings.load()

    canvas = _background(conf, Image)
    draw = ImageDraw.Draw(canvas, 'RGBA')

    # A bottom-up gradient scrim. Without it the text is unreadable over a busy
    # photograph — and the whole point of the card is that it can be read at a
    # glance in a list.
    scrim_top = int(SIZE[1] * 0.38)
    for y in range(scrim_top, SIZE[1]):
        alpha = int(215 * (y - scrim_top) / max(1, SIZE[1] - scrim_top))
        draw.line([(0, y), (SIZE[0], y)], fill=(9, 15, 32, alpha))

    accent = _hex(conf.thumbnail_accent_colour, (201, 168, 76))
    text_rgb = _hex(conf.thumbnail_text_colour, (255, 255, 255))

    title_font = _font(58)
    line_font = _font(34)
    small_font = _font(28)

    # Build bottom-up so the block always sits on the same baseline however many
    # detail lines a particular session happens to have.
    lines = [line for line in meeting.thumbnail_caption_lines if line]
    y = SIZE[1] - MARGIN
    for line in reversed(lines):
        y -= 44
        draw.text((MARGIN, y), _fit(draw, line, line_font, SIZE[0] - 2 * MARGIN),
                  font=line_font, fill=text_rgb + (235,))

    y -= 26
    for wrapped in reversed(_wrap(draw, meeting.title or 'Live session', title_font,
                                  SIZE[0] - 2 * MARGIN, max_lines=2)):
        y -= 68
        draw.text((MARGIN, y), wrapped, font=title_font, fill=text_rgb + (255,))

    # The accent rule above the title, and the session kind above that.
    y -= 22
    draw.rectangle([MARGIN, y, MARGIN + 96, y + 6], fill=accent + (255,))
    y -= 40
    draw.text((MARGIN, y), meeting.get_session_kind_display().upper(),
              font=small_font, fill=accent + (255,))

    buffer = io.BytesIO()
    canvas.convert('RGB').save(buffer, format='JPEG', quality=88, optimize=True)
    return buffer.getvalue()


def filename_for(meeting):
    from apps.communication.models import _safe_folder_name
    return f'{_safe_folder_name(meeting.title, limit=80)}-thumbnail.jpg'


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def _background(conf, Image):
    """The configured background, cropped to fill 1280×720 — else a flat panel."""
    source = getattr(conf, 'thumbnail_background', None)
    if source:
        try:
            with source.open('rb') as fh:
                img = Image.open(fh)
                img.load()
            return _cover(img.convert('RGB'), Image)
        except Exception:
            logger.warning('thumbnails: could not read the configured background', exc_info=True)
    return Image.new('RGB', SIZE, _brand_navy())


def _cover(img, Image):
    """Scale-and-crop to :data:`SIZE` — never stretch someone's artwork."""
    target_ratio = SIZE[0] / SIZE[1]
    width, height = img.size
    ratio = width / height if height else target_ratio
    if ratio > target_ratio:
        new_width = int(height * target_ratio)
        left = (width - new_width) // 2
        img = img.crop((left, 0, left + new_width, height))
    elif ratio < target_ratio:
        new_height = int(width / target_ratio)
        top = (height - new_height) // 2
        img = img.crop((0, top, width, top + new_height))
    return img.resize(SIZE, Image.LANCZOS)


def _brand_navy():
    raw = getattr(settings, 'BRAND_PRIMARY_COLOUR', '') or '#1F3864'
    return _hex(raw, (31, 56, 100))


def _hex(value, fallback):
    value = (value or '').strip().lstrip('#')
    if len(value) == 6:
        try:
            return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))
        except ValueError:
            pass
    return fallback


def _font(size):
    """A TrueType face at ``size``, or Pillow's bitmap default.

    The default font ignores ``size`` entirely, so on a box with no DejaVu the
    card comes out small but still legible — which beats failing to draw it.
    """
    from PIL import ImageFont
    candidates = [
        getattr(settings, 'SESSION_THUMBNAIL_FONT', ''),
        '/System/Library/Fonts/Supplemental/Arial Bold.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
        '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',
    ]
    for path in candidates:
        if not path:
            continue
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


def _width(draw, text, font):
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0]


def _fit(draw, text, font, max_width):
    """Truncate ``text`` with an ellipsis so it fits on one line."""
    if _width(draw, text, font) <= max_width:
        return text
    trimmed = text
    while trimmed and _width(draw, trimmed + '…', font) > max_width:
        trimmed = trimmed[:-1]
    return (trimmed + '…') if trimmed else ''


def _wrap(draw, text, font, max_width, *, max_lines=2):
    """Greedy word-wrap, ellipsising whatever will not fit in ``max_lines``."""
    words, lines, current = str(text).split(), [], ''
    for word in words:
        candidate = f'{current} {word}'.strip()
        if _width(draw, candidate, font) <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
            if len(lines) == max_lines:
                break
    if current and len(lines) < max_lines:
        lines.append(current)
    if len(lines) == max_lines and len(' '.join(lines).split()) < len(words):
        lines[-1] = _fit(draw, lines[-1] + ' …', font, max_width)
    return lines or ['']
