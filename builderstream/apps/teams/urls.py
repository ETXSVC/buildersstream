from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "teams"

router = DefaultRouter()
router.register("", views.TeamViewSet, basename="team")

urlpatterns = [
    path("", include(router.urls)),
]
