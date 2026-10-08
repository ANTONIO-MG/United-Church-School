"""Who a session is for — the single answer used by notifications *and* the calendar.

There are two questions here and they must never be allowed to drift apart:

1. **Who gets told?** (:func:`recipients_for`) — invite e-mails, the platform
   notification, and the 24-hour / 30-minute reminders.
2. **Who sees it on the calendar?** (:func:`visible_sessions`) — the queryset the
   calendar page renders.

If (2) were ever wider than (1) a student would find a session on their calendar
that nobody had invited them to; if it were narrower they would be reminded about
something they cannot open. So both are derived from the same
``MeetingRoom.audience`` field by the helpers below, and neither is computed
anywhere else in the codebase.

**The one deliberate asymmetry** is supervisory. Admin and staff can *see* every
session at every institution — that is what makes the calendar usable for finding
a free slot — but they are not *told* about every session, because a platform
with forty classes a week would drown them. Educators are the same for the
modules they teach. So the invariant is stated precisely as:

* anyone who is notified can see it, always; and
* anyone who can see it was notified, **unless** they are seeing it through the
  supervisory widening (admin/staff, or an educator's own modules).

Being told is therefore always a subset of being able to see, never the reverse
— which is the direction that would actually hurt somebody.
"""

import logging

from django.contrib.auth import get_user_model
from django.db.models import Q

from core.roles import role_of_user

logger = logging.getLogger('apps')


# ---------------------------------------------------------------------------
# Notification audience
# ---------------------------------------------------------------------------
def recipients_for(meeting, *, include_host=True):
    """Every :class:`User` who should be told about ``meeting``.

    Returns a ``User`` queryset, de-duplicated and limited to active accounts
    that can actually be reached. Named invitees are always included, whatever
    the audience — inviting a specific person to a module class is a normal
    thing to do and must not be silently dropped.
    """
    User = get_user_model()
    from apps.communication.models import MeetingRoom

    invited = Q(meeting_invites__meeting=meeting)

    if meeting.audience == MeetingRoom.AUDIENCE_EVERYONE:
        scope = Q(is_active=True)
    elif meeting.audience == MeetingRoom.AUDIENCE_INSTITUTION and meeting.institution_id:
        scope = Q(profile__programme_enrolments__programme__institution=meeting.institution) | \
                Q(profile__taught_modules__programme__institution=meeting.institution)
    elif meeting.audience == MeetingRoom.AUDIENCE_PROGRAMME and meeting.programme_id:
        scope = Q(profile__programme_enrolments__programme=meeting.programme) | \
                Q(profile__taught_modules__programme=meeting.programme)
    elif meeting.audience == MeetingRoom.AUDIENCE_COHORT and meeting.cohort_id:
        scope = Q(profile__programme_enrolments__cohort=meeting.cohort)
    elif meeting.audience == MeetingRoom.AUDIENCE_MODULE and meeting.module_id:
        scope = Q(profile__module_enrolments__programme_module=meeting.module) | \
                Q(profile__taught_modules=meeting.module)
    else:
        # AUDIENCE_PRIVATE, or a derived audience whose scope object was cleared
        # (an institution deleted, say). Falling back to "invitees only" is the
        # safe direction to fail in: nobody is told about a session they were
        # never named on.
        scope = Q(pk__in=[])

    people = User.objects.filter(Q(is_active=True) & (scope | invited)).distinct()
    if include_host and meeting.host_id:
        people = User.objects.filter(Q(pk__in=people.values('pk')) | Q(pk=meeting.host_id)).distinct()
    elif meeting.host_id:
        people = people.exclude(pk=meeting.host_id)
    return people


def student_recipients_for(meeting):
    """:func:`recipients_for` narrowed to students — used for attendance rollups."""
    return recipients_for(meeting, include_host=False).filter(
        Q(profile__user_type='student') | Q(profile__isnull=True))


