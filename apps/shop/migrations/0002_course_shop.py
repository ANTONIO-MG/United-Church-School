import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    """Course-style storefront: educator/program/rating/duration/level fields on
    Product, plus a ProductReview model (Phase B — Shop ↔ Courses)."""

    dependencies = [
        ('shop', '0001_initial'),
        ('accounts', '0003_subject_program'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='program',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='shop_products', to='accounts.program'),
        ),
        migrations.AddField(
            model_name='product',
            name='summary',
            field=models.CharField(blank=True, help_text='Short one-line tagline shown on the card.', max_length=300),
        ),
        migrations.AddField(
            model_name='product',
            name='educator',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='taught_products', to='accounts.person', help_text='The instructor / professor for a course.'),
        ),
        migrations.AddField(
            model_name='product',
            name='duration',
            field=models.CharField(blank=True, help_text='e.g. "12 weeks", "3 Months".', max_length=60),
        ),
        migrations.AddField(
            model_name='product',
            name='level',
            field=models.CharField(blank=True, choices=[('', '—'), ('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced'), ('all', 'All levels')], max_length=12),
        ),
        migrations.AddField(
            model_name='product',
            name='rating',
            field=models.DecimalField(decimal_places=2, default=0, help_text='Average review rating (0–5), recomputed from reviews.', max_digits=3),
        ),
        migrations.AddField(
            model_name='product',
            name='rating_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='product',
            name='students_count',
            field=models.PositiveIntegerField(default=0, help_text='Enrolled / sold count (display).'),
        ),
        migrations.AddField(
            model_name='product',
            name='featured',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='ProductReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('rating', models.PositiveSmallIntegerField(default=5, help_text='1–5 stars.')),
                ('comment', models.TextField(blank=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='shop.product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_reviews', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at'], 'unique_together': {('product', 'user')}},
        ),
    ]
