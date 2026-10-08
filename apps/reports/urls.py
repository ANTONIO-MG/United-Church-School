"""URL routes for reports & certificates (mounted at /reports/)."""

from django.urls import path

from . import term_views, views

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

    # Term reporting (GDE four terms): educator mark sheets, report cards and
    # the office's outstanding-mark-sheet overview. See apps.reports.term_views.
    path('marks/', term_views.marks_index, name='marks'),
    path('marks/<int:pk>/<int:year>/<int:term>/', term_views.mark_sheet, name='mark-sheet'),
    path('marks/<int:pk>/<int:year>/<int:term>/export.csv', term_views.mark_sheet_csv,
         name='mark-sheet-csv'),
    path('report-card/', term_views.report_card, name='report-card'),
    path('report-card/pdf/', term_views.report_card_pdf, name='report-card-pdf'),
    path('terms/', term_views.term_overview, name='term-overview'),
]
