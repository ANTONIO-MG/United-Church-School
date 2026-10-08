"""Default expense accounts for a training business (editable afterwards)."""
from django.db import migrations

CATEGORIES = [
    ('Educator & tutor fees', 'payroll', '5100'),
    ('Salaries & wages', 'payroll', '5000'),
    ('Printing & study materials', 'cost_of_sales', '4100'),
    ('Merchandise stock', 'cost_of_sales', '4200'),
    ('Courier & delivery', 'cost_of_sales', '4300'),
    ('Rent & utilities', 'operating', '6000'),
    ('Software & subscriptions', 'operating', '6100'),
    ('Marketing & advertising', 'operating', '6200'),
    ('Bank & PayFast fees', 'operating', '6300'),
    ('Professional fees', 'operating', '6400'),
    ('Travel', 'operating', '6500'),
    ('Equipment', 'operating', '6600'),
    ('Telephone & internet', 'operating', '6700'),
    ('Other', 'other', '9000'),
]


def seed(apps, schema_editor):
    ExpenseCategory = apps.get_model('finance', 'ExpenseCategory')
    for name, group, code in CATEGORIES:
        ExpenseCategory.objects.get_or_create(name=name, defaults={'group': group, 'code': code})


class Migration(migrations.Migration):
    dependencies = [('finance', '0009_invoices_estimates_expenses')]
    operations = [migrations.RunPython(seed, migrations.RunPython.noop)]
