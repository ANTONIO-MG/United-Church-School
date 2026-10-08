"""Images for seeded content — generated locally, committed with the repo.

The seed scripts need pictures: a cover for every course and diagrams inside the
guide lessons. Rather than link to an image host (which breaks offline and rots
over time) these are **drawn here with Pillow** and written into ``media/``, so
they are part of the checkout and keep working with no network at all.

Two kinds of picture:

* :func:`course_cover` — a clean gradient card carrying the course title.
* :func:`wireframe` — a labelled diagram of a part of the interface, described
  declaratively (a sidebar, a header, some panels). These are *diagrams*, not
  screenshots: they show a learner where things sit on the page without
  pretending to be a photograph of the product.

Everything is deterministic: the same spec always produces the same file, so
re-running a seed does not churn the repository.
"""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path

from django.conf import settings

logger = logging.getLogger('apps')

try:
    from PIL import Image, ImageDraw, ImageFont
    HAVE_PIL = True
except Exception:  # pragma: no cover - Pillow is in requirements, but never crash a seed
    HAVE_PIL = False

# Brand palette — the same Soft-UI colours the interface uses.
INK = (52, 71, 103)
MUTED = (131, 146, 171)
LINE = (227, 230, 238)
PAPER = (255, 255, 255)
WASH = (248, 249, 254)
CYAN = (23, 193, 232)
GREEN = (45, 206, 137)
AMBER = (251, 140, 0)
INDIGO = (94, 114, 228)
RED = (245, 54, 92)

TONES = {'cyan': CYAN, 'green': GREEN, 'amber': AMBER, 'indigo': INDIGO, 'red': RED}


def _font(size, bold=False):
    """A real TrueType face when one is available, else Pillow's bitmap default."""
    candidates = [
        '/System/Library/Fonts/Supplemental/Arial Bold.ttf' if bold else '/System/Library/Fonts/Supplemental/Arial.ttf',
        '/System/Library/Fonts/Helvetica.ttc',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/Library/Fonts/Arial.ttf',
    ]
    for path in candidates:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    try:
        return ImageFont.load_default(size)
    except Exception:  # pragma: no cover - very old Pillow
        return ImageFont.load_default()


def _media_path(relative):
    target = Path(settings.MEDIA_ROOT) / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    return target


