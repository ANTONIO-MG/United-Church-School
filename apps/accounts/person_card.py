"""The person card — who someone is, at a glance, with nothing private on it.

Clicking a name anywhere on the platform opens this as a small pop-up (the
``?fragment=1`` form, loaded by static/js/person-card.js); opened directly it is
a page of its own. It shows a picture, the name, the role, where they study or
teach, and the modules the viewer shares with them. Never an e-mail address,
phone number, date of birth, funding, guardians or grades — those belong to the
full profile, whose own visibility rules decide who sees them.

The owner's ``profile_visibility`` is honoured here too, but softly: a private
member's card still shows their name, picture and role (enough to know who
wrote a message), just nothing else.
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.urls import NoReverseMatch, reverse

from core.roles import role_of_user

from . import models


def _modules_of(person):
    """``(taught, enrolled)`` module offerings, by name."""
    taught = list(person.taught_modules.filter(is_active=True)
                  .select_related('programme__institution').order_by('code'))
    enrolled = []
    try:
        from apps.learning.models import ProgrammeModule
        enrolled = list(ProgrammeModule.objects.filter(enrolments__person=person, is_active=True)
                        .select_related('programme__institution').distinct().order_by('code'))
    except Exception:   # pragma: no cover
        pass
    return taught, enrolled


def _programmes_of(person):
    try:
        return [e.programme for e in person.programme_enrolments.select_related('programme__institution')
                if e.programme_id]
    except Exception:   # pragma: no cover
        return []


def card_context(request, person):
    from .views import _person_for, _shares_group

    viewer = _person_for(request.user)
    is_self = person.user_id == request.user.id
    viewer_role = role_of_user(request.user)
    is_team = viewer_role in ('admin', 'staff')

    limited = False
    if not is_self and not is_team and person.user_id:
        vis = models.UserSettings.for_user(person.user).profile_visibility
        if vis == models.UserSettings.VISIBILITY_PRIVATE:
            limited = True
        elif vis == models.UserSettings.VISIBILITY_MEMBERS and not _shares_group(viewer, person):
            limited = True

    ctx = {'person': person, 'is_self': is_self, 'limited': limited, 'is_team': is_team,
           'role_label': person.get_user_type_display()}
    if limited:
        return ctx

    taught, enrolled = _modules_of(person)
    mine = set()
    if viewer is not None and not is_self:
        t, e = _modules_of(viewer)
        mine = {m.pk for m in t + e}
    ctx.update(
        taught=taught[:8],
        programmes=_programmes_of(person)[:3],
        shared=[m for m in enrolled if m.pk in mine][:8],
        enrolled_count=len(enrolled),
        joined=getattr(person.user, 'date_joined', None),
    )
    links = {}
    try:
        links['profile'] = reverse('accounts:profile', args=[person.pk])
        if person.user_id and not is_self:
            links['message'] = reverse('communication:chat-direct', args=[person.user_id])
        if is_team and person.user_type == 'student':
            links['student360'] = reverse('staffdesk:student', args=[person.pk])
    except NoReverseMatch:  # pragma: no cover
        pass
    ctx['links'] = links
    return ctx


@login_required
def person_card(request, pk):
    person = get_object_or_404(models.Person.objects.select_related('user'), pk=pk)
    ctx = card_context(request, person)
    if request.GET.get('fragment'):
        return render(request, 'accounts/_person_card.html', ctx)
    ctx['page_title'] = str(person)
    return render(request, 'accounts/person-card.html', ctx)


@login_required
def person_card_for_user(request, user_id):
    """The same card, addressed by login id (what chat and notifications hold)."""
    person = get_object_or_404(models.Person.objects.select_related('user'), user_id=user_id)
    return person_card(request, person.pk)
