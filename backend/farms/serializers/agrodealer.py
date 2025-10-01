from farms.models.agrodealer import AgroDealer
from rest_framework import serializers
from users.choices import RoleChoices
from farms.utils.location_checks import LocationChecks

location_checks = LocationChecks()


class AgroDealerSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgroDealer
        fields = "__all__"

    def validate(self, attrs):
        user = self.request.user
        ward = attrs.get("ward")
        owner = attrs.get("owner")

        if owner and owner.role != RoleChoices.AGRODEALER:
            raise serializers.ValidationError(
                "Owner must have the role 'Agrodealer'."
            )

        location_checks.check_ward(ward, user)

        return attrs