# ---------------------------------------------------------------------------
# Calendar visibility
# ---------------------------------------------------------------------------
def sees_whole_calendar(user):
    """Admin and staff see every session at every institution.

    That is the point of the school calendar: it is where you look to find out
    what is already booked before you book something else. Note that this is
    visibility only — see the module docstring on why it does not also make them
    a recipient of every session's notifications.
    """
    return role_of_user(user) in ('admin', 'staff')


def is_supervisory_viewer(user, meeting):
    """True when ``user`` can see ``meeting`` only because of their role.

    In other words: they are not in the session's audience and were not invited,
    but their job lets them look. Exists so the invariant in the module docstring
    can be asserted precisely rather than approximately.
    """
    if not can_view(user, meeting):
        return False
    return not recipients_for(meeting).filter(pk=user.pk).exists()


def visible_sessions(user, queryset=None):
    """The sessions ``user`` may see on the calendar.

    * admin / staff — everything.
    * educator — everything on a module they teach, everything they host, and
      anything they were personally invited to.
    * student / parent — sessions whose audience covers them, plus personal
      invitations (which is how a one-on-one appears).
    * anonymous — nothing.
    """
    from apps.communication.models import MeetingRoom

    queryset = MeetingRoom.objects.all() if queryset is None else queryset
    queryset = queryset.filter(is_active=True)

    if user is None or not getattr(user, 'is_authenticated', False):
        return queryset.none()
    if sees_whole_calendar(user):
        return queryset

    person = getattr(user, 'profile', None)
    mine = Q(host=user) | Q(participants__user=user)

    if person is None:
        return queryset.filter(mine).distinct()

    if role_of_user(user) == 'educator':
        taught = Q(module__in=person.taught_modules.all()) | \
                 Q(programme__in=person.taught_modules.values('programme')) | \
                 Q(audience=MeetingRoom.AUDIENCE_EVERYONE)
        return queryset.filter(mine | taught).distinct()

    if role_of_user(user) == 'parent':
        # A parent sees exactly what their linked children see, which keeps the
        # calendar consistent with every other page ParentAccessMiddleware gates.
        from core.scoping import children_of
        children = list(children_of(user))
        if not children:
            return queryset.filter(mine).distinct()
        scope = Q(pk__in=[])
        for child in children:
            child_user = getattr(child, 'user', None)
            if child_user is not None:
                scope |= Q(pk__in=visible_sessions(child_user, queryset).values('pk'))
        return queryset.filter(mine | scope).distinct()

    # --- Student ---
    enrolled_programmes = person.programme_enrolments.values('programme')
    enrolled_cohorts = person.programme_enrolments.values('cohort')
    enrolled_modules = person.module_enrolments.values('programme_module')

    scope = (
        Q(audience=MeetingRoom.AUDIENCE_EVERYONE)
        | Q(audience=MeetingRoom.AUDIENCE_INSTITUTION,
            institution__programmes__in=enrolled_programmes)
        | Q(audience=MeetingRoom.AUDIENCE_PROGRAMME, programme__in=enrolled_programmes)
        | Q(audience=MeetingRoom.AUDIENCE_COHORT, cohort__in=enrolled_cohorts)
        | Q(audience=MeetingRoom.AUDIENCE_MODULE, module__in=enrolled_modules)
    )
    return queryset.filter(mine | scope).distinct()


def can_view(user, meeting):
    """True when ``user`` may open ``meeting``'s page."""
    from apps.communication.models import MeetingRoom
    return visible_sessions(user, MeetingRoom.objects.filter(pk=meeting.pk)).exists()


def can_manage(user, meeting=None):
    """True when ``user`` may create, edit or cancel sessions.

    Admin and staff always may. An educator may manage a session they host or
    one on a module they teach — but not another educator's class.
    """
    role = role_of_user(user)
    if role in ('admin', 'staff'):
        return True
    if role != 'educator':
        return False
    if meeting is None:
        return True                     # may create; the form limits the scope
    if meeting.host_id == user.pk:
        return True
    person = getattr(user, 'profile', None)
    if person is None or not meeting.module_id:
        return False
    return person.taught_modules.filter(pk=meeting.module_id).exists()
