"""Signal handlers for the learning app.

Right now there is one job: keep each module offering's **chat group** in step
with who may actually open the module.

The receivers live here rather than in ``communication`` because the dependency
runs learning → communication (``ProgrammeModule.chat_group``,
``LessonBlock.meeting``), never the other way. Reconciling is idempotent and
cheap — it is a set difference against the group's auto memberships — so firing
it on every enrolment write is fine.

Trial *expiry* is the one thing a signal cannot see: nothing is saved when a
free week simply runs out. ``manage.py sync_module_chats`` closes that gap and
is safe to run on a schedule.
"""

import logging

from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch import receiver

from apps.learning.models import ProgrammeModule
from .models import ModuleEnrolment
logger = logging.getLogger('apps')


def _sync(offering, why):
    if offering is None:
        return
    try:
        from apps.communication.services import sync_module_chat_members
        sync_module_chat_members(offering)
    except Exception:  # pragma: no cover — chat must never break enrolment
        logger.exception('chat sync failed for %s (%s)', offering, why)


@receiver(post_save, sender=ProgrammeModule)
def ensure_module_chat_group(sender, instance, created, **kwargs):
    """A new offering gets its room straight away, with its teachers in it."""
    if created:
        _sync(instance, 'offering created')


@receiver(post_save, sender=ModuleEnrolment)
def sync_chat_on_enrolment(sender, instance, **kwargs):
    """Paying, starting a trial or being locked out all land here.

    ``activate()``, ``start_trial()`` and ``lock()`` each save the row, so one
    receiver covers the whole lifecycle: unlocking adds the student to the room,
    locking removes them again.
    """
    _sync(instance.programme_module, 'enrolment saved')


@receiver(post_delete, sender=ModuleEnrolment)
def sync_chat_on_unenrol(sender, instance, **kwargs):
    _sync(instance.programme_module, 'enrolment deleted')


@receiver(m2m_changed, sender=ProgrammeModule.educators.through)
def sync_chat_on_educator_change(sender, instance, action, reverse=False, pk_set=None, **kwargs):
    """Teachers are members of the room whether or not anyone has paid.

    The relation can be edited from either end — ``offering.educators.add(person)``
    in the admin, or ``person.taught_modules.add(offering)`` when a teacher is
    assigned from their own profile. On the reverse edit ``instance`` is the
    *Person* and the offerings are in ``pk_set``, so syncing ``instance`` blindly
    handed a Person to a function expecting an offering: the exception was caught
    and logged, and the teacher silently never appeared in the module's room.
    """
    if action not in ('post_add', 'post_remove', 'post_clear'):
        return
    if not reverse:
        _sync(instance, 'educators changed')
        return
    # post_clear on the reverse side reports no pk_set — the offerings are
    # already detached, so there is nothing left to look up and nothing to sync.
    for offering in ProgrammeModule.objects.filter(pk__in=pk_set or ()):
        _sync(offering, 'educators changed')
