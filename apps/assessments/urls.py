"""URL routes for the assessments app (mounted at /assessments/)."""

from django.urls import path

from . import ai_import, authoring, views

app_name = 'assessments'

urlpatterns = [
    path('', views.index, name='index'),

    # Take / result (learners)
    path('<int:assessment_id>/take/', views.take, name='take'),
    path('attempt/<uuid:public_id>/submit/', views.submit, name='submit'),
    path('attempt/<uuid:public_id>/proctor/', views.proctor_event, name='proctor-event'),
    path('attempt/<uuid:public_id>/result/', views.result, name='result'),

    # Builder (educators)
    path('manage/', authoring.manage, name='manage'),
    path('manage/new/', authoring.create, name='create'),
    path('manage/ai/', ai_import.assessment_ai_import, name='ai-import'),
    path('<int:assessment_id>/build/', authoring.builder, name='builder'),
    path('<int:assessment_id>/build/status/', authoring.status_change, name='status-change'),
    path('<int:assessment_id>/build/proctoring/', authoring.proctoring_save, name='proctoring-save'),
    path('<int:assessment_id>/build/question/', authoring.question_save, name='question-save'),
    path('question/<int:question_id>/delete/', authoring.question_delete, name='question-delete'),

    # Manual marking queue (educators)
    path('marking/', authoring.marking_queue, name='marking-queue'),
    path('attempt/<uuid:public_id>/mark/', authoring.mark_attempt, name='mark-attempt'),
    # Rubric suggestion for one answer — advisory, never a mark.
    path('answer/<int:answer_id>/suggest/', authoring.suggest_marks, name='suggest-marks'),
]
