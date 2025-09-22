from django.urls import include, path
from notifications.viewsets import NotificationViewSet
from rest_framework.routers import DefaultRouter

app_name = "notifications"

router = DefaultRouter()
router.register(r"", NotificationViewSet, basename="notifications")

urlpatterns = [
    path("", include(router.urls)),
]
