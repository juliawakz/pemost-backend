import django_filters
from crops.models.crop_growth_stage import CropGrowthStage


class CropGrowthStageFilterSet(django_filters.FilterSet):
    # Filter by crop variety (exact match by ID)
    crop_variety = django_filters.CharFilter(
        field_name="crop_variety__id",
        lookup_expr="exact"
    )

    # Filter by crop variety name (partial, case-insensitive)
    crop_variety_name = django_filters.CharFilter(
        field_name="crop_variety__name",
        lookup_expr="icontains"
    )

    # Filter by crop type (via crop_variety -> crop_type -> name)
    crop_name = django_filters.CharFilter(
        field_name="crop_variety__crop__name",
        lookup_expr="icontains"
    )

    # Filter by growth stage (choice field, exact match)
    growth_stage = django_filters.CharFilter(
        field_name="growth_stage",
        lookup_expr="exact"
    )

    # Filter by severity (choice field, exact match)
    severity = django_filters.CharFilter(
        field_name="severity",
        lookup_expr="exact"
    )

    # Range filters for minimum_days
    min_days_gte = django_filters.NumberFilter(
        field_name="minimum_days",
        lookup_expr="gte"
    )
    min_days_lte = django_filters.NumberFilter(
        field_name="minimum_days",
        lookup_expr="lte"
    )

    # Range filters for maximum_days
    max_days_gte = django_filters.NumberFilter(
        field_name="maximum_days",
        lookup_expr="gte"
    )
    max_days_lte = django_filters.NumberFilter(
        field_name="maximum_days",
        lookup_expr="lte"
    )

    class Meta:
        model = CropGrowthStage
        fields = [
            "crop_variety",
            "crop_variety_name",
            "crop_name",
            "growth_stage",
            "severity",
            "min_days_gte",
            "min_days_lte",
            "max_days_gte",
            "max_days_lte",
        ]
