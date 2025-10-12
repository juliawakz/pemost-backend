import pytest
from unittest.mock import Mock
from users.factory import (
    SystemAdminFactory,
    SuperadminFactory,
    SuperExtensionFactory,
    EExtensionFactory,
    FarmerFactory,
    AgroDealerFactory,
)
from backend.users.user import (
    IsSystemAdminOrSuperUser,
    IsSuperadmin,
    IsSuperExtension,
    IsEExtension,
    IsFarmer,
    IsAgrodealer,
    CanGenerateApiKey,
    CanManageWorkRequest,
)


@pytest.mark.django_db
class TestIsSystemAdminOrSuperUser:
    """Tests for IsSystemAdminOrSuperUser permission"""

    def test_superuser_has_permission(self):
        """Test that superuser has permission"""
        user = SystemAdminFactory(is_superuser=True)
        request = Mock(user=user)
        permission = IsSystemAdminOrSuperUser()

        assert permission.has_permission(request, None) is True

    def test_system_admin_has_permission(self):
        """Test that system admin has permission"""
        user = SystemAdminFactory()
        request = Mock(user=user)
        permission = IsSystemAdminOrSuperUser()

        assert permission.has_permission(request, None) is True

    def test_regular_user_no_permission(self):
        """Test that regular user doesn't have permission"""
        user = FarmerFactory()
        request = Mock(user=user)
        permission = IsSystemAdminOrSuperUser()

        assert permission.has_permission(request, None) is False


@pytest.mark.django_db
class TestIsSuperadmin:
    """Tests for IsSuperadmin permission"""

    def test_superadmin_has_permission(self):
        """Test that superadmin has permission"""
        user = SuperadminFactory()
        request = Mock(user=user)
        permission = IsSuperadmin()

        assert permission.has_permission(request, None) is True

    def test_non_superadmin_no_permission(self):
        """Test that non-superadmin doesn't have permission"""
        user = FarmerFactory()
        request = Mock(user=user)
        permission = IsSuperadmin()

        assert permission.has_permission(request, None) is False


@pytest.mark.django_db
class TestIsSuperExtension:
    """Tests for IsSuperExtension permission"""

    def test_super_extension_has_permission(self):
        """Test that super extension has permission"""
        user = SuperExtensionFactory()
        request = Mock(user=user)
        permission = IsSuperExtension()

        assert permission.has_permission(request, None) is True

    def test_non_super_extension_no_permission(self):
        """Test that non-super extension doesn't have permission"""
        user = EExtensionFactory()
        request = Mock(user=user)
        permission = IsSuperExtension()

        assert permission.has_permission(request, None) is False


@pytest.mark.django_db
class TestIsEExtension:
    """Tests for IsEExtension permission"""

    def test_e_extension_has_permission(self):
        """Test that e-extension has permission"""
        user = EExtensionFactory()
        request = Mock(user=user)
        permission = IsEExtension()

        assert permission.has_permission(request, None) is True

    def test_non_e_extension_no_permission(self):
        """Test that non-e-extension doesn't have permission"""
        user = FarmerFactory()
        request = Mock(user=user)
        permission = IsEExtension()

        assert permission.has_permission(request, None) is False


@pytest.mark.django_db
class TestIsFarmer:
    """Tests for IsFarmer permission"""

    def test_farmer_has_permission(self):
        """Test that farmer has permission"""
        user = FarmerFactory()
        request = Mock(user=user)
        permission = IsFarmer()

        assert permission.has_permission(request, None) is True

    def test_farmer_can_access_own_object(self):
        """Test that farmer can access their own object"""
        user = FarmerFactory()
        request = Mock(user=user)
        obj = Mock(user=user)
        permission = IsFarmer()

        assert permission.has_object_permission(request, None, obj) is True

    def test_farmer_cannot_access_others_object(self):
        """Test that farmer cannot access others' object"""
        user = FarmerFactory()
        other_user = FarmerFactory()
        request = Mock(user=user)
        obj = Mock(user=other_user, owner=other_user)
        permission = IsFarmer()

        assert permission.has_object_permission(request, None, obj) is False

    def test_system_admin_can_access_any_object(self):
        """Test that system admin can access any farmer object"""
        admin = SystemAdminFactory()
        farmer = FarmerFactory()
        request = Mock(user=admin)
        obj = Mock(user=farmer, owner=farmer)
        permission = IsFarmer()

        assert permission.has_object_permission(request, None, obj) is True


@pytest.mark.django_db
class TestIsAgrodealer:
    """Tests for IsAgrodealer permission"""

    def test_agrodealer_has_permission(self):
        """Test that agrodealer has permission"""
        user = AgroDealerFactory()
        request = Mock(user=user)
        permission = IsAgrodealer()

        assert permission.has_permission(request, None) is True

    def test_non_agrodealer_no_permission(self):
        """Test that non-agrodealer doesn't have permission"""
        user = FarmerFactory()
        request = Mock(user=user)
        permission = IsAgrodealer()

        assert permission.has_permission(request, None) is False


@pytest.mark.django_db
class TestCanGenerateApiKey:
    """Tests for CanGenerateApiKey permission"""

    def test_superadmin_can_generate_api_key(self):
        """Test that superadmin can generate API keys"""
        user = SuperadminFactory()
        request = Mock(user=user)
        permission = CanGenerateApiKey()

        assert permission.has_permission(request, None) is True

    def test_non_superadmin_cannot_generate_api_key(self):
        """Test that non-superadmin cannot generate API keys"""
        user = SystemAdminFactory()
        request = Mock(user=user)
        permission = CanGenerateApiKey()

        assert permission.has_permission(request, None) is False


@pytest.mark.django_db
class TestCanManageWorkRequest:
    """Tests for CanManageWorkRequest permission"""

    def test_authenticated_user_has_permission(self):
        """Test that any authenticated user has base permission"""
        user = FarmerFactory()
        request = Mock(user=user)
        permission = CanManageWorkRequest()

        assert permission.has_permission(request, None) is True

    def test_sender_can_view_own_request(self):
        """Test that sender can view their own work request"""
        e_ext = EExtensionFactory()
        super_ext = SuperExtensionFactory()
        request = Mock(user=e_ext)
        obj = Mock(e_extension=e_ext, super_extension=super_ext)
        permission = CanManageWorkRequest()

        assert permission.has_object_permission(request, None, obj) is True

    def test_recipient_can_manage_request(self):
        """Test that recipient can manage work request"""
        e_ext = EExtensionFactory()
        super_ext = SuperExtensionFactory()
        request = Mock(user=super_ext)
        obj = Mock(e_extension=e_ext, super_extension=super_ext)
        permission = CanManageWorkRequest()

        assert permission.has_object_permission(request, None, obj) is True

    def test_unrelated_user_cannot_access_request(self):
        """Test that unrelated user cannot access work request"""
        e_ext = EExtensionFactory()
        super_ext = SuperExtensionFactory()
        other_user = FarmerFactory()
        request = Mock(user=other_user)
        obj = Mock(e_extension=e_ext, super_extension=super_ext)
        permission = CanManageWorkRequest()

        assert permission.has_object_permission(request, None, obj) is False

    def test_system_admin_can_access_any_request(self):
        """Test that system admin can access any work request"""
        admin = SystemAdminFactory()
        e_ext = EExtensionFactory()
        super_ext = SuperExtensionFactory()
        request = Mock(user=admin)
        obj = Mock(e_extension=e_ext, super_extension=super_ext)
        permission = CanManageWorkRequest()

        assert permission.has_object_permission(request, None, obj) is True
