from django.db.models import Q
from django_filters import rest_framework as filters
from farms.models.farm import Farm


class FarmFilterSet(filters.FilterSet):
    subcounty = filters.CharFilter(
        field_name="ward__subcounty", lookup_expr="exact"
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
            "owner",
            "subcounty",
            "farmer_last_name",
            "farmer_first_name",
            "farmer_name",
            "farmer_mobile_number",
        ]
