"""HTML routes for the accounts community area (mounted under the ``accounts``
namespace — see :mod:`config.urls`)."""

from django.urls import path

from . import person_card
from . import views

app_name = 'accounts'

urlpatterns = [
    # Onboarding — 3-step registration wizard (gated by OnboardingMiddleware).
    path('register/', views.register, name='register'),                     # step 1 · personal
    path('register/course/', views.register_course, name='register-course'),  # step 2 · grade & subjects
    path('register/family/', views.register_family, name='register-family'),  # step 3 · learner & family
    path('register/medical/', views.register_medical, name='register-medical'),  # step 4 · medical & documents
    path('register/review/', views.register_review, name='register-review'),  # step 5 · declarations → pay
    # The landing screen both payment routes finish on — holds for a few seconds
    # so the outcome is read before the dashboard replaces it.
    path('register/complete/', views.registration_complete, name='register-complete'),
    path('register/checkout/', views.enrol_checkout, name='enrol-checkout'),
    # A parent applies for a child from their own account (then walks the
    # same wizard above "acting for" the child).
    path('apply/', views.parent_apply, name='parent-apply'),
    path('apply/stop/', views.parent_apply_stop, name='parent-apply-stop'),
    path('apply/<int:child_id>/continue/', views.parent_apply_continue, name='parent-apply-continue'),
    path('apply/<int:child_id>/login/', views.parent_learner_login, name='parent-apply-login'),
    # Invite-based single-page registration (role decided by the invite link).
    path('invite/<uuid:token>/', views.accept_invite, name='accept-invite'),
    path('invite/<uuid:token>/accept/', views.invite_confirm, name='invite-confirm'),
    path('register/parent/', views.register_parent, name='register-parent'),
    path('register/educator/', views.register_educator, name='register-educator'),
    path('register/staff/', views.register_staff, name='register-staff'),   # team first-login profile
    path('staff/create/', views.staff_create, name='staff-create'),          # superuser creates team accounts
    path('educators/add/', views.add_educator, name='add-educator'),
    path('complete-profile/', views.complete_profile, name='complete-profile'),
    # Public parent/guardian registration via a student's invite token.
    path('parents/<uuid:token>/', views.parent_register, name='parent-register'),

    path('my-programmes/', views.my_programmes, name='my-programmes'),

    path('profile/', views.my_profile, name='my-profile'),
    path('profile/<int:pk>/', views.profile, name='profile'),
    path('people/<int:pk>/card/', person_card.person_card, name='person-card'),
    path('people/user/<int:user_id>/card/', person_card.person_card_for_user, name='person-card-user'),
    path('profile/<int:pk>/<slug:tab>/', views.profile, name='profile'),
    path('settings/', views.settings, name='settings'),
    # POPIA: download-my-data (right of access) + cookie-banner consent.
    path('privacy/export/', views.data_export, name='data-export'),
    path('privacy/export/pdf/', views.data_export_pdf, name='data-export-pdf'),
    path('privacy/cookies/', views.cookie_consent, name='cookie-consent'),
    # UI preferences set from the chrome (navbar theme buttons, language switcher).
    path('preferences/theme/', views.set_theme, name='set-theme'),
    path('preferences/language/', views.set_language, name='set-language'),

    # Close-account flow (verify → soft close → 30-day grace → purge command).
    path('settings/close/', views.close_account, name='close-account'),
    path('settings/close/done/', views.close_account_done, name='close-account-done'),

    # Admin/staff recovery desk: reactivate during grace, restore after purge.
    path('closed-accounts/', views.closed_accounts, name='closed-accounts'),
    path('closed-accounts/<int:pk>/reactivate/', views.reactivate_account, name='reactivate-account'),
    path('closed-accounts/archive/<int:pk>/restore/', views.restore_archive, name='restore-archive'),

    # Admin/staff: manage anyone's course + module enrolment
    path('members/', views.manage_members, name='manage-members'),
    # Public (to signed-in users) full profile page for any member.
    path('members/<int:pk>/', views.member_profile, name='member-profile'),
    path('members/<int:pk>/role/', views.member_role, name='member-role'),
    path('members/<int:pk>/enrol/', views.member_enrol, name='member-enrol'),
]
