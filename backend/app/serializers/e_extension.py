from app.models.e_extension import EExtensionOfficer
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_field
from locations.serializers.ward import MiniWardSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from users.serializers.user import MiniUserReadSerializer
from locations.models.ward import Ward

User = get_user_model()


class EExtensionOfficerReadSerializer(serializers.ModelSerializer):
    """
    Serializer for reading/retrieving E-Extension officer data.
    Includes nested user, wards, and super extension information.
    """
    user = MiniUserReadSerializer(read_only=True)
    wards = MiniWardSerializer(many=True, read_only=True)
    managed_farms_count = serializers.SerializerMethodField()
    super_extensions_count = serializers.SerializerMethodField()

    class Meta:
        model = EExtensionOfficer
        fields = [
            "id",
            "user",
            "wards",
            "super_extensions_count",
            "managed_farms_count",
            "is_visible",
            "is_archived",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "is_archived",
            "created_at",
            "updated_at",
        ]

    @extend_schema_field(serializers.IntegerField)
    def get_managed_farms_count(self, obj):
        """Return count of farms managed by this E-Extension"""
        return obj.managed_farms.count()

    @extend_schema_field(serializers.IntegerField)
    def get_super_extensions_count(self, obj):
        """Return count of super extensions managing this E-Extension"""
        return obj.super_extensions.count()


class EExtensionOfficerWriteSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new E-Extension officers.
    E-Extension officers can self-register.
    """
    wards = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Ward.objects.all(),
        required=True
    )

    class Meta:
        model = EExtensionOfficer
        fields = ["wards"]

    # -----------------------------
    # VALIDATION
    # -----------------------------
    def validate(self, attrs):
        """
        Validation logic:
        - E_EXTENSION users can only create their own profile.
        - Prevents duplicate officer profiles.
        """
        request = self.context.get("request")
        if request is None:
            raise ValidationError("Request context is missing.")
        user = request.user
        wards = attrs.get("wards")

        if not user.is_eextension():
            raise ValidationError(
                "Only a user with eextension role can register."
            )

        # Ensure only one profile per user
        if EExtensionOfficer.objects.filter(user=user).exists():
            raise ValidationError(
                "This user already has an E-Extension officer profile."
            )

        # Ensure at least one ward
        if not wards:
            raise ValidationError(
                "At least one ward must be assigned.")

        attrs["user"] = user

        return attrs

    # -----------------------------
    # CREATION
    # -----------------------------
    def create(self, validated_data):
        """Attach user and create the E-Extension profile."""
        return super().create(validated_data)

    # -----------------------------
    # REPRESENTATION
    # -----------------------------
    def to_representation(self, instance):
        """Return full E-Extension data after creation."""
        return EExtensionOfficerReadSerializer(
            instance, context=self.context
        ).data


class EExtensionOfficerUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating E-Extension officer data.
    Allows updating: wards, is_visible.
    """
    wards = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=__import__(
            'locations.models.ward',
            fromlist=['Ward']
        ).Ward.objects.all()
    )

    class Meta:
        model = EExtensionOfficer
        fields = [
            "wards",
            "is_visible",
        ]

    def validate_wards(self, value):
        """Ensure at least one ward is provided"""
        if not value:
            raise ValidationError(
                "At least one ward must be assigned."
            )
        return value

    def to_representation(self, instance):
        """Return full E-Extension data after update"""
        return EExtensionOfficerReadSerializer(
            instance, context=self.context
        ).data
