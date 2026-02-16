"""Service URL configuration."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "service"

router = DefaultRouter()
router.register("tickets", views.ServiceTicketViewSet)
router.register("warranties", views.WarrantyItemViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
