"""ModelForms for the finance pages (Bootstrap-styled to match the theme)."""

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


class InvoiceForm(StyledModelForm):
    class Meta:
        model = models.Invoice
        fields = ['customer', 'order', 'issue_date', 'due_date', 'status', 'tax_amount', 'notes']
        widgets = {
            'issue_date': DateInput(), 'due_date': DateInput(),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }


class InvoiceCreateForm(forms.Form):
    """The shared fields of a bulk invoice run (``finance:create-invoice``).

    A plain ``Form`` rather than a ``ModelForm``: the view creates one Invoice
    *per recipient*, so there is no single instance to bind to. What matters is
    that ``due_date`` arrives as a real ``date``. It used to be assigned
    straight from ``request.POST``, and the InvoiceItem post-save signal then
    called ``refresh_status()`` → ``is_overdue``, which compared a ``str`` to a
    ``date`` and raised — so adding a line item to an invoice that had a due
    date was a 500, which is the ordinary case.
    """

    AUDIENCE_USER = 'user'
    AUDIENCE_MODULE = 'module'
    AUDIENCE_CHOICES = [
        (AUDIENCE_USER, 'Individual user(s)'),
        (AUDIENCE_MODULE, 'Everyone enrolled in a subject'),
    ]

    audience = forms.ChoiceField(choices=AUDIENCE_CHOICES, initial=AUDIENCE_USER)
    due_date = forms.DateField(required=False, widget=DateInput())
    notes = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 2}))
    email_now = forms.BooleanField(required=False, initial=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Imported lazily: finance must not import shop/learning at module level
        # (shop is wired separately, and learning would create a cycle).
        from django.apps import apps as django_apps

        Product = django_apps.get_model('shop', 'Product')
        ProgrammeModule = django_apps.get_model('learning', 'ProgrammeModule')
        self.fields['product'] = forms.ModelChoiceField(
            queryset=Product.objects.filter(status='active').order_by('name'),
            required=False, empty_label='— none (add line items later) —',
            label='Initial item')
        self.fields['programme_module'] = forms.ModelChoiceField(
            queryset=ProgrammeModule.objects.filter(is_active=True)
                                            .select_related('programme')
                                            .order_by('programme__name', 'order', 'name'),
            required=False, empty_label='— choose —', label='Subject')
        _style_fields(self)

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('audience') == self.AUDIENCE_MODULE and not cleaned.get('programme_module'):
            self.add_error('programme_module', 'Choose the subject to invoice.')
        return cleaned


class InvoiceItemForm(StyledModelForm):
    """Add a line item — pick a product/course to auto-fill the
    description + price, or type a free-text line from scratch."""

    class Meta:
        model = models.InvoiceItem
        fields = ['product', 'description', 'quantity', 'unit_price']
        widgets = {
            'description': forms.TextInput(attrs={'placeholder': 'Leave blank to use the selected item'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].required = False
        self.fields['description'].required = False
        self.fields['product'].empty_label = '— choose a product / course —'

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get('product') and not cleaned.get('description'):
            self.add_error('description', 'Pick an item or enter a description.')
        return cleaned


class InvoicePaymentForm(StyledModelForm):
    class Meta:
        model = models.InvoicePayment
        fields = ['amount', 'method', 'reference', 'paid_at']
        widgets = {'paid_at': DateTimeInput()}


class GrantAccessForm(forms.Form):
    """Record a payment and open a student's modules, in one action.

    Admin/staff only. The amount and the proof are asked for together with the
    access being granted because they are the same decision: nobody's account
    should open without a record of what paid for it. The document is optional —
    staff do sometimes take cash in the room — but then they are on the record as
    the person who said so.
    """
    student = forms.ModelChoiceField(
        queryset=None, label='Student',
        help_text='Whose subjects are being opened.')
    amount = forms.DecimalField(
        max_digits=12, decimal_places=2, min_value=0, label='Amount received (R)')
    months = forms.IntegerField(
        min_value=1, max_value=24, initial=1, label='Months of access',
        help_text='Subjects are priced per month; this is how many are paid for.')
    method = forms.ChoiceField(
        choices=[('bank', 'EFT / bank transfer'), ('cash', 'Cash'), ('card', 'Card'),
                 ('cheque', 'Cheque'), ('online', 'Other online')],
        initial='bank', label='How it was paid')
    paid_on = forms.DateField(required=False, widget=DateInput(), label='Date paid',
                              help_text='The date on the deposit slip. Defaults to today.')
    reference = forms.CharField(max_length=120, required=False, label='Bank reference')
    document = forms.FileField(
        required=False, label='Proof of payment',
        help_text='A photograph or a PDF of the deposit slip. Filed against the student '
                  'and shown in their payment history.')
    note = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 2}),
                           label='Note', help_text='Anything worth remembering about this payment.')

    #: Proof documents are shown inline and downloaded by staff, so the types
    #: accepted are the ones a bank actually produces.
    ALLOWED = ('.pdf', '.png', '.jpg', '.jpeg', '.gif', '.webp', '.heic')
    MAX_BYTES = 10 * 1024 * 1024

    def __init__(self, *args, **kwargs):
        from apps.accounts.models import Person

        super().__init__(*args, **kwargs)
        self.fields['student'].queryset = (
            Person.objects.filter(user_type='student')
            .select_related('user').order_by('first_name', 'last_name'))
        for name, field in self.fields.items():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs['class'] = 'form-check-input'
            elif isinstance(widget, forms.Select):
                widget.attrs['class'] = 'form-control form-select'
            else:
                widget.attrs['class'] = 'form-control'

    def clean_document(self):
        document = self.cleaned_data.get('document')
        if not document:
            return document
        name = (document.name or '').lower()
        if not name.endswith(self.ALLOWED):
            raise forms.ValidationError(
                'Upload a PDF or an image (PNG, JPG, GIF, WEBP or HEIC).')
        if document.size > self.MAX_BYTES:
            raise forms.ValidationError('That file is larger than 10 MB — please compress it.')
        return document


