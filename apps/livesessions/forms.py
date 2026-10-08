"""The session scheduler form, and the settings form behind it.

The form's real job is to stop a session being created that nobody can see. The
audience field decides which of the scope pickers matters, and :meth:`clean`
enforces that pairing server-side — the page also hides the irrelevant ones, but
that is a convenience, not the control.

An educator's form is narrowed to the modules they teach, on the field
querysets, so a hand-edited POST cannot schedule a class on somebody else's
module.
"""

from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.communication.models import MeetingRoom

from .models import CalendarSubscription, LiveSessionSettings


class _DateTimeInput(forms.DateTimeInput):
    input_type = 'datetime-local'

    def __init__(self, attrs=None, format='%Y-%m-%dT%H:%M'):
        super().__init__(attrs, format)


class _Styled(forms.ModelForm):
    """Bootstrap classes, matching apps.communication.forms."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, (forms.CheckboxInput, forms.CheckboxSelectMultiple)):
                css = 'form-check-input'
            elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
                css = 'form-control form-select'
            else:
                css = 'form-control'
            widget.attrs['class'] = (widget.attrs.get('class', '') + ' ' + css).strip()


class SessionForm(_Styled):
    """Schedule (or edit) a live session."""

    #: audience → the field that must be filled in for it.
    REQUIRED_SCOPE = {
        MeetingRoom.AUDIENCE_INSTITUTION: 'institution',
        MeetingRoom.AUDIENCE_PROGRAMME: 'programme',
        MeetingRoom.AUDIENCE_COHORT: 'cohort',
        MeetingRoom.AUDIENCE_MODULE: 'module',
    }

    invitees = forms.ModelMultipleChoiceField(
        queryset=get_user_model().objects.none(), required=False,
        widget=forms.SelectMultiple(attrs={'size': 8}),
        help_text='Invite named people. Required for a one-on-one or an invite-only session; '
                  'optional (and additional) for the rest.')

    class Meta:
        model = MeetingRoom
        fields = ['title', 'description', 'session_kind', 'scheduled_start', 'scheduled_end',
                  'audience', 'institution', 'programme', 'cohort', 'module', 'week',
                  'calendar_event', 'record_automatically', 'publish_recording',
                  'is_recurring', 'recurrence']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'scheduled_start': _DateTimeInput(),
            'scheduled_end': _DateTimeInput(),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        User = get_user_model()

        conf = LiveSessionSettings.load()
        self.fields['record_automatically'].initial = conf.auto_record
        self.fields['publish_recording'].initial = conf.publish_recordings

        for name in ('institution', 'programme', 'cohort', 'module', 'week', 'calendar_event'):
            self.fields[name].required = False
        self.fields['week'].help_text = 'Optional — puts the session on the module schedule ' \
                                        'next to the week or topic it covers.'
        self.fields['calendar_event'].help_text = 'Optional — the test or exam this session ' \
                                                  'prepares for or reviews.'

        from core.scoping import is_scoped, taught_module_qs, taught_programmes
        self.is_scoped = bool(user is not None and is_scoped(user))

        if self.is_scoped:
            # An educator schedules on their own modules only, and cannot address
            # the whole platform or a whole institution.
            self.fields['module'].queryset = taught_module_qs(user)
            self.fields['programme'].queryset = taught_programmes(user)
            self.fields['audience'].choices = [
                (value, label) for value, label in MeetingRoom.AUDIENCE_CHOICES
                if value in (MeetingRoom.AUDIENCE_MODULE, MeetingRoom.AUDIENCE_COHORT,
                             MeetingRoom.AUDIENCE_PROGRAMME, MeetingRoom.AUDIENCE_PRIVATE)
            ]
            from apps.learning.models import Cohort, Institution
            self.fields['cohort'].queryset = Cohort.objects.filter(
                programme__in=self.fields['programme'].queryset)
            self.fields['institution'].queryset = Institution.objects.none()
            from core.scoping import taught_students
            self.fields['invitees'].queryset = taught_students(user).order_by('first_name', 'username')
        else:
            self.fields['invitees'].queryset = User.objects.filter(is_active=True) \
                                                   .order_by('first_name', 'username')

    def clean(self):
        cleaned = super().clean()
        audience = cleaned.get('audience')
        start, end = cleaned.get('scheduled_start'), cleaned.get('scheduled_end')

        if start and end and end <= start:
            self.add_error('scheduled_end', 'The session has to end after it starts.')
        if start and not self.instance.pk and start < timezone.now() - timezone.timedelta(minutes=5):
            self.add_error('scheduled_start', 'That start time is in the past.')

        needed = self.REQUIRED_SCOPE.get(audience)
        if needed and not cleaned.get(needed):
            self.add_error(needed, f'Choose the {needed} this session is for.')

        if audience == MeetingRoom.AUDIENCE_PRIVATE and not cleaned.get('invitees'):
            self.add_error('invitees', 'An invite-only session needs at least one invitee.')

        # A week belongs to a module; letting them disagree would file the
        # recording under a module the session was not for.
        week, module = cleaned.get('week'), cleaned.get('module')
        if week and module and week.phase.programme_module_id != module.pk:
            self.add_error('week', 'That week belongs to a different module.')

        return cleaned


class LiveSessionSettingsForm(_Styled):
    """The admin-facing behaviour switches (credentials stay in the environment)."""

    class Meta:
        model = LiveSessionSettings
        exclude = ['updated_at', 'updated_by']

    def clean_reminder_leads(self):
        raw = (self.cleaned_data.get('reminder_leads') or '').strip()
        leads = []
        for chunk in raw.split(','):
            chunk = chunk.strip()
            if not chunk:
                continue
            if not chunk.isdigit() or int(chunk) <= 0:
                raise forms.ValidationError(
                    'Use whole numbers of minutes, separated by commas — e.g. "1440, 30".')
            leads.append(str(int(chunk)))
        return ','.join(leads) or '1440,30'


class CalendarSubscriptionForm(_Styled):
    """Connect an outside calendar by its iCalendar feed URL.

    Validation happens against the *live* feed, not just its shape: a URL that
    parses but is unreachable, private, or not actually a calendar would
    otherwise be saved and then fail quietly in a background job half an hour
    later, with the person long gone from the page.
    """

    class Meta:
        model = CalendarSubscription
        fields = ['name', 'url', 'provider', 'colour', 'blocks_time']
        widgets = {
            'url': forms.URLInput(attrs={
                'placeholder': 'https://calendar.google.com/calendar/ical/…/basic.ics'}),
            'colour': forms.TextInput(attrs={'type': 'color'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields['name'].help_text = 'What to call it on your calendar — "My Outlook diary".'
        self.fields['url'].label = 'Calendar feed address (.ics)'

    def clean_url(self):
        url = (self.cleaned_data.get('url') or '').strip()
        if self.user is not None:
            clash = CalendarSubscription.objects.filter(user=self.user, url=url)
            if self.instance.pk:
                clash = clash.exclude(pk=self.instance.pk)
            if clash.exists():
                raise forms.ValidationError('You have already connected that calendar.')

        from . import ics
        text, error = ics.fetch(url)
        if error:
            raise forms.ValidationError(error)
        if 'BEGIN:VEVENT' not in text:
            # An empty calendar is legitimate — say so rather than refusing it.
            self._empty_feed = True
        return url
