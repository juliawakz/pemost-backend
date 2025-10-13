from app.models.agrodealer import Agrodealer
from django.contrib.auth import get_user_model
from locations.serializers.ward import MiniWardSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from users.serializers.user import MiniUserReadSerializer

User = get_user_model()


class AgrodealerReadSerializer(serializers.ModelSerializer):
    """
    Serializer for reading/retrieving agrodealer data.
    Includes nested user and ward information, and location details.
    """
    user = MiniUserReadSerializer(read_only=True)
    ward = MiniWardSerializer(read_only=True)
    latitude = serializers.FloatField(read_only=True)
    longitude = serializers.FloatField(read_only=True)

    class Meta:
        model = Agrodealer
        fields = [
            "id",
            "name",
            "user",
            "ward",
            "location",
            "latitude",
            "longitude",
            "address",
            "is_visible",
            "is_archived",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "address",
            "is_archived",
            "created_at",
            "updated_at",
        ]


class AgrodealerWriteSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new agrodealers.
    Requires: name, user, ward, location.
    Address is auto-generated from location.
    """
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='AGRODEALER')
    )

    class Meta:
        model = Agrodealer
        fields = [
            "name",
            "user",
            "ward",
            "location",
        ]

    def validate_user(self, value):
        """Ensure user has AGRODEALER role"""
        if not hasattr(value, 'is_agrodealer') or not value.is_agrodealer():
            raise ValidationError("User must have the role 'AGRODEALER'.")
        return value

    def validate_location(self, value):
        """Ensure location is not empty"""
        if not value:
            raise ValidationError("Location cannot be empty.")
        return value

    def to_representation(self, instance):
        """Return full agrodealer data after creation"""
        return AgrodealerReadSerializer(instance, context=self.context).data


class AgrodealerUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating agrodealer data.
    Allows updating: name, ward, location, is_visible.
    """

    class Meta:
        model = Agrodealer
        fields = [
            "name",
            "ward",
            "location",
            "is_visible",
        ]

    def validate_location(self, value):
        """Ensure location is not empty"""
        if value and not value:
            raise ValidationError("Location cannot be empty.")
        return value

    def to_representation(self, instance):
        """Return full agrodealer data after update"""
        return AgrodealerReadSerializer(instance, context=self.context).data
