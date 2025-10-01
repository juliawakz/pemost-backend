from farms.models.plantation import Plantation
from rest_framework import serializers


class PlantationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plantation
        fields = "__all__"

    def validate(self, attrs):
        user = self.context["request"].user
        farm = attrs.get("farm")

        if not (user.is_superuser or user.is_system_admin()):
            if user.is_super_extension():
                if not user.counties.filter(name=farm.ward.subcounty.county.name).exists():
                    raise serializers.ValidationError(
                        f"You're not allowed to add a farm {farm} outside\
                            your region(s)."
                    )
            elif user.is_e_extension():
                if not user.wards.filter(name=farm.ward.name).exists():
                    raise serializers.ValidationError(
                        f"You're not allowed to add a farm {farm} outside\
                            your region(s)."
                    )
            elif user.is_farmer():
                if farm.owner != user:
                    raise serializers.ValidationError(
                        f"You must own the farm {farm} to create a plantation."
                    )
            elif user.is_agrodealer():
                raise serializers.ValidationError(
                    "You are not allowed to perform this action."
                )

        return attrs
