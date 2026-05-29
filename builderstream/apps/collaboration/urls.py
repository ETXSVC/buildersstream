"""Collaboration REST URL configuration."""
from rest_framework.routers import DefaultRouter

from .views import ChannelViewSet, MessageViewSet

app_name = "collaboration"

router = DefaultRouter()
router.register(r"channels", ChannelViewSet, basename="channel")
router.register(r"messages", MessageViewSet, basename="message")

urlpatterns = router.urls
