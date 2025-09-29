from rest_framework import serializers
from farms.utils.farm import FarmUtils
from users.choices import RoleChoices


class FarmsImportSerializer(serializers.Serializer):
    data_file = serializers.FileField(write_only=True, required=True)

    def create(self, validated_data):
        user = self.request.user
        if user.role == RoleChoices.AGRODEALER or user.role == RoleChoices.FARMER:
            raise serializers.ValidationError(
                "You are not allowed to perform this action."
            )

        shapefile = validated_data.pop("data_file", None)
        info = FarmUtils.import_data(shapefile)
        return info
