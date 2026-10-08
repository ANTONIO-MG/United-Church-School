"""Context processor exposing the current user's profile + community stats to
every template (drives the Social sidebar profile card and navbar avatar).

The three numbers under the sidebar avatar are the ones a candidate should be
able to answer at a glance: **how many modules** they are carrying, **how much of
the year's tests and exams** they have worked through, and **how ready** they
look for the next one. (They used to be Groups / Tasks / Messages, which were a
count of a concept the platform no longer has and two numbers already shown as
badges three rows below.)

Guarded so a missing table (e.g. before ``migrate``) or any DB error never
takes down every page that renders through this context processor.
"""

from . import models
from core.request_cache import cached_per_request


def _build_account_stats(request):
    user = getattr(request, 'user', None)
    if user is None or not user.is_authenticated:
        return {'account_stats': {}}

    try:
        profile = getattr(user, 'profile', None)

        name = ''
        title = 'Member'
        avatar_url = ''

        if profile is not None:
            name = f'{profile.first_name} {profile.last_name}'.strip()
            try:
                title = profile.get_user_type_display()
            except Exception:
                title = 'Member'
            avatar_url = profile.avatar_url     # their picture, or the right default

        if not name:
            name = user.get_full_name() or user.get_username()

        return {
            'account_stats': dict(
                {'profile': {'name': name, 'title': title, 'avatar_url': avatar_url}},
                **_study_tiles(user, profile))
        }
    except Exception:
        return {'account_stats': {}}


def _study_tiles(user, person):
    """The three sidebar numbers: modules, tests-and-exams completion, readiness.

    Its own ``try`` so a schedule that has not been built yet costs the tiles
    their values, not the whole profile card.
    """
    blank = {'module_count': 0, 'completion_pct': 0, 'readiness': None}
    if person is None:
        return blank
    try:
        from apps.learning import progress
        rows = progress.phase_rows(user, person)
        return {
            'module_count': progress.module_count(person),
            'completion_pct': progress.overall_completion(user, person, rows=rows),
            'readiness': progress.readiness(user, person, rows=rows),
        }
    except Exception:
        return blank


def account_stats(request):
    """Cached for the life of the request — these are nav badges, and this
    processor runs once per template rendered in a response, not once per
    response."""
    return cached_per_request(request, 'account_stats', lambda: _build_account_stats(request))
