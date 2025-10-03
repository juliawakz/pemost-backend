# urls.py
from django.urls import include, path
from crops.viewsets.crop import CropViewset
from crops.viewsets.crop_variety import CropVarietyViewset
from crops.viewsets.crop_growth_stage import CropGrowthStageViewset
from rest_framework.routers import DefaultRouter
from crops.views.growth_stage import CropGrowthStageChoicesView
from crops.views.severity import SeverityChoicesView

app_name = "crops"

router = DefaultRouter()
router.register(r"crops", CropViewset, basename="crop")
router.register(r"varieties", CropVarietyViewset, basename="crop_variety")
router.register(r"growth/stages", CropGrowthStageViewset, basename="growth_stage")

urlpatterns = [
    path(
        "growth/stages/choices/",
        CropGrowthStageChoicesView.as_view(),
        name="growth-stage-choices"
    ),
    path(
        "severity/choices/",
        SeverityChoicesView.as_view(),
        name="severity-choices"
    ),
    path("", include(router.urls)),
]
