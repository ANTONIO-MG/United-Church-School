"""Context processor for the (retired) CrewAI widget.

The CrewAI + Ollama assistant has been retired — replaced by the Microsoft Teams
live classroom and the Claude admin layer. This now reports the widget as
disabled and never imports CrewAI, so nothing heavy loads at request time. The
``AiReport`` / ``AiInsight`` / ``AssistantAction`` tables are kept (repurposed
for Teams recaps).
"""


def ai_assistant(request):
    pending = 0
    try:
        from .models import AssistantAction
        user = getattr(request, 'user', None)
        if user is not None and user.is_authenticated:
            qs = AssistantAction.objects.filter(status=AssistantAction.STATUS_PENDING)
            person = getattr(user, 'profile', None)
            is_admin_staff = (user.is_staff or user.is_superuser
                              or (person and person.user_type in ('admin', 'staff')))
            if not is_admin_staff:
                qs = qs.filter(created_by=user)
            pending = qs.count()
    except Exception:
        pending = 0
    return {'ai_assistant': {'enabled': False, 'crewai_installed': False,
                             'model': '', 'pending_actions': pending}}
