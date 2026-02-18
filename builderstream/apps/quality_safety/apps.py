from django.apps import AppConfig


class QualitySafetyConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.quality_safety"
    verbose_name = "Quality & Safety"

    def ready(self):
        import apps.quality_safety.signals  # noqa: F401
