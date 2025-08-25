from django.contrib.auth import get_user_model
from rest_framework import serializers
from users.exceptions import AccountNotRegisteredException

User = get_user_model()


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "full_name",
            "email",
            "phone_number",
            "profile_photo",
            "type"
        )
        extra_kwargs = {
            "id": {"read_only": True},
            "email": {"read_only": True},
            "full_name": {"read_only": True},
            "type": {"read_only": True}
        }


class ProfileExistsSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, write_only=True)
    user = ProfileSerializer(
        read_only=True,
    )

    def validate(self, attrs):
        email = attrs.get("email")

        user = User.objects.filter(email=email).first()

        if not user:
            raise AccountNotRegisteredException()

        attrs = {"user": user}

        return attrs
