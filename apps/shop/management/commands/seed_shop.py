"""Seed the school shop: the UCS uniform and the additional fees.

Idempotent — matched on SKU, so running it again updates rather than
duplicates. Prices are the *United Church School Fees 2026* "Additional Fees /
Expenses" list; the items, sizes and descriptions live in
``core/school.py`` (``SHOP_ITEMS``), so a price changes there and nowhere else.

School fees themselves (registration, levy, monthly fees) are not shop items:
they are billed on the learner's enrolment invoice from the grade's fee
schedule (see ``apps/admissions/services.py``).

    python manage.py seed_shop
    python manage.py seed_shop --retire-others   # also deactivate items not in the list
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.shop.models import Product, ProductCategory, ProductVariant
from core import school


class Command(BaseCommand):
    help = "Create/refresh the school shop (UCS uniform and additional fees, 2026 prices)."

    def add_arguments(self, parser):
        parser.add_argument('--quiet', action='store_true')
        parser.add_argument('--retire-others', action='store_true',
                            help='Deactivate any product whose SKU is not in core.school.SHOP_ITEMS.')

    @transaction.atomic
    def handle(self, *args, **options):
        self.quiet = options['quiet']
        from apps.learning.models import Institution
        institution = Institution.objects.filter(code=school.SCHOOL['code']).first()

        categories = {}
        for key, (name, description) in school.SHOP_CATEGORIES.items():
            categories[key], _ = ProductCategory.objects.update_or_create(
                name=name, defaults={'description': description, 'status': 'active'})

        made = 0
        for sku, name, price, category, fulfilment, sizes, description in school.SHOP_ITEMS:
            product, created = Product.objects.update_or_create(sku=sku, defaults={
                'name': name, 'category': categories[category], 'price': price,
                'fulfilment': fulfilment, 'description': description, 'summary': description[:200],
                'status': 'active', 'stock': 999, 'track_stock': False,
                'institution': institution,
            })
            made += created
            for order, (size, adjustment) in enumerate(sizes, 1):
                ProductVariant.objects.update_or_create(
                    product=product, name=size,
                    defaults={'price_adjustment': adjustment, 'stock': 999, 'is_active': True,
                              'order': order, 'sku': f'{sku}-{order:02d}'})
            self._say(f'  {sku:20} R{price:>8,.2f}  {name}'
                      f'{f" · {len(sizes)} sizes" if sizes else ""}{"" if created else "  (updated)"}')

        if options['retire_others']:
            keep = [row[0] for row in school.SHOP_ITEMS]
            retired = Product.objects.exclude(sku__in=keep).filter(status='active').update(status='inactive')
            self._say(f'  retired {retired} product(s) not on the 2026 list')

        self._say(self.style.SUCCESS(f'School shop ready: {len(school.SHOP_ITEMS)} items ({made} new).'))

    def _say(self, message):
        if not self.quiet:
            self.stdout.write(message)
