"""Forms for managing the academic spine (admin/staff only):
Institution → Programme → ProgrammeModule (offering) → Cohort.

Bootstrap-styled to match the dashboard. The module "add" form hides the
canonical-Module / offering split from the admin — they just add a module with a
code, name and monthly price, and the form get-or-creates the canonical
:class:`~apps.learning.models.Module` behind the scenes.
"""
from django import forms

from . import models


def _style(form):
    for _name, field in form.fields.items():
        widget = field.widget
        if isinstance(widget, forms.CheckboxInput):
            widget.attrs['class'] = (widget.attrs.get('class', '') + ' form-check-input').strip()
        elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
            widget.attrs['class'] = (widget.attrs.get('class', '') + ' form-control form-select').strip()
        else:
            widget.attrs['class'] = (widget.attrs.get('class', '') + ' form-control').strip()
        if isinstance(widget, (forms.TextInput, forms.Textarea, forms.NumberInput,
                               forms.EmailInput, forms.URLInput)):
            widget.attrs.setdefault('placeholder', field.label)


class _StyledModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style(self)


class InstitutionForm(_StyledModelForm):
    class Meta:
        model = models.Institution
        fields = ['code', 'name', 'accent_colour', 'accent_name', 'logo',
                  'website', 'description', 'order', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'accent_colour': forms.TextInput(attrs={'type': 'color'}),
        }


class InstitutionBlueprintForm(InstitutionForm):
    """Create a school *and* the structure it needs to be usable.

    A school with no grades and no subjects is an empty shell: nobody can
    register for it and nothing can be scheduled against it. So the add form
    asks what to build — Grade 1 to Grade 12 with the CAPS subjects and fees, or
    nothing — and builds it, plus the year's calendar, in the same submit.
    Everything it creates is ordinary editable data.
    """
    blueprint = forms.ChoiceField(
        choices=[], initial='school', label='Structure to create',
        help_text='The grades and subjects to build under this school. '
                  'You can add, rename or remove any of it afterwards.')
    price_per_month = forms.DecimalField(
        max_digits=8, decimal_places=2, initial=0, label='Extra price per subject per month (R)',
        help_text='Normally 0 — learners pay the grade\'s school fees, not per subject.')
    create_calendar = forms.BooleanField(
        required=False, initial=True, label="Create this year's school calendar",
        help_text='Term dates, holidays, fee deadlines, public holidays and a template of the '
                  'examination windows (confirm those against the official timetable).')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from core import academic_spine

        self.fields['blueprint'].choices = academic_spine.BLUEPRINT_CHOICES
        self.blueprints = academic_spine.BLUEPRINTS
        _style(self)

    def save(self, commit=True):
        """Save the institution, then build the chosen structure under it, and
        make sure every programme has at least one cohort so students can pick an
        intake at registration straight away."""
        from django.utils import timezone

        from core import academic_spine

        institution = super().save(commit=commit)
        self.blueprint_result = academic_spine.apply_blueprint(
            institution, self.cleaned_data.get('blueprint'),
            price=self.cleaned_data.get('price_per_month') or 0,
            calendar=self.cleaned_data.get('create_calendar', True))
        # Every grade gets the current school year as its class, so the
        # registration picker always has one.
        year = timezone.now().year
        for programme in institution.programmes.all():
            if not programme.cohorts.exists():
                models.Cohort.objects.get_or_create(
                    programme=programme, code=str(year),
                    defaults={'name': f'{programme.display_name} · {year}'})
        return institution


