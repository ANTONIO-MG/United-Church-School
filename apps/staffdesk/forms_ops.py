"""Forms for the ops pages: audit filters, appeal decisions, parent links."""

from django import forms
from django.contrib.auth import get_user_model

from apps.accounts.models import ActivityLog, ParentLink
from core.roles import role_of_user


class AuditFilterForm(forms.Form):
    """GET filters for the audit log. Every field is optional."""

    user = forms.CharField(required=False, label='User')
    action = forms.ChoiceField(required=False, choices=[('', 'Any action')] + ActivityLog.ACTION_CHOICES)
    date_from = forms.DateField(required=False, label='From', widget=forms.DateInput(attrs={'type': 'date'}))
    date_to = forms.DateField(required=False, label='To', widget=forms.DateInput(attrs={'type': 'date'}))
    q = forms.CharField(required=False, label='Text')


class AppealDecisionForm(forms.Form):
    decision = forms.ChoiceField(choices=[('approve', 'Approve'), ('deny', 'Deny')])
    note = forms.CharField(required=False, max_length=1000, widget=forms.Textarea(attrs={'rows': 2}))


class ParentLinkForm(forms.Form):
    """Link a parent account to a student account, both found by e-mail.

    E-mail rather than a dropdown because the student list runs to hundreds; the
    page offers a datalist of addresses so it still autocompletes.
    """

    parent_email = forms.EmailField(label='Parent e-mail')
    student_email = forms.EmailField(label='Student e-mail')
    relationship = forms.CharField(required=False, max_length=60)

    def _user(self, field, role):
        User = get_user_model()
        user = User.objects.filter(email__iexact=self.cleaned_data[field]).first()
        if user is None:
            self.add_error(field, 'No account uses that e-mail.')
        elif role_of_user(user) != role:
            self.add_error(field, f'That account is not a {role}.')
        else:
            return user
        return None

    def clean(self):
        data = super().clean()
        if self.errors:
            return data
        parent = self._user('parent_email', 'parent')
        student = self._user('student_email', 'student')
        if parent and student:
            if ParentLink.objects.filter(parent=parent, student=student).exists():
                raise forms.ValidationError('Those two accounts are already linked.')
            if not ParentLink.can_add_parent(student):
                raise forms.ValidationError(
                    f'That student already has {ParentLink.MAX_PER_STUDENT} parents linked — '
                    'remove one first.')
        data['parent'], data['student'] = parent, student
        return data
