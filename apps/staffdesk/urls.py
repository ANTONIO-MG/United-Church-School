"""/staff/ — the admin team's pages for what used to need Django admin or a shell.

Split into one URL module per area so each area can grow on its own:

* ``urls_ops``      — background jobs, moderation, audit log, invitations & parent links
* ``urls_academic`` — certificates & grades, at-risk students, content imports
* ``urls_dash``     — operations dashboard, educator dashboard, student 360
* ``urls_backups``  — database backups and restore points (administrators only)
"""

from django.urls import include, path

app_name = 'staffdesk'

urlpatterns = [
    path('', include('apps.staffdesk.urls_ops')),
    path('', include('apps.staffdesk.urls_academic')),
    path('', include('apps.staffdesk.urls_dash')),
    path('', include('apps.staffdesk.urls_backups')),
]
