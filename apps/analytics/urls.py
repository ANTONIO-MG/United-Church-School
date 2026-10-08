"""URL routes for analytics (mounted at /analytics/)."""

from django.urls import path

from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('export/modules/', views.export_subjects, name='export-modules'),
]
