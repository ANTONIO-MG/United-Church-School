"""Draw a :class:`~apps.reports.models.Certificate` as artwork.

One renderer, three outputs. :func:`render_image` composes the whole certificate
— black corner wedges, the interlocking gold lattice down both margins, the gold
seal and every line of text — into a Pillow image; the PNG, the PDF and the
on-screen preview are all that same image. There is deliberately no second
layout implementation, so the download can never disagree with the preview.

Everything is positioned as a fraction of the canvas, so the design is
resolution-independent: ask for a bigger ``scale`` and you get a crisper
certificate, not a different one.

Fonts are bundled under ``static/fonts/certificate/`` (Poppins and Great Vibes,
both SIL Open Font License) rather than taken from the host, so a Linux server
renders exactly what a designer sees on a Mac.
"""

import io
import logging
import os

from django.conf import settings

logger = logging.getLogger('apps')

# A4 landscape at 150dpi. Everything else is a fraction of these two numbers.
BASE_W, BASE_H = 1754, 1240

# The gold ramp used for every gilded element, dark→light→dark so the strokes
# read as metal rather than flat yellow.
GOLD_STOPS = [
    (0.00, (0x8A, 0x6B, 0x1F)),
    (0.18, (0xF3, 0xDE, 0x8E)),
    (0.34, (0xC9, 0xA2, 0x27)),
    (0.52, (0xFD, 0xF3, 0xC0)),
    (0.70, (0xC5, 0x9B, 0x22)),
    (0.86, (0xE8, 0xCE, 0x74)),
    (1.00, (0x9A, 0x77, 0x22)),
]
INK = (0x11, 0x11, 0x11)
PAPER = (0xFF, 0xFF, 0xFF)


# ---------------------------------------------------------------------------
# Fonts
# ---------------------------------------------------------------------------
FONT_DIR = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'certificate')
FONT_FILES = {
    'script': 'GreatVibes-Regular.ttf',
    'bold': 'Poppins-Bold.ttf',
    'semibold': 'Poppins-SemiBold.ttf',
    'regular': 'Poppins-Regular.ttf',
}


def font_path(name):
    """Absolute path to a bundled font, or ``None`` when it is missing."""
    path = os.path.join(FONT_DIR, FONT_FILES[name])
    return path if os.path.exists(path) else None


def _font(name, size):
    """Load a bundled font at ``size``, falling back to Pillow's default.

    The fallback keeps a certificate renderable on a checkout whose fonts were
    not fetched — it will look plain, but it will never raise mid-download.
    """
    from PIL import ImageFont
    path = font_path(name)
    if path:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            logger.warning('reports: could not load certificate font %s', path)
    try:
        return ImageFont.load_default(size)
    except TypeError:            # Pillow < 10.1 has no size argument
        return ImageFont.load_default()


def fonts_available():
    """True when every bundled font is present — used by the health check."""
    return all(font_path(name) for name in FONT_FILES)


# ---------------------------------------------------------------------------
# Gilding
# ---------------------------------------------------------------------------
def _gold_sheet(size):
    """A diagonal gold gradient the size of the canvas, used to fill strokes."""
    from PIL import Image

    width, height = size
    ramp = Image.new('RGB', (256, 1))
    pixels = ramp.load()
    for x in range(256):
        t = x / 255.0
        # Find the pair of stops this position falls between and mix them.
        lower = GOLD_STOPS[0]
        upper = GOLD_STOPS[-1]
        for i in range(len(GOLD_STOPS) - 1):
            if GOLD_STOPS[i][0] <= t <= GOLD_STOPS[i + 1][0]:
                lower, upper = GOLD_STOPS[i], GOLD_STOPS[i + 1]
                break
        span = (upper[0] - lower[0]) or 1
        k = (t - lower[0]) / span
        pixels[x, 0] = tuple(int(lower[1][c] + (upper[1][c] - lower[1][c]) * k) for c in range(3))

    # Stretch the ramp over the canvas, then tilt it so the sheen runs corner
    # to corner instead of straight across.
    diagonal = int((width ** 2 + height ** 2) ** 0.5) + 2
    sheet = ramp.resize((diagonal, diagonal), Image.BILINEAR).rotate(45, expand=False)
    left = (diagonal - width) // 2
    top = (diagonal - height) // 2
    return sheet.crop((left, top, left + width, top + height))


