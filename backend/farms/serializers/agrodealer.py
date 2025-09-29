from farms.models.agrodealer import AgroDealer
from rest_framework import serializers
from users.choices import RoleChoices


class AgroDealerSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgroDealer
        fields = "__all__"

    def validate(self, attrs):
        user = self.request.user
        if user.role == RoleChoices.AGRODEALER or user.role == RoleChoices.FARMER:
            raise serializers.ValidationError(
                "You are not allowed to perform this action."
            )
        if attrs and attrs.role != RoleChoices.AGRODEALER:
            raise serializers.ValidationError(
                "Owner must have the role 'Agrodealer'."
            )
        return attrs
