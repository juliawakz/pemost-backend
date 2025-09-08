import django_filters
from locations.models.ward import Ward


class WardFilter(django_filters.FilterSet):
    # local fields
    ward_id = django_filters.NumberFilter(field_name="ward_id", lookup_expr="exact")
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")

    # subcounty relations
    subcounty_name = django_filters.CharFilter(field_name="subcounty__name", lookup_expr="icontains")
    subcounty_id = django_filters.NumberFilter(field_name="subcounty__subcounty_id", lookup_expr="exact")

    # county relations through subcounty
    county_name = django_filters.CharFilter(field_name="subcounty__county__name", lookup_expr="icontains")
    county_id = django_filters.NumberFilter(field_name="subcounty__county__county_id", lookup_expr="exact")

    class Meta:
        model = Ward
        fields = [
            "ward_id",
            "name",
            "subcounty_name",
            "subcounty_id",
            "county_name",
            "county_id"
        ]