# ---------------------------------------------------------------------------
# Wave-style document editor: invoice / estimate header + line formset
# ---------------------------------------------------------------------------
def _customer_field(form):
    from django.contrib.auth import get_user_model
    field = form.fields['customer']
    field.queryset = get_user_model().objects.filter(is_active=True).order_by('first_name', 'last_name', 'email')
    field.label_from_instance = lambda u: (f'{u.get_full_name()} · {u.email}' if u.get_full_name() else u.email or u.get_username())


class InvoiceEditForm(StyledModelForm):
    class Meta:
        model = models.Invoice
        fields = ['customer', 'issue_date', 'due_date', 'summary', 'po_number', 'notes', 'footer']
        widgets = {'issue_date': DateInput(), 'due_date': DateInput(),
                   'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Notes / terms, e.g. banking details or what the fee covers'}),
                   'summary': forms.TextInput(attrs={'placeholder': 'e.g. Semester 2 tuition — FREP'})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _customer_field(self)


class EstimateEditForm(StyledModelForm):
    class Meta:
        model = models.Estimate
        fields = ['customer', 'issue_date', 'valid_until', 'summary', 'po_number', 'notes', 'footer']
        widgets = {'issue_date': DateInput(), 'valid_until': DateInput(),
                   'notes': forms.Textarea(attrs={'rows': 3}),
                   'summary': forms.TextInput(attrs={'placeholder': 'e.g. Grade 8 school fees, 2027'})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _customer_field(self)


class _LineForm(StyledModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.shop.models import Product
        self.fields['product'].queryset = Product.objects.filter(status='active').order_by('name')
        self.fields['product'].required = False
        self.fields['description'].widget.attrs['placeholder'] = 'Item'
        self.fields['detail'].widget.attrs['placeholder'] = 'Description (optional)'
        self.fields['quantity'].widget.attrs['min'] = 1
        self.fields['unit_price'].widget.attrs['step'] = '0.01'
        self.fields['discount_percent'].widget.attrs.update({'step': '0.5', 'min': 0, 'max': 100})

    def has_changed(self):
        # A line the editor added but nobody filled in (no item, no name, no
        # price) is not a line — skip it rather than fail the whole invoice.
        if not self.instance.pk:
            prefix = self.prefix + '-'
            filled = [self.data.get(prefix + name, '').strip()
                      for name in ('product', 'description', 'unit_price')]
            if not filled[0] and not filled[1] and filled[2] in ('', '0', '0.00'):
                return False
        return super().has_changed()

    def clean(self):
        data = super().clean()
        if not self.cleaned_data.get('DELETE') and not data.get('description') and not data.get('product'):
            self.add_error('description', 'Name the item or pick one from the shop.')
        return data


class InvoiceLineForm(_LineForm):
    class Meta:
        model = models.InvoiceItem
        fields = ['product', 'description', 'detail', 'quantity', 'unit_price', 'discount_percent']


class EstimateLineForm(_LineForm):
    class Meta:
        model = models.EstimateItem
        fields = ['product', 'description', 'detail', 'quantity', 'unit_price', 'discount_percent']


InvoiceLineFormSet = forms.inlineformset_factory(models.Invoice, models.InvoiceItem, form=InvoiceLineForm,
                                                 extra=0, can_delete=True)
EstimateLineFormSet = forms.inlineformset_factory(models.Estimate, models.EstimateItem, form=EstimateLineForm,
                                                  extra=0, can_delete=True)


# ---------------------------------------------------------------------------
# Expenses
# ---------------------------------------------------------------------------
class ExpenseForm(StyledModelForm):
    REPEAT_CHOICES = [('', 'Does not repeat'), ('1:weekly', 'Every week'), ('1:monthly', 'Every month'),
                      ('3:monthly', 'Every quarter'), ('1:yearly', 'Every year')]
    repeat = forms.ChoiceField(choices=REPEAT_CHOICES, required=False, label='Repeat')
    repeat_until = forms.DateField(required=False, widget=DateInput(), label='Until (blank = never ends)')
    new_vendor = forms.CharField(required=False, label='…or a new vendor',
                                 widget=forms.TextInput(attrs={'placeholder': 'New vendor name'}))

    class Meta:
        model = models.Expense
        fields = ['date', 'category', 'vendor', 'description', 'amount', 'vat_treatment', 'paid_through',
                  'reference', 'status', 'due_date', 'institution', 'receipt', 'notes']
        widgets = {'date': DateInput(), 'due_date': DateInput(), 'notes': forms.Textarea(attrs={'rows': 2}),
                   'amount': forms.NumberInput(attrs={'step': '0.01', 'min': '0'})}
        labels = {'institution': 'Cost centre', 'vat_treatment': 'VAT'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = models.ExpenseCategory.objects.filter(is_active=True)
        self.fields['vendor'].queryset = models.Vendor.objects.filter(is_active=True)
        self.fields['vendor'].required = False
        if self.instance.pk:
            del self.fields['repeat'], self.fields['repeat_until']

    def clean(self):
        data = super().clean()
        if data.get('amount') is not None and data['amount'] <= 0:
            self.add_error('amount', 'Enter an amount above zero.')
        return data

    def save(self, commit=True):
        expense = super().save(commit=False)
        name = (self.cleaned_data.get('new_vendor') or '').strip()
        if name and not expense.vendor_id:
            expense.vendor, _ = models.Vendor.objects.get_or_create(name=name[:160])
        if commit:
            expense.save()
        return expense


class RecurringExpenseForm(StyledModelForm):
    class Meta:
        model = models.RecurringExpense
        fields = ['name', 'category', 'vendor', 'description', 'amount', 'vat_treatment', 'paid_through',
                  'institution', 'every', 'frequency', 'start_date', 'end_date', 'next_date', 'is_active', 'notes']
        widgets = {'start_date': DateInput(), 'end_date': DateInput(), 'next_date': DateInput(),
                   'notes': forms.Textarea(attrs={'rows': 2})}
        labels = {'institution': 'Cost centre', 'next_date': 'Next expense on'}


class VendorForm(StyledModelForm):
    class Meta:
        model = models.Vendor
        fields = ['name', 'email', 'phone', 'vat_number', 'notes', 'is_active']
        widgets = {'notes': forms.Textarea(attrs={'rows': 2})}


class ExpenseCategoryForm(StyledModelForm):
    class Meta:
        model = models.ExpenseCategory
        fields = ['name', 'code', 'group', 'description', 'is_active']
