from django.contrib.auth import get_user_model
from farms.models.agrodealer import AgroDealer
from farms.utils.location_checks import LocationChecks
from locations.models.ward import Ward
from rest_framework import serializers

location_checks = LocationChecks()
User = get_user_model()


class AgroDealerSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )
    ward = serializers.PrimaryKeyRelatedField(
        queryset=Ward.objects.all()
    )

    class Meta:
        model = AgroDealer
        fields = "__all__"

    def validate(self, attrs):
        user = self.request.user
        ward = attrs.get("ward")
        owner = attrs.get("owner")

        if owner and not owner.is_agrodealer():
            raise serializers.ValidationError(
                "Owner must have the role 'Agrodealer'."
            )

        location_checks.check_ward(ward, user)

        return attrs
