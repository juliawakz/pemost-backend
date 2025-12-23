from crops.models.crop import Crop
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from users.serializers.user import MiniUserReadSerializer


class CropSerializer(serializers.ModelSerializer):
    created_by = MiniUserReadSerializer(read_only=True)
    updated_by = MiniUserReadSerializer(read_only=True)

    class Meta:
        model = Crop
        fields = ["id", "name", "created_by", "updated_by"]
        read_only_fields = ["created_by", "updated_by"]

    def validate(self, attrs):
        request = self.context["request"]
        user = request.user

        # --- Permission checks ---
        if not (user.is_superuser or user.is_systemadmin() or
                user.is_superextension() or user.is_eextension()):
            raise PermissionDenied("You are not allowed to manage crops.")

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


class MiniCropSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crop
        fields = ["id", "name"]
