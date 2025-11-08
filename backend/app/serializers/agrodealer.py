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
    items_for_sale = serializers.ListField(
        child=serializers.CharField(),
        read_only=True
    )

    class Meta:
        model = Agrodealer
        fields = [
            "id",
            "name",
            "user",
            "ward",
            "location",
            "address",
            "items_for_sale",
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
    Requires: name, ward, and location.
    The user is automatically assigned from the request.
    """
    items_for_sale = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True
    )

    class Meta:
        model = Agrodealer
        fields = ["name", "ward", "location", "items_for_sale"]

    def validate(self, attrs):
        """Ensure only AGRODEALER users can create."""
        request = self.context.get("request")
        if request is None:
            raise ValidationError("Request context is missing.")
        user = request.user
        location = attrs.get("location")
        name = attrs.get("name")

        if not user.is_agrodealer():
            raise ValidationError(
                "Only a user with agrodealer role can register an agrodealer."
            )

        if Agrodealer.objects.filter(
                name=name,
                user=user,
                location=location).exists():
            raise ValidationError(
                "You can only have one agrodealer in the same location"
            )

        attrs["user"] = user

        return attrs

    def validate_location(self, value):
        """Ensure location is not empty"""
        if not value:
            raise ValidationError("Location cannot be empty.")
        return value

    def create(self, validated_data):
        """Attach the requesting user automatically"""
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)

    def to_representation(self, instance):
        """Return full agrodealer data after creation"""
        return AgrodealerReadSerializer(instance, context=self.context).data


class AgrodealerUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating agrodealer data.
    Allows updating: name, ward, location, is_visible.
    """

    items_for_sale = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True
    )

    class Meta:
        model = Agrodealer
        fields = [
            "name",
            "ward",
            "location",
            "is_visible",
            "items_for_sale"
        ]

    def validate_location(self, value):
        """Ensure location is not empty"""
        if not value:
            raise ValidationError("Location cannot be empty.")
        return value

    def to_representation(self, instance):
        """Return full agrodealer data after update"""
        return AgrodealerReadSerializer(instance, context=self.context).data
