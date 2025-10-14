from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "full_name",
            "id_number",
            "email",
            "phone_number",
            "profile_photo",
            "role",
            "is_verified"
        )
        extra_kwargs = {
            "id": {"read_only": True},
            "email": {"read_only": True},
            "full_name": {"read_only": True},
            "role": {"read_only": True},
            "is_verified": {"read_only": True},
        }
