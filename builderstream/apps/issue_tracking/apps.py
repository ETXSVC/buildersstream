"""Issue Tracking app configuration."""
from django.apps import AppConfig


class IssueTrackingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.issue_tracking"
    verbose_name = "Issue Tracking"

    def ready(self):
        import apps.issue_tracking.signals  # noqa: F401
