"""Document URL configuration."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "documents"

router = DefaultRouter()
router.register("folders", views.FolderViewSet)
router.register("files", views.DocumentViewSet)
router.register("rfis", views.RFIViewSet)
router.register("submittals", views.SubmittalViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
