from django.contrib.auth import get_user_model
from farms.models.farm import Farm
from farms.utils.location_checks import LocationChecks
from locations.models.ward import Ward
from rest_framework import serializers

location_checks = LocationChecks()

User = get_user_model()


class FarmSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )
    ward = serializers.PrimaryKeyRelatedField(
        queryset=Ward.objects.all()
    )

    class Meta:
        model = Farm
        fields = "__all__"

    def validate(self, attrs):
        owner = attrs.get("owner")
        ward = attrs.get("ward")
        user = self.context["request"].user

        if owner and not owner.is_farmer():
            raise serializers.ValidationError(
                "Owner must have the role 'Farmer'."
            )

        location_checks.check_ward_farmer(ward, user)

        return attrs
