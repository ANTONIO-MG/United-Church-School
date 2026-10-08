from django.urls import path

from . import views_backups as views

urlpatterns = [
    path('backups/', views.backup_list, name='backups'),
    path('backups/create/', views.backup_create, name='backup-create'),
    path('backups/upload/', views.backup_upload, name='backup-upload'),
    path('backups/status/', views.restore_status, name='backup-status'),
    path('backups/<str:name>/download/', views.backup_download, name='backup-download'),
    path('backups/<str:name>/delete/', views.backup_delete, name='backup-delete'),
    path('backups/<str:name>/restore/', views.backup_restore, name='backup-restore'),
]