class ProgrammeForm(_StyledModelForm):
    """A grade: its name, number, CAPS phase and the year's fee schedule."""
    class Meta:
        model = models.Programme
        fields = ['full_name', 'abbreviation', 'code', 'name', 'grade', 'level', 'depth_default',
                  'registration_fee', 'annual_levy', 'monthly_fee',
                  'description', 'order', 'is_active']
        labels = {
            'full_name': 'Grade name',
            'abbreviation': 'Short name',
            'code': 'Record code',
            'name': 'Short display name',
            'grade': 'Grade number',
            'level': 'Phase',
            'registration_fee': 'Registration fee — new learners (R)',
            'annual_levy': 'Annual levy (R)',
            'monthly_fee': 'Monthly school fees (R)',
        }
        help_texts = {
            'full_name': 'e.g. "Grade 5".',
            'abbreviation': 'Used for search and in content titles, e.g. "Grade 5".',
        }
        widgets = {'description': forms.Textarea(attrs={'rows': 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['full_name'].required = True
        # Derived in clean() when left blank, so they must not fail field-level
        # validation first — required checks run before clean() ever sees them.
        for derived in ('code', 'name', 'abbreviation'):
            self.fields[derived].required = False

    def clean(self):
        cleaned = super().clean()
        # Everything can be driven off the full name and the abbreviation; the
        # record code and short name are derived when they are left blank so the
        # person filling this in only has to answer the two questions that matter.
        abbreviation = (cleaned.get('abbreviation') or '').strip()
        full_name = (cleaned.get('full_name') or '').strip()
        if not abbreviation and full_name:
            abbreviation = ''.join(word[0] for word in full_name.split() if word[0].isalpha())[:30].upper()
            cleaned['abbreviation'] = abbreviation
        if not (cleaned.get('code') or '').strip():
            cleaned['code'] = abbreviation[:30]
        if not (cleaned.get('name') or '').strip():
            cleaned['name'] = abbreviation or full_name[:160]
        return cleaned


class CohortForm(_StyledModelForm):
    class Meta:
        model = models.Cohort
        fields = ['code', 'name', 'class_teacher', 'start_date', 'end_date', 'is_active']
        labels = {'code': 'Class code (e.g. 2026)', 'name': 'Class name'}
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }


class ProgrammeModuleForm(_StyledModelForm):
    """Edit an existing offering; the canonical module it points at is fixed."""
    class Meta:
        model = models.ProgrammeModule
        fields = ['code', 'name', 'subject_group', 'depth_level', 'price_per_month',
                  'description', 'order', 'is_active']
        widgets = {'description': forms.Textarea(attrs={'rows': 2})}


class ProgrammeModuleAddForm(forms.Form):
    """Add a subject to a grade. Get-or-creates the canonical subject, then the
    offering, so the admin never sees the two-level split."""
    module_code = forms.CharField(
        max_length=20, label='Subject code',
        help_text='Canonical code, e.g. "MATH" — shared with the same subject in other grades.')
    module_name = forms.CharField(max_length=160, label='Subject name',
                                  help_text='e.g. "Mathematics".')
    offering_code = forms.CharField(
        max_length=20, required=False, label="Code in this grade",
        help_text='Optional. Defaults to the subject code.')
    subject_group = forms.ChoiceField(
        required=False, label='Subject choice', choices=models.ProgrammeModule.GROUP_CHOICES,
        help_text='Grade 10 – 12 only: leave as Compulsory unless learners choose between subjects.')
    price_per_month = forms.DecimalField(
        max_digits=8, decimal_places=2, initial=0, label='Extra price per month (R)',
        help_text="Normally 0 — the grade's school fees cover every subject.")
    depth_level = forms.ChoiceField(
        required=False, label='Depth',
        choices=[('', '— inherit the grade depth —')] + list(models.DEPTH_CHOICES))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style(self)

    def save(self, programme):
        cd = self.cleaned_data
        code = cd['module_code'].strip().upper()
        name = cd['module_name'].strip() or code
        module = models.Module.objects.filter(code=code).first()
        if module is None:
            module = (models.Module.objects.filter(name=name).first()
                      or models.Module.objects.create(code=code, name=name))
        offering_code = (cd.get('offering_code') or code).strip().upper()
        offering, _ = models.ProgrammeModule.objects.get_or_create(
            programme=programme, code=offering_code,
            defaults={
                'module': module,
                'name': name if name != module.name else '',
                'price_per_month': cd['price_per_month'] or 0,
                'subject_group': cd.get('subject_group') or '',
                'depth_level': cd.get('depth_level') or '',
            })
        return offering
