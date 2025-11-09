from datetime import datetime

from app.choices import WorkRequestStatusChoices
from app.models import EExtensionOfficer
from app.models.farm import Farm
from app.models.farmer_work_request import FarmerWorkRequest
from app.serializers.e_extension import MiniEExtensionOfficerSerializer
from app.serializers.farm import MiniFarmReadSerializer
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.template.loader import render_to_string
from notifications.tasks import send_email_task
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from rest_framework.exceptions import ValidationError
from users.serializers.user import MiniUserReadSerializer

User = get_user_model()


# ===== Farmer Work Request Serializers =====
class FarmerWorkRequestReadSerializer(serializers.ModelSerializer):
    """
    Serializer for reading/retrieving farmer work requests.
    Includes nested e-extension user information and farms.
    """
    farms = MiniFarmReadSerializer(many=True, read_only=True)
    e_extension = MiniEExtensionOfficerSerializer(read_only=True)
    farmer = serializers.SerializerMethodField()

    class Meta:
        model = FarmerWorkRequest
        fields = [
            "id",
            "farmer",
            "farms",
            "e_extension",
            "status",
            "message",
            "response_message",
            "notification_sent",
            "responded_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields  # All fields read-only for read serializer

    @extend_schema_field(MiniUserReadSerializer)
    def get_farmer(self, obj):
        """Get farmer info (assumed from the first farm owner)."""
        first_farm = obj.farms.first()
        if first_farm and hasattr(first_farm, "farmer"):
            return MiniUserReadSerializer(first_farm.farmer).data
        return None


class FarmerWorkRequestCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating farmer work requests.
    Allows multiple farms to be included in one request.
    """
    e_extension = serializers.PrimaryKeyRelatedField(
        queryset=EExtensionOfficer.objects.all()
    )
    farms = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Farm.objects.all(),
        help_text="List of farm IDs to include in this request"
    )

    class Meta:
        model = FarmerWorkRequest
        fields = [
            "farms",
            "e_extension",
            "message",
        ]

    def validate(self, attrs):
        """
        Ensure farms belong to the farmer, are within e-extension wards,
        and have no duplicate requests.
        """
        request = self.context.get('request')
        if not request or not request.user:
            raise ValidationError(
                "Authenticated farmer is required."
            )

        farmer = request.user
        e_extension = attrs.get("e_extension")
        farms = attrs.get("farms", [])

        # Ensure all farms belong to the requesting farmer
        invalid_farms = [farm for farm in farms if farm.farmer != farmer]
        if invalid_farms:
            raise ValidationError({
                "message":
                f"You cannot include farms that don't belong to you: "
                f"{', '.join([farm.name for farm in invalid_farms])}"
            })

        # Ensure all farms fall within the wards the e-extension operates in
        eext_wards = getattr(e_extension, "wards", None)
        if eext_wards is None:
            raise ValidationError(
                {
                    "message": "E-Extension officer has no wards."
                }
            )

        eext_ward_ids = set(eext_wards.values_list("id", flat=True))
        farms_outside = [
            farm for farm in farms if farm.ward.id not in eext_ward_ids]

        if farms_outside:
            raise ValidationError({
                "message":
                f"The following farm(s) are outside the E-Extension's"
                f" operational wards: "
                f"{', '.join([farm.name for farm in farms_outside])}"
            })

        # Check if they're already working together (e_extension already manages farms)
        farms_already_managed = [
            farm for farm in farms
            if e_extension in farm.e_extensions.all()
        ]

        if farms_already_managed:
            raise ValidationError({
                "message":
                f"You are already working with this E-Extension officer on: "
                f"{', '.join([farm.name for farm in farms_already_managed])}"
            })

        # Check for existing pending requests for same farms and e-extension
        existing = FarmerWorkRequest.objects.filter(
            Q(e_extension=e_extension),
            Q(status=WorkRequestStatusChoices.PENDING),
            is_archived=False,
            farms__in=farms
        ).distinct()

        if existing.exists():
            raise ValidationError({
                "message": "One or more of these farm(s) already has a pending"
                " request with this E-Extension officer."
            })

        return attrs

    def create(self, validated_data):
        """Create the request and associate multiple farms."""
        farms = validated_data.pop("farms", [])

        work_request = FarmerWorkRequest.objects.create(**validated_data)
        work_request.farms.set(farms)
        work_request.save()

        eextension = work_request.e_extension

        farms_data = []
        for farm in work_request.farms.all():
            farms_data.append({
                "name": farm.name,
                "ward": farm.ward.name if farm.ward else "N/A",
            })

        html_template = render_to_string(
            "email_farm_work_request.html",
            {
                "eextension_name": eextension.user.first_name,
                "farmer_name": work_request.farms.first().farmer.first_name,
                "farms": farms_data,
                "current_year": datetime.now().year,
            },
        )

        send_email_task.delay(
            eextension.user.email,
            settings.EMAIL_FROM,
            "New Farm Work Request Received",
            "",
            html_template,
        )

        # Mark as notified
        work_request.notification_sent = True
        work_request.save(update_fields=["notification_sent"])

        return work_request

    def to_representation(self, instance):
        """Return full work request data after creation."""
        return FarmerWorkRequestReadSerializer(
            instance, context=self.context
        ).data


class AcceptRejectFarmRequestSerializer(serializers.Serializer):
    """
    Serializer for accepting or rejecting work requests.
    """
    work_request = serializers.PrimaryKeyRelatedField(
        queryset=FarmerWorkRequest.objects.all()
    )
    status = serializers.CharField(
        required=True,
        max_length=10
    )
    response_message = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=500
    )

    def validate(self, attrs):
        request = self.context["request"]
        status = attrs.get("status")
        work_request = attrs.get("work_request")
        response_message = attrs.get("response_message")

        allowed_status = ["accept", "reject"]

        if status.lower() not in allowed_status:
            raise serializers.ValidationError(
                {
                    "message":
                    f"Status must be one of: {', '.join(allowed_status)}"
                }
            )

        # Only the recipient can accept
        if work_request.e_extension.user != request.user:
            raise serializers.ValidationError(
                {
                    "message": "This request can only be accepted or rejected "
                    "by its E-Extension officer owner."
                }
            )

        # Check if already accepted/rejected
        if work_request.status != WorkRequestStatusChoices.PENDING:
            raise serializers.ValidationError(
                {
                    "message":
                    f"This request has already been {work_request.status.lower()}."
                }
            )

        if not response_message:
            attrs["response_message"] = ""

        return attrs
