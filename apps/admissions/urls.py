from django.urls import path

from . import views

app_name = 'admissions'

urlpatterns = [
    path('my-application/', views.my_application, name='my-application'),
    path('documents/<int:pk>/', views.document_file, name='document-file'),
    path('office/', views.office_list, name='office-list'),
    path('office/<uuid:public_id>/', views.office_detail, name='office-detail'),
]
