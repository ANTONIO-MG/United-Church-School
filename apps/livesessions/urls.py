"""Routes for the school calendar and live sessions (mounted at ``/calendar/``)."""

from django.urls import path

from . import views

app_name = 'livesessions'

urlpatterns = [
    path('', views.calendar, name='calendar'),
    path('day/<str:on>/', views.day, name='day'),
    path('feed.json', views.feed, name='feed'),
    path('school-calendar.ics', views.ics, name='ics'),
    # The subscribable feed Google / Outlook / Apple poll. Unauthenticated by
    # necessity — the token is the credential — and therefore exempted from the
    # site-wide login gate in apps.accounts.middleware.
    path('feed/<uuid:token>.ics', views.personal_feed, name='personal-feed'),

    # Connected calendars (the forms live on the user's settings page).
    path('connections/add/', views.connect_calendar, name='connect-calendar'),
    path('connections/<int:pk>/refresh/', views.refresh_calendar, name='refresh-calendar'),
    path('connections/<int:pk>/remove/', views.disconnect_calendar, name='disconnect-calendar'),
    path('connections/reset-link/', views.rotate_calendar_token, name='rotate-calendar-token'),

    path('sessions/new/', views.session_create, name='session-create'),
    path('sessions/past/', views.past_sessions, name='past-sessions'),
    path('sessions/<int:pk>/', views.session_detail, name='session-detail'),
    # The identified hand-off into the live room — the only route students take.
    path('sessions/<int:pk>/join/', views.session_join, name='session-join'),
    path('sessions/<int:pk>/register/', views.session_register, name='session-register'),
    path('sessions/<int:pk>/register/resolve/', views.resolve_attendee, name='resolve-attendee'),
    path('sessions/<int:pk>/edit/', views.session_edit, name='session-edit'),
    path('sessions/<int:pk>/cancel/', views.session_cancel, name='session-cancel'),

    path('settings/', views.settings_page, name='settings'),

    # YouTube recordings — staff scan/map screen (admin/staff only).
    path('recordings/manage/', views.youtube_admin, name='youtube-admin'),
]
