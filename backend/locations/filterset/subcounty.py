import django_filters
from locations.models.subcounty import SubCounty


class SubCountyFilter(django_filters.FilterSet):
    # local fields
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    subcounty_id = django_filters.NumberFilter(field_name="subcounty_id", lookup_expr="exact")

    # county relations
    county_name = django_filters.CharFilter(field_name="county__name", lookup_expr="icontains")
    county_id = django_filters.NumberFilter(field_name="county__county_id", lookup_expr="exact")

    class Meta:
        model = SubCounty
        fields = ["subcounty_id", "name", "county_name", "county_id"]
