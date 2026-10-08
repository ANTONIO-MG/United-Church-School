"""The one door onto a module material.

Every material — a study guide, a question pack, a solution workbook, a live
session link — is reached through :func:`material_open`, and that view asks both
gates before it hands anything over:

* :class:`apps.learning.access.Gate` — have they paid / bought / are they staff
* :class:`apps.learning.sequence.SequenceGate` — have they earned it yet

This exists because the alternative does not actually gate anything. A material
that carries a file used to be linked at its raw storage URL, which meant the
solution workbook for a mock was a plain link that could be opened directly,
bookmarked, or pasted into the cohort chat. The listing said "locked"; the file
did not care. Now the listing and the file are the same decision.

The response is deliberately a streamed :class:`~django.http.FileResponse`
rather than a redirect to storage: a redirect would hand out the very URL this
view exists to keep private.
"""

import logging
import mimetypes

from django.contrib import messages as flash
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

from . import models
from .access import Gate
from .sequence import SequenceGate

logger = logging.getLogger('apps')


def _week_scope(material):
    """The materials the sequence gate reasons over — this material's own week.

    A material that hangs off the phase rather than a week (a blueprint) has no
    week to be sequenced within, so it stands alone and the gate lets it through.
    """
    if material.week_id:
        return list(material.week.materials.all())
    return [material]


@login_required
def material_open(request, pk):
    """Open one material, if both gates allow it.

    Redirects to whatever the material points at (lesson, assessment, meeting,
    external URL) or streams its file. A refusal goes back to the module page
    carrying the reason, because the reason is the teaching — "submit your
    attempt to see the solution" is the whole product.
    """
    material = get_object_or_404(
        models.ModuleMaterial.objects.select_related(
            'phase__programme_module__programme__institution', 'week', 'lesson',
            'assessment', 'meeting', 'product'),
        pk=pk)
    offering = material.phase.programme_module

    person = getattr(request.user, 'profile', None)
    gate = Gate(request.user, offering, person=person)
    state = gate.for_material(material)

    back = reverse('learning:module-feed', args=[offering.pk])

    if not state.visible:
        # Unpublished, and this viewer is not an author. Saying "you may not see
        # this" would confirm it exists; a 404 is the honest answer.
        raise Http404('No such material.')

    if state.open:
        scope = _week_scope(material)
        sequence = SequenceGate(request.user, scope, bypass=gate.can_author)
        is_open, reason = sequence.check(material, scope)
        if not is_open:
            state.open, state.reason = False, reason

    if not state.open:
        flash.warning(request, f'{material.title} — {state.reason_label}.')
        return redirect(back)

    # --- Open. Send them where the material actually lives. ---
    if material.lesson_id:
        return redirect('learning:lesson-view', lesson_id=material.lesson_id)
    if material.assessment_id:
        return redirect('assessments:take', assessment_id=material.assessment_id)
    if material.meeting_id:
        return redirect(material.meeting.get_join_url())
    if material.file:
        return _stream(material)
    if material.url:
        return redirect(material.url)

    flash.info(request, f'{material.title} has nothing attached to it yet.')
    return redirect(back)


def _stream(material):
    """Stream the material's file without disclosing its storage URL."""
    name = material.file.name.rsplit('/', 1)[-1] or 'download'
    content_type = mimetypes.guess_type(name)[0] or 'application/octet-stream'
    try:
        handle = material.file.open('rb')
    except (FileNotFoundError, OSError, ValueError):
        logger.exception('material %s: file missing from storage', material.pk)
        raise Http404('That file is no longer available.')
    # inline: a PDF study guide should open in the browser, not land in Downloads.
    return FileResponse(handle, content_type=content_type, filename=name, as_attachment=False)
