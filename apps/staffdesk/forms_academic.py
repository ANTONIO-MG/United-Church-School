"""Forms for the academic half of the staff desk: grades, certificates, at-risk
triage and the content-import runner.

The import forms never take a free-typed path. Every file or folder a command
may be pointed at is offered as a choice built from a fixed set of roots on the
server (see :func:`pack_choices` / :func:`folder_choices`), so the page cannot be
used to make a management command read an arbitrary file.
"""

import json
from pathlib import Path

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model

from apps.learning.models import Institution, Programme, ProgrammeModule
from apps.reports.models import Certificate, ModuleWeighting

User = get_user_model()


def _offerings():
    return (ProgrammeModule.objects.filter(is_active=True)
            .select_related('programme__institution').order_by('programme__code', 'code'))


class OfferingChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f'{obj.reference} — {obj.name or obj.module}'


class StudentChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        name = (obj.get_full_name() or '').strip()
        return f'{name} <{obj.email}>' if name else obj.email


# ---------------------------------------------------------------------------
# Grades & certificates
# ---------------------------------------------------------------------------
class GradeOverrideForm(forms.Form):
    value = forms.DecimalField(label='Final mark (%)', min_value=0, max_value=100,
                               max_digits=5, decimal_places=2)
    reason = forms.CharField(label='Reason', widget=forms.Textarea(attrs={'rows': 3}),
                             help_text='Kept on the grade and shown to staff. Required.')


class ModuleWeightingForm(forms.ModelForm):
    """ModelForm over ModuleWeighting — the model's own ``clean`` enforces the
    100% total, and the grade scale is edited as JSON."""

    grade_scale = forms.JSONField(
        required=False, widget=forms.Textarea(attrs={'rows': 4, 'class': 'font-monospace'}),
        help_text='Optional, e.g. [{"min": 75, "letter": "A"}, {"min": 0, "letter": "F"}]. '
                  'Leave blank for the default A–F scale.')

    class Meta:
        model = ModuleWeighting
        fields = ['assignments_pct', 'quizzes_pct', 'tests_pct', 'exams_pct', 'tasks_pct',
                  'pass_mark_pct', 'extra_credit_pct', 'grade_scale']
        labels = {
            'assignments_pct': 'Assignments %', 'quizzes_pct': 'Quizzes %', 'tests_pct': 'Tests %',
            'exams_pct': 'Exams %', 'tasks_pct': 'Study tasks %', 'pass_mark_pct': 'Pass mark %',
            'extra_credit_pct': 'Extra-credit cap %',
        }

    def clean_grade_scale(self):
        scale = self.cleaned_data.get('grade_scale') or []
        if not isinstance(scale, list):
            raise forms.ValidationError('The scale must be a list of {"min", "letter"} bands.')
        for band in scale:
            if not isinstance(band, dict) or 'min' not in band or 'letter' not in band:
                raise forms.ValidationError('Each band needs a "min" and a "letter".')
            try:
                float(band['min'])
            except (TypeError, ValueError):
                raise forms.ValidationError(f'“{band["min"]}” is not a number.')
        return scale

    def clean(self):
        cleaned = super().clean()
        for name in ('pass_mark_pct', 'extra_credit_pct'):
            if (cleaned.get(name) or 0) > 100:
                self.add_error(name, 'At most 100.')
        return cleaned


class CertificateIssueForm(forms.Form):
    KIND_MODULE, KIND_PROGRAMME = 'module', 'programme'

    student = StudentChoiceField(queryset=User.objects.none())
    kind = forms.ChoiceField(choices=[(KIND_MODULE, 'Module'), (KIND_PROGRAMME, 'Programme')],
                             initial=KIND_MODULE)
    module = OfferingChoiceField(queryset=ProgrammeModule.objects.none(), required=False,
                                 help_text='For a subject certificate.')
    programme = forms.ModelChoiceField(queryset=Programme.objects.none(), required=False,
                                       help_text='For a grade certificate.')
    title = forms.CharField(max_length=200, required=False,
                            help_text='Leave blank for the standard wording.')
    final_mark = forms.DecimalField(min_value=0, max_value=100, max_digits=5, decimal_places=2,
                                    required=False,
                                    help_text="Blank = the learner's current mark (grade certificate: the "
                                              'average across its subjects).')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student'].queryset = (User.objects.filter(profile__user_type='student', is_active=True)
                                           .order_by('first_name', 'last_name', 'email'))
        self.fields['module'].queryset = _offerings()
        self.fields['programme'].queryset = (Programme.objects.filter(is_active=True)
                                             .select_related('institution').order_by('code'))

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('kind') == self.KIND_MODULE and not cleaned.get('module'):
            self.add_error('module', 'Choose the subject this certificate is for.')
        if cleaned.get('kind') == self.KIND_PROGRAMME and not cleaned.get('programme'):
            self.add_error('programme', 'Choose the grade this certificate is for.')
        return cleaned


