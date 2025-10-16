from app.models.super_extension import SuperExtensionOfficer
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_field
from locations.serializers.county import MinimalCountySerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from users.serializers.user import MiniUserReadSerializer

User = get_user_model()


class SuperExtensionOfficerReadSerializer(serializers.ModelSerializer):
    """
    Serializer for reading/retrieving Super Extension officer data.
    Includes nested user, counties, and managed E-Extension information.
    """
    user = MiniUserReadSerializer(read_only=True)
    counties = MinimalCountySerializer(many=True, read_only=True)
    managed_e_extensions_count = serializers.SerializerMethodField()

    class Meta:
        model = SuperExtensionOfficer
        fields = [
            "id",
            "user",
            "counties",
            "managed_e_extensions_count",
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
    def get_managed_e_extensions_count(self, obj):
        """Return count of E-Extensions managed by this Super Extension"""
        return obj.managed_e_extensions.count()


class SuperExtensionOfficerWriteSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new Super Extension officers.
    Requires: user, counties.
    """
    counties = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=__import__('locations.models.county',
                            fromlist=['County']).County.objects.all(),
        required=True
    )

    class Meta:
        model = SuperExtensionOfficer
        fields = [
            "counties",
        ]

    def validate(self, attrs):
        """Ensure user has SUPER_EXTENSION role"""
        request = self.context.get("request")
        if request is None:
            raise ValidationError("Request context is missing.")
        user = request.user
        counties = attrs.get("counties")

        if not user.is_superextension():
            raise ValidationError(
                "Only a user with super extension role can register."
            )

        # Check if user already has a Super Extension profile
        if SuperExtensionOfficer.objects.filter(user=user).exists():
            raise ValidationError(
                "This user already has a Super Extension officer profile."
            )

        # Ensure at least one ward
        if not counties:
            raise ValidationError(
                "At least one ward must be assigned.")

        attrs["user"] = user

        return attrs

    def to_representation(self, instance):
        """Return full Super Extension data after creation"""
        return SuperExtensionOfficerReadSerializer(
            instance, context=self.context
        ).data


class SuperExtensionOfficerUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating Super Extension officer data.
    Allows updating: counties.
    """
    counties = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=__import__('locations.models.county',
                            fromlist=['County']).County.objects.all(),
        required=False
    )

    class Meta:
        model = SuperExtensionOfficer
        fields = [
            "counties",
        ]

    def to_representation(self, instance):
        """Return full Super Extension data after update"""
        return SuperExtensionOfficerReadSerializer(
            instance, context=self.context
        ).data


class MiniSuperExtensionOfficerSerializer(
        SuperExtensionOfficerReadSerializer):
    class Meta:
        model = SuperExtensionOfficer
        fields = [
            "id",
            "user",
        ]
