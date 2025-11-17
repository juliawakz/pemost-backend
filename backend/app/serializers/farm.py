from app.models.farm import Farm
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes
from locations.serializers.ward import MiniWardSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from users.serializers.user import MiniUserReadSerializer
from app.serializers.e_extension import MiniEExtensionOfficerSerializer
from locations.serializers.ward import MiniWardSerializer

User = get_user_model()


class FarmReadSerializer(serializers.ModelSerializer):
    """
    Serializer for reading/retrieving farm data.
    Includes nested user and ward information, and calculated size.
    """
    farmer = MiniUserReadSerializer(read_only=True)
    ward = MiniWardSerializer(read_only=True)
    e_extensions_count = serializers.SerializerMethodField()
    e_extensions = MiniEExtensionOfficerSerializer(
        read_only=True,
        many=True
    )
    metadata = serializers.SerializerMethodField()

    class Meta:
        model = Farm
        fields = [
            "id",
            "name",
            "boundary",
            "user_size",
            "calc_size",
            "ward",
            "farmer",
            "e_extensions_count",
            "e_extensions",
            "alert_status",
            "is_visible",
            "is_archived",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "calc_size",
            "alert_status",
            "is_archived",
            "created_at",
            "updated_at"
        ]

    @extend_schema_field(serializers.IntegerField)
    def get_e_extensions_count(self, obj):
        """Return count of e-extensions managing this farm"""
        return obj.e_extensions.count()

    @extend_schema_field({
        'type': 'object',
        'properties': {
            'pest_and_interventions': {
                'type': 'object',
                'properties': {
                    'interventions': {
                        'type': 'array',
                        'items': {
                            'oneOf': [
                                {'type': 'string'},
                                {
                                    'type': 'object',
                                    'properties': {
                                        'stage': {'type': 'string'},
                                        'name': {'type': 'string'},
                                        'scientific_name': {'type': 'string'},
                                        'presence_period': {'type': 'string'},
                                        'no_of_plants_affected': {
                                            'type': 'string'
                                        },
                                        'action_threshold': {'type': 'string'},
                                        'action_threshold_risk': {
                                            'type': 'string'
                                        },
                                        'crop_growth_stage': {
                                            'type': 'string'
                                        },
                                        'cultural': {'type': 'string'},
                                        'cultural_description': {
                                            'type': 'string'
                                        },
                                        'biological': {'type': 'string'},
                                        'biological_description': {
                                            'type': 'string'
                                        }
                                    }
                                }
                            ]
                        }
                    }
                }
            }
        },
        'example': {
            'pest_and_interventions': {
                'interventions': [
                    {
                        'stage': 'Vegetative',
                        'name': 'Fall Armyworm',
                        'scientific_name': 'Spodoptera frugiperda',
                        'presence_period': '20-40 days',
                        'no_of_plants_affected': '5-10%',
                        'action_threshold': '10% infestation',
                        'action_threshold_risk': 'High',
                        'crop_growth_stage': 'Vegetative',
                        'cultural': 'Manual removal',
                        'cultural_description': 'Remove affected leaves',
                        'biological': 'Bacillus thuringiensis',
                        'biological_description': 'Apply Bio-pesticide'
                    }
                ]
            }
        }
    })
    def get_metadata(self, obj):
        """
        Return farm metadata including pest and intervention information.
        Updated by pest occurrence processing system.
        """
        return obj.metadata


class FarmWriteSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new farms.
    Requires: name, boundary, ward.
    Optional: user_size (farmer's estimated size).
    The user is automatically assigned from the request.
    """
    class Meta:
        model = Farm
        fields = ["name", "boundary", "user_size", "ward"]

    # -----------------------------
    # VALIDATION METHODS
    # -----------------------------
    def validate_name(self, value):
        """Ensure farm name is unique."""
        if Farm.objects.filter(name=value).exists():
            raise ValidationError("A farm with this name already exists.")
        return value

    def validate_boundary(self, value):
        """Ensure boundary is not empty."""
        if not value or getattr(value, "empty", False):
            raise ValidationError("Boundary cannot be empty.")
        return value

    def validate(self, attrs):
        """
        Validate user permissions:
        - Farmers can only create their own farms.
        """
        request = self.context.get("request")
        if request is None:
            raise ValidationError("Request context is missing.")
        user = request.user

        # Ensure the user creating a farm is a farmer
        if getattr(user, "role", None) != "FARMER":
            raise ValidationError("You must have the role 'FARMER'.")

        attrs["farmer"] = user

        return attrs

    # -----------------------------
    # CREATION LOGIC
    # -----------------------------
    def create(self, validated_data):
        """Create a farm and attach the correct user."""
        return super().create(validated_data)

    # -----------------------------
    # OUTPUT REPRESENTATION
    # -----------------------------
    def to_representation(self, instance):
        """Return full farm data after creation."""
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
            "is_visible"
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


class MiniFarmReadSerializer(serializers.ModelSerializer):
    """Minimal representation of a Farm."""
    ward = MiniWardSerializer()

    class Meta:
        model = Farm
        fields = ["id", "name", "ward", "boundary"]
