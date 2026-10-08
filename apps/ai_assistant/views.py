"""The admin Claude chat (the only surviving AI-assistant UI).

The CrewAI + Ollama assistant (inbox, uploads, AI Studio, AI Secretary) was
retired — live classes are now Microsoft Teams and recaps are generated from the
transcript. What remains here is the full-page, claude.ai-style chat for
admins/staff, backed by :mod:`apps.ai_assistant.admin_ai`.
"""

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from core.errors import note


def _is_admin_staff(user):
    if not (user and user.is_authenticated):
        return False
    person = getattr(user, 'profile', None)
    return bool(user.is_staff or user.is_superuser
                or (person and person.user_type in ('admin', 'staff')))


def _deny_non_admin(request):
    """Return a redirect response if the user isn't admin/staff, else None."""
    if not _is_admin_staff(request.user):
        note('AI-2001', request)
        messages.error(request, 'The AI assistant is available to admins and staff only.')
        return redirect('myhub:index')
    return None


def claude_chat(request):
    """Full-page, claude.ai-style chat UI for the admin AI assistant."""
    denied = _deny_non_admin(request)
    if denied:
        return denied
    from .admin_ai import is_enabled
    from .models import AdminAIThread

    threads = AdminAIThread.objects.filter(user=request.user)[:50]
    active = None
    public_id = request.GET.get('thread')
    if public_id:
        active = threads.filter(public_id=public_id).first()
    return render(request, 'ai_assistant/chat.html', {
        'page_title': 'AI Assistant',
        'threads': threads,
        'active_thread': active,
        'ai_enabled': is_enabled(),
    })


@require_POST
def claude_chat_send(request):
    """JSON endpoint: append a user message, get Claude's reply, record both."""
    import json

    denied = _deny_non_admin(request)
    if denied:
        return JsonResponse({'error': 'forbidden'}, status=403)

    from . import admin_ai
    from .models import AdminAIMessage, AdminAIThread

    try:
        data = json.loads(request.body or '{}')
    except ValueError:
        data = {}
    message = (data.get('message') or '').strip()
    if not message:
        return JsonResponse({'error': 'A message is required.'}, status=400)

    thread = None
    public_id = data.get('thread')
    if public_id:
        thread = AdminAIThread.objects.filter(user=request.user, public_id=public_id).first()
    if thread is None:
        thread = AdminAIThread.objects.create(user=request.user, title=message[:60])

    history = [{'role': m.role, 'content': m.content} for m in thread.messages.all()]
    AdminAIMessage.objects.create(thread=thread, role=AdminAIMessage.ROLE_USER, content=message)

    answer, usage = admin_ai.ask(history, message)
    AdminAIMessage.objects.create(
        thread=thread, role=AdminAIMessage.ROLE_ASSISTANT, content=answer,
        input_tokens=usage.get('input_tokens', 0), output_tokens=usage.get('output_tokens', 0),
        model=usage.get('model', ''))

    thread.total_input_tokens += usage.get('input_tokens', 0)
    thread.total_output_tokens += usage.get('output_tokens', 0)
    thread.save(update_fields=['total_input_tokens', 'total_output_tokens', 'updated_at'])

    return JsonResponse({
        'answer': answer,
        'thread': str(thread.public_id),
        'title': thread.title,
        'usage': usage,
        'thread_tokens': thread.total_tokens,
    })


def claude_chat_thread(request, public_id):
    """JSON: a thread's full message history (for loading a past conversation)."""
    denied = _deny_non_admin(request)
    if denied:
        return JsonResponse({'error': 'forbidden'}, status=403)
    from .models import AdminAIThread
    thread = get_object_or_404(AdminAIThread, user=request.user, public_id=public_id)
    return JsonResponse({
        'thread': str(thread.public_id),
        'title': thread.title,
        'messages': [{'role': m.role, 'content': m.content} for m in thread.messages.all()],
        'thread_tokens': thread.total_tokens,
    })
