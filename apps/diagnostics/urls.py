"""Developer diagnostics routes (mounted at ``/diagnostics/``, admin/staff only)."""

from django.urls import path

from . import views

app_name = 'diagnostics'

urlpatterns = [
    path('', views.log, name='log'),
    path('dictionary/', views.dictionary, name='dictionary'),
    path('dictionary.json', views.dictionary_json, name='dictionary-json'),
    path('export/', views.export_log, name='export'),
    path('<int:pk>/', views.event_detail, name='event'),
]
