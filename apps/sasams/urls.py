from django.urls import path

from . import views

app_name = 'sasams'

urlpatterns = [
    path('', views.index, name='index'),
    path('download/', views.download, name='download'),
    path('learner-numbers/', views.learner_numbers, name='learner-numbers'),
]
