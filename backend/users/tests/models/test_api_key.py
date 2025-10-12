import pytest
from django.utils import timezone
from datetime import timedelta
from users.factory import SuperadminFactory, ApiKeyFactory
from users.models import ApiKey


@pytest.mark.django_db
class TestApiKey:
    """Tests for API Key model"""

    def test_create_api_key(self):
        """Test creating an API key"""
        superadmin = SuperadminFactory()
        api_key = ApiKeyFactory(
            user=superadmin,
            name="Test API Key"
        )

        assert api_key.key.startswith("pemost_")
        assert len(api_key.key) > 40
        assert api_key.prefix == api_key.key[:8]
        assert api_key.is_active is True
        assert api_key.expires_at > timezone.now()
        assert api_key.last_used_at is None

    def test_api_key_string_representation(self):
        """Test API key string representation"""
        superadmin = SuperadminFactory()
        api_key = ApiKeyFactory(
            user=superadmin,
            name="Production Key"
        )

        expected = f"Production Key ({api_key.prefix}...)"
        assert str(api_key) == expected

    def test_api_key_is_valid_active_not_expired(self):
        """Test that active and not expired key is valid"""
        api_key = ApiKeyFactory(
            is_active=True,
            expires_at=timezone.now() + timedelta(days=30)
        )

        assert api_key.is_valid() is True

    def test_api_key_is_valid_inactive(self):
        """Test that inactive key is not valid"""
        api_key = ApiKeyFactory(
            is_active=False,
            expires_at=timezone.now() + timedelta(days=30)
        )

        assert api_key.is_valid() is False

    def test_api_key_is_valid_expired(self):
        """Test that expired key is not valid"""
        api_key = ApiKeyFactory(
            is_active=True,
            expires_at=timezone.now() - timedelta(days=1)
        )

        assert api_key.is_valid() is False

    def test_api_key_record_usage(self):
        """Test recording API key usage"""
        api_key = ApiKeyFactory()

        assert api_key.last_used_at is None

        api_key.record_usage()
        api_key.refresh_from_db()

        assert api_key.last_used_at is not None
        assert api_key.last_used_at <= timezone.now()

    def test_api_key_generate_key_is_unique(self):
        """Test that generated keys are unique"""
        key1 = ApiKey.generate_key()
        key2 = ApiKey.generate_key()

        assert key1 != key2
        assert key1.startswith("pemost_")
        assert key2.startswith("pemost_")

    def test_api_key_auto_generates_on_save(self):
        """Test that key is auto-generated on save if not provided"""
        superadmin = SuperadminFactory()
        api_key = ApiKey.objects.create(
            user=superadmin,
            name="Auto Generated Key"
        )

        assert api_key.key is not None
        assert api_key.key.startswith("pemost_")
        assert api_key.prefix == api_key.key[:8]
