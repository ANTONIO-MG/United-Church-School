"""/staff/ academic pages: grades & certificates, at-risk students, content
imports and AI reports. Views in :mod:`apps.staffdesk.views_academic`."""

from django.urls import path

from . import views_academic as views

urlpatterns = [
    # Grades
    path('grades/', views.grades, name='grades'),
    path('grades/recompute-module/', views.grades_recompute_module, name='grades-recompute-module'),
    path('grades/weightings/', views.weightings, name='weightings'),
    path('grades/weightings/<int:module_id>/', views.weighting_edit, name='weighting-edit'),
    path('grades/<int:pk>/', views.grade_detail, name='grade-detail'),
    path('grades/<int:pk>/recompute/', views.grade_recompute, name='grade-recompute'),
    path('grades/<int:pk>/override/', views.grade_override, name='grade-override'),
    path('grades/<int:pk>/override/clear/', views.grade_override_clear, name='grade-override-clear'),

    # Certificates
    path('certificates/', views.certificates, name='certificates'),
    path('certificates/issue/', views.certificate_issue, name='certificate-issue'),
    path('certificates/<int:pk>/revoke/', views.certificate_revoke, name='certificate-revoke'),
    path('certificates/<int:pk>/reinstate/', views.certificate_reinstate, name='certificate-reinstate'),
    path('certificates/<int:pk>/regenerate/', views.certificate_regenerate, name='certificate-regenerate'),

    # At-risk students
    path('at-risk/', views.at_risk, name='at-risk'),
    path('at-risk/scan/', views.at_risk_scan, name='at-risk-scan'),
    path('at-risk/snapshots/', views.snapshots, name='snapshots'),
    path('at-risk/snapshots/take/', views.snapshot_take, name='snapshot-take'),
    path('at-risk/snapshots/<int:pk>/', views.snapshot_detail, name='snapshot-detail'),
    path('at-risk/<int:pk>/', views.at_risk_detail, name='at-risk-detail'),
    path('at-risk/<int:pk>/triage/', views.at_risk_triage, name='at-risk-triage'),
    path('at-risk/<int:pk>/notify/<str:who>/', views.at_risk_notify, name='at-risk-notify'),

    # Content imports
    path('imports/', views.imports, name='imports'),
    path('imports/run/<str:command>/', views.import_run, name='import-run'),
    path('imports/runs/<int:pk>/', views.import_run_detail, name='import-run-detail'),
    path('imports/runs/<int:pk>/status/', views.import_run_status, name='import-run-status'),

    # AI reports & insights
    path('ai-reports/', views.ai_reports, name='ai-reports'),
    path('ai-reports/insights/', views.ai_insights, name='ai-insights'),
    path('ai-reports/insights/<int:pk>/', views.ai_insight_detail, name='ai-insight-detail'),
    path('ai-reports/insights/<int:pk>/status/', views.ai_insight_status, name='ai-insight-status'),
    path('ai-reports/<int:pk>/', views.ai_report_detail, name='ai-report-detail'),
]
