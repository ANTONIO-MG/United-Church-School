"""ModelForms for the shop CRUD / checkout pages.

Mirrors the MyHub theme's styling helpers (Bootstrap ``form-control`` /
``form-select`` and native ``<input type="date">`` pickers) so the shop pages
look identical to the rest of the dashboard.
"""

from django import forms

from core import validators as v

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


class ProductCategoryForm(StyledModelForm):
    class Meta:
        model = models.ProductCategory
        fields = ['name', 'slug', 'description', 'status']
        widgets = {'description': forms.Textarea(attrs={'rows': 3})}


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    """A file input that takes several files and cleans each one.

    ``validators`` run per file, so one oversized PDF in a batch of five names
    that file rather than rejecting the lot with no clue why.
    """

    def __init__(self, *args, file_validators=(), **kwargs):
        kwargs.setdefault('widget', MultipleFileInput())
        kwargs.setdefault('required', False)
        self.file_validators = list(file_validators)
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        files = data if isinstance(data, (list, tuple)) else ([data] if data else [])
        cleaned, errors = [], []
        for upload in files:
            upload = super().clean(upload, initial)
            for validator in self.file_validators:
                try:
                    validator(upload)
                except forms.ValidationError as exc:
                    errors.extend(f'{upload.name}: {message}' for message in exc.messages)
            cleaned.append(upload)
        if errors:
            raise forms.ValidationError(errors)
        return cleaned


