from django.apps import AppConfig


class MsTeamsConfig(AppConfig):
    """Microsoft Teams live-classroom integration (via Microsoft Graph).

    Creates/manages Teams meetings from the LMS with app-only (client-credentials)
    auth, and pulls back transcript / recording / attendance after class. Stays
    dormant until ``MS_GRAPH_*`` is configured — see docs/TEAMS_INTEGRATION.md.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.msteams'
    label = 'msteams'
    verbose_name = 'Microsoft Teams'
