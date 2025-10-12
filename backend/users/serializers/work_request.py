from rest_framework import serializers
from django.contrib.auth import get_user_model
from users.models import (
    EExtensionWorkRequest,
    FarmerWorkRequest
)
from users.choices import WorkRequestStatusChoices
User = get_user_model()


class MinimalUserSerializer(serializers.ModelSerializer):
    """Minimal user info for display in work requests"""
    role = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "full_name", "phone_number", "role"]
        read_only_fields = fields


class EExtensionWorkRequestSerializer(serializers.ModelSerializer):
    """Serializer for E-Extension to Super Extension work requests"""
    e_extension_detail = MinimalUserSerializer(source='e_extension', read_only=True)
    super_extension_detail = MinimalUserSerializer(source='super_extension', read_only=True)

    class Meta:
        model = EExtensionWorkRequest
        fields = [
            "id",
            "e_extension",
            "super_extension",
            "e_extension_detail",
            "super_extension_detail",
            "status",
            "message",
            "response_message",
            "notification_sent",
            "created_at",
            "responded_at",
        ]
        read_only_fields = [
            "id",
            "status",
            "notification_sent",
            "response_message",
            "created_at",
            "responded_at",
            "e_extension_detail",
            "super_extension_detail",
        ]

    def validate(self, attrs):
        request = self.context.get('request')
        if request and request.method == 'POST':
            # Ensure e_extension is the requester
            if not request.user.is_e_extension():
                raise serializers.ValidationError(
                    "Only E-Extension officers can send work requests to Super Extension officers."
                )

            # Auto-set e_extension to current user
            attrs['e_extension'] = request.user

            super_extension = attrs.get('super_extension')
            if not super_extension.is_super_extension():
                raise serializers.ValidationError({
                    "super_extension": "The selected user is not a Super Extension officer."
                })

            # Check if e-extension and super-extension are in the same county
            e_ext_profile = request.user.e_extension_profile
            super_ext_profile = super_extension.super_extension_profile

            e_ext_counties = set(e_ext_profile.wards.values_list('subcounty__county', flat=True))
            super_ext_counties = set(super_ext_profile.counties.values_list('id', flat=True))

            if not e_ext_counties.intersection(super_ext_counties):
                raise serializers.ValidationError({
                    "super_extension": "You can only send work requests to Super Extension officers in your county."
                })

            # Check for existing pending request
            existing = EExtensionWorkRequest.objects.filter(
                e_extension=request.user,
                super_extension=super_extension,
                status=WorkRequestStatusChoices.PENDING
            ).exists()

            if existing:
                raise serializers.ValidationError(
                    "You already have a pending request with this Super Extension officer."
                )

        return attrs


class FarmerWorkRequestSerializer(serializers.ModelSerializer):
    """Serializer for Farmer to E-Extension work requests"""
    farmer_detail = MinimalUserSerializer(source='farmer', read_only=True)
    e_extension_detail = MinimalUserSerializer(source='e_extension', read_only=True)

    class Meta:
        model = FarmerWorkRequest
        fields = [
            "id",
            "farmer",
            "e_extension",
            "farmer_detail",
            "e_extension_detail",
            "status",
            "message",
            "response_message",
            "notification_sent",
            "created_at",
            "responded_at",
        ]
        read_only_fields = [
            "id",
            "status",
            "notification_sent",
            "response_message",
            "created_at",
            "responded_at",
            "farmer_detail",
            "e_extension_detail",
        ]

    def validate(self, attrs):
        request = self.context.get('request')
        if request and request.method == 'POST':
            # Ensure farmer is the requester
            if not request.user.is_farmer():
                raise serializers.ValidationError(
                    "Only Farmers can send work requests to E-Extension officers."
                )

            # Auto-set farmer to current user
            attrs['farmer'] = request.user

            e_extension = attrs.get('e_extension')
            if not e_extension.is_e_extension():
                raise serializers.ValidationError({
                    "e_extension": "The selected user is not an E-Extension officer."
                })

            # Check if farmer has any farms to manage
            from farms.models import Farm
            farmer_farms = Farm.objects.filter(owner=request.user)
            if not farmer_farms.exists():
                raise serializers.ValidationError(
                    "You must have at least one farm registered to send work requests."
                )

            # Optionally check if e-extension operates in same ward as farmer's farms
            e_ext_profile = e_extension.e_extension_profile
            e_ext_wards = e_ext_profile.wards.all()
            farmer_wards = farmer_farms.values_list('ward', flat=True)

            # Allow request if e-extension operates in any of farmer's wards
            if not e_ext_wards.filter(id__in=farmer_wards).exists():
                raise serializers.ValidationError({
                    "e_extension": "This E-Extension officer does not operate in the ward(s) where your farms are located."
                })

            # Check for existing pending request
            existing = FarmerWorkRequest.objects.filter(
                farmer=request.user,
                e_extension=e_extension,
                status=WorkRequestStatusChoices.PENDING
            ).exists()

            if existing:
                raise serializers.ValidationError(
                    "You already have a pending request with this E-Extension officer."
                )

        return attrs


class AcceptRejectRequestSerializer(serializers.Serializer):
    """Serializer for accepting/rejecting work requests"""
    response_message = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=500,
        help_text="Optional message when accepting/rejecting the request"
    )
