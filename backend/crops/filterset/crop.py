import django_filters
from crops.models.crop import Crop


class CropFilterSet(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name="name",
        lookup_expr="icontains"
    )

    class Meta:
        model = Crop
        fields = ["name"]
