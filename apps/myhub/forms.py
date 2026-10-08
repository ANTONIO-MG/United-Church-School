"""Forms for the calendar.

Once this held a ModelForm per MyHub CRUD page — professors, students, courses,
library, fees, holidays, CMS, blog. Those models and their pages are gone; what
is left is the event form the calendar posts to.
"""

from django import forms

from . import models


class DateInput(forms.DateInput):
    input_type = 'date'

    def __init__(self, attrs=None, format='%Y-%m-%d'):
        super().__init__(attrs, format)


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
        elif isinstance(widget, forms.FileInput):
            css = 'form-control'
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


class EventForm(StyledModelForm):
    class Meta:
        model = models.Event
        fields = ['title', 'start', 'end', 'all_day', 'location', 'color', 'description']
        widgets = {
            'start': DateTimeInput(), 'end': DateTimeInput(),
            'description': forms.Textarea(attrs={'rows': 3}),
        }
