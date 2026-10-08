"""Enrolment overrides for admin/staff — **Programme → Modules**.

Registration itself does not live here: a candidate picks a programme and its
modules in :mod:`apps.accounts.views`, and
:mod:`apps.learning.enrolment` writes the ``ProgrammeEnrolment`` /
``ModuleEnrolment`` rows and raises the invoice. What is left in this module is
the admin's hand: putting a person into (or out of) specific modules, and
attaching an educator to a programme's teaching roster.

This used to be the ``Course → Subject`` layer of the old MyHub codebase, where
a student belonged to one course and was auto-added to all of its subjects.
The school enrols by grade and bills by grade, so that layer is gone.
"""

from apps.learning.models import ProgrammeModule


def modules_for_programme(programme):
    """Active module offerings under ``programme``."""
    if programme is None:
        return ProgrammeModule.objects.none()
    return ProgrammeModule.objects.filter(
        programme=programme, is_active=True).order_by('order', 'name')


def enrol_educator(person, programme):
    """Add ``person`` to the teaching roster of every active module offering of
    ``programme``. Chat-group membership follows via the ProgrammeModule
    signals. Returns the offerings they now teach."""
    offerings = list(modules_for_programme(programme))
    for offering in offerings:
        offering.educators.add(person)
    return offerings


def set_module_membership(person, *, add_ids=None, remove_ids=None):
    """Admin/staff override: enrol ``person`` into specific module offerings, or
    drop them. Added modules start locked, exactly as registration leaves them —
    it is an enrolment, not a free pass; use ``ModuleEnrolment.activate`` (or a
    settled invoice) to open one.

    Returns the ``ModuleEnrolment`` rows the person now holds for the modules
    that were added.
    """
    if person is None:
        return []

    from apps.learning.models import ModuleEnrolment, ProgrammeEnrolment

    added = []
    for offering in ProgrammeModule.objects.filter(
            pk__in=list(add_ids or [])).select_related('programme'):
        ProgrammeEnrolment.objects.get_or_create(
            person=person, programme=offering.programme, defaults={'is_active': True})
        enrolment, _ = ModuleEnrolment.objects.get_or_create(
            person=person, programme_module=offering,
            defaults={'price_at_enrolment': offering.price_per_month or 0})
        added.append(enrolment)

    if remove_ids:
        ModuleEnrolment.objects.filter(
            person=person, programme_module_id__in=list(remove_ids)).delete()

    return added
