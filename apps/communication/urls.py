"""HTML routes for the communication app (mounted at ``/communication/`` under
the ``communication`` namespace)."""

from django.urls import path

from . import support, views, whatsapp_views

app_name = 'communication'

urlpatterns = [
    # Support / help centre (all users, role-scoped content)
    path('support/', support.support, name='support'),

    # Chat
    path('chat/', views.chat_home, name='chat-home'),
    path('chat/direct/<int:user_id>/', views.chat_direct, name='chat-direct'),
    path('chat/<int:group_id>/', views.chat_room, name='chat-room'),

    # Direct-message connection requests (student ↔ student gate)
    path('connect/<int:user_id>/', views.connection_request, name='connection-request'),
    path('connect/<int:pk>/respond/', views.connection_respond, name='connection-respond'),

    # Meetings / calls / class sessions
    path('meetings/', views.meetings_list, name='meetings'),
    path('meetings/new/', views.meeting_create, name='meeting-create'),
    path('meet/<slug:slug>/', views.meeting_room, name='meeting-room'),
    # Start a voice/video call from a chat conversation (Jitsi for students,
    # Teams for staff/educators) — returns to the chat when the call ends.
    path('chat/<int:group_id>/call/', views.chat_call, name='chat-call'),

    # Discussions (Q&A-style forum)
    path('discussions/', views.discussions, name='discussions'),
    path('discussions/new/', views.discussion_create, name='discussion-create'),
    path('discussions/<int:pk>/', views.discussion_detail, name='discussion-detail'),

    # WhatsApp bot webhook (Meta Cloud API). Public + unauthenticated by
    # necessity: signature-checked in the view, and exempted from the site-wide
    # login gate in apps.accounts.middleware.
    path('whatsapp/webhook/', whatsapp_views.webhook, name='whatsapp-webhook'),

    # Notifications + preferences
    path('notifications/', views.notifications_list, name='notifications'),
    path('notifications/preferences/', views.notification_preferences, name='notification-preferences'),
    path('notifications/<int:pk>/', views.notification_detail, name='notification-detail'),

    # Polled by the client to play a sound when a new message/notification lands.
    path('alerts/counts/', views.alert_counts, name='alert-counts'),

    # Unified activity feed composer
    path('feed/post/', views.feed_create, name='feed-create'),
    path('feed/<int:pk>/like/', views.feed_like, name='feed-like'),
    path('feed/<int:pk>/comment/', views.feed_comment, name='feed-comment'),

    # The wall — the social feed on every profile (person / course / module).
    # Backed by Discussion + DiscussionReply; each action returns to the page it
    # was fired from, so the wall works inline wherever it is rendered.
    path('wall/post/', views.wall_post, name='wall-post'),
    path('wall/<int:pk>/like/', views.wall_like, name='wall-like'),
    path('wall/<int:pk>/comment/', views.wall_comment, name='wall-comment'),
    path('wall/comment/<int:pk>/like/', views.wall_comment_like, name='wall-comment-like'),

    # Announcements (bulk notifications) — staff/admin
    path('announcements/', views.announcement_list, name='announcements'),
    path('announcements/new/', views.announcement_compose, name='announcement-compose'),
    path('announcements/audience/', views.announcement_audience_preview, name='announcement-audience'),
    path('announcements/people/', views.announcement_people_search, name='announcement-people'),
    path('announcements/<int:pk>/', views.announcement_detail, name='announcement-detail'),
    path('announcements/<int:pk>/edit/', views.announcement_compose, name='announcement-edit'),
    path('announcements/<int:pk>/action/', views.announcement_action, name='announcement-action'),

    # Attendance (automated class-session attendance)
    path('attendance/', views.attendance_sessions, name='attendance'),
    path('attendance/<int:pk>/', views.attendance_session, name='attendance-session'),
    # Presence heartbeat — accrues real time attended (see services.record_presence_ping).
    path('attendance/<int:pk>/ping/', views.attendance_ping, name='attendance-ping'),

    # Collaboration workspaces (shared files + notes)
    path('workspaces/', views.workspaces, name='workspaces'),
    path('workspaces/<int:pk>/', views.workspace_detail, name='workspace-detail'),

    # In-system e-mail (admin / staff / educator)
    path('mail/', views.mail_inbox, name='mail-inbox'),
    path('mail/compose/', views.mail_compose, name='mail-compose'),
    path('mail/<int:pk>/', views.mail_read, name='mail-read'),
    path('mail/<int:pk>/action/', views.mail_action, name='mail-action'),
]
