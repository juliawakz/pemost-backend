from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from crops.models.crop_variety import CropVariety


class CropVarietySerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)
    updated_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = CropVariety
        fields = "__all__"
        read_only_fields = ["created_by", "updated_by"]

    def validate(self, attrs):
        request = self.context["request"]
        user = request.user

        # --- Permission checks ---
        if not (user.is_superuser or user.is_system_admin() or
                user.is_super_extension() or user.is_e_extension()):
            raise PermissionDenied(
                "You are not allowed to manage crop varieties."
            )

        return attrs

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user and request.user.is_authenticated:
            validated_data["created_by"] = request.user
            validated_data["updated_by"] = request.user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        request = self.context.get("request")
        if request and request.user and request.user.is_authenticated:
            validated_data["updated_by"] = request.user
        return super().update(instance, validated_data)
