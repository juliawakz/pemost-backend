import django_filters
from app.models.agrodealer import Agrodealer


class AgrodealerFilterSet(django_filters.FilterSet):
    """
    FilterSet for Agrodealer model.
    Allows filtering by name, ward, user, and visibility.
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

    class Meta:
        model = Agrodealer
        fields = [
            'name',
            'ward',
            'ward_name',
            'user',
            'user_email',
            'is_visible',
            'is_archived',
        ]
