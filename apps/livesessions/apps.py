from django.apps import AppConfig


class LiveSessionsConfig(AppConfig):
    """The live-session layer: calendar, audience, reminders and the after-class pipeline.

    :mod:`apps.msteams` owns the conversation with Microsoft Graph. This app owns
    everything the platform does around it — who a session is for, who sees it on
    the school calendar, when they are reminded, and the chain that turns a
    finished meeting into a filed recording, a transcript, a summary and a
    playable past session. See docs/LIVE_SESSIONS.md.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.livesessions'
    label = 'livesessions'
    verbose_name = 'Live sessions'
