"""Estimating app configuration."""
from django.apps import AppConfig


class EstimatingConfig(AppConfig):
    """Configuration for the Estimating app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.estimating"
    verbose_name = "Estimating & Takeoffs"

    def ready(self):
        """Import signals when app is ready."""
        import apps.estimating.signals  # noqa: F401
