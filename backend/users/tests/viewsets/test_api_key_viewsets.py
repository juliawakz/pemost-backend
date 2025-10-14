from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from users.factory import FarmerFactory, SuperadminFactory, SystemAdminFactory
from users.models import ApiKey


@pytest.mark.django_db
class TestApiKeyViewSet:
    """Tests for API Key viewset"""

    def setup_method(self):
        """Set up test data"""
        self.client = APIClient()

    def test_create_api_key_as_superadmin(self):
        """Test superadmin can create API key"""
        superadmin = SuperadminFactory()

        self.client.force_authenticate(user=superadmin)

        data = {
            'name': 'Test API Key',
            'is_active': True,
        }

        response = self.client.post('/api/v2/api-keys/', data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'Test API Key'
        assert response.data['key'].startswith('pemost_')
        assert response.data['is_active'] is True
        assert ApiKey.objects.count() == 1

        # Verify full key is shown on creation
        api_key = ApiKey.objects.first()
        assert response.data['key'] == api_key.key

    def test_create_api_key_with_expiration(self):
        """Test creating API key with custom expiration"""
        superadmin = SuperadminFactory()
        future_date = timezone.now() + timedelta(days=90)

        self.client.force_authenticate(user=superadmin)

        data = {
            'name': 'Short-lived Key',
            'expires_at': future_date.isoformat(),
        }

        response = self.client.post('/api/v2/api-keys/', data)

        assert response.status_code == status.HTTP_201_CREATED
        api_key = ApiKey.objects.first()
        assert api_key.expires_at.date() == future_date.date()

    def test_create_api_key_non_superadmin_fails(self):
        """Test non-superadmin cannot create API key"""
        farmer = FarmerFactory()

        self.client.force_authenticate(user=farmer)

        data = {
            'name': 'Test API Key',
        }

        response = self.client.post('/api/v2/api-keys/', data)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_list_api_keys_as_superadmin(self):
        """Test superadmin can list their API keys"""
        superadmin = SuperadminFactory()
        other_superadmin = SuperadminFactory()

        # Create API keys for both users
        ApiKey.objects.create(user=superadmin, name='Key 1')
        ApiKey.objects.create(user=superadmin, name='Key 2')
        ApiKey.objects.create(user=other_superadmin, name='Other Key')

        self.client.force_authenticate(user=superadmin)

        response = self.client.get('/api/v2/api-keys/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2

    def test_list_api_keys_masks_key(self):
        """Test that API keys are masked in list view"""
        superadmin = SuperadminFactory()

        api_key = ApiKey.objects.create(user=superadmin, name='Test Key')

        self.client.force_authenticate(user=superadmin)

        response = self.client.get('/api/v2/api-keys/')

        assert response.status_code == status.HTTP_200_OK
        result_key = response.data['results'][0]['key']
        assert result_key.startswith(api_key.prefix)
        assert '*' in result_key
        assert result_key != api_key.key

    def test_retrieve_api_key_detail(self):
        """Test retrieving single API key"""
        superadmin = SuperadminFactory()
        api_key = ApiKey.objects.create(user=superadmin, name='Test Key')

        self.client.force_authenticate(user=superadmin)

        response = self.client.get(f'/api/v2/api-keys/{api_key.id}/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == str(api_key.id)
        assert response.data['name'] == 'Test Key'
        # Key should be masked in detail view
        assert '*' in response.data['key']

    def test_deactivate_api_key(self):
        """Test deactivating an API key"""
        superadmin = SuperadminFactory()
        api_key = ApiKey.objects.create(
            user=superadmin,
            name='Test Key',
            is_active=True
        )

        self.client.force_authenticate(user=superadmin)

        response = self.client.post(f'/api/v2/api-keys/{api_key.id}/deactivate/')

        assert response.status_code == status.HTTP_200_OK
        api_key.refresh_from_db()
        assert api_key.is_active is False
        assert response.data['is_active'] is False

    def test_deactivate_already_inactive_key(self):
        """Test deactivating already inactive key"""
        superadmin = SuperadminFactory()
        api_key = ApiKey.objects.create(
            user=superadmin,
            name='Test Key',
            is_active=False
        )

        self.client.force_authenticate(user=superadmin)

        response = self.client.post(f'/api/v2/api-keys/{api_key.id}/deactivate/')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'already inactive' in str(response.data)

    def test_reactivate_api_key(self):
        """Test reactivating an API key"""
        superadmin = SuperadminFactory()
        api_key = ApiKey.objects.create(
            user=superadmin,
            name='Test Key',
            is_active=False
        )

        self.client.force_authenticate(user=superadmin)

        response = self.client.post(f'/api/v2/api-keys/{api_key.id}/reactivate/')

        assert response.status_code == status.HTTP_200_OK
        api_key.refresh_from_db()
        assert api_key.is_active is True
        assert response.data['is_active'] is True

    def test_reactivate_already_active_key(self):
        """Test reactivating already active key"""
        superadmin = SuperadminFactory()
        api_key = ApiKey.objects.create(
            user=superadmin,
            name='Test Key',
            is_active=True
        )

        self.client.force_authenticate(user=superadmin)

        response = self.client.post(f'/api/v2/api-keys/{api_key.id}/reactivate/')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'already active' in str(response.data)

    def test_cannot_manage_other_users_api_key(self):
        """Test superadmin cannot manage another superadmin's API key"""
        superadmin1 = SuperadminFactory()
        superadmin2 = SuperadminFactory()

        api_key = ApiKey.objects.create(user=superadmin2, name='Other Key')

        self.client.force_authenticate(user=superadmin1)

        # Try to deactivate
        response = self.client.post(f'/api/v2/api-keys/{api_key.id}/deactivate/')
        assert response.status_code == status.HTTP_404_NOT_FOUND

        # Try to retrieve
        response = self.client.get(f'/api/v2/api-keys/{api_key.id}/')
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_system_admin_can_view_all_api_keys(self):
        """Test system admin can view all API keys"""
        admin = SystemAdminFactory()
        superadmin1 = SuperadminFactory()
        superadmin2 = SuperadminFactory()

        ApiKey.objects.create(user=superadmin1, name='Key 1')
        ApiKey.objects.create(user=superadmin2, name='Key 2')

        self.client.force_authenticate(user=admin)

        response = self.client.get('/api/v2/api-keys/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2

    def test_update_api_key_name(self):
        """Test updating API key name"""
        superadmin = SuperadminFactory()
        api_key = ApiKey.objects.create(user=superadmin, name='Old Name')

        self.client.force_authenticate(user=superadmin)

        data = {'name': 'New Name'}
        response = self.client.patch(f'/api/v2/api-keys/{api_key.id}/', data)

        assert response.status_code == status.HTTP_200_OK
        api_key.refresh_from_db()
        assert api_key.name == 'New Name'

    def test_delete_api_key(self):
        """Test deleting API key"""
        superadmin = SuperadminFactory()
        api_key = ApiKey.objects.create(user=superadmin, name='Test Key')

        self.client.force_authenticate(user=superadmin)

        response = self.client.delete(f'/api/v2/api-keys/{api_key.id}/')

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert ApiKey.objects.count() == 0

    def test_api_key_is_valid_field_in_response(self):
        """Test that is_valid field is included in response"""
        superadmin = SuperadminFactory()

        # Create active key
        active_key = ApiKey.objects.create(
            user=superadmin,
            name='Active Key',
            is_active=True
        )

        # Create expired key
        expired_key = ApiKey.objects.create(
            user=superadmin,
            name='Expired Key',
            is_active=True,
            expires_at=timezone.now() - timedelta(days=1)
        )

        # Create inactive key
        inactive_key = ApiKey.objects.create(
            user=superadmin,
            name='Inactive Key',
            is_active=False
        )

        self.client.force_authenticate(user=superadmin)

        # Check active key
        response = self.client.get(f'/api/v2/api-keys/{active_key.id}/')
        assert response.data['is_valid'] is True

        # Check expired key
        response = self.client.get(f'/api/v2/api-keys/{expired_key.id}/')
        assert response.data['is_valid'] is False

        # Check inactive key
        response = self.client.get(f'/api/v2/api-keys/{inactive_key.id}/')
        assert response.data['is_valid'] is False

    def test_filter_by_active_status(self):
        """Test filtering API keys by active status"""
        superadmin = SuperadminFactory()

        ApiKey.objects.create(user=superadmin, name='Active 1', is_active=True)
        ApiKey.objects.create(user=superadmin, name='Active 2', is_active=True)
        ApiKey.objects.create(user=superadmin, name='Inactive', is_active=False)

        self.client.force_authenticate(user=superadmin)

        response = self.client.get('/api/v2/api-keys/', {'is_active': 'true'})

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2

    def test_unauthenticated_cannot_access(self):
        """Test unauthenticated users cannot access API keys"""
        response = self.client.get('/api/v2/api-keys/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        response = self.client.post('/api/v2/api-keys/', {'name': 'Test'})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
