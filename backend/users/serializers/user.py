from django.contrib.auth import get_user_model
from rest_framework import serializers
from users.utils.user import UserUtils

User = get_user_model()
user_utils = UserUtils()


class UserSerializer(serializers.ModelSerializer):
    """Read-only serializer for user data (for responses)"""
    role = serializers.CharField(read_only=True)
    full_name = serializers.CharField(read_only=True)
    profile_photo_url = serializers.CharField(read_only=True)
    is_verified = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id", "email", "first_name", "last_name", "phone_number",
            "id_number", "role", "is_verified", "full_name",
            "profile_photo_url", "created_at", "updated_at"
        ]
        read_only_fields = fields
