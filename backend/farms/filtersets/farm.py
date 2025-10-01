from django.db.models import Q
from django_filters import rest_framework as filters
from farms.models.farm import Farm


class FarmFilterSet(filters.FilterSet):
    county = filters.CharFilter(
        field_name="ward__subcounty__county", lookup_expr="exact"
    )
    subcounty = filters.CharFilter(
        field_name="ward__subcounty", lookup_expr="exact"
    )
    ward = filters.CharFilter(
        field_name="ward", lookup_expr="exact"
    )
    county_name = filters.CharFilter(
        field_name="ward__subcounty__county__name", lookup_expr="exact"
    )
    subcounty_name = filters.CharFilter(
        field_name="ward__subcounty__name", lookup_expr="exact"
    )
    ward_name = filters.CharFilter(
        field_name="ward__name", lookup_expr="exact"
    )
    farmer_first_name = filters.CharFilter(
        field_name="owner__first_name", lookup_expr="icontains"
    )
    farmer_last_name = filters.CharFilter(
        field_name="owner__last_name", lookup_expr="icontains"
    )
    farmer_mobile_number = filters.CharFilter(
        field_name="owner__mobile_number", lookup_expr="exact"
    )
    farmer_name = filters.CharFilter(
        method="filter_farmer_name", label="name"
    )

    def filter_farmer_name(self, queryset, name, value):
        return queryset.filter(
            Q(owner__first_name__icontains=value) | Q(owner__last_name__icontains=value)
        )

    class Meta:
        model = Farm
        fields = [
            "id",
            "ward",
            "subcounty",
            "county",
            "county_name",
            "subcounty_name",
            "county_name",
            "owner",
            "farmer_last_name",
            "farmer_first_name",
            "farmer_name",
            "farmer_mobile_number",
        ]
