from django.contrib import admin

from .models import Application, ApplicationDocument, Guardian


class GuardianInline(admin.StackedInline):
    model = Guardian
    extra = 0
    fields = (('role', 'title', 'full_name'), ('id_number', 'email'),
              ('cell_phone', 'home_phone', 'work_phone'), 'residential_address',
              ('occupation', 'employer', 'employer_phone'), 'invite_sent_at')
    readonly_fields = ('invite_sent_at',)


class DocumentInline(admin.TabularInline):
    model = ApplicationDocument
    extra = 0
    fields = ('kind', 'file', 'original_name', 'expiry_date', 'verified', 'note')
    readonly_fields = ('original_name',)


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('learner_name', 'programme', 'year', 'status', 'is_new_learner',
                    'submitted_at', 'office_pastel_account', 'office_transfer_received')
    list_filter = ('status', 'year', 'programme', 'is_new_learner', 'is_south_african')
    search_fields = ('person__first_name', 'person__last_name', 'person__user__email',
                     'id_number', 'passport_number', 'guardians__full_name', 'office_account_number')
    readonly_fields = ('public_id', 'submitted_at', 'signed_at', 'signed_ip', 'signed_device',
                       'invoice_uid', 'created_at', 'updated_at')
    inlines = [GuardianInline, DocumentInline]
    fieldsets = (
        ('Application', {'fields': (('person', 'status', 'year'), ('programme', 'is_new_learner'),
                                    ('highest_grade_passed', 'year_grade_passed'),
                                    'submitted_at', 'invoice_uid', 'public_id')}),
        ('Identity', {'fields': (('is_south_african', 'id_document_type'),
                                 ('id_number', 'passport_number', 'permit_number'),
                                 ('document_country', 'document_expiry'),
                                 ('study_permit_number', 'study_permit_expiry'),
                                 'permanent_residency')}),
        ('Learner', {'fields': ('gender', 'physical_address', ('home_language', 'race', 'religion'),
                                'writing_hand')}),
        ('General', {'fields': (('has_father', 'has_mother', 'lives_with'),
                                ('fee_payer', 'fee_payer_name', 'fee_payer_can_afford'),
                                ('siblings_at_ucs', 'sibling_names'), 'smsweb_number')}),
        ('Previous school', {'fields': ('previous_school', 'previous_school_address',
                                        'previous_school_phone')}),
        ('Emergency contact', {'fields': (('emergency_name', 'emergency_relationship'),
                                          ('emergency_cell_phone', 'emergency_home_phone',
                                           'emergency_email'))}),
        ('Medical', {'fields': ('has_medical_condition', 'medical_conditions', 'medication',
                                ('medical_aid_name', 'medical_aid_number', 'medical_aid_plan'),
                                ('medical_aid_main_member', 'medical_aid_main_member_phone',
                                 'medical_aid_main_member_id'),
                                'doctor_contact',
                                ('medical_expenses_name', 'medical_expenses_phone',
                                 'medical_expenses_relationship'))}),
        ('Declarations', {'fields': (('accept_terms', 'accept_indemnity', 'extramural_participation'),
                                     ('accept_learner_code', 'accept_parent_code', 'accept_prospectus'),
                                     ('accept_fees', 'accept_popia', 'media_consent',
                                      'acknowledge_documents'),
                                     ('signed_by', 'signed_relationship'),
                                     ('signed_at', 'signed_ip'), 'signed_device')}),
        ('Office use only', {'fields': (('office_account_number', 'office_pastel_account'),
                                        ('office_smsweb', 'office_learner_profile',
                                         'office_transfer_received'),
                                        'office_letter_date', 'office_notes',
                                        ('registrar', 'registrar_signed_at'),
                                        ('decided_by', 'decided_at'), 'decision_note')}),
        ('Record', {'fields': (('created_at', 'updated_at'),)}),
    )


@admin.register(ApplicationDocument)
class ApplicationDocumentAdmin(admin.ModelAdmin):
    list_display = ('application', 'kind', 'original_name', 'verified', 'expiry_date', 'created_at')
    list_filter = ('kind', 'verified')
    search_fields = ('application__person__first_name', 'application__person__last_name',
                     'original_name')
