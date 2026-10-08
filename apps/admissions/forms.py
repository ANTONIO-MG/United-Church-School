"""Forms for the application for admission (wizard steps 3 – 5) and the office."""
from django import forms

from apps.accounts.forms import DateInput, StyledModelForm, _style_fields

from .models import REQUIRED_DECLARATIONS, Application, ApplicationDocument, Guardian

_RADIO_BOOL = forms.RadioSelect(choices=[(True, 'Yes'), (False, 'No')])


def _bool_radio(form, *names):
    """Render boolean model fields as Yes / No radios. An unanswered nullable
    field stays ``None``; an unanswered non-null one keeps the model default."""
    for name in names:
        field = form.fields.get(name)
        if field is None:
            continue
        model_field = form._meta.model._meta.get_field(name)
        blank_value = None if model_field.null else model_field.get_default()
        form.fields[name] = forms.TypedChoiceField(
            label=field.label, help_text=field.help_text, required=field.required,
            choices=[(True, 'Yes'), (False, 'No')], coerce=lambda v: v in (True, 'True', 'true', '1'),
            empty_value=blank_value, widget=forms.RadioSelect,
            initial=form.initial.get(name, field.initial))


class LearnerDetailsForm(StyledModelForm):
    """Step 3 · the learner's identity document, background and previous school."""

    class Meta:
        model = Application
        fields = [
            'highest_grade_passed', 'year_grade_passed',
            'is_south_african', 'id_document_type', 'id_number', 'passport_number',
            'permit_number', 'document_country', 'document_expiry',
            'study_permit_number', 'study_permit_expiry', 'permanent_residency',
            'physical_address', 'home_language', 'race', 'religion', 'writing_hand',
            'previous_school', 'previous_school_address', 'previous_school_phone',
        ]
        widgets = {
            'document_expiry': DateInput(), 'study_permit_expiry': DateInput(),
            'physical_address': forms.Textarea(attrs={'rows': 2}),
            'highest_grade_passed': forms.TextInput(attrs={'placeholder': 'e.g. Grade 6'}),
            'home_language': forms.TextInput(attrs={'placeholder': 'e.g. isiZulu'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _bool_radio(self, 'is_south_african')
        _style_fields(self)
        for name in ('id_document_type', 'physical_address', 'home_language'):
            self.fields[name].required = True

    def clean(self):
        cleaned = super().clean()
        kind = cleaned.get('id_document_type')
        if kind in (Application.DOC_SA_ID, Application.DOC_BIRTH_CERT) and not cleaned.get('id_number'):
            self.add_error('id_number', 'Enter the ID / birth certificate number.')
        if kind == Application.DOC_PASSPORT:
            if not cleaned.get('passport_number'):
                self.add_error('passport_number', 'Enter the passport number.')
            if not cleaned.get('document_expiry'):
                self.add_error('document_expiry', 'Enter the passport expiry date.')
        if kind == Application.DOC_ASYLUM and not cleaned.get('permit_number'):
            self.add_error('permit_number', 'Enter the permit number.')
        if cleaned.get('is_south_african') is False and not cleaned.get('study_permit_number'):
            self.add_error('study_permit_number',
                           'Non-South African learners need a study permit.')
        return cleaned


class GeneralForm(StyledModelForm):
    """Step 3 · "General" — who the learner lives with and who pays the fees."""

    class Meta:
        model = Application
        fields = ['has_father', 'has_mother', 'lives_with', 'fee_payer', 'fee_payer_name',
                  'fee_payer_can_afford', 'siblings_at_ucs', 'sibling_names', 'smsweb_number']
        widgets = {'smsweb_number': forms.TextInput(attrs={'type': 'tel',
                                                           'placeholder': '082 123 4567'})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _bool_radio(self, 'has_father', 'has_mother', 'fee_payer_can_afford')
        _style_fields(self)
        for name in ('lives_with', 'fee_payer', 'smsweb_number', 'fee_payer_can_afford'):
            self.fields[name].required = True


class GuardianForm(StyledModelForm):
    """Step 3 · one parent / guardian. Leave the name blank to skip."""

    class Meta:
        model = Guardian
        fields = ['title', 'full_name', 'id_number', 'cell_phone', 'home_phone', 'work_phone',
                  'email', 'residential_address', 'occupation', 'employer', 'employer_phone']
        widgets = {'residential_address': forms.Textarea(attrs={'rows': 2})}

    def __init__(self, *args, role=None, **kwargs):
        self.role = role
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False

    @property
    def is_blank(self):
        return not (getattr(self, 'cleaned_data', {}).get('full_name') or '').strip()

    def clean(self):
        cleaned = super().clean()
        if (cleaned.get('full_name') or '').strip() and not (
                cleaned.get('cell_phone') or cleaned.get('home_phone')):
            self.add_error('cell_phone', 'Give at least one contact number.')
        return cleaned


class EmergencyForm(StyledModelForm):
    """Step 3 · a friend or relative to call in an emergency."""

    class Meta:
        model = Application
        fields = ['emergency_name', 'emergency_relationship', 'emergency_cell_phone',
                  'emergency_home_phone', 'emergency_email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ('emergency_name', 'emergency_relationship', 'emergency_cell_phone'):
            self.fields[name].required = True


class MedicalForm(StyledModelForm):
    """Step 4 · the medical form ("updated information in case of emergency")."""

    class Meta:
        model = Application
        fields = ['has_medical_condition', 'medical_conditions', 'medication',
                  'medical_aid_name', 'medical_aid_number', 'medical_aid_plan',
                  'medical_aid_main_member', 'medical_aid_main_member_phone',
                  'medical_aid_main_member_id', 'doctor_contact',
                  'medical_expenses_name', 'medical_expenses_phone', 'medical_expenses_relationship']
        widgets = {'medical_conditions': forms.Textarea(attrs={'rows': 2}),
                   'medication': forms.Textarea(attrs={'rows': 2})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _bool_radio(self, 'has_medical_condition')
        _style_fields(self)
        self.fields['medical_expenses_name'].required = True
        self.fields['medical_expenses_phone'].required = True

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('has_medical_condition') and not (cleaned.get('medical_conditions') or '').strip():
            self.add_error('medical_conditions', 'Please describe the condition or allergy.')
        return cleaned


class DocumentUploadForm(forms.ModelForm):
    """One supporting document."""

    class Meta:
        model = ApplicationDocument
        fields = ['kind', 'file', 'expiry_date']
        widgets = {'expiry_date': DateInput()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['expiry_date'].required = False
        _style_fields(self)


class DeclarationsForm(StyledModelForm):
    """Step 5 · the declarations a parent signs, plus the electronic signature."""

    confirm_signature = forms.BooleanField(
        label='I confirm that typing my name above is my signature, and that all the information '
              'in this application is true and correct.')

    class Meta:
        model = Application
        fields = list(REQUIRED_DECLARATIONS[:5]) + ['extramural_participation'] + list(
            REQUIRED_DECLARATIONS[5:]) + ['media_consent', 'signed_by', 'signed_relationship']
        labels = {'signed_by': 'Full name of parent / guardian (your signature)'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in REQUIRED_DECLARATIONS:
            self.fields[name].required = True
            self.fields[name].error_messages['required'] = 'Please read and accept this to apply.'
        self.fields['signed_by'].required = True
        self.fields['signed_relationship'].required = True


class OfficeChecklistForm(StyledModelForm):
    """Office use only — the page-1 checklist and the admission decision."""

    class Meta:
        model = Application
        fields = ['status', 'office_account_number', 'office_pastel_account', 'office_smsweb',
                  'office_learner_profile', 'office_transfer_received', 'office_letter_date',
                  'office_notes', 'decision_note']
        widgets = {'office_letter_date': DateInput(),
                   'office_notes': forms.Textarea(attrs={'rows': 3}),
                   'decision_note': forms.Textarea(attrs={'rows': 2})}
