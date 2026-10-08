"""HTML routes for tasks (mounted at ``/tasks/`` under the ``orgtasks`` namespace)."""

from django.urls import path

from . import views

app_name = 'orgtasks'

urlpatterns = [
    path('', views.my_tasks, name='my-tasks'),
    path('all/', views.all_tasks, name='all-tasks'),
    path('task/<int:pk>/', views.task_detail, name='task-detail'),

    path('manage/add/', views.add_task, name='add-task'),
    path('manage/<int:pk>/edit/', views.edit_task, name='edit-task'),
    path('manage/<int:pk>/delete/', views.delete_task, name='delete-task'),
    path('assignment/<int:pk>/update/', views.assignment_update, name='assignment-update'),
]
