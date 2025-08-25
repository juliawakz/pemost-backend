from app.models import County, Crop_Type, Crop_Variety, Farm, SubCounty, Ward
from django.db.models import Q
from django_filters import rest_framework as filters
from fcm_django.models import FCMDevice


class FCMDeviceFilter(filters.FilterSet):
    registration_id = filters.CharFilter(field_name="registration_id", lookup_expr="icontains")
    type = filters.CharFilter(field_name="type", lookup_expr="icontains")
    user = filters.CharFilter(field_name="user", lookup_expr="icontains")
    name = filters.CharFilter(field_name="name", lookup_expr="icontains")

    class Meta:
        model = FCMDevice
        fields = ["id", "name", "registration_id", "type", "user"]


class CountyFilter(filters.FilterSet):
    county_name = filters.CharFilter(field_name="name", lookup_expr="icontains")
    county_number = filters.NumberFilter(
        field_name="county_num", lookup_expr="icontains"
    )

    class Meta:
        model = County
        fields = ["id", "county_name", "county_number"]


class SubCountyFilter(filters.FilterSet):
    subcounty_name = filters.CharFilter(field_name="name", lookup_expr="icontains")
    county_name = filters.CharFilter(
        field_name="county__name", lookup_expr="icontains"
    )

    class Meta:
        model = SubCounty
        fields = ["id", "subcounty_name", "county_name"]


class WardFilter(filters.FilterSet):
    ward_name = filters.CharFilter(field_name="name", lookup_expr="icontains")
    subcounty_name = filters.CharFilter(
        field_name="subcounty__name", lookup_expr="icontains"
    )
    county_name = filters.CharFilter(
        field_name="subcounty__county__name", lookup_expr="icontains"
    )
    county_number = filters.NumberFilter(
        field_name="subcounty__county__county_num", lookup_expr="icontains"
    )

    class Meta:
        model = Ward
        fields = ["id", "ward_name", "subcounty_name", "county_name", "county_number"]


class FarmFilter(filters.FilterSet):
    subcounty = filters.CharFilter(field_name="ward__subcounty", lookup_expr="exact")
    farmer_first_name = filters.CharFilter(
        field_name="owner__first_name", lookup_expr="icontains"
    )
    farmer_last_name = filters.CharFilter(
        field_name="owner__last_name", lookup_expr="icontains"
    )
    farmer_mobile_number = filters.CharFilter(
        field_name="owner__mobile_number", lookup_expr="exact"
    )
    farmer_name = filters.CharFilter(method="filter_farmer_name", label="name")

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


class CropFilter(filters.FilterSet):
    crop_variety = filters.CharFilter(
        field_name="crop_variety", lookup_expr="icontains"
    )

    class Meta:
        model = Crop_Variety
        fields = ["id", "crop_type", "crop_variety"]


class CropTypeFilter(filters.FilterSet):
    class Meta:
        model = Crop_Type
        fields = ["id", "name"]
