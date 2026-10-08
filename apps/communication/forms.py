"""Forms for the communication app's HTML pages.

Bootstrap-styled (the MyHub theme expects ``form-control`` / ``form-select``),
mirroring :mod:`apps.myhub.forms`.
"""

from django import forms

from . import models


class _StyledForm(forms.ModelForm):
    """Apply Bootstrap classes + placeholders to every field."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, (forms.CheckboxInput, forms.CheckboxSelectMultiple, forms.RadioSelect)):
                css = 'form-check-input'
            elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
                css = 'form-control form-select'
            else:
                css = 'form-control'
            widget.attrs['class'] = (widget.attrs.get('class', '') + ' ' + css).strip()
            if isinstance(widget, (forms.TextInput, forms.Textarea, forms.EmailInput, forms.URLInput)):
                widget.attrs.setdefault('placeholder', field.label)


class _DateTimeInput(forms.DateTimeInput):
    input_type = 'datetime-local'

    def __init__(self, attrs=None, format='%Y-%m-%dT%H:%M'):
        super().__init__(attrs, format)


class MeetingRoomForm(_StyledForm):
    """Create / schedule a video-audio meeting or class session."""

    class Meta:
        model = models.MeetingRoom
        fields = ['title', 'description', 'group', 'scheduled_start', 'scheduled_end',
                  'is_recurring', 'recurrence', 'requires_login']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'scheduled_start': _DateTimeInput(),
            'scheduled_end': _DateTimeInput(),
        }


class AnnouncementForm(_StyledForm):
    """Compose a broadcast notification (admin / staff only).

    The audience is either *everyone* or any mix of institutions, programmes,
    cohorts, modules and named people; both can be narrowed by role. ``when``
    decides what the submit does: send now, schedule for later, or save a draft.
    """

    WHEN_NOW, WHEN_LATER, WHEN_DRAFT = 'now', 'later', 'draft'
    when = forms.ChoiceField(choices=[(WHEN_NOW, 'Send now'), (WHEN_LATER, 'Schedule for later'),
                                      (WHEN_DRAFT, 'Save as draft')],
                             initial=WHEN_NOW, widget=forms.RadioSelect)
    roles = forms.MultipleChoiceField(choices=models.Announcement.ROLE_CHOICES, required=False,
                                      widget=forms.CheckboxSelectMultiple,
                                      label='Only these roles')

    class Meta:
        model = models.Announcement
        fields = ['title', 'body', 'level', 'url', 'url_label', 'media_url', 'audience', 'roles',
                  'institutions', 'programmes', 'cohorts', 'modules', 'users', 'include_parents',
                  'is_important', 'send_email', 'scheduled_for']
        labels = {
            'title': 'Headline', 'body': 'Message', 'level': 'Tone',
            'url': 'Link', 'url_label': 'Link button text', 'media_url': 'Video link',
            'include_parents': 'Copy parents / guardians',
            'is_important': 'Important — reach people who muted announcements',
            'send_email': 'Also send by e-mail', 'scheduled_for': 'Send at',
        }
        widgets = {
            'body': forms.Textarea(attrs={'rows': 7}),
            'audience': forms.RadioSelect,
            'institutions': forms.SelectMultiple(attrs={'data-pick': 'institution'}),
            'programmes': forms.SelectMultiple(attrs={'data-pick': 'programme'}),
            'cohorts': forms.SelectMultiple(attrs={'data-pick': 'cohort'}),
            'modules': forms.SelectMultiple(attrs={'data-pick': 'module'}),
            'users': forms.SelectMultiple(attrs={'data-pick': 'person'}),
            'scheduled_for': _DateTimeInput(),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        from django.contrib.auth import get_user_model
        from apps.learning.models import Cohort, Institution, Programme, ProgrammeModule

        A = models.Announcement
        self.fields['audience'].choices = [(A.AUDIENCE_ALL, 'Everyone'),
                                           (A.AUDIENCE_TARGETED, 'Choose who')]
        if self.instance.pk and self.instance.audience not in (A.AUDIENCE_ALL, A.AUDIENCE_TARGETED):
            self.initial['audience'] = A.AUDIENCE_TARGETED
        self.fields['institutions'].queryset = Institution.objects.filter(is_active=True).order_by('name')
        self.fields['programmes'].queryset = (Programme.objects.filter(is_active=True)
                                              .select_related('institution').order_by('institution__name', 'name'))
        self.fields['cohorts'].queryset = (Cohort.objects.filter(is_active=True)
                                           .select_related('programme').order_by('programme__name', 'code'))
        self.fields['modules'].queryset = (ProgrammeModule.objects.filter(is_active=True)
                                           .select_related('programme', 'module').order_by('programme__name', 'code'))
        # People are picked through a search box, so only the chosen ones need
        # rendering as <option>s; validation still checks every active account.
        User = get_user_model()
        self.fields['users'].queryset = User.objects.filter(is_active=True)
        if self.is_bound:
            chosen = self.data.getlist('users')
        elif self.initial.get('users'):
            chosen = list(self.initial['users'])     # deep link (?user=) or a duplicate
        else:
            chosen = list(self.instance.users.values_list('pk', flat=True)) if self.instance.pk else []
        from .broadcast import person_label
        self.fields['users'].widget.choices = [
            (u.pk, person_label(u))
            for u in User.objects.filter(pk__in=[c for c in chosen if str(c).isdigit()]).select_related('profile')]
        for name in ('institutions', 'programmes', 'cohorts', 'modules', 'users'):
            self.fields[name].required = False
        self.fields['level'].choices = [('info', 'Update'), ('success', 'Good news'),
                                        ('warning', 'Reminder'), ('error', 'Urgent')]
        self.fields['title'].widget.attrs['placeholder'] = 'e.g. New worksheet available for Grade 10 Mathematics'
        self.fields['body'].widget.attrs['placeholder'] = 'Write your message. Links are made clickable.'
        self.fields['url'].widget.attrs['placeholder'] = '/learning/... or https://...'
        self.fields['url_label'].widget.attrs['placeholder'] = 'Open the worksheet'
        self.fields['media_url'].widget.attrs['placeholder'] = 'https://youtu.be/...'
        if self.instance.pk and self.instance.status == A.STATUS_SCHEDULED:
            self.initial.setdefault('when', self.WHEN_LATER)
        self._scope_for_educator(user)

    def _scope_for_educator(self, user):
        """An educator notifies only their own audience: the subjects they
        teach, the grades those are in, the classes they are class teacher of
        and the people they may reach (their learners, those learners' parents,
        colleagues and the office) — never the whole school."""
        from core.roles import role_of_user
        self.educator_scoped = role_of_user(user) == 'educator'
        if not self.educator_scoped:
            return
        from core.scoping import directory_users
        from apps.learning.models import Programme
        person = getattr(user, 'profile', None)
        A = models.Announcement
        taught = person.taught_modules.filter(is_active=True) if person else self.fields['modules'].queryset.none()
        classes = person.classes_taught.filter(is_active=True) if person else self.fields['cohorts'].queryset.none()
        self.fields['audience'].choices = [(A.AUDIENCE_TARGETED, 'Choose who')]
        self.initial['audience'] = A.AUDIENCE_TARGETED
        self.fields['institutions'].queryset = self.fields['institutions'].queryset.none()
        self.fields['modules'].queryset = self.fields['modules'].queryset.filter(pk__in=taught.values('pk'))
        self.fields['cohorts'].queryset = self.fields['cohorts'].queryset.filter(pk__in=classes.values('pk'))
        self.fields['programmes'].queryset = self.fields['programmes'].queryset.filter(
            pk__in=Programme.objects.filter(modules__in=taught).values('pk')
        ) | self.fields['programmes'].queryset.filter(pk__in=classes.values('programme_id'))
        self.fields['users'].queryset = directory_users(user)

    def clean_url(self):
        url = (self.cleaned_data.get('url') or '').strip()
        if url and not (url.startswith('/') and not url.startswith('//')) \
                and not url.lower().startswith(('http://', 'https://')):
            raise forms.ValidationError('Use a page on this site (starting with /) or a full https:// link.')
        return url

    def clean(self):
        cleaned = super().clean()
        A = models.Announcement
        if getattr(self, 'educator_scoped', False) and cleaned.get('audience') != A.AUDIENCE_TARGETED:
            self.add_error('audience', 'Teachers send notifications to their own subjects, grades, '
                                       'classes or learners — choose who.')
        if cleaned.get('audience') == A.AUDIENCE_TARGETED and not any(
                cleaned.get(n) for n in ('institutions', 'programmes', 'cohorts', 'modules', 'users')):
            self.add_error('audience', 'Pick at least one institution, programme, cohort, module or person.')
        if cleaned.get('when') == self.WHEN_LATER:
            from django.utils import timezone
            when = cleaned.get('scheduled_for')
            if not when:
                self.add_error('scheduled_for', 'Pick when it should go out.')
            elif when <= timezone.now():
                self.add_error('scheduled_for', 'That time has already passed.')
        return cleaned

class DiscussionForm(_StyledForm):
    """Start a discussion / post (Q&A-style)."""

    class Meta:
        model = models.Discussion
        fields = ['title', 'body', 'module', 'tags', 'mentions']
        widgets = {
            'body': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Share your question or topic…'}),
            'mentions': forms.SelectMultiple(attrs={'size': 5}),
        }


class DiscussionReplyForm(_StyledForm):
    """Reply to a discussion."""

    class Meta:
        model = models.DiscussionReply
        fields = ['body']
        widgets = {'body': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Write a reply…'})}


# ---------------------------------------------------------------------------
# Attendance
# ---------------------------------------------------------------------------
class ClassSessionForm(_StyledForm):
    """Open a class session that attendance is recorded against."""

    class Meta:
        model = models.ClassSession
        fields = ['module', 'title', 'session_date', 'starts_at', 'ends_at',
                  'meeting', 'late_after_minutes', 'is_open']
        widgets = {
            'session_date': forms.DateInput(attrs={'type': 'date'}),
            'starts_at': _DateTimeInput(),
            'ends_at': _DateTimeInput(),
        }


# ---------------------------------------------------------------------------
# Notification preferences
# ---------------------------------------------------------------------------
class NotificationPreferenceForm(_StyledForm):
    """Per-user notification & reminder settings.

    The channel tick-boxes are independent: take e-mail, WhatsApp, both or
    neither. The in-app bell is always on and is not offered as a choice —
    it is the platform's own record of what it told you.
    """

    class Meta:
        model = models.NotificationPreference
        fields = ['email_enabled', 'whatsapp_enabled', 'browser_enabled',
                  'notify_mentions', 'notify_messages', 'notify_announcements',
                  'notify_deadlines', 'notify_meetings', 'notify_grades',
                  'notify_content', 'notify_assessments', 'notify_tasks', 'notify_weekly',
                  'digest', 'quiet_hours_start', 'quiet_hours_end', 'reminder_lead_minutes']
        labels = {
            'email_enabled': 'Send me a copy by e-mail',
            'whatsapp_enabled': 'Send me a copy on WhatsApp',
        }
        widgets = {
            'quiet_hours_start': forms.TimeInput(attrs={'type': 'time'}),
            'quiet_hours_end': forms.TimeInput(attrs={'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Tell people where WhatsApp will land, and say so plainly when there is
        # no number on file — a tick-box that silently does nothing is worse
        # than one that is not offered.
        person = getattr(getattr(self.instance, 'user', None), 'profile', None)
        number = getattr(getattr(person, 'contact', None), 'primary_phone', '')
        field = self.fields['whatsapp_enabled']
        if number:
            field.help_text = (f'Sent to {number} — the number on your contact details. '
                               'Change it under Contact on your profile.')
        else:
            field.help_text = ('Add a phone number under Contact on your profile first — '
                               'there is nowhere to send it yet.')


# ---------------------------------------------------------------------------
# Collaboration workspaces
# ---------------------------------------------------------------------------
class WorkspaceForm(_StyledForm):
    class Meta:
        model = models.Workspace
        fields = ['name', 'description', 'module', 'members']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'members': forms.SelectMultiple(attrs={'size': 6}),
        }


class WorkspaceFileForm(_StyledForm):
    class Meta:
        model = models.WorkspaceFile
        fields = ['file', 'title']


class WorkspaceNoteForm(_StyledForm):
    class Meta:
        model = models.WorkspaceNote
        fields = ['title', 'body', 'pinned']
        widgets = {'body': forms.Textarea(attrs={'rows': 5})}
