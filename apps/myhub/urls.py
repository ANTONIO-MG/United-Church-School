"""URL routing for the MyHub dashboard (mounted at ``/myhub/`` under the
``myhub`` namespace).

Grouped by section: dashboards, the CRUD sections (Professors, Students,
Courses, Library, Staff, Holiday, Fees, CMS), the theme showcase
pages (Apps, Charts, Bootstrap UI, Plugins, Forms/Tables) and the auth/utility
pages. List/edit/create views also accept an optional ``<int:pk>`` so the same
view can render an "edit" form. A few ``name=`` aliases use underscores to match
hard-coded ``{% url %}`` tags inherited from the original theme templates.
"""

from django.urls import path

from . import search, views

app_name = 'myhub'

urlpatterns = [
    # ----- Global navbar search -----
    path('search/suggest/', search.suggest, name='search-suggest'),

    # ----- Dashboards -----
    # One name, one URL. There used to be a second ``index/`` route carrying the
    # same name; Django resolves a duplicate name to the *last* pattern, so
    # ``reverse('myhub:index')`` returned /myhub/index/ while every allow-list in
    # the project spelled the dashboard /myhub/ — which locked parent accounts
    # into an infinite redirect (ParentAccessMiddleware refused the page it was
    # itself redirecting to).
    path('', views.index, name='index'),
    path('event-management/', views.event_management, name='event-management'),
    path('events.json', views.events_feed, name='events-feed'),
    path('events/', views.events, name='events'),
    path('events/<int:pk>/', views.event_detail, name='event-detail'),
    path('add-reminder/', views.add_reminder, name='add-reminder'),

    # ----- Professors -----

    # ----- Students -----

    # ----- Courses -----

    # Course profile (profile-style page: overview/modules/lessons/…)

    # ----- Library -----

    # ----- Staff -----

    # ----- Holiday -----

    # ----- Fees -----

    # ----- CMS -----

    # ----- Apps -----

    # ----- Charts -----

    # ----- Bootstrap UI -----

    # ----- Plugins -----

    # ----- Forms / Tables -----

    # ----- Social theme: component reference -----

    # ----- Auth / utility -----
    path('page-login/', views.page_login, name='page-login'),
    path('page-register/', views.page_register, name='page-register'),
    path('logout/', views.page_logout, name='logout'),
    path('page-forgot-password/', views.page_forgot_password, name='page-forgot-password'),
]
