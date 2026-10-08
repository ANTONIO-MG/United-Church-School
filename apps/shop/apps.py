from django.apps import AppConfig


class ShopConfig(AppConfig):
    """App config for the shop app.

    ``ready()`` imports :mod:`apps.shop.signals` so the order-total
    recalculation and audit-logging handlers are connected at startup.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.shop'
    verbose_name = 'Shop'

    def ready(self):
        from . import signals  # noqa: F401  (import for side effects)
