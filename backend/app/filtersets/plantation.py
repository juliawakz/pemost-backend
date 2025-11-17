import django_filters
from app.models.plantation import Plantation


class PlantationFilterSet(django_filters.FilterSet):
    """
    FilterSet for Plantation model.
    Allows filtering by maturity status and other plantation attributes.
    """
    is_matured = django_filters.BooleanFilter(
        field_name='is_matured'
    )

    class Meta:
        model = Plantation
        fields = [
            'is_matured',
        ]
