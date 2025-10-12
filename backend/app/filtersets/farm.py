import django_filters
from app.models.farm import Farm


class FarmFilterSet(django_filters.FilterSet):
    """
    FilterSet for Farm model.
    Allows filtering by name, ward, user, visibility, and size ranges.
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
            'name',
            'ward',
            'ward_name',
            'user',
            'user_email',
            'is_visible',
            'is_archived',
        ]
