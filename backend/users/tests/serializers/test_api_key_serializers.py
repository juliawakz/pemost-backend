import pytest
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIRequestFactory
from users.factory import SuperadminFactory, FarmerFactory
from users.serializers.api_key import ApiKeySerializer, ApiKeyCreateSerializer


@pytest.mark.django_db
class TestApiKeySerializer:
    """Tests for API Key serializer"""

    def setup_method(self):
        """Set up test data"""
        self.factory = APIRequestFactory()

    def test_create_api_key_as_superadmin(self):
        """Test creating an API key as superadmin"""
        superadmin = SuperadminFactory()

        data = {
            'name': 'Test API Key',
            'is_active': True,
        }

        request = self.factory.post('/fake-url/')
        request.user = superadmin

        serializer = ApiKeyCreateSerializer(
            data=data,
            context={'request': request}
        )

        assert serializer.is_valid(), serializer.errors
        api_key = serializer.save()

        assert api_key.user == superadmin
        assert api_key.name == 'Test API Key'
        assert api_key.key.startswith('pemost_')
        assert api_key.is_active is True

    def test_non_superadmin_cannot_create_api_key(self):
        """Test that non-superadmin cannot create API key"""
        farmer = FarmerFactory()

        data = {
            'name': 'Test API Key',
        }

        request = self.factory.post('/fake-url/')
        request.user = farmer

        serializer = ApiKeyCreateSerializer(
            data=data,
            context={'request': request}
        )

        assert not serializer.is_valid()
        assert 'Only Superadmin users can generate API keys' in str(serializer.errors)

    def test_api_key_with_custom_expiration(self):
        """Test creating API key with custom expiration"""
        superadmin = SuperadminFactory()
        future_date = timezone.now() + timedelta(days=90)

        data = {
            'name': 'Short-lived Key',
            'expires_at': future_date.isoformat(),
        }

        request = self.factory.post('/fake-url/')
        request.user = superadmin

        serializer = ApiKeyCreateSerializer(
            data=data,
            context={'request': request}
        )

        assert serializer.is_valid(), serializer.errors
        api_key = serializer.save()

        # Check expiration is set (may have slight time difference)
        assert api_key.expires_at.date() == future_date.date()

    def test_api_key_representation_masks_key(self):
        """Test that API key is masked in representation (except on creation)"""
        superadmin = SuperadminFactory()

        data = {
            'name': 'Test Key',
        }

        request = self.factory.post('/fake-url/')
        request.user = superadmin

        serializer = ApiKeySerializer(
            data=data,
            context={'request': request}
        )

        assert serializer.is_valid()
        api_key = serializer.save()

        # Default representation should mask the key
        default_serializer = ApiKeySerializer(api_key)
        representation = default_serializer.data

        assert representation['key'].startswith(api_key.prefix)
        assert '*' in representation['key']
        assert 'is_valid' in representation

    def test_api_key_create_shows_full_key(self):
        """Test that full key is shown on creation"""
        superadmin = SuperadminFactory()

        data = {
            'name': 'Test Key',
        }

        request = self.factory.post('/fake-url/')
        request.user = superadmin

        serializer = ApiKeyCreateSerializer(
            data=data,
            context={'request': request}
        )

        assert serializer.is_valid()
        api_key = serializer.save()

        # Create serializer should show full key
        representation = serializer.data
        assert representation['key'] == api_key.key
        assert representation['key'].startswith('pemost_')
