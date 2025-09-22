from django.urls import include, path
from farms.viewsets.agrodealer import AgrodealerViewset
from farms.viewsets.farm import FarmViewset
from rest_framework.routers import DefaultRouter

app_name = "farms"

router = DefaultRouter()
router.register(r"", FarmViewset, basename="farms")
router.register(r"agrodealers", AgrodealerViewset, basename="agrodealers")

urlpatterns = [
    path("", include(router.urls)),
]
