from app.viewsets.agrodealer import AgrodealerViewset
from app.viewsets.e_extension import EExtensionOfficerViewset
from app.viewsets.farm import FarmViewset
from app.viewsets.super_extension import SuperExtensionOfficerViewset
from app.viewsets.work_request import (
    EExtensionWorkRequestViewset,
    FarmerWorkRequestViewset,
)
from django.urls import include, path
from rest_framework.routers import DefaultRouter

app_name = "app"

router = DefaultRouter()
router.register(r"farms", FarmViewset, basename="farms")
router.register(r"agrodealers", AgrodealerViewset, basename="agrodealers")
router.register(
    r"e-extension",
    EExtensionOfficerViewset,
    basename="e-extension-officers"
)
router.register(
    r"super-extension",
    SuperExtensionOfficerViewset,
    basename="super-extension-officers"
)
router.register(
    r"farmers/work-requests",
    FarmerWorkRequestViewset,
    basename="farmer-work-requests"
)
router.register(
    r"e-extensions/work-requests",
    EExtensionWorkRequestViewset,
    basename="e-extension-work-requests"
)

urlpatterns = [
    path("", include(router.urls)),
]
