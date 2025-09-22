from farms.models.farm import Farm
from farms.utils.shapefileIO import import_farms
from rest_framework import serializers
from users.choices import RoleChoices


class FarmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Farm
        fields = "__all__"

    def validate(self, attrs):
        owner = attrs.get("owner")
        ward = attrs.get("ward")
        user = self.request.user
        if user.role == RoleChoices.AGRODEALER or user.role == RoleChoices.FARMER:
            raise serializers.ValidationError(
                "You are not allowed to perform this action."
            )
        if owner and ward and ward not in owner.wards.all():
            raise serializers.ValidationError(
                "Farm ward must be one of the wards where\
                    the owner is registered."
            )
        if owner.role != RoleChoices.FARMER:
            raise serializers.ValidationError(
                "Owner must have the role 'Farmer'."
            )
        return attrs


class FarmsImportSerializer(serializers.Serializer):
    import_file = serializers.FileField(write_only=True, required=True)

    def create(self, validated_data):
        shapefile = validated_data.pop("import_file", None)
        info = import_farms(shapefile)
        return info
