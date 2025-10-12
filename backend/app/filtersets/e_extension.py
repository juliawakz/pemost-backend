import django_filters
from app.models.e_extension import EExtensionOfficer


class EExtensionOfficerFilterSet(django_filters.FilterSet):
    """
    FilterSet for EExtensionOfficer model.
    Allows filtering by user details, wards, and visibility.
    """
    user = django_filters.CharFilter(
        field_name='user__id',
        lookup_expr='exact'
    )
    user_email = django_filters.CharFilter(
        field_name='user__email',
        lookup_expr='icontains'
    )
    user_first_name = django_filters.CharFilter(
        field_name='user__first_name',
        lookup_expr='icontains'
    )
    user_last_name = django_filters.CharFilter(
        field_name='user__last_name',
        lookup_expr='icontains'
    )
    ward = django_filters.CharFilter(
        field_name='wards__id',
        lookup_expr='exact'
    )
    ward_name = django_filters.CharFilter(
        field_name='wards__name',
        lookup_expr='icontains'
    )
    is_visible = django_filters.BooleanFilter(
        field_name='is_visible'
    )
    is_archived = django_filters.BooleanFilter(
        field_name='is_archived'
    )

    class Meta:
        model = EExtensionOfficer
        fields = [
            'user',
            'user_email',
            'user_first_name',
            'user_last_name',
            'ward',
            'ward_name',
            'is_visible',
            'is_archived',
        ]