class ProductForm(StyledModelForm):
    """Add / edit a product or service.

    The fulfilment type is chosen first and decides which of the sections below
    matter; the template shows only those (``data-for`` on each section). Fields
    for the other types are still posted and saved — harmless, and switching a
    product's type back does not lose what was typed.
    """

    new_files = MultipleFileField(
        label='Add files', file_validators=v.validate_download,
        help_text='PDF, Word, Excel, PowerPoint or ZIP — up to 200 MB each. Select several at once.')
    new_images = MultipleFileField(
        label='Add gallery images', file_validators=v.validate_image,
        help_text='JPG, PNG or WebP, up to 5 MB each.')

    LENGTH_CHOICES = [(30, '30 min'), (45, '45 min'), (60, '1 hour'), (90, '1½ hours'),
                      (120, '2 hours'), (180, '3 hours')]
    BOOKING_SETTINGS = ('buffer_minutes', 'min_notice_hours', 'reschedule_cutoff_hours',
                        'booking_window_days')
    lengths = forms.TypedMultipleChoiceField(
        label='Session lengths students can book', choices=LENGTH_CHOICES, coerce=int,
        required=False, widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = models.Product
        fields = ['fulfilment', 'name', 'category', 'summary', 'description',
                  'price', 'discount_percent', 'image', 'featured', 'status', 'sku',
                  'educator', 'duration', 'level', 'validity_days',
                  'buffer_minutes', 'min_notice_hours', 'reschedule_cutoff_hours', 'booking_window_days',
                  'track_stock', 'stock', 'weight_kg', 'length_cm', 'width_cm', 'height_cm',
                  'institution', 'programme', 'module']
        labels = {
            'fulfilment': 'What are you selling?',
            'discount_percent': 'Discount %',
            'image': 'Cover image',
            'validity_days': 'Access lasts (days)',
            'track_stock': 'Track stock',
            'weight_kg': 'Weight (kg)', 'length_cm': 'Length (cm)',
            'width_cm': 'Width (cm)', 'height_cm': 'Height (cm)',
            'educator': 'Educator / author',
            'buffer_minutes': 'Gap between sessions (min)',
            'min_notice_hours': 'Book at least (hours ahead)',
            'reschedule_cutoff_hours': 'Reschedule until (hours before)',
            'booking_window_days': 'Bookable up to (days ahead)',
        }
        widgets = {
            'fulfilment': forms.RadioSelect,
            'description': forms.Textarea(attrs={'rows': 6}),
            'summary': forms.TextInput(attrs={'placeholder': 'One line shown on the product card'}),
            'price': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'discount_percent': forms.NumberInput(attrs={'step': '0.5', 'min': '0', 'max': '100'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fulfilment'].widget.attrs['class'] = 'btn-check'
        self.fields['sku'].required = False
        self.fields['sku'].help_text = 'Leave blank to generate one.'
        self.fields['lengths'].initial = self.instance.lengths
        # Session settings have sensible model defaults; only a 1-on-1 needs them.
        for name in self.BOOKING_SETTINGS:
            self.fields[name].required = False
        self.fields['lengths'].widget.attrs['class'] = 'form-check-input'

    def save(self, commit=True):
        product = super().save(commit=False)
        lengths = self.cleaned_data.get('lengths')
        if lengths:
            product.session_lengths = ','.join(str(m) for m in sorted(lengths))
        if commit:
            product.save()
            self.save_m2m()
        return product

    def clean(self):
        data = super().clean()
        for name in self.BOOKING_SETTINGS:
            if data.get(name) is None:
                data[name] = models.Product._meta.get_field(name).default
        if data.get('fulfilment') == models.Product.FULFIL_BOOKING and not data.get('lengths'):
            self.add_error('lengths', 'Choose at least one session length.')
        if data.get('fulfilment') == models.Product.FULFIL_DIGITAL:
            has_files = bool(self.instance.pk and self.instance.deliverables())
            if not has_files and not data.get('new_files'):
                self.add_error('new_files', 'A digital product needs at least one file to deliver.')
        return data


class ProductVariantForm(StyledModelForm):
    class Meta:
        model = models.ProductVariant
        fields = ['name', 'sku', 'price_adjustment', 'stock', 'is_active']
        widgets = {'price_adjustment': forms.NumberInput(attrs={'step': '0.01'})}


ProductVariantFormSet = forms.inlineformset_factory(
    models.Product, models.ProductVariant, form=ProductVariantForm,
    extra=0, can_delete=True)


def educator_choices():
    """People who may run 1-on-1s: educators, and staff/admin who also teach."""
    from apps.accounts.models import Person
    return (Person.objects.filter(user_type__in=('educator', 'staff', 'admin'), user__is_active=True)
            .select_related('user').order_by('user__first_name', 'user__last_name'))


class EducatorRateForm(StyledModelForm):
    class Meta:
        model = models.EducatorRate
        fields = ['educator', 'hourly_rate', 'is_active']
        widgets = {'hourly_rate': forms.NumberInput(attrs={'step': '0.01', 'min': '0'})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['educator'].queryset = educator_choices()


EducatorRateFormSet = forms.inlineformset_factory(
    models.Product, models.EducatorRate, form=EducatorRateForm, extra=0, can_delete=True)


class TimeInput(forms.TimeInput):
    input_type = 'time'

    def __init__(self, attrs=None, format='%H:%M'):
        super().__init__(attrs, format)


class AvailabilityForm(StyledModelForm):
    class Meta:
        model = models.EducatorAvailability
        fields = ['weekday', 'start_time', 'end_time']
        widgets = {'start_time': TimeInput(), 'end_time': TimeInput()}

    def clean(self):
        data = super().clean()
        if data.get('start_time') and data.get('end_time') and data['end_time'] <= data['start_time']:
            self.add_error('end_time', 'Must be after the start.')
        return data


class TimeOffForm(StyledModelForm):
    class Meta:
        model = models.EducatorTimeOff
        fields = ['start', 'end', 'reason']
        widgets = {'start': DateTimeInput(), 'end': DateTimeInput()}

    def clean(self):
        data = super().clean()
        if data.get('start') and data.get('end') and data['end'] <= data['start']:
            self.add_error('end', 'Must be after the start.')
        return data


def availability_formsets(person, data=None):
    from apps.accounts.models import Person
    hours = forms.inlineformset_factory(Person, models.EducatorAvailability, form=AvailabilityForm,
                                        extra=0, can_delete=True)
    away = forms.inlineformset_factory(Person, models.EducatorTimeOff, form=TimeOffForm,
                                       extra=0, can_delete=True)
    return (hours(data, instance=person, prefix='hours'),
            away(data, instance=person, prefix='away'))


class ProductReviewForm(StyledModelForm):
    class Meta:
        model = models.ProductReview
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(choices=[(i, f'{i} ★') for i in range(5, 0, -1)]),
            'comment': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Share your experience…'}),
        }


class OrderForm(StyledModelForm):
    class Meta:
        model = models.Order
        fields = ['buyer', 'status', 'note']
        widgets = {'note': forms.Textarea(attrs={'rows': 3})}


class OrderItemForm(StyledModelForm):
    class Meta:
        model = models.OrderItem
        fields = ['product', 'quantity', 'unit_price', 'expiry_date']
        widgets = {'expiry_date': DateInput()}


class PaymentForm(StyledModelForm):
    class Meta:
        model = models.Payment
        fields = ['amount', 'method', 'status', 'reference', 'paid_at']
        widgets = {'paid_at': DateTimeInput()}


class DiscountForm(StyledModelForm):
    """Admin/staff only — see the staff_required gate on the discount views."""

    class Meta:
        model = models.Discount
        fields = ['name', 'code', 'discount_type', 'value', 'institution', 'programme',
                  'category', 'products', 'starts_at', 'ends_at', 'min_spend',
                  'max_uses', 'is_active']
        widgets = {
            'starts_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'ends_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'code': forms.TextInput(attrs={'placeholder': 'Blank = automatic promotion'}),
            'products': forms.SelectMultiple(attrs={'size': 8}),
        }


class AddressForm(StyledModelForm):
    class Meta:
        model = models.Address
        fields = ['recipient', 'phone', 'street_address', 'complex', 'suburb', 'city',
                  'province', 'postal_code', 'address_type', 'company']
        widgets = {'postal_code': forms.TextInput(attrs={'inputmode': 'numeric', 'maxlength': 4})}

    def clean_postal_code(self):
        code = (self.cleaned_data.get('postal_code') or '').strip()
        if not (code.isdigit() and len(code) == 4):
            raise forms.ValidationError('South African postal codes are 4 digits.')
        return code

    def clean_phone(self):
        phone = ''.join(ch for ch in (self.cleaned_data.get('phone') or '') if ch.isdigit() or ch == '+')
        if len(phone.lstrip('+')) < 9:
            raise forms.ValidationError('Enter a mobile number the courier can SMS.')
        return phone
