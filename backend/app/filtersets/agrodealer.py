import django_filters
from app.models.agrodealer import Agrodealer
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D


class AgrodealerFilterSet(django_filters.FilterSet):
    """
    FilterSet for Agrodealer model.
    Allows filtering by name, ward, user, and visibility.
    """
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains'
    )
    ward = django_filters.CharFilter(
        field_name='ward__id',
        lookup_expr='exact'
    )
    ward_name = django_filters.CharFilter(
        field_name='ward__name',
        lookup_expr='icontains'
    )
    user = django_filters.CharFilter(
        field_name='user__id',
        lookup_expr='exact'
    )
    user_email = django_filters.CharFilter(
        field_name='user__email',
        lookup_expr='icontains'
    )
    is_visible = django_filters.BooleanFilter(
        field_name='is_visible'
    )
    is_archived = django_filters.BooleanFilter(
        field_name='is_archived'
    )
    lat = django_filters.NumberFilter(method="filter_distance")
    lon = django_filters.NumberFilter(method="filter_distance")
    distance = django_filters.NumberFilter(method="filter_distance")

    class Meta:
        model = Agrodealer
        fields = [
            'name',
            'ward',
            'ward_name',
            'user',
            'user_email',
            'is_visible',
            'is_archived',
            "lat",
            "lon",
            "distance"
        ]

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
