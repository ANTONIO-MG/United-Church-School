"""URL routes for the learning app (mounted at /learning/ under the ``learning`` namespace)."""

from django.urls import path

from . import (ai_import, authoring, content_import, manage, material_open,
               module_build, module_feed, views)

app_name = 'learning'

urlpatterns = [
    path('', views.lessons, name='lessons'),
    path('lessons/<int:lesson_id>/session/', views.session_action, name='session-action'),

    # --- Student modules: lock / unlock (institution→programme→module spine) ---
    path('modules/', views.my_modules, name='my-modules'),
    path('modules/<int:module_id>/unlock/', views.module_unlock, name='module-unlock'),

    # --- Module feed: the schedule + its tabs. This is where clicking a module
    #     from the dashboard, My Modules or My Programmes lands. ---
    # Admin/staff: get a topic's content in, by JSON or from documents.
    path('content/import/', content_import.content_import, name='content-import'),

    # The one gated door onto a material — see apps.learning.material_open.
    path('materials/<int:pk>/open/', material_open.material_open, name='material-open'),

    path('modules/<int:pk>/feed/', module_feed.module_feed, name='module-feed'),
    path('modules/<int:pk>/feed/<slug:tab>/', module_feed.module_feed, name='module-feed-tab'),

    # --- Module schedule builder (educators/staff) ---
    path('modules/<int:pk>/build/', module_build.module_build, name='module-build'),
    path('modules/<int:pk>/build/scaffold/', module_build.module_scaffold, name='module-scaffold'),
    path('modules/<int:pk>/build/phases/save/', module_build.phase_save, name='module-phase-add'),
    path('modules/<int:pk>/build/phases/<int:phase_id>/save/', module_build.phase_save, name='module-phase-save'),
    path('modules/<int:pk>/build/phases/<int:phase_id>/delete/', module_build.phase_delete, name='module-phase-delete'),
    path('modules/<int:pk>/build/weeks/save/', module_build.week_save, name='module-week-add'),
    path('modules/<int:pk>/build/weeks/<int:week_id>/save/', module_build.week_save, name='module-week-save'),
    path('modules/<int:pk>/build/weeks/<int:week_id>/delete/', module_build.week_delete, name='module-week-delete'),
    path('modules/<int:pk>/build/materials/save/', module_build.material_save, name='module-material-add'),
    path('modules/<int:pk>/build/materials/<int:material_id>/save/', module_build.material_save, name='module-material-save'),
    path('modules/<int:pk>/build/materials/<int:material_id>/delete/', module_build.material_delete, name='module-material-delete'),
    path('modules/<int:pk>/build/materials/<int:material_id>/publish/', module_build.material_publish, name='module-material-publish'),
    path('modules/<int:pk>/build/materials/reorder/', module_build.material_reorder, name='module-material-reorder'),

    # --- Academic-structure management (admin/staff): institution → programme → module/cohort ---
    path('manage/institutions/', manage.institutions, name='manage-institutions'),
    path('manage/institutions/add/', manage.institution_add, name='manage-institution-add'),
    path('manage/institutions/<int:pk>/', manage.institution_detail, name='manage-institution'),
    path('manage/institutions/<int:pk>/edit/', manage.institution_edit, name='manage-institution-edit'),
    path('manage/institutions/<int:pk>/delete/', manage.institution_delete, name='manage-institution-delete'),
    path('manage/institutions/<int:institution_pk>/programmes/add/', manage.programme_add, name='manage-programme-add'),
    path('manage/programmes/<int:pk>/', manage.programme_detail, name='manage-programme'),
    path('manage/programmes/<int:pk>/edit/', manage.programme_edit, name='manage-programme-edit'),
    path('manage/programmes/<int:pk>/delete/', manage.programme_delete, name='manage-programme-delete'),
    path('manage/programmes/<int:programme_pk>/modules/add/', manage.module_add, name='manage-module-add'),
    path('manage/modules/<int:pk>/edit/', manage.module_edit, name='manage-module-edit'),
    path('manage/modules/<int:pk>/delete/', manage.module_delete, name='manage-module-delete'),
    path('manage/programmes/<int:programme_pk>/cohorts/add/', manage.cohort_add, name='manage-cohort-add'),
    path('manage/cohorts/<int:pk>/edit/', manage.cohort_edit, name='manage-cohort-edit'),
    path('manage/cohorts/<int:pk>/delete/', manage.cohort_delete, name='manage-cohort-delete'),

    # --- Lesson viewer (learner) ---
    path('lessons/<int:lesson_id>/view/', views.lesson_view, name='lesson-view'),
    path('lessons/<int:lesson_id>/complete/', views.lesson_complete, name='lesson-complete'),
    path('blocks/<int:block_id>/track/', views.lesson_block_track, name='lesson-block-track'),
    # Player: per-section progress, private notes and bookmarks
    path('sections/<int:section_id>/progress/', views.section_progress, name='section-progress'),
    path('lessons/<int:lesson_id>/note/', views.note_save, name='lesson-note-save'),
    path('lessons/<int:lesson_id>/bookmark/', views.bookmark_add, name='lesson-bookmark-add'),
    path('bookmarks/<int:bookmark_id>/delete/', views.bookmark_delete, name='lesson-bookmark-delete'),

    # --- Lesson creator (educators/staff) ---
    path('lessons/manage/', authoring.lesson_manage, name='lesson-manage'),
    path('lessons/new/', authoring.lesson_create, name='lesson-create'),
    path('lessons/ai/', ai_import.lesson_ai_import, name='lesson-ai-import'),
    path('lessons/<int:lesson_id>/ai/extend/', ai_import.lesson_ai_extend, name='lesson-ai-extend'),
    path('modules/<int:module_id>/live/schedule/', authoring.module_live_schedule, name='module-live-schedule'),
    path('lessons/<int:lesson_id>/edit/', authoring.lesson_editor, name='lesson-editor'),
    path('lessons/<int:lesson_id>/meta/', authoring.lesson_meta_save, name='lesson-meta-save'),
    path('lessons/<int:lesson_id>/publish/', authoring.lesson_publish, name='lesson-publish'),
    path('lessons/<int:lesson_id>/delete/', authoring.lesson_delete, name='lesson-delete'),
    # sections (the tear-drops)
    path('lessons/<int:lesson_id>/sections/add/', authoring.section_add, name='section-add'),
    path('lessons/<int:lesson_id>/sections/reorder/', authoring.section_reorder, name='section-reorder'),
    path('sections/<int:section_id>/save/', authoring.section_save, name='section-save'),
    path('sections/<int:section_id>/delete/', authoring.section_delete, name='section-delete'),
    # blocks
    path('lessons/<int:lesson_id>/blocks/add/', authoring.block_add, name='block-add'),
    path('lessons/<int:lesson_id>/blocks/reorder/', authoring.block_reorder, name='block-reorder'),
    path('blocks/<int:block_id>/save/', authoring.block_save, name='block-save'),
    path('blocks/<int:block_id>/move/', authoring.block_move, name='block-move'),
    path('blocks/<int:block_id>/delete/', authoring.block_delete, name='block-delete'),
    path('blocks/<int:block_id>/upload/', authoring.block_upload, name='block-upload'),
    # lesson attachments (PDFs, images, text files …)
    path('lessons/<int:lesson_id>/attachments/add/', authoring.attachment_add, name='attachment-add'),
    path('attachments/<int:resource_id>/delete/', authoring.attachment_delete, name='attachment-delete'),
    # interactive blocks
    path('lessons/<int:lesson_id>/attach/quiz/', authoring.attach_quiz, name='attach-quiz'),
    path('lessons/<int:lesson_id>/attach/meeting/', authoring.attach_meeting, name='attach-meeting'),

    # --- ProgrammeModule profile (profile-style page: feed/chat/lessons/assessments/…) ---
    path('modules/<int:pk>/', views.module_profile, name='module-profile'),
    path('modules/<int:pk>/<slug:tab>/', views.module_profile, name='module-profile'),

]
