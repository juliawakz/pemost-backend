import django_filters
from locations.models.county import County


class CountyFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name="name",
        lookup_expr="icontains"
    )
    # case-insensitive and partial matches

    class Meta:
        model = County
        fields = [
            "county_id",
            "name"
        ]
