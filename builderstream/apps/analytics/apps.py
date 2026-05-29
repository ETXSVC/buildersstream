from django.apps import AppConfig


class AnalyticsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.analytics"
    verbose_name = "Analytics & Reporting Engine"

    def ready(self):
        pass  # no signals needed — analytics is read-only aggregation
