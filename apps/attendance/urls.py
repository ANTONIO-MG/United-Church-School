from django.urls import path

from . import views

app_name = 'attendance'

urlpatterns = [
    path('', views.index, name='index'),
    path('register/<int:pk>/', views.register_detail, name='register'),
    path('reports/', views.reports, name='reports'),
    path('reports/export.csv', views.reports_csv, name='reports-csv'),
    path('learner/<int:person_id>/', views.learner_record, name='learner'),
    path('my/', views.my_attendance, name='my'),
]
