"""URL routes for reports & certificates (mounted at /reports/)."""

from django.urls import path

from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.my_reports, name='my-reports'),
    path('progress/', views.my_progress, name='my-progress'),

    # Certificates. The preview, the PNG and the PDF are all the same rendered
    # artwork (apps.reports.certificate_render), so they cannot drift apart.
    path('certificates/<int:pk>/', views.certificate_view, name='certificate'),
    path('certificates/<int:pk>/image/', views.certificate_image, name='certificate-image'),
    path('certificates/<int:pk>/pdf/', views.certificate_pdf, name='certificate-pdf'),
    path('certificates/<int:pk>/png/', views.certificate_png, name='certificate-png'),
    path('verify/<uuid:verification_uuid>/', views.verify_certificate, name='verify'),
]