class ReasonForm(forms.Form):
    reason = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}))


# ---------------------------------------------------------------------------
# At-risk triage
# ---------------------------------------------------------------------------
class TriageForm(forms.Form):
    ACTIONS = ['ack', 'resolve', 'reopen', 'note']

    action = forms.ChoiceField(choices=[(a, a) for a in ACTIONS])
    note = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 2}))

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('action') == 'note' and not (cleaned.get('note') or '').strip():
            self.add_error('note', 'Write the note first.')
        return cleaned


class NotifyForm(forms.Form):
    title = forms.CharField(max_length=200)
    body = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}))


# ---------------------------------------------------------------------------
# Content imports
# ---------------------------------------------------------------------------
def _base_dir():
    return Path(settings.BASE_DIR)


def source_roots():
    """Folders on the server that hold source documents for import_content_folder.

    ``settings.CONTENT_SOURCE_ROOTS`` wins when set; otherwise the conventional
    ``content_sources/`` beside the project and under MEDIA_ROOT.
    """
    configured = getattr(settings, 'CONTENT_SOURCE_ROOTS', None)
    roots = configured or [_base_dir() / 'content_sources', Path(settings.MEDIA_ROOT) / 'content_sources']
    return [Path(r) for r in roots if Path(r).is_dir()]


def pack_choices():
    """Every ``thrive-pack`` JSON file the import_content_pack form may offer."""
    base = _base_dir()
    files = []
    for folder in (base / 'fixtures' / 'content_packs', base / 'core' / 'seed_packs'):
        files.extend(sorted(folder.glob('*.json')) if folder.is_dir() else [])
    for root in source_roots():
        # Packs drafted by import_content_folder land in <folder>/_packs/.
        files.extend(sorted(root.glob('*/_packs/*.json')))
    return [(str(p), _relative(p)) for p in files]


def folder_choices():
    return [(str(p), _relative(p)) for root in source_roots()
            for p in sorted(root.iterdir()) if p.is_dir() and not p.name.startswith(('.', '_'))]


def seed_pack_names():
    folder = _base_dir() / 'core' / 'seed_packs'
    return sorted(p.name for p in folder.glob('*.json')) if folder.is_dir() else []


def _relative(path):
    try:
        return str(Path(path).relative_to(_base_dir()))
    except ValueError:
        return str(path)


def _code_choices(qs, field, blank='All'):
    codes = sorted({c for c in qs.values_list(field, flat=True) if c})
    return [('', blank)] + [(c, c) for c in codes]


class _ScopeMixin(forms.Form):
    """The institution / programme / module filters scaffold_module_schedule and
    sync_module_chats share — choices, never typed codes."""

    institution = forms.ChoiceField(required=False)
    programme = forms.ChoiceField(required=False)
    module = forms.ChoiceField(required=False, label='Subject offering code')
    dry_run = forms.BooleanField(required=False, initial=True, label='Dry run — report only, change nothing')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['institution'].choices = _code_choices(Institution.objects.filter(is_active=True), 'code')
        self.fields['programme'].choices = _code_choices(Programme.objects.filter(is_active=True), 'code')
        self.fields['module'].choices = _code_choices(ProgrammeModule.objects.filter(is_active=True), 'code')

    def scope_args(self):
        d = self.cleaned_data
        argv = []
        for name in ('institution', 'programme', 'module'):
            if d.get(name):
                argv += [f'--{name}', d[name]]
        if d.get('dry_run'):
            argv.append('--dry-run')
        return argv


