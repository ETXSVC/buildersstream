from rest_framework.routers import DefaultRouter
from .views import NotificationViewSet, NotificationPreferenceViewSet

router = DefaultRouter()
router.register("notifications", NotificationViewSet, basename="notifications")
router.register("notification-preferences", NotificationPreferenceViewSet, basename="notification-preferences")

urlpatterns = router.urls
