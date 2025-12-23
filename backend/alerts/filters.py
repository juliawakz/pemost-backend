import django_filters
from alerts.models import Alert
from app.choices import AlertStatusChoices


class AlertFilter(django_filters.FilterSet):
    """
    Custom filterset for Alert model with enhanced filtering capabilities.

    Filters:
    - alert_type: Filter by alert type (YELLOW, RED, GREEN, NONE)
    - read: Filter by read status (true/false)
    - farm: Filter by farm ID
    - start_date: Filter alerts created on or after this date
      (format: YYYY-MM-DD)
    - end_date: Filter alerts created on or before this date
      (format: YYYY-MM-DD)
    """
    alert_type = django_filters.CharFilter(
        method="filter_alert_type",
        help_text="Filter by alert type (YELLOW, RED, GREEN, NONE)"
    )

    def filter_alert_type(self, queryset, name, value):
        return queryset.filter(alert_type__iexact=value)

    start_date = django_filters.DateFilter(
        field_name='created_at',
        lookup_expr='gte',
        help_text="Filter alerts created on or after this date (YYYY-MM-DD)"
    )

    end_date = django_filters.DateFilter(
        field_name='created_at',
        lookup_expr='lte',
        help_text="Filter alerts created on or before this date (YYYY-MM-DD)"
    )

    read = django_filters.BooleanFilter(
        field_name='read',
        help_text="Filter by read status (true/false)"
    )

    farm = django_filters.UUIDFilter(
        field_name='farm',
        help_text="Filter by farm UUID"
    )

    class Meta:
        model = Alert
        fields = ['alert_type', 'read', 'farm', 'start_date', 'end_date']
