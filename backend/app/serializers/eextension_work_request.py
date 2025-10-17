from datetime import datetime

from app.choices import WorkRequestStatusChoices
from app.models import SuperExtensionOfficer
from app.models.eextension_work_request import EExtensionWorkRequest
from app.serializers.e_extension import MiniEExtensionOfficerSerializer
from app.serializers.super_extension import MiniSuperExtensionOfficerSerializer
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.template.loader import render_to_string
from notifications.tasks import send_email_task
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

User = get_user_model()


class EExtensionWorkRequestReadSerializer(serializers.ModelSerializer):
    """
    Serializer for reading/retrieving E-Extension work requests.
    Includes nested e-extension and super-extension user information.
    """
    e_extension = MiniEExtensionOfficerSerializer(read_only=True)
    super_extension = MiniSuperExtensionOfficerSerializer(read_only=True)

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
        queryset=SuperExtensionOfficer.objects.all()
    )

    class Meta:
        model = EExtensionWorkRequest
        fields = [
            "super_extension",
            "message"
        ]

    def validate(self, attrs):
        """Check if there's already a pending or accepted request"""
        request = self.context.get('request')
        if not request or not request.user:
            raise ValidationError("Authenticated user required.")

        e_extension = getattr(request.user, "e_extension_users", None)
        if not e_extension:
            raise ValidationError(
                "A user with e_extension profile is required.")

        super_extension = attrs.get('super_extension')

        # Prevent duplicate requests
        if EExtensionWorkRequest.objects.filter(
            Q(
                e_extension=e_extension,
                super_extension=super_extension,
                status=WorkRequestStatusChoices.PENDING,
                is_archived=False
            ) |
            Q(
                e_extension=e_extension,
                super_extension=super_extension,
                status=WorkRequestStatusChoices.ACCEPTED
            )
        ).exists():
            raise ValidationError(
                "You already have a pending or accepted request"
                "to this Super Extension officer."
            )

        attrs["e_extension"] = e_extension

        return attrs

    def create(self, validated_data):
        """Create the work request and send an HTML email notification"""
        e_extension = validated_data["e_extension"]
        super_extension = validated_data["super_extension"]
        message = validated_data.get("message", "N/A")

        # Create the work request
        instance = super().create(validated_data)

        html_template = render_to_string(
            "email_e_extension_work_request.html",
            {
                "super_extension_name": super_extension.user.first_name,
                "eextension_name": e_extension.user.first_name,
                "message": message,
                "current_year": datetime.now().year,
            },
        )

        send_email_task.delay(
            super_extension.user.email,
            settings.EMAIL_FROM,
            "New E-Extension Work Request Received",
            "",
            html_template,
        )

        # Mark as notified
        instance.notification_sent = True

        instance.save(update_fields=["notification_sent"])

        return instance

    def to_representation(self, instance):
        """Return full work request data after creation"""
        return EExtensionWorkRequestReadSerializer(
            instance, context=self.context
        ).data


class AcceptRejectRequestSerializer(serializers.Serializer):
    """
    Serializer for accepting or rejecting work requests.
    """
    work_request = serializers.PrimaryKeyRelatedField(
        queryset=EExtensionWorkRequest.objects.all()
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
        if work_request.super_extension.user != request.user:
            raise serializers.ValidationError(
                {
                    "message": "This request can only be accepted or rejected "
                    "by its Super-Extension officer owner."
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
