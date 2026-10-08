"""Fixture helpers shared by the app test suites.

The academic spine needs three rows before a module offering can exist — an
institution, a programme under it, and a canonical module the offering points
at. Tests do not care about that chain; they care that they have *a module a
candidate can be registered for*. :func:`make_module` builds the chain once and
reuses it, so a test that needs two modules gets two offerings on one programme
rather than two parallel institutions.
"""

from django.utils.text import slugify

_COUNTER = {'n': 0}


def make_programme(institution_code='TESTINST', programme_code='TESTPROG', **extra):
    """A school + grade, created once per code pair and reused. ``extra`` sets
    Programme fields on creation (e.g. ``monthly_fee`` for a fee-paying grade);
    by default the grade charges nothing, so its subjects are open."""
    from apps.learning.models import Institution, Programme

    institution, _ = Institution.objects.get_or_create(
        code=institution_code, defaults={'name': f'{institution_code} Institution'})
    programme, _ = Programme.objects.get_or_create(
        institution=institution, code=programme_code,
        defaults={'name': f'{programme_code} Programme', **extra})
    return programme


def make_module(name='Test Module', code='', *, programme=None, price=0, **extra):
    """A :class:`learning.ProgrammeModule` a test can hang content off.

    ``name`` and ``code`` behave the way the old ``Subject`` fixture did, so a
    call site only has to swap the model name. Everything the spine needs
    underneath is created for you.
    """
    from apps.learning.models import Module, ProgrammeModule

    programme = programme or make_programme()
    if not code:
        _COUNTER['n'] += 1
        code = (slugify(name).upper().replace('-', '')[:12] or 'MOD') + str(_COUNTER['n'])

    canonical, _ = Module.objects.get_or_create(
        code=code, defaults={'name': name})
    offering, _ = ProgrammeModule.objects.get_or_create(
        programme=programme, code=code,
        defaults={'module': canonical, 'name': name,
                  'price_per_month': price, **extra})
    return offering


def enrol(person, offering, *, status=None, active=True):
    """Register ``person`` on ``offering`` — enrolment is a ModuleEnrolment row.

    Replaces the old ``subject.students.add(person)``: there is no membership
    M2M any more, because being on a module is an enrolment with a state. That
    state matters — registration alone leaves a module LOCKED, and the access
    middleware then redirects the candidate away from it. ``active=True``
    (the default) opens it, which is what ``students.add`` used to mean; pass
    ``active=False`` to test the paywall itself, or ``status=`` to pin an exact
    state. Also registers the programme, since a module is never held alone.
    """
    from apps.learning.models import ModuleEnrolment, ProgrammeEnrolment

    ProgrammeEnrolment.objects.get_or_create(
        person=person, programme=offering.programme, defaults={'is_active': True})
    enrolment, _ = ModuleEnrolment.objects.get_or_create(
        person=person, programme_module=offering,
        defaults={'price_at_enrolment': offering.price_per_month or 0})
    if status:
        enrolment.status = status
        enrolment.save(update_fields=['status', 'updated_at'])
    elif active:
        enrolment.activate(months=12)
    return enrolment
