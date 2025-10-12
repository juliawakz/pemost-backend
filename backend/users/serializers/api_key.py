from rest_framework import serializers
from django.contrib.auth import get_user_model
from users.models import ApiKey
from datetime import timedelta
from django.utils import timezone

User = get_user_model()


class ApiKeySerializer(serializers.ModelSerializer):
    """Serializer for API Keys"""
    key = serializers.CharField(read_only=True, help_text="The actual API key (only shown once after creation)")
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = ApiKey
        fields = [
            "id",
            "name",
            "key",
            "prefix",
            "user",
            "user_email",
            "is_active",
            "expires_at",
            "last_used_at",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "key",
            "prefix",
            "user",
            "user_email",
            "last_used_at",
            "created_at",
        ]

    def validate(self, attrs):
        request = self.context.get('request')
        if request and request.method == 'POST':
            # Only systemadmin can create API keys
            if not (request.user.is_systemadmin() or request.user.is_superuser):
                raise serializers.ValidationError(
                    "Only systemadmin/superuser users can generate API keys."
                )

            # Auto-set user to current user
            attrs['user'] = request.user

            # Set default expiration if not provided (1 year)
            if 'expires_at' not in attrs or attrs['expires_at'] is None:
                attrs['expires_at'] = timezone.now() + timedelta(days=365)

        return attrs

    def to_representation(self, instance):
        data = super().to_representation(instance)

        # Only show the full key on creation (when in context)
        if not self.context.get('show_key', False):
            data['key'] = f"{instance.prefix}..." + "*" * 32

        # Add validity status
        data['is_valid'] = instance.is_valid()

        return data


class ApiKeyCreateSerializer(ApiKeySerializer):
    """Serializer for creating API Keys - shows full key"""

    def create(self, validated_data):
        instance = super().create(validated_data)
        # Set flag to show full key in response
        self.context['show_key'] = True
        return instance
