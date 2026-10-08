"""Routes for the admin Claude chat (mounted at ``/assistant/`` under the
``assistant`` namespace). The CrewAI inbox / AI Studio / AI Secretary were
retired; only the admin chat remains."""

from django.urls import path

from . import views

app_name = 'assistant'

urlpatterns = [
    # Advanced "Claude-style" chat (admin / staff only)
    path('chat/', views.claude_chat, name='chat'),
    path('chat/send/', views.claude_chat_send, name='chat-send'),
    path('chat/threads/<uuid:public_id>/', views.claude_chat_thread, name='chat-thread'),
]
