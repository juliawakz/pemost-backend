import django_filters
from notifications.models import Notification


class NotificationFilterSet(django_filters.FilterSet):
    class Meta:
        model = Notification
        fields = [
            "channel",
            "is_read",
            "subject"
        ]
