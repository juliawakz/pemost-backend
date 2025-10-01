from farms.models.farm import Farm
from rest_framework import serializers
from users.choices import RoleChoices
from farms.utils.location_checks import LocationChecks

location_checks = LocationChecks()


class FarmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Farm
        fields = "__all__"

    def validate(self, attrs):
        owner = attrs.get("owner")
        ward = attrs.get("ward")
        user = self.request.user

        if owner.role != RoleChoices.FARMER:
            raise serializers.ValidationError(
                "Owner must have the role 'Farmer'."
            )

        location_checks.check_ward(ward, user)

        return attrs
