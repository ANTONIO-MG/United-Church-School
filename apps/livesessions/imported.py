"""Querying imported YouTube videos for the surfaces that show them.

One place for "which videos belong here", used by My Programme, the module
Schedule, the past-sessions list and the lesson player. Everything filters on the
video's *playlist* mapping (module + cohort) and the placement flags a staff
member set — a video is never shown until its playlist has been mapped.
"""

from . import models

# surface name -> the playlist flag that gates it
SURFACE_FLAG = {
    'past_sessions': 'show_past_sessions',
    'my_programme': 'show_my_programme',
    'schedule': 'show_schedule',
}


def videos_for_module(module, cohort=None, surface=None):
    """Active, unhidden videos whose playlist maps to this module (and cohort, if
    given). ``surface`` further limits to playlists flagged for that placement.
    """
    if module is None:
        return models.YouTubeVideo.objects.none()
    qs = models.YouTubeVideo.objects.filter(
        is_hidden=False, playlist__is_active=True, playlist__programme_module=module)
    if cohort is not None:
        qs = qs.filter(playlist__cohort=cohort)
    if surface in SURFACE_FLAG:
        qs = qs.filter(**{f'playlist__{SURFACE_FLAG[surface]}': True})
    return qs.select_related('playlist').order_by('-published_at', 'position')


def videos_for_lesson(lesson):
    """Videos explicitly attached to a lesson (for the lesson player)."""
    if lesson is None:
        return models.YouTubeVideo.objects.none()
    return (models.YouTubeVideo.objects
            .filter(lesson=lesson, is_hidden=False, playlist__is_active=True)
            .select_related('playlist').order_by('position', '-published_at'))


def has_any_for_module(module, cohort=None, surface=None):
    return videos_for_module(module, cohort, surface).exists()


def videos_for_person(person, surface='past_sessions'):
    """Every imported video across the modules a person is enrolled on, for the
    given placement — the re-watch library. Module-level (all intakes)."""
    if person is None:
        return models.YouTubeVideo.objects.none()
    from apps.learning.models import ModuleEnrolment
    module_ids = list(ModuleEnrolment.objects.filter(person=person)
                      .values_list('programme_module_id', flat=True).distinct())
    if not module_ids:
        return models.YouTubeVideo.objects.none()
    qs = models.YouTubeVideo.objects.filter(
        is_hidden=False, playlist__is_active=True,
        playlist__programme_module_id__in=module_ids)
    if surface in SURFACE_FLAG:
        qs = qs.filter(**{f'playlist__{SURFACE_FLAG[surface]}': True})
    return qs.select_related('playlist', 'playlist__programme_module').order_by('-published_at')
