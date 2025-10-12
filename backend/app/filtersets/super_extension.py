import django_filters
from app.models.super_extension import SuperExtensionOfficer


class SuperExtensionOfficerFilterSet(django_filters.FilterSet):
    """
    FilterSet for SuperExtensionOfficer model.
    Allows filtering by user details and counties.
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
    county = django_filters.CharFilter(
        field_name='counties__id',
        lookup_expr='exact'
    )
    county_name = django_filters.CharFilter(
        field_name='counties__name',
        lookup_expr='icontains'
    )
    is_archived = django_filters.BooleanFilter(
        field_name='is_archived'
    )

    class Meta:
        model = SuperExtensionOfficer
        fields = [
            'user',
            'user_email',
            'user_first_name',
            'user_last_name',
            'county',
            'county_name',
            'is_archived',
        ]
