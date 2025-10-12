from django.urls import include, path
from rest_framework.routers import DefaultRouter
from app.viewsets.farm import FarmViewset

app_name = "app"

router = DefaultRouter()
router.register(r"farms", FarmViewset, basename="farms")

urlpatterns = [
    path("", include(router.urls)),
]
