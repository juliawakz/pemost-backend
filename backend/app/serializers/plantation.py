from app.models.plantation import Plantation
from app.serializers.farm import MiniFarmReadSerializer
from crops.serializers.crop_variety import MiniCropVarietySerializer
from rest_framework import serializers
from django.db.models import Q


class PlantationReadSerializer(serializers.ModelSerializer):
    """Serializer for reading plantation data with nested relationships"""
    farm = MiniFarmReadSerializer(read_only=True)
    crop_variety = MiniCropVarietySerializer(read_only=True)

    class Meta:
        model = Plantation
        fields = [
            "id",
            "farm",
            "crop_variety",
            "transplanting_date",
            "notification_end_date",
            "is_matured",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class PlantationWriteSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating plantations"""

    class Meta:
        model = Plantation
        fields = [
            "farm",
            "crop_variety",
            "transplanting_date",
        ]

    def validate(self, attrs):
        user = self.context["request"].user
        farm = attrs.get("farm")

        # Check farm ownership/access permissions
        if not (user.is_superuser or user.is_systemadmin()):
            if user.is_farmer():
                if farm.farmer != user:
                    raise serializers.ValidationError(
                        f"You must own the farm '{farm.name}' to manage plantations."
                    )
            elif user.is_eextension():
                # E-extension must be managing this farm
                try:
                    e_ext_profile = user.e_extension_users
                    if e_ext_profile not in farm.e_extensions.all():
                        raise serializers.ValidationError(
                            f"You are not managing the farm '{farm.name}'."
                        )
                except AttributeError:
                    raise serializers.ValidationError(
                        "E-Extension profile not found."
                    )
            elif user.is_agrodealer():
                raise serializers.ValidationError(
                    "Agrodealers are not allowed to manage plantations."
                )
            else:
                raise serializers.ValidationError(
                    "You do not have permission to manage plantations."
                )

        # Check for active (non-matured) plantations only when creating
        # (self.instance is None for create operations)
        if self.instance is None:
            active_plantation = Plantation.objects.filter(
                Q(farm=farm),
                Q(is_matured=False),
                Q(is_archived=False)
            ).first()

            if active_plantation:
                raise serializers.ValidationError(
                    f"This farm already has an active plantation "
                    f"({active_plantation.crop_variety.name}) planted on "
                    f"{active_plantation.transplanting_date}. "
                    f"Please wait until {active_plantation.notification_end_date} "
                    f"when it matures before adding a new plantation."
                )

        return attrs

    def to_representation(self, instance):
        """Return full plantation data after creation/update"""
        return PlantationReadSerializer(instance, context=self.context).data
