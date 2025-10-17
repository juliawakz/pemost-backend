from app.viewsets.agrodealer import AgrodealerViewset
from app.viewsets.e_extension import EExtensionOfficerViewset
from app.viewsets.eextension_work_request import (
    AcceptRejectEExtensionWorkRequestView,
    EExtensionWorkRequestViewset,
)
from app.viewsets.farm import FarmViewset
from app.viewsets.farmer_work_request import (
    AcceptRejectFarmWorkRequestView,
    FarmerWorkRequestViewset,
)
from app.viewsets.super_extension import SuperExtensionOfficerViewset
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
    path(
        "farmers/work-requests/accept/reject/",
        AcceptRejectFarmWorkRequestView.as_view(),
        name="accept-reject-farm-work-request"
    ),
    path(
        "e-extensions/work-requests/accept/reject/",
        AcceptRejectEExtensionWorkRequestView.as_view(),
        name="accept-reject-farm-work-request"
    ),
    path("", include(router.urls)),
]
