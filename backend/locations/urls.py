# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from locations.viewsets.county import CountyViewSet
from locations.viewsets.subcounty import SubCountyViewSet
from locations.viewsets.ward import WardViewSet

app_name = "locations"

router = DefaultRouter()
router.register(r"counties", CountyViewSet, basename="county")
router.register(r"subcounties", SubCountyViewSet, basename="subcounty")
router.register(r"wards", WardViewSet, basename="ward")

urlpatterns = [
    path("", include(router.urls)),
]
