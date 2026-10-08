"""Revision routes (mounted at ``/revision/`` under the ``revision`` namespace)."""

from django.urls import path

from . import views

app_name = 'revision'

urlpatterns = [
    path('', views.home, name='home'),
    path('session/', views.session, name='session'),
]
