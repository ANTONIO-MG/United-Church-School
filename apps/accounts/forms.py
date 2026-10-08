"""Forms for the accounts community pages (profile / settings / groups).

Bootstrap-styled to match the dashboard theme (same helper as MyHub).
"""

from allauth.account.forms import ResetPasswordKeyForm, SignupForm
from captcha.fields import CaptchaField
from django import forms
from django.utils import timezone

from core import countries

from . import models


class DateInput(forms.DateInput):
    input_type = 'date'

    def __init__(self, attrs=None, format='%Y-%m-%d'):
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


class ProfileForm(StyledModelForm):
    """A user editing their own profile on the settings page.

    Deliberately *only* the profile picture. Legal name, gender and date of
    birth are identity: they are captured at registration, they appear on
    results and certificates, and a candidate quietly editing them after the
    fact would break the link between an account and the person who sat the
    assessments. Those need an administrator, so they render read-only on the
    settings page and are not in this form at all — a field that is merely
    ``disabled`` in the template is still POST-able.
    """

    class Meta:
        model = models.Person
        fields = ['profile_picture']


class UserSettingsForm(StyledModelForm):
    """Preferences & privacy toggles the user controls on the settings page.

    Bound to :class:`accounts.models.UserSettings`; the closure bookkeeping
    fields are intentionally excluded (they are driven by the close-account
    flow, not edited here). Prepopulates from the current values because it is
    a ``ModelForm`` bound to the user's existing ``UserSettings`` instance.

    ``email_digest`` is not offered here — bundling frequency lives with the
    rest of the delivery choices on the notification-preferences page, and
    having it in two places meant two answers to one question.
    """

    #: Offered in the picker, newest-first by how often our candidates need them.
    #: The full IANA list is ~600 entries — a dropdown nobody can use. Anything
    #: outside this list can still be stored (the field is a plain CharField and
    #: the middleware validates whatever it finds), it is just not offered here.
    COMMON_ZONES = [
        'Africa/Johannesburg', 'Africa/Lagos', 'Africa/Nairobi', 'Africa/Cairo',
        'Africa/Accra', 'Africa/Harare', 'Africa/Gaborone', 'Africa/Windhoek',
        'Europe/London', 'Europe/Amsterdam', 'Europe/Berlin', 'Europe/Dublin',
        'Asia/Dubai', 'Asia/Kolkata', 'Asia/Shanghai', 'Asia/Singapore',
        'Australia/Perth', 'Australia/Sydney',
        'America/New_York', 'America/Chicago', 'America/Denver', 'America/Los_Angeles',
        'America/Toronto', 'America/Sao_Paulo', 'UTC',
    ]

    class Meta:
        model = models.UserSettings
        fields = ['profile_visibility', 'show_email', 'show_activity',
                  'allow_messages', 'theme', 'language', 'timezone']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # A dropdown, not a free-text box: a typo in a zone name would silently
        # fall back to the platform default and quietly show everyone the wrong
        # session time, which is the one failure this field exists to prevent.
        from django.conf import settings as django_settings
        default = django_settings.TIME_ZONE
        self.fields['timezone'] = forms.ChoiceField(
            label='Time zone', required=False,
            choices=[('', f'Platform default ({default})')] + [(z, z.replace('_', ' '))
                                                               for z in self.COMMON_ZONES],
            help_text='Session times, reminders and the calendar are shown in this zone.',
            widget=forms.Select(attrs={'class': 'form-control form-select'}),
        )


