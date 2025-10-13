from app.choices import WorkRequestStatusChoices
from app.models.work_request import EExtensionWorkRequest, FarmerWorkRequest
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from users.serializers.user import MiniUserReadSerializer

User = get_user_model()


# ===== Farmer Work Request Serializers =====

class FarmerWorkRequestReadSerializer(serializers.ModelSerializer):
    """
    Serializer for reading/retrieving farmer work requests.
    Includes nested farmer and e-extension user information.
    """
    farmer = MiniUserReadSerializer(read_only=True)
    e_extension = MiniUserReadSerializer(read_only=True)

    class Meta:
        model = FarmerWorkRequest
        fields = [
            "id",
            "farmer",
            "e_extension",
            "status",
            "message",
            "response_message",
            "notification_sent",
            "responded_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "status",
            "response_message",
            "notification_sent",
            "responded_at",
            "created_at",
            "updated_at",
        ]


class FarmerWorkRequestCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating farmer work requests.
    Only farmers can create requests to e-extensions.
    """
    e_extension = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='E_EXTENSION')
    )

    class Meta:
        model = FarmerWorkRequest
        fields = [
            "e_extension",
            "message",
        ]

    def validate_e_extension(self, value):
        """Ensure target user is an E-Extension officer"""
        if not hasattr(value, 'is_eextension') or not value.is_eextension():
            raise ValidationError(
                "Target user must be an E-Extension officer."
            )
        return value

    def validate(self, attrs):
        """Check if there's already a pending request"""
        request = self.context.get('request')
        if request and request.user:
            farmer = request.user
            e_extension = attrs.get('e_extension')

            # Check for existing pending request
            existing = FarmerWorkRequest.objects.filter(
                farmer=farmer,
                e_extension=e_extension,
                status=WorkRequestStatusChoices.PENDING,
                is_archived=False
            ).exists()

            if existing:
                raise ValidationError(
                    "You already have a pending request to this "
                    "E-Extension officer."
                )

        return attrs

    def create(self, validated_data):
        """Create the request with the authenticated farmer"""
        request = self.context.get('request')
        validated_data['farmer'] = request.user
        return super().create(validated_data)

    def to_representation(self, instance):
        """Return full work request data after creation"""
        return FarmerWorkRequestReadSerializer(
            instance, context=self.context
        ).data


class AcceptRejectRequestSerializer(serializers.Serializer):
    """
    Serializer for accepting or rejecting work requests.
    """
    response_message = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=500
    )


# ===== E-Extension Work Request Serializers =====

class EExtensionWorkRequestReadSerializer(serializers.ModelSerializer):
    """
    Serializer for reading/retrieving E-Extension work requests.
    Includes nested e-extension and super-extension user information.
    """
    e_extension = MiniUserReadSerializer(read_only=True)
    super_extension = MiniUserReadSerializer(read_only=True)

    class Meta:
        model = EExtensionWorkRequest
        fields = [
            "id",
            "e_extension",
            "super_extension",
            "status",
            "message",
            "response_message",
            "notification_sent",
            "responded_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "status",
            "response_message",
            "notification_sent",
            "responded_at",
            "created_at",
            "updated_at",
        ]


class EExtensionWorkRequestCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating E-Extension work requests.
    Only E-Extensions can create requests to Super Extensions.
    """
    super_extension = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='SUPER_EXTENSION')
    )

    class Meta:
        model = EExtensionWorkRequest
        fields = [
            "super_extension",
            "message",
        ]

    def validate_super_extension(self, value):
        """Ensure target user is a Super Extension officer"""
        if (not hasattr(value, 'is_superextension') or
                not value.is_superextension()):
            raise ValidationError(
                "Target user must be a Super Extension officer."
            )
        return value

    def validate(self, attrs):
        """Check if there's already a pending request"""
        request = self.context.get('request')
        if request and request.user:
            e_extension = request.user
            super_extension = attrs.get('super_extension')

            # Check for existing pending request
            existing = EExtensionWorkRequest.objects.filter(
                e_extension=e_extension,
                super_extension=super_extension,
                status=WorkRequestStatusChoices.PENDING,
                is_archived=False
            ).exists()

            if existing:
                raise ValidationError(
                    "You already have a pending request to this "
                    "Super Extension officer."
                )

        return attrs

    def create(self, validated_data):
        """Create the request with the authenticated e-extension"""
        request = self.context.get('request')
        validated_data['e_extension'] = request.user
        return super().create(validated_data)

    def to_representation(self, instance):
        """Return full work request data after creation"""
        return EExtensionWorkRequestReadSerializer(
            instance, context=self.context
        ).data
