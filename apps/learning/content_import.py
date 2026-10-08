"""The staff screen for getting a topic's content into a module.

Two doors, one importer — the same shape the whole pipeline is built on:

* **Paste or upload JSON.** A ``thrive-pack`` written by hand (or exported from a
  previous draft). Validated and imported. No model, no cost, repeatable.
* **Upload the documents.** The guide, the question paper and the solution
  workbook. Text is extracted locally, Claude shapes it into *the same JSON*, and
  that JSON is shown for review **before** anything is imported.

The second door never reaches the database on its own. It produces JSON in a
textarea; importing it is a second, deliberate click on the first door. That is
the whole safety argument: a human sees the figures before they become a paper.

Admin and staff only, enforced here rather than by hiding a menu item.
"""

import json
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render
from django.urls import reverse

from core import content_pack
from core.roles import role_flags

from . import models

logger = logging.getLogger('apps')

#: Belt and braces beside ``extract.MAX_BYTES`` — refuse an implausible upload
#: before it is read into memory at all.
MAX_UPLOAD_BYTES = 40 * 1024 * 1024
MAX_FILES = 12


def _guard(request):
    """Importing content is an administrative act, not a teaching one.

    Educators author in the builder, where what they write is scoped to what
    they teach. A pack names its own module and programme, so importing one is
    the power to write into *any* module — which is admin and staff only.
    """
    return role_flags(request)['is_admin_staff']


@login_required
def content_import(request):
    """Import a content pack — by JSON, or by drafting one from documents."""
    if not _guard(request):
        return HttpResponseForbidden('Content packs are imported by administrators.')

    context = {
        'page_title': 'Import content',
        'ai_enabled': content_pack.drafting.is_enabled(),
        'offerings': (models.ProgrammeModule.objects.filter(is_active=True)
                      .select_related('programme__institution')
                      .order_by('programme__institution__code', 'programme__code', 'code')),
        'pack_json': '',
        'problems': [],
        'form': {},
    }

    if request.method != 'POST':
        return render(request, 'learning/content_import.html', context)

    action = request.POST.get('action')
    context['form'] = request.POST.dict()

    if action == 'draft':
        return _draft_from_documents(request, context)
    if action == 'validate':
        return _validate_only(request, context)
    if action == 'import':
        return _import_json(request, context)

    messages.error(request, 'Unknown action.')
    return render(request, 'learning/content_import.html', context)


# ---------------------------------------------------------------------------
# Door 1 — JSON in
# ---------------------------------------------------------------------------
def _read_pack(request, context):
    """The pack from the textarea or the uploaded ``.json``. ``None`` on error."""
    raw = (request.POST.get('pack_json') or '').strip()
    upload = request.FILES.get('pack_file')
    if upload and not raw:
        raw = upload.read().decode('utf-8', errors='replace')
    if not raw:
        messages.error(request, 'Paste a pack, or choose a .json file.')
        return None

    context['pack_json'] = raw
    try:
        pack = json.loads(raw)
    except json.JSONDecodeError as exc:
        context['problems'] = [f'Not valid JSON — {exc}']
        return None
    return pack


def _validate_only(request, context):
    pack = _read_pack(request, context)
    if pack is None:
        return render(request, 'learning/content_import.html', context)
    problems = content_pack.validate(pack)
    context['problems'] = problems
    if problems:
        messages.warning(request, f'{len(problems)} problem(s) — nothing was imported.')
    else:
        messages.success(request, 'This pack is valid. Import it when you are ready.')
    return render(request, 'learning/content_import.html', context)


def _import_json(request, context):
    pack = _read_pack(request, context)
    if pack is None:
        return render(request, 'learning/content_import.html', context)

    problems = content_pack.validate(pack)
    if problems:
        context['problems'] = problems
        messages.error(request, f'{len(problems)} problem(s) — nothing was imported.')
        return render(request, 'learning/content_import.html', context)

    try:
        result = content_pack.import_pack(pack, actor=request.user, validate=False)
    except content_pack.PackImportError as exc:
        context['problems'] = [str(exc)]
        messages.error(request, 'Nothing was imported.')
        return render(request, 'learning/content_import.html', context)

    messages.success(request, f'Imported into {result.topic} — {result}. '
                              f'Everything is in draft; publish it on the schedule.')
    for warning in result.warnings:
        messages.warning(request, warning)

    offering = result.topic.programme_module
    return redirect(reverse('learning:module-build', args=[offering.pk]))


# ---------------------------------------------------------------------------
# Door 2 — documents in, JSON out (never straight to the database)
# ---------------------------------------------------------------------------
def _draft_from_documents(request, context):
    offering = models.ProgrammeModule.objects.filter(
        pk=request.POST.get('offering') or 0).select_related('programme__institution').first()
    topic_code = (request.POST.get('topic_code') or '').strip()
    topic_title = (request.POST.get('topic_title') or '').strip()

    if offering is None or not topic_code or not topic_title:
        messages.error(request, 'Choose the subject and name the topic before drafting.')
        return render(request, 'learning/content_import.html', context)

    uploads = request.FILES.getlist('documents')[:MAX_FILES]
    if not uploads:
        messages.error(request, 'Choose the documents to read.')
        return render(request, 'learning/content_import.html', context)
    if sum(f.size for f in uploads) > MAX_UPLOAD_BYTES:
        messages.error(request, 'Those documents are too large together (max 40 MB).')
        return render(request, 'learning/content_import.html', context)

    text, metas, errors = content_pack.extract_many(
        [(f.read(), f.name) for f in uploads])
    for error in errors:
        messages.warning(request, error)
    if not text:
        messages.error(request, 'Nothing could be read from those files.')
        return render(request, 'learning/content_import.html', context)

    context['extracted'] = metas
    programme_code = f'{offering.programme.institution.code}-{offering.programme.code}'
    try:
        pack, problems = content_pack.draft_pack(
            text, module=offering.code, programme=programme_code,
            topic_code=topic_code, topic_title=topic_title,
            cohort=(request.POST.get('cohort') or '').strip(),
            week=_int(request.POST.get('week')),
            note=request.POST.get('note') or '')
    except content_pack.DraftingError as exc:
        messages.error(request, str(exc))
        return render(request, 'learning/content_import.html', context)

    context['pack_json'] = content_pack.as_json(pack)
    context['problems'] = problems
    context['drafted'] = True
    if problems:
        messages.warning(
            request,
            f'Drafted with {len(problems)} problem(s) to fix. Read it against the '
            f'source, correct it below, then import. Nothing has been imported.')
    else:
        messages.success(
            request,
            'Drafted and valid. Read it against the source before importing — '
            'the figures are the part worth checking.')
    return render(request, 'learning/content_import.html', context)


def _int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