class CloseAccountForm(forms.Form):
    """Verify a member really wants to close their account.

    The user must (a) tick the acknowledgement box and (b) confirm by entering
    their current password, their e-mail address, or the literal word
    ``CLOSE``. The check is done against the specific user passed in.
    """

    confirm = forms.CharField(
        label='Confirm',
        widget=forms.PasswordInput(render_value=False),
        help_text='Type your password, your e-mail address, or the word CLOSE to confirm.',
    )
    understand = forms.BooleanField(
        label="I understand my account will be closed and purged after 30 days.",
        required=True,
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        _style_fields(self)

    def clean_confirm(self):
        value = (self.cleaned_data.get('confirm') or '').strip()
        email = (self.user.email or '').strip()
        username = (self.user.get_username() or '').strip()
        ok = (
            value == 'CLOSE'
            or (email and value.lower() == email.lower())
            or (username and value.lower() == username.lower())
            or self.user.check_password(value)
        )
        if not ok:
            raise forms.ValidationError(
                'That did not match. Enter your password, your e-mail, or the word CLOSE.')
        return value


# ---------------------------------------------------------------------------
# Sign-up
# ---------------------------------------------------------------------------
# Bump when the Terms & Conditions text changes materially, so existing consent
# records stay attributable to the wording that was actually agreed to.
TERMS_VERSION = '2026-07'


class UCSResetPasswordKeyForm(ResetPasswordKeyForm):
    """allauth's "choose a new password" form, plus a new-password-must-differ rule.

    allauth checks that the two boxes match and that the password passes
    ``AUTH_PASSWORD_VALIDATORS``, but it will happily let someone "reset" to the
    password they already had — which is a no-op that looks like a successful
    reset, and leaves a compromised password in place.
    """

    def clean_password1(self):
        # ResetPasswordKeyForm defines no clean_password1 of its own — the field's
        # own SetPasswordField.clean() has already applied AUTH_PASSWORD_VALIDATORS
        # by this point, so read the cleaned value rather than calling super().
        password = self.cleaned_data.get('password1')
        if self.user and password and self.user.check_password(password):
            raise forms.ValidationError(
                'That is already your current password. Please choose a different one.')
        return password


class UCSSignupForm(SignupForm):
    """The hub's sign-up form: allauth's ``SignupForm`` plus recorded consent.

    Sign-up deliberately runs through allauth rather than ``create_user`` so the
    project's ``AUTH_PASSWORD_VALIDATORS``, the password-confirm check and the
    e-mail-format/uniqueness rules all actually apply — they are configured in
    ``ACCOUNT_SIGNUP_FIELDS`` and were previously bypassed entirely.

    The Terms & Conditions box is a real, ``required`` form field: the checkbox
    it replaces existed only in the template with no ``name``, so it was never
    posted and never enforced. Acceptance is stamped onto the user's Person
    profile, because an un-recorded tickbox proves nothing after the fact.
    """

    terms = forms.BooleanField(
        required=True,
        label='I agree to the Terms & Conditions',
        error_messages={
            'required': 'Please accept the Terms & Conditions to create your account.',
        },
    )

    # Math CAPTCHA ("3 + 4 = ?"). A self-hosted, keyless bot check that validates
    # itself against the CaptchaStore — see the CAPTCHA_* settings. In tests set
    # CAPTCHA_TEST_MODE=True and answer 'PASSED'.
    captcha = CaptchaField(
        label='Solve the sum',
        error_messages={'invalid': 'That answer was wrong — solve the sum and try again.'},
    )

    def save(self, request):
        user = super().save(request)
        # The Person profile is created by a post_save signal on User.
        profile = getattr(user, 'profile', None)
        if profile is not None:
            profile.terms_accepted_at = timezone.now()
            profile.terms_version = TERMS_VERSION
            profile.save(update_fields=['terms_accepted_at', 'terms_version'])
        return user


# Roles a person can self-select at registration (admin/staff are assigned by an
# administrator, never chosen here).
SELF_REGISTER_ROLES = [
    ('student', 'Student'),
    ('parent', 'Parent / Guardian'),
    ('educator', 'Educator'),
]


class WizardRegistrationForm(StyledModelForm):
    """One-shot onboarding: role + profile + contact details. The ONE course to
    join is picked separately in the template (``enrol_choice``) and enrols the
    person into all that course's modules — see accounts.services.enrol_person.
    Completing it satisfies the onboarding gates (registered + profile)."""

    user_type = forms.ChoiceField(choices=SELF_REGISTER_ROLES, label='I am registering as')

    class Meta:
        model = models.Person
        fields = ['user_type', 'first_name', 'last_name', 'gender', 'date_of_birth',
                  'phone', 'profile_picture',
                  'enrolled_class', 'child_name']
        widgets = {
            'date_of_birth': DateInput(),
            'enrolled_class': forms.TextInput(attrs={'placeholder': 'e.g. Grade 10 / Year 1'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        for optional in ('child_name', 'gender', 'date_of_birth',
                         'profile_picture', 'enrolled_class'):
            self.fields[optional].required = False

    def clean(self):
        cleaned = super().clean()
        role = cleaned.get('user_type')
        if role == 'parent' and not cleaned.get('child_name'):
            self.add_error('child_name', 'Please name the child/dependant you are registering for.')
        # The course choice for students & educators is a single picker
        # (``enrol_choice``) validated in the register view.
        return cleaned


class CompleteProfileForm(StyledModelForm):
    """Step 2 of onboarding: finish the personal profile before entering the hub."""

    class Meta:
        model = models.Person
        fields = ['first_name', 'last_name', 'gender', 'date_of_birth',
                  'phone', 'profile_picture']
        widgets = {
            'date_of_birth': DateInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True


# ---------------------------------------------------------------------------
# 3-step registration wizard (apps.accounts.views.register / register_course /
# register_review). Step 1 writes to Person + the grouped side-tables. Only the
# "lean" fields are required; everything else is optional and editable later.
# ---------------------------------------------------------------------------
GUARDIAN_RELATIONSHIP_CHOICES = [
    ('parent', 'Parent'), ('guardian', 'Guardian'), ('sponsor', 'Sponsor'),
]


class RegBasicsForm(StyledModelForm):
    """Step 1 · the learner (Person): title, name, gender, date of birth and
    photo. Parents and guardians are captured in full on step 3 (the
    application's family section), so they are not asked for here."""

    class Meta:
        model = models.Person
        fields = ['title', 'first_name', 'last_name', 'gender', 'date_of_birth', 'profile_picture']
        widgets = {'date_of_birth': DateInput()}
        labels = {'first_name': "Learner's first name(s)", 'last_name': "Learner's surname",
                  'profile_picture': 'Learner photo'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for required in ('first_name', 'last_name', 'gender', 'date_of_birth'):
            self.fields[required].required = True
        self.fields['title'].required = False


class ParentRegistrationForm(StyledModelForm):
    """Single-page registration for an invited parent/guardian/sponsor."""
    relationship = forms.CharField(max_length=60, label='Relationship to the student',
                                   help_text='e.g. Mother, Father, Guardian, Sponsor')
    confirm_student = forms.BooleanField(label='Yes, this is the student I am registering for')

    class Meta:
        model = models.Person
        fields = ['first_name', 'last_name', 'phone']
        widgets = {'phone': forms.TextInput(attrs={'type': 'tel', 'placeholder': 'Phone'})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['phone'].required = True


class EducatorRegistrationForm(StyledModelForm):
    """Single-page registration for an invited educator."""
    confirm_programme = forms.BooleanField(label='Yes, this is the programme I will be teaching')

    class Meta:
        model = models.Person
        fields = ['first_name', 'last_name', 'phone']
        widgets = {'phone': forms.TextInput(attrs={'type': 'tel', 'placeholder': 'Phone'})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['phone'].required = True


class AddEducatorForm(forms.Form):
    """Admin/staff: invite an educator to a programme by e-mail."""
    email = forms.EmailField(label="Educator's e-mail address")
    programme = forms.ModelChoiceField(queryset=None, label='Programme they will teach')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.learning.models import Programme
        self.fields['programme'].queryset = (
            Programme.objects.filter(is_active=True)
            .select_related('institution').order_by('institution__name', 'name'))
        _style_fields(self)


class RegContactForm(StyledModelForm):
    """Step 1 · one phone number and a simple area / city / province.

    The number is entered through a country picker: ``phone_country`` holds the
    ISO code (a hidden input the picker drives) and ``primary_phone`` the number
    including its dialling code. There is no separate WhatsApp field — the one
    number is both, which is what the label says.
    """

    class Meta:
        model = models.PersonContact
        fields = ['phone_country', 'primary_phone', 'suburb', 'city', 'province']
        widgets = {
            'phone_country': forms.HiddenInput(),
            'primary_phone': forms.TextInput(attrs={
                'type': 'tel', 'inputmode': 'tel', 'autocomplete': 'tel',
                'placeholder': '+27 82 123 4567',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in ('primary_phone', 'city'):
            self.fields[f].required = True
        self.fields['phone_country'].required = False
        if not (self.initial.get('phone_country') or getattr(self.instance, 'phone_country', '')):
            self.initial['phone_country'] = countries.DEFAULT_COUNTRY

    def clean_primary_phone(self):
        """Normalise to ``+<code> <digits>`` — one space, no punctuation.

        The picker writes the dialling code and the person types the rest, so
        what arrives is a mix of spaces, dashes and brackets. Storing a single
        canonical shape keeps ``tel:`` links and WhatsApp deep-links working.
        """
        raw = (self.cleaned_data.get('primary_phone') or '').strip()
        if not raw:
            return raw
        digits = ''.join(ch for ch in raw if ch.isdigit())
        if not digits:
            raise forms.ValidationError('Enter a phone number.')

        iso = (self.data.get(self.add_prefix('phone_country'))
               or self.initial.get('phone_country') or countries.DEFAULT_COUNTRY)
        code = countries.dial_code(iso).lstrip('+')

        # Whether or not the code survived the typing, end up with exactly one.
        if code and digits.startswith(code):
            national = digits[len(code):]
        elif raw.startswith('+'):
            return f'+{digits}'
        else:
            national = digits
        national = national.lstrip('0')          # drop the trunk prefix (082 → 82)
        if not national:
            raise forms.ValidationError('Enter the number after the country code.')
        return f'+{code} {national}' if code else f'+{national}'


class RegConsentForm(StyledModelForm):
    """Step 1 · POPIA consent. The first two are mandatory to operate the LMS;
    the rest are optional opt-ins. Audit fields (date/version/IP/device) are
    stamped by the view, not the form."""
    class Meta:
        model = models.PersonConsent
        fields = ['privacy_policy_accepted', 'data_processing_accepted', 'marketing_consent',
                  'research_consent', 'ai_personalisation_consent', 'analytics_consent',
                  'cookie_consent', 'data_sharing_consent']
        labels = {
            'privacy_policy_accepted': 'Privacy policy',
            'data_processing_accepted': 'Data processing',
            'marketing_consent': 'Marketing e-mails',
            'research_consent': 'Research use',
            'ai_personalisation_consent': 'AI personalisation',
            'analytics_consent': 'Product analytics',
            'cookie_consent': 'Non-essential cookies',
            'data_sharing_consent': 'Partner data sharing',
        }
        help_texts = {
            'privacy_policy_accepted': "You've read and accept our Privacy Policy. Required.",
            'data_processing_accepted': 'United Church School may process your personal information to run the learning account. Required.',
            'marketing_consent': 'Send me school news, newsletters and platform updates by e-mail.',
            'research_consent': 'Use my anonymised data to improve teaching and for research.',
            'ai_personalisation_consent': 'Personalise my learning experience using AI.',
            'analytics_consent': 'Allow usage analytics that help us improve the platform.',
            'cookie_consent': 'Allow non-essential cookies (preferences, analytics).',
            'data_sharing_consent': 'Share data with the Department of Education and partner organisations where relevant.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['privacy_policy_accepted'].required = True
        self.fields['data_processing_accepted'].required = True


class PrivacyConsentForm(StyledModelForm):
    """Manage the optional POPIA opt-ins on the settings → Privacy & consent tab.
    The two mandatory consents (privacy policy + data processing) are captured at
    registration and shown read-only in the UI; the view re-stamps the audit
    fields (date/version/IP/device) on every save."""
    class Meta:
        model = models.PersonConsent
        fields = ['marketing_consent', 'research_consent', 'ai_personalisation_consent',
                  'analytics_consent', 'cookie_consent', 'data_sharing_consent']
        labels = {
            'marketing_consent': 'Marketing e-mails & updates',
            'research_consent': 'Use my (anonymised) data for research',
            'ai_personalisation_consent': 'Personalise my learning with AI',
            'analytics_consent': 'Product analytics to improve the platform',
            'cookie_consent': 'Non-essential cookies',
            'data_sharing_consent': 'Share my data with partner organisations',
        }


#: The Step-1 sections, in render order:
#: (key, form_class, person_attr | None, section title, icon-file, open?).
#: ``icon`` is a PNG under ``static/images/reg/``. ``person_attr`` is the
#: reverse-OneToOne used to reach/lazily-create the side-table; None means the
#: form is bound to the Person itself.
#:
#: Three sections, all open by default — there is little enough left to ask that
#: collapsing it only hides how short the form is. Education, study preferences,
#: funding and learning tools used to be four more sections; funding and device
#: are now two fields inside "About you" and the rest are gone.
WIZARD_STEP1_FORMS = [
    ('basics', RegBasicsForm, None, 'About the learner', 'about.png', True),
    ('contact', RegContactForm, 'contact', 'Contact details', 'contact.png', True),
    ('consent', RegConsentForm, 'consent', 'Consent (POPIA)', 'consent.png', True),
]


# ---------------------------------------------------------------------------
# Superuser: create an admin / staff / educator account
# ---------------------------------------------------------------------------
STAFF_ROLE_CHOICES = [
    ('admin', 'Administrator'),
    ('staff', 'Staff'),
    ('educator', 'Educator'),
]


class StaffAccountForm(forms.Form):
    """A superuser creates a team account. It is made with a **verified** e-mail
    and a **random password** (e-mailed to them); they set their own password and
    complete their profile on first login."""
    first_name = forms.CharField(max_length=50, label='First name')
    last_name = forms.CharField(max_length=50, label='Last name')
    email = forms.EmailField(label='E-mail address')
    user_type = forms.ChoiceField(choices=STAFF_ROLE_CHOICES, label='Role', initial='staff')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style_fields(self)

    def clean_email(self):
        from django.contrib.auth import get_user_model
        email = (self.cleaned_data['email'] or '').strip().lower()
        if get_user_model().objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with that e-mail address already exists.')
        return email


# ---------------------------------------------------------------------------
# A parent applies for another child from their own account
# ---------------------------------------------------------------------------
#: How the parent is related to the child (stored on ParentLink.relationship)
#: and which guardian section of step 3 they are pre-filled into.
PARENT_RELATIONSHIP_CHOICES = [
    ('Mother', 'Mother'), ('Father', 'Father'), ('Legal guardian', 'Legal guardian'),
    ('Grandparent', 'Grandparent'), ('Other family', 'Other family member'),
    ('Sponsor', 'Sponsor'),
]
RELATIONSHIP_GUARDIAN_ROLE = {'Mother': 'mother', 'Father': 'father'}


def application_year_choices():
    """The school years a parent can apply for: this one and the next."""
    from core import school
    return [(school.YEAR, str(school.YEAR)), (school.YEAR + 1, str(school.YEAR + 1))]


class ParentApplyStartForm(forms.Form):
    """Start an application for a child from a parent account: who the child
    is, how the parent is related, the school year — and, optionally, the
    child's own e-mail address if they should sign in with it."""
    first_name = forms.CharField(max_length=50, label="Child's first name(s)")
    last_name = forms.CharField(max_length=50, label="Child's surname")
    relationship = forms.ChoiceField(choices=PARENT_RELATIONSHIP_CHOICES,
                                     label='Your relationship to the child')
    year = forms.TypedChoiceField(coerce=int, label='School year applied for')
    email = forms.EmailField(
        required=False, label="Child's own e-mail (optional)",
        help_text='Only if your child should sign in with their own e-mail address. '
                  'Leave it blank and a learner login is generated for them.')

    def __init__(self, *args, parent=None, **kwargs):
        self.parent = parent
        super().__init__(*args, **kwargs)
        self.fields['year'].choices = application_year_choices()
        _style_fields(self)

    def clean_email(self):
        from django.contrib.auth import get_user_model
        from django.db.models import Q
        email = (self.cleaned_data.get('email') or '').strip().lower()
        if not email:
            return ''
        if self.parent is not None and email == (self.parent.email or '').lower():
            raise forms.ValidationError(
                "That is your own e-mail address. Use your child's own address, or leave it blank.")
        if get_user_model().objects.filter(Q(email__iexact=email) | Q(username__iexact=email)).exists():
            raise forms.ValidationError(
                'That e-mail address already belongs to an account. If it is your child\'s '
                'existing account, ask the school office to link it to you instead.')
        return email


class LearnerPasswordForm(forms.Form):
    """A parent sets the password for a child's generated learner login."""
    password1 = forms.CharField(label='New password', widget=forms.PasswordInput(
        attrs={'autocomplete': 'new-password'}), strip=False)
    password2 = forms.CharField(label='Repeat the password', widget=forms.PasswordInput(
        attrs={'autocomplete': 'new-password'}), strip=False)

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        _style_fields(self)

    def clean(self):
        from django.contrib.auth import password_validation
        cleaned = super().clean()
        p1, p2 = cleaned.get('password1'), cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            self.add_error('password2', 'The two passwords do not match.')
        elif p1:
            try:
                password_validation.validate_password(p1, self.user)
            except forms.ValidationError as exc:
                self.add_error('password1', exc)
        return cleaned
