"""Service & Warranty Management URL configuration."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    DispatchBoardView,
    ServiceAgreementViewSet,
    ServiceTicketViewSet,
    WarrantyClaimViewSet,
    WarrantyViewSet,
)

app_name = "service"

router = DefaultRouter()
router.register("tickets", ServiceTicketViewSet)
router.register("warranties", WarrantyViewSet)
router.register("warranty-claims", WarrantyClaimViewSet)
router.register("agreements", ServiceAgreementViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("dispatch-board/", DispatchBoardView.as_view(), name="dispatch-board"),
]