def _paste_gold(canvas, mask, gold):
    """Paint the gold sheet onto ``canvas`` wherever ``mask`` is opaque."""
    canvas.paste(gold, (0, 0), mask)


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------
def _draw_centred(draw, cx, cy, text, font, fill, *, tracking=0):
    """Draw ``text`` centred on the point ``(cx, cy)``.

    Positioning is by Pillow's ``mm`` anchor — the visual middle of the glyphs —
    rather than by a nominal top-left. Anchoring on the top-left means every
    line has to account for that font's ascent by hand, which is exactly how the
    headline ends up sitting on top of the line beneath it.

    ``tracking`` adds letter-spacing in pixels, which is what gives the headline
    and the small caps their engraved feel; Pillow has no native support for it,
    so the string is drawn one glyph at a time.
    """
    if not text:
        return
    if not tracking:
        draw.text((cx, cy), text, font=font, fill=fill, anchor='mm')
        return
    widths = [draw.textlength(ch, font=font) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = cx - total / 2
    for ch, w in zip(text, widths):
        draw.text((x + w / 2, cy), ch, font=font, fill=fill, anchor='mm')
        x += w + tracking


def _fit_font(draw, text, name, start_size, max_width, min_size=10):
    """Largest size of ``name`` at which ``text`` still fits ``max_width``.

    Names and course titles vary wildly in length; without this a long one would
    simply run off the edge of the certificate.
    """
    size = start_size
    while size > min_size:
        font = _font(name, size)
        if draw.textlength(text, font=font) <= max_width:
            return font
        size -= max(1, size // 40)
    return _font(name, min_size)


def _wrap(draw, text, font, max_width):
    """Greedy word wrap to ``max_width``, returning a list of lines."""
    words = (text or '').split()
    if not words:
        return []
    lines, current = [], words[0]
    for word in words[1:]:
        candidate = f'{current} {word}'
        if draw.textlength(candidate, font=font) <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


# ---------------------------------------------------------------------------
# Ornament
# ---------------------------------------------------------------------------
# How far in from each edge the ornament is allowed to reach. Everything
# between these two fractions stays white, which is what keeps the certificate
# legible — the border is decoration, not a background for the text.
MARGIN = 0.225

# The vertical rhythm, as fractions of the sheet height. Kept here as data —
# rather than as numbers sprinkled through render_image — because the tests
# assert that consecutive lines do not collide, and they have to be able to read
# the same values the renderer draws with. Great Vibes is the tight constraint:
# its capitals carry tall swashes and its descenders are long, so the name needs
# roughly a sixth of the sheet to itself.
LAYOUT = {
    'seal_y': 0.130,
    'headline_y': 0.300, 'headline_size': 0.082,
    'kind_y': 0.372, 'kind_size': 0.029,
    'presented_y': 0.400, 'presented_size': 0.027,
    'name_y': 0.500, 'name_size': 0.128,
    'rule_y': 0.580,
    'body_y': 0.618, 'body_size': 0.026, 'body_step': 0.035,
    'sig_rule_y': 0.778, 'sig_name_size': 0.025, 'sig_role_size': 0.023,
    'footer_y': 0.905,
}


def _draw_corners(draw, w, h):
    """The black wedges that anchor the four corners of the sheet."""
    # Thin band across the top, sliced off at an angle on its right end.
    draw.polygon([(0, 0), (0.60 * w, 0), (0.556 * w, 0.033 * h), (0, 0.033 * h)], fill=INK)
    draw.polygon([(0, 0), (0.055 * w, 0), (0, 0.078 * h)], fill=INK)
    # Top-right corner, cut on the diagonal.
    draw.polygon([(0.80 * w, 0), (w, 0), (w, 0.19 * h)], fill=INK)
    # Bottom-left triangle rising off the corner.
    draw.polygon([(0, h), (0, 0.63 * h), (0.26 * w, h)], fill=INK)
    # Band across the bottom, sliced on its left end, plus the corner.
    draw.polygon([(0.44 * w, h), (0.497 * w, 0.962 * h), (w, 0.962 * h), (w, h)], fill=INK)
    draw.polygon([(0.92 * w, h), (w, 0.85 * h), (w, h)], fill=INK)


def _lattice_mask(w, h):
    """Mask of the interlocking gold diamonds down the left and right margins.

    Two overlapping columns a side, each row offset by half a diamond, which is
    what makes the chain read as woven rather than as a row of separate shapes.
    Nothing is drawn inside :data:`MARGIN` — see the note there.
    """
    from PIL import Image, ImageDraw

    mask = Image.new('L', (w, h), 0)
    pen = ImageDraw.Draw(mask)
    stroke = max(2, int(0.009 * w))
    radius = 0.105 * w
    # Just under 2r, so consecutive diamonds overlap and read as a chain rather
    # than as a grid of separate tiles.
    step = radius * 1.45

    def diamond(cx, cy, r, width):
        pen.polygon([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)],
                    outline=255, width=width)

    for side in (0, 1):
        edge = -0.02 * w if side == 0 else w + 0.02 * w
        direction = 1 if side == 0 else -1
        for column in range(2):
            cx = edge + direction * column * step
            offset = step / 2 if column % 2 else 0
            for row in range(-1, int(h / step) + 3):
                cy = row * step + offset
                diamond(cx, cy, radius, stroke)
                diamond(cx, cy, radius * 0.48, max(2, int(stroke * 0.55)))
    return mask


def _seal_mask(w, h):
    """Mask of the scalloped gold medal above the headline."""
    import math

    from PIL import Image, ImageDraw

    mask = Image.new('L', (w, h), 0)
    pen = ImageDraw.Draw(mask)
    cx, cy = w / 2, 0.130 * h
    outer = 0.048 * w

    # Ribbon tails first, so the medal sits on top of them. Fully opaque — a
    # partial mask value lets the white paper through and the gilt goes chalky.
    pen.polygon([(cx - outer * 0.62, cy + outer * 0.35), (cx - outer * 0.12, cy + outer * 0.45),
                 (cx - outer * 0.30, cy + outer * 1.90), (cx - outer * 0.80, cy + outer * 1.30)], fill=255)
    pen.polygon([(cx + outer * 0.62, cy + outer * 0.35), (cx + outer * 0.12, cy + outer * 0.45),
                 (cx + outer * 0.30, cy + outer * 1.90), (cx + outer * 0.80, cy + outer * 1.30)], fill=255)

    # Scalloped rim: 24 points alternating between two radii.
    points = []
    teeth = 24
    for i in range(teeth * 2):
        angle = math.pi * i / teeth
        r = outer if i % 2 == 0 else outer * 0.88
        points.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    pen.polygon(points, fill=255)
    return mask


def _seal_engraving(draw, w, h):
    """The concentric rings pressed into the medal, drawn over the gilt."""
    cx, cy = w / 2, 0.130 * h
    outer = 0.048 * w
    line = max(1, int(0.0016 * w))
    draw.ellipse([cx - outer * 0.74, cy - outer * 0.74, cx + outer * 0.74, cy + outer * 0.74],
                 outline=(0x8A, 0x6B, 0x1F), width=line * 2)
    draw.ellipse([cx - outer * 0.58, cy - outer * 0.58, cx + outer * 0.58, cy + outer * 0.58],
                 outline=(0xE8, 0xD2, 0x8A), width=line)


# ---------------------------------------------------------------------------
# The certificate
# ---------------------------------------------------------------------------
def render_image(data, scale=1.0):
    """Render the certificate described by ``data`` and return a Pillow image.

    ``data`` is the plain dict from :func:`apps.reports.certificates.render_data`
    — deliberately not a model, so this stays a pure drawing function that is
    trivial to test with made-up values.
    """
    from PIL import Image, ImageDraw

    w, h = int(BASE_W * scale), int(BASE_H * scale)
    canvas = Image.new('RGB', (w, h), PAPER)
    draw = ImageDraw.Draw(canvas)

    # Black first, gold over it: on the printed template the gilt chain crosses
    # in front of the corner wedges rather than stopping at them.
    _draw_corners(draw, w, h)
    gold = _gold_sheet((w, h))
    _paste_gold(canvas, _lattice_mask(w, h), gold)
    _paste_gold(canvas, _seal_mask(w, h), gold)
    _seal_engraving(draw, w, h)

    cx = w / 2
    # The clear white column between the two ornament margins.
    text_width = (1 - 2 * MARGIN) * w

    L = LAYOUT

    # CERTIFICATE / OF <KIND>
    headline = _fit_font(draw, 'CERTIFICATE', 'bold', int(L['headline_size'] * h), text_width * 0.94)
    _draw_centred(draw, cx, L['headline_y'] * h, 'CERTIFICATE', headline, INK, tracking=0.0035 * w)
    sub_font = _fit_font(draw, data['kind_line'], 'bold', int(L['kind_size'] * h), text_width * 0.8)
    _draw_centred(draw, cx, L['kind_y'] * h, data['kind_line'], sub_font, INK, tracking=0.0022 * w)

    # Presentation line
    presented = _font('regular', int(L['presented_size'] * h))
    _draw_centred(draw, cx, L['presented_y'] * h, 'This certificate is presented to:', presented, INK)

    # The holder's name, in script, shrunk to fit if it is a long one.
    name_font = _fit_font(draw, data['student_name'], 'script', int(L['name_size'] * h), text_width)
    _draw_centred(draw, cx, L['name_y'] * h, data['student_name'], name_font, INK)

    # Rule under the name
    rule_y = L['rule_y'] * h
    hairline = max(1, int(0.0016 * h))
    draw.line([(cx - text_width / 2, rule_y), (cx + text_width / 2, rule_y)], fill=INK, width=hairline)

    # Award wording, wrapped. Capped at three lines so a very long course title
    # can never push the signatures off the sheet.
    body = _font('regular', int(L['body_size'] * h))
    lines = _wrap(draw, data['award_line'], body, text_width)[:3]
    y = L['body_y'] * h
    for line in lines:
        _draw_centred(draw, cx, y, line, body, (0x2A, 0x2A, 0x2A))
        y += L['body_step'] * h

    # Two signature blocks, as on the printed template.
    sig_rule_y = L['sig_rule_y'] * h
    sig_name = _font('bold', int(L['sig_name_size'] * h))
    sig_role = _font('regular', int(L['sig_role_size'] * h))
    for centre, (who, role) in zip((0.335 * w, 0.665 * w), data['signatures']):
        draw.line([(centre - 0.085 * w, sig_rule_y), (centre + 0.085 * w, sig_rule_y)],
                  fill=INK, width=hairline)
        who_font = _fit_font(draw, who, 'bold', int(L['sig_name_size'] * h), 0.20 * w)
        _draw_centred(draw, centre, sig_rule_y + 0.030 * h, who, who_font, INK)
        _draw_centred(draw, centre, sig_rule_y + 0.066 * h, role, sig_role, (0x3A, 0x3A, 0x3A))

    # Verification footer — small, but the reason the certificate is checkable.
    footer = f"Certificate No. {data['number']}  ·  Verify at {data['verify_url']}"
    tiny = _fit_font(draw, footer, 'regular', int(0.018 * h), 0.62 * w, min_size=8)
    _draw_centred(draw, cx, L['footer_y'] * h, footer, tiny, (0x60, 0x60, 0x60))
    return canvas


def render_png(data, scale=1.0):
    """The certificate as PNG ``bytes``."""
    buf = io.BytesIO()
    render_image(data, scale=scale).save(buf, format='PNG', optimize=True)
    return buf.getvalue()


def render_pdf(data, scale=2.0):
    """The certificate as a single-page A4-landscape PDF, in ``bytes``.

    Rendered from the same image as the PNG, at twice the working resolution, so
    the printed sheet matches the download pixel for pixel. PDF metadata carries
    the certificate number and verification URL so the file stays identifiable
    even when it is separated from the platform.
    """
    image = render_image(data, scale=scale)
    buf = io.BytesIO()
    image.save(
        buf, format='PDF', resolution=150.0 * scale,
        title=f"{data['title']} — {data['student_name']}",
        author=data['issuer'],
        subject=f"Certificate No. {data['number']}",
        keywords=f"certificate {data['number']} {data['verify_url']}",
    )
    return buf.getvalue()