def _rounded(draw, box, radius, fill=None, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def _text(draw, xy, text, font, fill=INK, anchor=None):
    draw.text(xy, text, font=font, fill=fill, anchor=anchor)


def _wrap(draw, text, font, max_width):
    """Greedy word wrap to ``max_width`` pixels."""
    words, lines, line = text.split(), [], ''
    for word in words:
        trial = f'{line} {word}'.strip()
        if draw.textlength(trial, font=font) <= max_width or not line:
            line = trial
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


# ---------------------------------------------------------------------------
# Course cover
# ---------------------------------------------------------------------------
def course_cover(relative, title, subtitle='', tone='cyan', size=(1200, 600)):
    """Draw a gradient cover card for a course. Returns the media-relative path."""
    if not HAVE_PIL:
        return ''
    target = _media_path(relative)
    if target.exists():
        return relative

    width, height = size
    accent = TONES.get(tone, CYAN)
    image = Image.new('RGB', size, PAPER)
    draw = ImageDraw.Draw(image)

    # Diagonal wash from the accent colour into near-white.
    for y in range(height):
        t = y / height
        draw.line(
            [(0, y), (width, y)],
            fill=(int(accent[0] + (250 - accent[0]) * t),
                  int(accent[1] + (252 - accent[1]) * t),
                  int(accent[2] + (255 - accent[2]) * t)))

    # Soft circles for depth.
    overlay = Image.new('RGBA', size, (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)
    odraw.ellipse([width * 0.62, -height * 0.28, width * 1.15, height * 0.62], fill=(255, 255, 255, 38))
    odraw.ellipse([width * 0.52, height * 0.42, width * 0.98, height * 1.25], fill=(255, 255, 255, 26))
    image = Image.alpha_composite(image.convert('RGBA'), overlay).convert('RGB')
    draw = ImageDraw.Draw(image)

    title_font = _font(64, bold=True)
    sub_font = _font(30)
    lines = _wrap(draw, title, title_font, width * 0.62)
    y = height / 2 - (len(lines) * 74) / 2 - (24 if subtitle else 0)
    for line in lines:
        _text(draw, (72, y), line, title_font, fill=PAPER)
        y += 74
    if subtitle:
        for line in _wrap(draw, subtitle, sub_font, width * 0.58)[:2]:
            _text(draw, (72, y + 10), line, sub_font, fill=(255, 255, 255, 220))
            y += 38

    image.save(target, 'PNG', optimize=True)
    return relative


# ---------------------------------------------------------------------------
# Interface diagrams
# ---------------------------------------------------------------------------
def wireframe(relative, title, blocks, *, tone='cyan', size=(1100, 660)):
    """Draw a labelled diagram of part of the interface.

    ``blocks`` is a list of dicts describing rectangles in a 0–100 coordinate
    space, so a layout reads like the thing it depicts::

        [{'x': 0,  'y': 0,  'w': 18, 'h': 100, 'label': 'Menu', 'kind': 'nav'},
         {'x': 20, 'y': 0,  'w': 80, 'h': 12,  'label': 'Search', 'kind': 'bar'},
         {'x': 20, 'y': 15, 'w': 52, 'h': 85,  'label': 'The lesson', 'kind': 'panel'},
         {'x': 74, 'y': 15, 'w': 26, 'h': 85,  'label': 'Your notes', 'kind': 'accent'}]

    ``kind`` picks the styling: ``nav`` (dark), ``bar`` (wash), ``panel``
    (white card), ``accent`` (tinted), ``row`` (a list row).
    """
    if not HAVE_PIL:
        return ''
    target = _media_path(relative)
    if target.exists():
        return relative

    width, height = size
    accent = TONES.get(tone, CYAN)
    pad, header = 34, 76
    image = Image.new('RGB', size, WASH)
    draw = ImageDraw.Draw(image)

    # Caption strip along the top.
    title_font = _font(28, bold=True)
    _text(draw, (pad, 26), title, title_font, fill=INK)
    draw.line([(pad, header - 12), (width - pad, header - 12)], fill=LINE, width=2)

    stage = (pad, header, width - pad, height - pad)
    sw = stage[2] - stage[0]
    sh = stage[3] - stage[1]
    label_font = _font(19, bold=True)
    small_font = _font(15)

    for block in blocks:
        x0 = stage[0] + sw * block.get('x', 0) / 100
        y0 = stage[1] + sh * block.get('y', 0) / 100
        x1 = x0 + sw * block.get('w', 10) / 100
        y1 = y0 + sh * block.get('h', 10) / 100
        kind = block.get('kind', 'panel')

        if kind == 'nav':
            _rounded(draw, [x0, y0, x1, y1], 14, fill=INK)
            text_fill, sub_fill = PAPER, (196, 205, 222)
        elif kind == 'bar':
            _rounded(draw, [x0, y0, x1, y1], 12, fill=PAPER, outline=LINE, width=2)
            text_fill, sub_fill = MUTED, MUTED
        elif kind == 'accent':
            tint = tuple(int(c + (255 - c) * 0.86) for c in accent)
            _rounded(draw, [x0, y0, x1, y1], 14, fill=tint, outline=accent, width=2)
            text_fill, sub_fill = INK, MUTED
        elif kind == 'row':
            _rounded(draw, [x0, y0, x1, y1], 10, fill=PAPER, outline=LINE, width=2)
            draw.ellipse([x0 + 14, (y0 + y1) / 2 - 9, x0 + 32, (y0 + y1) / 2 + 9],
                         fill=tuple(int(c + (255 - c) * 0.75) for c in accent))
            text_fill, sub_fill = INK, MUTED
        else:  # panel
            _rounded(draw, [x0, y0, x1, y1], 14, fill=PAPER, outline=LINE, width=2)
            text_fill, sub_fill = INK, MUTED

        inset = 46 if kind == 'row' else 16
        label = block.get('label', '')
        note = block.get('note', '')

        # ``cells`` draws text at fixed x positions inside the block, so a table
        # row lines up as a table instead of collapsing into a sentence.
        cells = block.get('cells')
        if cells:
            cy = (y0 + y1) / 2 - 10
            for text, cx in cells:
                _text(draw, (x0 + inset + (x1 - x0 - inset) * cx / 100, cy),
                      str(text), label_font, fill=text_fill)
            continue

        if label:
            lines = _wrap(draw, label, label_font, (x1 - x0) - inset - 12)
            ty = y0 + 14 if not note and (y1 - y0) < 70 else y0 + 14
            if kind == 'row':
                ty = (y0 + y1) / 2 - 11
            for line in lines[:3]:
                _text(draw, (x0 + inset, ty), line, label_font, fill=text_fill)
                ty += 24
            if note:
                for line in _wrap(draw, note, small_font, (x1 - x0) - inset - 12)[:4]:
                    _text(draw, (x0 + inset, ty + 4), line, small_font, fill=sub_fill)
                    ty += 21

    image.save(target, 'PNG', optimize=True)
    return relative


def concept_card(relative, title, points, *, tone='indigo', kicker='', size=None):
    """A "key idea" card: a coloured band, a title, and the points that matter.

    Used inside seeded coursework so lessons carry a real picture rather than a
    wall of prose — and one that says something, unlike a stock photograph.
    """
    if not HAVE_PIL:
        return ''
    target = _media_path(relative)
    if target.exists():
        return relative

    # Height follows the content so the card is not mostly empty space.
    if size is None:
        size = (1100, 200 + (56 if kicker else 0) + len(points[:6]) * 62)
    width, height = size
    accent = TONES.get(tone, INDIGO)
    image = Image.new('RGB', size, PAPER)
    draw = ImageDraw.Draw(image)

    # Left band + a soft tint behind the whole card.
    draw.rectangle([0, 0, 18, height], fill=accent)
    tint = tuple(int(c + (255 - c) * 0.955) for c in accent)
    draw.rectangle([18, 0, width, height], fill=tint)

    x = 74
    y = 62
    if kicker:
        kfont = _font(20, bold=True)
        _text(draw, (x, y), kicker.upper(), kfont, fill=accent)
        y += 40

    tfont = _font(44, bold=True)
    for line in _wrap(draw, title, tfont, width - x - 70)[:3]:
        _text(draw, (x, y), line, tfont, fill=INK)
        y += 56

    y += 24
    pfont = _font(26)
    bullet = accent
    for point in points[:6]:
        draw.ellipse([x + 2, y + 11, x + 14, y + 23], fill=bullet)
        lines = _wrap(draw, point, pfont, width - x - 110)[:2]
        ly = y
        for line in lines:
            _text(draw, (x + 32, ly), line, pfont, fill=(58, 69, 96))
            ly += 34
        y = ly + 16

    image.save(target, 'PNG', optimize=True)
    return relative


def media_url(relative):
    """Public URL for a generated file, for use in a lesson block's ``data.url``."""
    if not relative:
        return ''
    return f"{settings.MEDIA_URL.rstrip('/')}/{relative.lstrip('/')}"


# ---------------------------------------------------------------------------
# Profile pictures supplied by the operator
# ---------------------------------------------------------------------------
# Avatars are displayed at most a couple of hundred pixels across, so there is
# no reason to commit multi-megabyte originals. Square-cropped and capped here.
AVATAR_PX = 512
AVATAR_QUALITY = 82


def profile_picture_pool(source_dir, dest='profile_pics/seed'):
    """Copy the supplied sample avatars into ``media/``, resized, and list them.

    Returns media-relative paths (already inside ``MEDIA_ROOT``) ready to be
    assigned to ``Person.profile_picture``. Copying rather than referencing the
    original folder means the pictures are committed with the repository, so the
    seeded users keep their faces on any checkout — and each is centre-cropped
    to a square and capped at :data:`AVATAR_PX`, which turns a 100 MB folder of
    camera originals into a couple of megabytes fit to commit.
    """
    source = Path(source_dir)
    if not source.is_dir():
        return []
    target_dir = Path(settings.MEDIA_ROOT) / dest
    target_dir.mkdir(parents=True, exist_ok=True)

    out = []
    names = sorted(
        (p for p in source.iterdir()
         if p.suffix.lower() in {'.jpg', '.jpeg', '.png', '.webp'} and not p.name.startswith('.')),
        # Numeric filenames first, in numeric order, so the assignment is stable.
        key=lambda p: (0, int(p.stem)) if p.stem.isdigit() else (1, p.stem.lower()),
    )
    for index, path in enumerate(names, start=1):
        out_name = f'avatar{index:02d}.jpg'
        destination = target_dir / out_name
        if not destination.exists():
            if not _write_avatar(path, destination):
                continue
        out.append(f'{dest}/{out_name}')
    return out


def _write_avatar(source, destination):
    """Centre-crop to a square, cap the size, save as JPEG. True on success."""
    if not HAVE_PIL:
        destination.write_bytes(source.read_bytes())
        return True
    try:
        with Image.open(source) as image:
            image = image.convert('RGB')
            width, height = image.size
            side = min(width, height)
            left = (width - side) // 2
            # Faces sit above centre far more often than below it, so bias the
            # crop upward rather than taking the exact middle.
            top = max(0, (height - side) // 3)
            image = image.crop((left, top, left + side, top + side))
            if side > AVATAR_PX:
                image = image.resize((AVATAR_PX, AVATAR_PX), Image.LANCZOS)
            image.save(destination, 'JPEG', quality=AVATAR_QUALITY, optimize=True)
        return True
    except Exception:  # pragma: no cover - a corrupt sample must not stop a seed
        logger.warning('seed_media: could not process avatar %s', source)
        return False


def stable_pick(pool, key):
    """Pick one item from ``pool`` for ``key``, the same way every run."""
    if not pool:
        return ''
    digest = hashlib.md5(str(key).encode('utf-8')).hexdigest()
    return pool[int(digest, 16) % len(pool)]
