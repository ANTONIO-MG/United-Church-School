from django.urls import path

from . import views_ops as v

urlpatterns = [
    path('jobs/', v.jobs, name='ops-jobs'),
    path('jobs/run-due/', v.jobs_run_due, name='ops-jobs-run-due'),
    path('jobs/<str:name>/run/', v.job_run, name='ops-job-run'),

    path('moderation/', v.moderation, name='ops-moderation'),
    path('moderation/violations/<int:pk>/', v.violation_action, name='ops-violation-action'),
    path('moderation/penalties/<int:pk>/lift/', v.penalty_lift, name='ops-penalty-lift'),
    path('moderation/appeals/<int:pk>/', v.appeal_decide, name='ops-appeal-decide'),

    path('audit/', v.audit, name='ops-audit'),
    path('audit/export/', v.audit_export, name='ops-audit-export'),

    path('invitations/', v.invitations, name='ops-invitations'),
    path('invitations/<int:pk>/', v.invitation_action, name='ops-invitation-action'),
    path('parent-links/', v.parent_links, name='ops-parent-links'),
    path('parent-links/<int:pk>/remove/', v.parent_link_remove, name='ops-parent-link-remove'),
]
