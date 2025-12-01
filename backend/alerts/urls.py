from alerts.viewsets import AlertViewSet
from django.urls import include, path
from rest_framework.routers import DefaultRouter

app_name = "alerts"

router = DefaultRouter()
router.register(r"", AlertViewSet, basename="alerts")

urlpatterns = [
    path("", include(router.urls)),
]
