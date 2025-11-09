import django_filters
from app.models.farm import Farm


class FarmFilterSet(django_filters.FilterSet):
    """
    FilterSet for Farm model.
    Allows filtering by name, ward, farmer, visibility, and size ranges.
    """
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains'
    )
    id = django_filters.CharFilter(
        field_name='id',
        lookup_expr='exact'
    )
    ward = django_filters.CharFilter(
        field_name='ward__id',
        lookup_expr='exact'
    )
    ward_name = django_filters.CharFilter(
        field_name='ward__name',
        lookup_expr='icontains'
    )
    farmer_first_name = django_filters.CharFilter(
        field_name='farmer__first_name',
        lookup_expr='icontains'
    )
    farmer_email = django_filters.CharFilter(
        field_name='farmer__email',
        lookup_expr='icontains'
    )
    is_visible = django_filters.BooleanFilter(
        field_name='is_visible'
    )
    is_archived = django_filters.BooleanFilter(
        field_name='is_archived'
    )
    calc_size_min = django_filters.NumberFilter(
        field_name='calc_size',
        lookup_expr='gte'
    )
    calc_size_max = django_filters.NumberFilter(
        field_name='calc_size',
        lookup_expr='lte'
    )
    user_size_min = django_filters.NumberFilter(
        field_name='user_size',
        lookup_expr='gte'
    )
    user_size_max = django_filters.NumberFilter(
        field_name='user_size',
        lookup_expr='lte'
    )

    class Meta:
        model = Farm
        fields = [
            'id',
            'name',
            'ward',
            'ward_name',
            'farmer_first_name',
            'farmer_email',
            'is_visible',
            'is_archived',
        ]
