from app.models.farm import Farm
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_field
from locations.serializers.ward import MiniWardSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from users.serializers.user import MiniUserReadSerializer

User = get_user_model()


class FarmReadSerializer(serializers.ModelSerializer):
    """
    Serializer for reading/retrieving farm data.
    Includes nested user and ward information, and calculated size.
    """
    user = MiniUserReadSerializer(read_only=True)
    ward = MiniWardSerializer(read_only=True)
    e_extensions_count = serializers.SerializerMethodField()

    class Meta:
        model = Farm
        fields = [
            "id",
            "name",
            "boundary",
            "user_size",
            "calc_size",
            "ward",
            "user",
            "e_extensions_count",
            "is_visible",
            "is_archived",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "calc_size",
            "is_archived",
            "created_at",
            "updated_at",
        ]

    @extend_schema_field(serializers.IntegerField)
    def get_e_extensions_count(self, obj):
        """Return count of e-extensions managing this farm"""
        return obj.e_extensions.count()


class FarmWriteSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new farms.
    Requires: name, boundary, ward, user.
    Optional: user_size (farmer's estimated size).
    """
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='FARMER')
    )

    class Meta:
        model = Farm
        fields = [
            "name",
            "boundary",
            "user_size",
            "ward",
            "user",
        ]

    def validate_name(self, value):
        """Ensure farm name is unique"""
        if Farm.objects.filter(name=value).exists():
            raise ValidationError("A farm with this name already exists.")
        return value

    def validate_user(self, value):
        """Ensure user has FARMER role"""
        if not value.is_farmer():
            raise ValidationError("User must have the role 'FARMER'.")
        return value

    def validate_boundary(self, value):
        """Ensure boundary is not empty"""
        if not value or value.empty:
            raise ValidationError("Boundary cannot be empty.")
        return value

    def to_representation(self, instance):
        """Return full farm data after creation"""
        return FarmReadSerializer(instance, context=self.context).data


class FarmUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating farm data.
    Only allows updating: name, boundary, and user_size.
    """

    class Meta:
        model = Farm
        fields = [
            "name",
            "boundary",
            "user_size",
        ]

    def validate_name(self, value):
        """Ensure farm name is unique (excluding current instance)"""
        instance = self.instance
        if instance and Farm.objects.filter(name=value).exclude(id=instance.id).exists():
            raise ValidationError("A farm with this name already exists.")
        return value

    def validate_boundary(self, value):
        """Ensure boundary is not empty"""
        if value and value.empty:
            raise ValidationError("Boundary cannot be empty.")
        return value

    def to_representation(self, instance):
        """Return full farm data after update"""
        return FarmReadSerializer(instance, context=self.context).data


# Keep the old serializer for backward compatibility (if needed)
class FarmSerializer(serializers.ModelSerializer):
    """
    Legacy serializer - use FarmReadSerializer, FarmWriteSerializer,
    or FarmUpdateSerializer instead.
    """
    class Meta:
        model = Farm
        fields = "__all__"
