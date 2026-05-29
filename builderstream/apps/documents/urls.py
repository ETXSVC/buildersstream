"""Document & Photo Control URL configuration."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.documents import views

app_name = "documents"

router = DefaultRouter()
router.register("folders", views.DocumentFolderViewSet, basename="documentfolder")
router.register("documents", views.DocumentViewSet, basename="document")
router.register("rfis", views.RFIViewSet, basename="rfi")
router.register("submittals", views.SubmittalViewSet, basename="submittal")
router.register("photos", views.PhotoViewSet, basename="photo")
router.register("photo-albums", views.PhotoAlbumViewSet, basename="photoalbum")

urlpatterns = [
    path("", include(router.urls)),
]
