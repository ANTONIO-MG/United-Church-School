"""WebSocket URL routing for the communication app.

Mounted by config/asgi.py. Two sockets today:

* ``ws/alerts/``            — one per signed-in user: live notification / message
                              events that drive the navbar bell + sounds.
* ``ws/chat/<group_id>/``   — one per open conversation: a "new message" poke so
                              the messenger refreshes instantly instead of on its
                              5-second timer.
* ``ws/lesson/<lesson_id>/``— one per lesson: live presence ("who is in this
                              lesson right now"), peer-announced roster.
"""

from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path('ws/alerts/', consumers.AlertConsumer.as_asgi()),
    path('ws/chat/<int:group_id>/', consumers.ChatConsumer.as_asgi()),
    path('ws/lesson/<int:lesson_id>/', consumers.LessonPresenceConsumer.as_asgi()),
]
