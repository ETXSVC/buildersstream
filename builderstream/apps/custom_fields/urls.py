from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.custom_fields import views

app_name = "custom_fields"

router = DefaultRouter()
router.register("definitions", views.CustomFieldDefinitionViewSet, basename="customfielddefinition")

urlpatterns = [
    path("", include(router.urls)),
]
