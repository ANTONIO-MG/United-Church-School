from django.urls import path

from . import views, views_promotion

app_name = 'admissions'

urlpatterns = [
    path('my-application/', views.my_application, name='my-application'),
    path('documents/<int:pk>/', views.document_file, name='document-file'),
    path('office/', views.office_list, name='office-list'),
    path('office/<uuid:public_id>/', views.office_detail, name='office-detail'),
    # Year-end promotion and the next school year.
    path('promotion/', views_promotion.promotion_index, name='promotion'),
    path('promotion/<int:programme_id>/<int:year>/', views_promotion.promotion_class,
         name='promotion-class'),
    path('new-year/', views_promotion.new_year, name='new-year'),
]

# Bulk learner import / export (school office) — apps/admissions/views_bulk.py
from . import views_bulk  # noqa: E402

urlpatterns += [
    path('import/', views_bulk.bulk_import, name='bulk-import'),
    path('import/template.xlsx', views_bulk.bulk_template, name='bulk-template'),
    path('export/', views_bulk.bulk_export, name='bulk-export'),
]
