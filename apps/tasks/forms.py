"""ModelForms for the tasks pages (Bootstrap-styled to match the theme)."""

from django import forms
from django.db.models import Q

from . import models


class DateTimeInput(forms.DateTimeInput):
    input_type = 'datetime-local'

    def __init__(self, attrs=None, format='%Y-%m-%dT%H:%M'):
        super().__init__(attrs, format)


def _style_fields(form):
    for name, field in form.fields.items():
        widget = field.widget
        if isinstance(widget, (forms.CheckboxInput, forms.RadioSelect, forms.CheckboxSelectMultiple)):
            css = 'form-check-input'
        elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
            css = 'form-control form-select'
        else:
            css = 'form-control'
        existing = widget.attrs.get('class', '')
        widget.attrs['class'] = (existing + ' ' + css).strip()
        if isinstance(widget, (forms.TextInput, forms.Textarea, forms.EmailInput,
                               forms.NumberInput, forms.URLInput)):
            widget.attrs.setdefault('placeholder', field.label)


class StyledModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style_fields(self)


class TaskForm(StyledModelForm):
    """Create/edit a task, narrowed to what the author may actually reach.

    Passing ``user`` filters every target dropdown — who it is for *and* what it
    delivers — to that person's teaching audience. Because the filtering is done
    by replacing each field's ``queryset``, Django re-validates the POST against
    the same narrowed set, so an educator cannot assign work to a class they do
    not teach even by editing the HTML. Admin/staff get the unfiltered form.
    """

    class Meta:
        model = models.Task
        fields = ['title', 'description', 'assign_to', 'assignee', 'module', 'programme', 'priority', 'due_date', 'max_score',
                  'attachment', 'lesson', 'assessment', 'status']
        widgets = {
            'due_date': DateTimeInput(),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        if user is None:
            return

        from core.scoping import (
            is_scoped, taught_people, taught_programmes, taught_module_qs,
        )
        if not is_scoped(user):
            return

        modules = taught_module_qs(user)
        self.fields['module'].queryset = modules
        self.fields['programme'].queryset = taught_programmes(user)
        self.fields['assignee'].queryset = taught_people(user)

        # …and the same for the activity a task delivers.
        from apps.assessments.models import Assessment
        from apps.learning.models import Lesson
        self.fields['lesson'].queryset = Lesson.objects.filter(module__in=modules)
        self.fields['assessment'].queryset = Assessment.objects.filter(module__in=modules)

        # "All users" is an institution-wide broadcast — not an educator's to make.
        self.fields['assign_to'].choices = [
            (value, label) for value, label in models.Task.ASSIGN_CHOICES
            if value != models.Task.ASSIGN_ALL
        ]

    def clean(self):
        cleaned = super().clean()
        assign_to = cleaned.get('assign_to')
        # The target matching ``assign_to`` must actually be filled in, otherwise
        # the fan-out silently resolves to nobody.
        required = {
            models.Task.ASSIGN_USER: 'assignee',
            models.Task.ASSIGN_SUBJECT: 'module',
            models.Task.ASSIGN_PROGRAMME: 'programme',
        }.get(assign_to)
        if required and not cleaned.get(required):
            self.add_error(required, 'Pick who this task is for.')
        return cleaned


class AssignmentProgressForm(StyledModelForm):
    """An assignee updates their own progress (no scoring)."""

    class Meta:
        model = models.TaskAssignment
        fields = ['status', 'progress', 'feedback']
        widgets = {'feedback': forms.Textarea(attrs={'rows': 2})}


class GradeForm(StyledModelForm):
    """Staff / educators grade an assignment."""

    class Meta:
        model = models.TaskAssignment
        fields = ['score', 'status', 'feedback']
        widgets = {'feedback': forms.Textarea(attrs={'rows': 2})}
