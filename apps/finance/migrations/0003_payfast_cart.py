import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    """Phase C — e-commerce + PayFast: invoice pay-token, product-linked line
    items, and a real payment lifecycle (status/gateway/ref/raw) on payments."""

    dependencies = [
        ('finance', '0002_initial'),
        ('shop', '0002_course_shop'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='public_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True),
        ),
        migrations.AddField(
            model_name='invoiceitem',
            name='product',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='invoice_items', to='shop.product'),
        ),
        migrations.AlterField(
            model_name='invoiceitem',
            name='description',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='invoicepayment',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed')], db_index=True, default='completed', max_length=10),
        ),
        migrations.AddField(
            model_name='invoicepayment',
            name='gateway',
            field=models.CharField(choices=[('manual', 'Manual'), ('payfast', 'PayFast')], default='manual', max_length=10),
        ),
        migrations.AddField(
            model_name='invoicepayment',
            name='gateway_ref',
            field=models.CharField(blank=True, help_text='Gateway payment id (e.g. PayFast pf_payment_id).', max_length=120),
        ),
        migrations.AddField(
            model_name='invoicepayment',
            name='raw',
            field=models.JSONField(blank=True, default=dict, help_text='Raw gateway callback payload.'),
        ),
        migrations.AlterField(
            model_name='invoicepayment',
            name='reference',
            field=models.CharField(blank=True, max_length=120),
        ),
    ]
