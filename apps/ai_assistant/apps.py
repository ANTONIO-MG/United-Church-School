from django.apps import AppConfig


class AiAssistantConfig(AppConfig):
    """App config for the AI assistant."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.ai_assistant'
    label = 'ai_assistant'
    verbose_name = 'AI Assistant'
