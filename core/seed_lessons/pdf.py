"""Printable PDF worksheets for the seeded lessons (reportlab, no Django needed).

One worksheet per lesson day: the school name, grade, subject, day and date, a
name/date line, the instructions, numbered exercises with answer space, and the
day's homework. Uses reportlab's built-in Helvetica so generation needs no font
files and stays fast (a few milliseconds a sheet).
"""
from html import unescape
from io import BytesIO
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)

NAVY = colors.HexColor('#00498B')
SCHOOL_NAME = 'United Church School'

# Built-in Type 1 fonts only cover WinAnsi (≈ Latin-1 plus curly quotes and
# dashes). Anything else is spelled out so it never prints as a black box.
_REPLACE = {
    '→': '->', '←': '<-', '↔': '<->', '⇒': '=>', '≤': '<=', '≥': '>=', '≠': '!=',
    '≈': '~', '√': 'sqrt', 'π': 'pi', '∞': 'infinity', '−': '-', '∑': 'sum', 'Δ': 'delta',
    'θ': 'theta', 'α': 'alpha', 'β': 'beta', 'λ': 'lambda', 'μ': 'micro', 'Ω': 'ohm',
    '✓': 'v', '✔': 'v', '✗': 'x', '★': '*', '☆': '*', '●': '*', '○': 'o', '■': '#', '□': '[ ]',
    '₀': '0', '₁': '1', '₂': '2', '₃': '3', '₄': '4', '₅': '5', '₆': '6', '₇': '7', '₈': '8',
    '₉': '9', '⁻': '-', '⁰': '^0', '⁴': '^4', '⁵': '^5', '⁶': '^6', '⁷': '^7', '⁸': '^8',
    '⁹': '^9', 'ⁿ': '^n', '​': '',
}


def clean(text):
    """``text`` made safe for a reportlab Paragraph in a built-in font."""
    text = unescape(str(text or ''))
    for bad, good in _REPLACE.items():
        text = text.replace(bad, good)
    out = []
    for ch in text:
        try:
            ch.encode('cp1252')
            out.append(ch)
        except UnicodeEncodeError:
            out.append('?')
    text = ''.join(out)
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def strip_html(html):
    """Plain text from a little HTML (for homework instructions)."""
    text = re.sub(r'<\s*br\s*/?>', '\n', html or '')
    text = re.sub(r'</(p|li|h\d)>', '\n', text)
    text = re.sub(r'<[^>]+>', '', text)
    return unescape(re.sub(r'\n{2,}', '\n', text).strip())


def _styles(grade):
    base = getSampleStyleSheet()
    body_size = 14 if grade <= 3 else (12 if grade <= 6 else 10.5)
    return {
        'school': ParagraphStyle('school', parent=base['Normal'], fontName='Helvetica-Bold',
                                 fontSize=10, textColor=NAVY, leading=12),
        'title': ParagraphStyle('title', parent=base['Title'], fontName='Helvetica-Bold',
                                fontSize=17 if grade <= 3 else 15, leading=20,
                                alignment=TA_LEFT, textColor=colors.black, spaceAfter=2),
        'meta': ParagraphStyle('meta', parent=base['Normal'], fontSize=9,
                               textColor=colors.HexColor('#555555'), leading=11),
        'h': ParagraphStyle('h', parent=base['Heading3'], fontName='Helvetica-Bold',
                            fontSize=body_size + 1, textColor=NAVY, spaceBefore=8, spaceAfter=4),
        'body': ParagraphStyle('body', parent=base['Normal'], fontSize=body_size,
                               leading=body_size * 1.35),
        'small': ParagraphStyle('small', parent=base['Normal'], fontSize=8,
                                textColor=colors.HexColor('#777777'), leading=10),
    }


def _ruled(rows, width, height):
    """``rows`` full-width ruled answer lines."""
    table = Table([['']] * rows, colWidths=[width], rowHeights=[height] * rows, hAlign='LEFT')
    table.setStyle(TableStyle([('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.HexColor('#9AA5B1'))]))
    return table


def worksheet_pdf(*, grade, subject, day_number, day, topic, date_label=''):
    """The worksheet for one lesson day, as PDF bytes."""
    st = _styles(grade)
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
        topMargin=15 * mm, bottomMargin=15 * mm,
        title=f'Grade {grade} {subject} - Day {day_number} worksheet',
        author=SCHOOL_NAME, subject=topic)

    story = [
        Paragraph(clean(f'{SCHOOL_NAME}  |  Grade {grade}  |  {subject}'), st['school']),
        Spacer(1, 3),
        Paragraph(clean(f'Day {day_number} worksheet: {day["title"]}'), st['title']),
        Paragraph(clean(f'Term 1, Week 1{(" - " + date_label) if date_label else ""}  |  '
                        f'Topic: {topic}'), st['meta']),
        Spacer(1, 8),
    ]
    name_line = Table(
        [['Name: ______________________________', 'Date: ________________']],
        colWidths=[110 * mm, 64 * mm], hAlign='LEFT')
    name_line.setStyle(TableStyle([('FONTSIZE', (0, 0), (-1, -1), 10),
                                   ('LEFTPADDING', (0, 0), (-1, -1), 0)]))
    story += [name_line, Spacer(1, 6)]

    sheet = day.get('worksheet') or {}
    story.append(Paragraph('Instructions', st['h']))
    story.append(Paragraph(clean(sheet.get('instructions', '')), st['body']))

    story.append(Paragraph('Exercises', st['h']))
    gap = 10 if grade <= 3 else 6
    rows = 2 if grade <= 3 else 1
    width = A4[0] - 36 * mm
    for index, line in enumerate(sheet.get('exercises') or [], 1):
        text = re.sub(r'^\s*\d+[\.\)]\s*', '', str(line))   # we number them ourselves
        story.append(KeepTogether([
            Paragraph(clean(f'{index}. {text}'), st['body']),
            _ruled(rows, width, 11 * mm if grade <= 3 else 8 * mm),
            Spacer(1, gap),
        ]))

    homework = day.get('homework') or {}
    if homework:
        story.append(Paragraph(clean(f'Homework: {homework.get("title", "")}'), st['h']))
        story.append(Paragraph(clean(strip_html(homework.get('instructions', ''))), st['body']))
        for index, task in enumerate(homework.get('tasks') or [], 1):
            story.append(Paragraph(clean(f'{index}. {strip_html(task)}'), st['body']))

    story += [Spacer(1, 10),
              Paragraph(clean('Use this sheet alongside the lesson on the learning platform. '
                              'Content follows the CAPS curriculum for this grade and subject.'),
                        st['small'])]
    doc.build(story)
    return buf.getvalue()
