from django.urls import path

from . import views_dash as views

urlpatterns = [
    path('', views.home, name='home'),
    path('students/', views.students, name='students'),
    path('students/<int:person_id>/', views.student_detail, name='student'),
    path('teaching/', views.teaching, name='teaching'),
    path('teaching/nudge/<int:module_id>/', views.nudge, name='teaching-nudge'),
]
