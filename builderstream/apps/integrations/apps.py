from django.apps import AppConfig


class IntegrationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.integrations"
    verbose_name = "Integration Ecosystem & Open API"

    def ready(self):
        pass  # signals imported if needed
