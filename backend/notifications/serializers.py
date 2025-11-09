from fcm_django.models import FCMDevice
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


class FCMDeviceSerializer(serializers.ModelSerializer):
    """
    Serializer for FCM device registration.
    Used for mobile web push notifications.
    """

    class Meta:
        model = FCMDevice
        fields = [
            "id",
            "name",
            "registration_id",
            "device_id",
            "active",
            "type",
        ]
        read_only_fields = ["id"]

    def validate_registration_id(self, value):
        """
        Ensure the registration token is valid
        """
        if not value or len(value) < 10:
            raise serializers.ValidationError(
                "Invalid FCM registration token"
            )
        return value

    def create(self, validated_data):
        """
        Create or update FCM device for the authenticated user
        """
        user = self.context['request'].user
        registration_id = validated_data.get('registration_id')

        # Check if device already exists
        device, created = FCMDevice.objects.update_or_create(
            registration_id=registration_id,
            defaults={
                'user': user,
                'name': validated_data.get('name', 'Web Device'),
                'device_id': validated_data.get('device_id'),
                'active': True,
                'type': validated_data.get('type', 'web'),
            }
        )

        return device