class SeedPacksForm(forms.Form):
    def argv(self):
        return []


class ContentPackForm(forms.Form):
    path = forms.ChoiceField(label='Pack')
    check = forms.BooleanField(required=False, initial=True, label='Validate only — touch nothing')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['path'].choices = pack_choices()

    def argv(self):
        argv = [self.cleaned_data['path']]
        if self.cleaned_data.get('check'):
            argv.append('--check')
        return argv


class ContentFolderForm(forms.Form):
    folder = forms.ChoiceField()
    programme = forms.ChoiceField(help_text='Grade full code every pack belongs to (e.g. UCS-GR10).')
    cohort = forms.CharField(max_length=30, required=False)
    only = forms.CharField(max_length=80, required=False, label='Only this topic directory',
                           help_text='e.g. TAX T5. Blank = every topic.')
    mode = forms.ChoiceField(choices=[
        ('dry_run', 'Dry run — list what would be read'),
        ('draft', 'Draft packs to JSON (uses the model, imports nothing)'),
        ('reuse_import', 'Import packs already drafted (no model)'),
        ('draft_import', 'Draft and import (uses the model)'),
    ], initial='dry_run')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['folder'].choices = folder_choices()
        programmes = Programme.objects.filter(is_active=True).select_related('institution')
        self.fields['programme'].choices = sorted({(p.full_code, p.full_code) for p in programmes})

    def clean_only(self):
        only = (self.cleaned_data.get('only') or '').strip()
        if '/' in only or '\\' in only or '..' in only:
            raise forms.ValidationError('A topic directory name, not a path.')
        return only

    def argv(self):
        d = self.cleaned_data
        argv = [d['folder'], '--programme', d['programme']]
        if d.get('cohort'):
            argv += ['--cohort', d['cohort']]
        if d.get('only'):
            argv += ['--only', d['only']]
        argv += {
            'dry_run': ['--dry-run'], 'draft': [],
            'reuse_import': ['--reuse', '--import'], 'draft_import': ['--import'],
        }[d['mode']]
        return argv


class ScaffoldScheduleForm(_ScopeMixin):
    weeks_test = forms.IntegerField(min_value=1, max_value=26, initial=4, label='Weeks per test block')
    weeks_exam = forms.IntegerField(min_value=1, max_value=26, initial=6, label='Weeks per exam block')
    with_weeks_from_topics = forms.BooleanField(required=False, label="Name each week after the next study-guide topic")

    def argv(self):
        d = self.cleaned_data
        argv = self.scope_args() + ['--weeks-test', str(d['weeks_test']), '--weeks-exam', str(d['weeks_exam'])]
        if d.get('with_weeks_from_topics'):
            argv.append('--with-weeks-from-topics')
        return argv


class SyncChatsForm(_ScopeMixin):
    def argv(self):
        return self.scope_args()


#: command name -> (form class, title, one-line description, bootstrap icon)
IMPORT_COMMANDS = {
    'import_seed_packs': (SeedPacksForm, 'Import bundled seed packs',
                          'Re-lay the packs in core/seed_packs/ onto the schedule. Idempotent; '
                          'content lands unpublished.', 'bi-box-seam'),
    'import_content_pack': (ContentPackForm, 'Import one content pack',
                            'Validate or import a content-pack JSON file as drafts.', 'bi-filetype-json'),
    'import_content_folder': (ContentFolderForm, 'Draft a folder of documents',
                              'Turn a folder of guides, mocks and solutions into packs, one per topic.',
                              'bi-folder2-open'),
    'scaffold_module_schedule': (ScaffoldScheduleForm, 'Scaffold subject schedules',
                                 'Give offerings the standard four test blocks and two exam blocks. '
                                 'Leaves existing blocks alone.', 'bi-calendar3-week'),
    'sync_module_chats': (SyncChatsForm, 'Sync subject chats',
                          "Create each offering's chat group and reconcile who is in it.", 'bi-chat-dots'),
}


def pretty_json(value):
    return json.dumps(value, indent=2, sort_keys=True, default=str)
