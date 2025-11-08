from backend.locations.models.county import County
from backend.locations.models.subcounty import SubCounty
from backend.locations.serializers.county import CountySerializer
from rest_framework import viewsets
from django.db.models import Prefetch

class LocationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = County.objects.prefetch_related(
        Prefetch("subcounties", queryset=SubCounty.objects.prefetch_related("wards"))
    )
    serializer_class = CountySerializer
