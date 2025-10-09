import django_filters
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from backend.farms.models.agrovet import AgroDealer


class AgroDealerFilterSet(django_filters.FilterSet):
    lat = django_filters.NumberFilter(method="filter_distance")
    lon = django_filters.NumberFilter(method="filter_distance")
    distance = django_filters.NumberFilter(method="filter_distance")

    class Meta:
        model = AgroDealer
        fields = ["lat", "lon", "distance"]

    def filter_distance(self, queryset, name, value):
        """
        Filters AgroDealers within `distance` km of (lat, lon).
        """
        lat = self.data.get("lat")
        lon = self.data.get("lon")
        distance = self.data.get("distance")

        if lat and lon and distance:
            try:
                ref_point = Point(float(lon), float(lat), srid=4326)
                return (
                    queryset.filter(location__distance_lte=(ref_point, D(km=float(distance))))
                    .annotate(distance=Distance("location", ref_point))
                    .order_by("distance")
                )
            except (ValueError, TypeError):
                return queryset  # fallback if params are invalid
        return queryset
