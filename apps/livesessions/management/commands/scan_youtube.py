"""Scan the configured YouTube channel and upsert its playlists + videos.

    python manage.py scan_youtube          # scan everything
    python manage.py scan_youtube --prune  # also hide videos gone from a playlist

Only raw metadata is written — a playlist's mapping (module/cohort/placement) and
a video's lesson attachment set by staff are never overwritten. New playlists
arrive unmapped and appear on the mapping screen for a human to place.

Reads via apps.livesessions.youtube (owner OAuth for unlisted, or a public API
key). Safe to run on a cron; it is idempotent.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.livesessions import models, youtube


class Command(BaseCommand):
    help = 'Scan the YouTube channel and import playlists + videos.'

    def add_arguments(self, parser):
        parser.add_argument('--prune', action='store_true',
                            help='Hide videos that are no longer in their playlist.')

    def handle(self, *args, **opts):
        if not youtube.can_scan():
            self.stderr.write(self.style.ERROR(
                'YouTube is not configured for reading. Set YOUTUBE_CLIENT_ID/SECRET/'
                'REFRESH_TOKEN (with youtube.readonly) or YOUTUBE_API_KEY, and '
                'YOUTUBE_CHANNEL_ID. See docs.'))
            return

        playlists = youtube.scan_channel()
        if not playlists:
            self.stdout.write(self.style.WARNING(
                'No playlists returned. Check the channel id / credentials / scopes.'))
            return

        now = timezone.now()
        n_pl = n_vid_new = n_vid_upd = 0
        for pl in playlists:
            obj, created = models.YouTubePlaylist.objects.update_or_create(
                youtube_id=pl['id'],
                defaults={
                    'title': pl.get('title', '')[:300],
                    'description': pl.get('description', ''),
                    'thumbnail_url': pl.get('thumbnail', '')[:500],
                    'item_count': pl.get('count', 0) or 0,
                    'last_scanned_at': now,
                },
            )
            n_pl += 1
            seen = []
            for v in pl.get('videos', []):
                seen.append(v['video_id'])
                published = v.get('published_at') or None
                _, v_created = models.YouTubeVideo.objects.update_or_create(
                    youtube_id=v['video_id'],
                    defaults={
                        'playlist': obj,
                        'title': v.get('title', '')[:300],
                        'description': v.get('description', ''),
                        'thumbnail_url': v.get('thumbnail', '')[:500],
                        'published_at': published,
                        'position': v.get('position', 0) or 0,
                    },
                )
                n_vid_new += int(v_created)
                n_vid_upd += int(not v_created)
            if opts.get('prune') and seen:
                gone = obj.videos.exclude(youtube_id__in=seen).update(is_hidden=True)
                if gone:
                    self.stdout.write(f'  · {obj.title}: hid {gone} removed video(s)')

        unmapped = models.YouTubePlaylist.objects.filter(
            is_active=True, programme_module__isnull=True).count()
        self.stdout.write(self.style.SUCCESS(
            f'Scanned {n_pl} playlist(s): {n_vid_new} new video(s), {n_vid_upd} updated. '
            f'{unmapped} playlist(s) still need mapping.'))
