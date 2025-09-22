from notifications.models import Notification
from rest_framework import serializers


class NotificationSerializer(serializers.ModelSerializer):
    message_to = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Notification
        fields = [
            "id",
            "channel",
            "message",
            "subject",
            "message_type",
            "is_read",
            "message_to",
            "created_at",
            "updated_at",
        ]
