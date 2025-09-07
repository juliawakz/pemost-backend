# urls.py
from django.urls import include, path
from locations.viewsets.county import CountyViewSet
from locations.viewsets.subcounty import SubCountyViewSet
from locations.viewsets.ward import WardViewSet
from rest_framework.routers import DefaultRouter

app_name = "locations"

router = DefaultRouter()
router.register(r"counties", CountyViewSet, basename="county")
router.register(r"subcounties", SubCountyViewSet, basename="subcounty")
router.register(r"wards", WardViewSet, basename="ward")

urlpatterns = [
    path("", include(router.urls)),
]
