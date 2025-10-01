import django_filters
from crops.models.crop_variety import CropVariety


class CropVarietyFilterSet(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name="name",
        lookup_expr="icontains"
    )
    crop = django_filters.NumberFilter(
        field_name="crop",
        lookup_expr="exact"
    )
    crop_name = django_filters.CharFilter(
        field_name="crop__name",
        lookup_expr="icontains"
    )

    class Meta:
        model = CropVariety
        fields = ["crop", "crop_name", "name"]
