from django.urls import include, path
from farms.views.farm import FarmsImportView
from farms.viewsets.agrodealer import AgrodealerViewset
from farms.viewsets.farm import FarmViewset
from farms.viewsets.plantation import PlatationViewset
from rest_framework.routers import DefaultRouter

app_name = "farms"

router = DefaultRouter()
router.register(r"farms", FarmViewset, basename="farms")
router.register(r"agrodealers", AgrodealerViewset, basename="agrodealers")
router.register(r"plantations", PlatationViewset, basename="plantations")

urlpatterns = [
    path("", include(router.urls)),
    path("upload/farm/", FarmsImportView.as_view(), name="upload_new_farms")
]
