import pytest
from rest_framework import status
from rest_framework.test import APIClient
from users.factory import (
    SystemAdminFactory,
    SuperadminFactory,
    SuperExtensionFactory,
    EExtensionFactory,
    FarmerFactory,
    AgroDealerFactory,
    SuperExtensionOfficerProfileFactory,
    EExtensionOfficerProfileFactory,
    FarmerProfileFactory,
)
from locations.factory.county import CountyFactory
from locations.factory.subcounty import SubCountyFactory
from locations.factory.ward import WardFactory
from users.models import EExtensionWorkRequest, FarmerWorkRequest
from users.choices import WorkRequestStatusChoices


@pytest.mark.django_db
class TestUserVisibilityFiltering:
    """Tests for user visibility filtering based on RBAC rules"""

    def setup_method(self):
        """Set up test data"""
        self.client = APIClient()

        # Create location hierarchy
        self.county = CountyFactory()
        self.subcounty = SubCountyFactory(county=self.county)
        self.ward = WardFactory(subcounty=self.subcounty)

    def test_system_admin_can_see_all_users(self):
        """Test system admin can see all users"""
        admin = SystemAdminFactory()

        # Create various users
        SuperadminFactory()
        SuperExtensionFactory()
        EExtensionFactory()
        FarmerFactory()
        AgroDealerFactory()

        self.client.force_authenticate(user=admin)

        response = self.client.get('/api/v2/users/')

        assert response.status_code == status.HTTP_200_OK
        # 6 users total (5 created + 1 admin)
        assert response.data['count'] == 6

    def test_super_extension_sees_visible_e_extensions(self):
        """Test super extension can see visible e-extensions in their county"""
        super_ext = SuperExtensionFactory()
        super_ext_profile = SuperExtensionOfficerProfileFactory(user=super_ext)
        super_ext_profile.counties.add(self.county)

        # Create visible e-extension in same county
        visible_e_ext = EExtensionFactory()
        visible_profile = EExtensionOfficerProfileFactory(
            user=visible_e_ext,
            is_visible=True
        )
        visible_profile.wards.add(self.ward)

        # Create invisible e-extension in same county
        invisible_e_ext = EExtensionFactory()
        invisible_profile = EExtensionOfficerProfileFactory(
            user=invisible_e_ext,
            is_visible=False
        )
        invisible_profile.wards.add(self.ward)

        # Create visible e-extension in different county
        other_county = CountyFactory()
        other_subcounty = SubCountyFactory(county=other_county)
        other_ward = WardFactory(subcounty=other_subcounty)

        other_e_ext = EExtensionFactory()
        other_profile = EExtensionOfficerProfileFactory(
            user=other_e_ext,
            is_visible=True
        )
        other_profile.wards.add(other_ward)

        self.client.force_authenticate(user=super_ext)

        response = self.client.get('/api/v2/users/')

        assert response.status_code == status.HTTP_200_OK
        user_ids = [user['id'] for user in response.data['results']]

        # Should see visible e-extension in same county
        assert str(visible_e_ext.id) in user_ids
        # Should NOT see invisible e-extension
        assert str(invisible_e_ext.id) not in user_ids
        # Should NOT see e-extension in different county
        assert str(other_e_ext.id) not in user_ids

    def test_super_extension_sees_e_extensions_who_sent_requests(self):
        """Test super extension can see e-extensions who sent work requests"""
        super_ext = SuperExtensionFactory()
        super_ext_profile = SuperExtensionOfficerProfileFactory(user=super_ext)
        super_ext_profile.counties.add(self.county)

        # Create invisible e-extension who sent a request
        e_ext_with_request = EExtensionFactory()
        e_ext_profile = EExtensionOfficerProfileFactory(
            user=e_ext_with_request,
            is_visible=False
        )
        e_ext_profile.wards.add(self.ward)

        # Create work request
        EExtensionWorkRequest.objects.create(
            e_extension=e_ext_with_request,
            super_extension=super_ext,
            status=WorkRequestStatusChoices.PENDING
        )

        # Create invisible e-extension without request
        e_ext_no_request = EExtensionFactory()
        no_request_profile = EExtensionOfficerProfileFactory(
            user=e_ext_no_request,
            is_visible=False
        )
        no_request_profile.wards.add(self.ward)

        self.client.force_authenticate(user=super_ext)

        response = self.client.get('/api/v2/users/')

        assert response.status_code == status.HTTP_200_OK
        user_ids = [user['id'] for user in response.data['results']]

        # Should see e-extension who sent request even though not visible
        assert str(e_ext_with_request.id) in user_ids
        # Should NOT see invisible e-extension without request
        assert str(e_ext_no_request.id) not in user_ids

    def test_e_extension_sees_visible_farmers(self):
        """Test e-extension can see visible farmers in their ward"""
        e_ext = EExtensionFactory()
        e_ext_profile = EExtensionOfficerProfileFactory(user=e_ext)
        e_ext_profile.wards.add(self.ward)

        # Create visible farmer in same ward
        visible_farmer = FarmerFactory()
        visible_profile = FarmerProfileFactory(
            user=visible_farmer,
            is_visible=True
        )
        visible_profile.wards.add(self.ward)

        # Create invisible farmer in same ward
        invisible_farmer = FarmerFactory()
        invisible_profile = FarmerProfileFactory(
            user=invisible_farmer,
            is_visible=False
        )
        invisible_profile.wards.add(self.ward)

        # Create visible farmer in different ward
        other_ward = WardFactory(subcounty=self.subcounty)
        other_farmer = FarmerFactory()
        other_profile = FarmerProfileFactory(
            user=other_farmer,
            is_visible=True
        )
        other_profile.wards.add(other_ward)

        self.client.force_authenticate(user=e_ext)

        response = self.client.get('/api/v2/users/')

        assert response.status_code == status.HTTP_200_OK
        user_ids = [user['id'] for user in response.data['results']]

        # Should see visible farmer in same ward
        assert str(visible_farmer.id) in user_ids
        # Should NOT see invisible farmer
        assert str(invisible_farmer.id) not in user_ids
        # Should NOT see farmer in different ward
        assert str(other_farmer.id) not in user_ids

    def test_e_extension_sees_farmers_who_sent_requests(self):
        """Test e-extension can see farmers who sent work requests"""
        e_ext = EExtensionFactory()
        e_ext_profile = EExtensionOfficerProfileFactory(user=e_ext)
        e_ext_profile.wards.add(self.ward)

        # Create invisible farmer who sent a request
        farmer_with_request = FarmerFactory()
        farmer_profile = FarmerProfileFactory(
            user=farmer_with_request,
            is_visible=False
        )
        farmer_profile.wards.add(self.ward)

        # Create work request
        FarmerWorkRequest.objects.create(
            farmer=farmer_with_request,
            e_extension=e_ext,
            status=WorkRequestStatusChoices.PENDING
        )

        # Create invisible farmer without request
        farmer_no_request = FarmerFactory()
        no_request_profile = FarmerProfileFactory(
            user=farmer_no_request,
            is_visible=False
        )
        no_request_profile.wards.add(self.ward)

        self.client.force_authenticate(user=e_ext)

        response = self.client.get('/api/v2/users/')

        assert response.status_code == status.HTTP_200_OK
        user_ids = [user['id'] for user in response.data['results']]

        # Should see farmer who sent request even though not visible
        assert str(farmer_with_request.id) in user_ids
        # Should NOT see invisible farmer without request
        assert str(farmer_no_request.id) not in user_ids

    def test_e_extension_sees_all_agrodealers(self):
        """Test e-extension can see all agrodealers"""
        e_ext = EExtensionFactory()
        e_ext_profile = EExtensionOfficerProfileFactory(user=e_ext)
        e_ext_profile.wards.add(self.ward)

        # Create multiple agrodealers
        agrodealer1 = AgroDealerFactory()
        agrodealer2 = AgroDealerFactory()

        self.client.force_authenticate(user=e_ext)

        response = self.client.get('/api/v2/users/')

        assert response.status_code == status.HTTP_200_OK
        user_ids = [user['id'] for user in response.data['results']]

        # Should see all agrodealers
        assert str(agrodealer1.id) in user_ids
        assert str(agrodealer2.id) in user_ids

    def test_farmer_sees_e_extensions_in_ward(self):
        """Test farmer can see e-extensions in their ward"""
        farmer = FarmerFactory()
        farmer_profile = FarmerProfileFactory(user=farmer)
        farmer_profile.wards.add(self.ward)

        # Create e-extension in same ward
        e_ext_same_ward = EExtensionFactory()
        same_ward_profile = EExtensionOfficerProfileFactory(user=e_ext_same_ward)
        same_ward_profile.wards.add(self.ward)

        # Create e-extension in different ward
        other_ward = WardFactory(subcounty=self.subcounty)
        e_ext_other_ward = EExtensionFactory()
        other_ward_profile = EExtensionOfficerProfileFactory(user=e_ext_other_ward)
        other_ward_profile.wards.add(other_ward)

        self.client.force_authenticate(user=farmer)

        response = self.client.get('/api/v2/users/')

        assert response.status_code == status.HTTP_200_OK
        user_ids = [user['id'] for user in response.data['results']]

        # Should see e-extension in same ward
        assert str(e_ext_same_ward.id) in user_ids
        # Should NOT see e-extension in different ward
        assert str(e_ext_other_ward.id) not in user_ids

    def test_farmer_sees_all_agrodealers(self):
        """Test farmer can see all agrodealers"""
        farmer = FarmerFactory()
        FarmerProfileFactory(user=farmer)

        # Create multiple agrodealers
        agrodealer1 = AgroDealerFactory()
        agrodealer2 = AgroDealerFactory()

        self.client.force_authenticate(user=farmer)

        response = self.client.get('/api/v2/users/')

        assert response.status_code == status.HTTP_200_OK
        user_ids = [user['id'] for user in response.data['results']]

        # Should see all agrodealers
        assert str(agrodealer1.id) in user_ids
        assert str(agrodealer2.id) in user_ids

    def test_agrodealer_sees_only_themselves(self):
        """Test agrodealer can only see themselves"""
        agrodealer = AgroDealerFactory()

        # Create other users
        FarmerFactory()
        EExtensionFactory()
        SuperExtensionFactory()

        self.client.force_authenticate(user=agrodealer)

        response = self.client.get('/api/v2/users/')

        assert response.status_code == status.HTTP_200_OK
        # Should only see themselves
        assert response.data['count'] == 1
        assert response.data['results'][0]['id'] == str(agrodealer.id)

    def test_superadmin_visibility(self):
        """Test superadmin visibility rules"""
        superadmin = SuperadminFactory()

        # Create other users
        farmer = FarmerFactory()
        e_ext = EExtensionFactory()

        self.client.force_authenticate(user=superadmin)

        response = self.client.get('/api/v2/users/')

        assert response.status_code == status.HTTP_200_OK
        user_ids = [user['id'] for user in response.data['results']]

        # Superadmin should see themselves
        assert str(superadmin.id) in user_ids

    def test_filter_by_role(self):
        """Test filtering users by role"""
        admin = SystemAdminFactory()

        # Create users of different roles
        FarmerFactory.create_batch(3)
        EExtensionFactory.create_batch(2)
        AgroDealerFactory.create_batch(2)

        self.client.force_authenticate(user=admin)

        # Filter by farmer role
        response = self.client.get('/api/v2/users/', {'role': 'FARMER'})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 3

        # Filter by e-extension role
        response = self.client.get('/api/v2/users/', {'role': 'E_EXTENSION'})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2

    def test_accepted_request_makes_user_visible(self):
        """Test that accepting a work request makes the user visible"""
        super_ext = SuperExtensionFactory()
        super_ext_profile = SuperExtensionOfficerProfileFactory(user=super_ext)
        super_ext_profile.counties.add(self.county)

        # Create invisible e-extension
        e_ext = EExtensionFactory()
        e_ext_profile = EExtensionOfficerProfileFactory(
            user=e_ext,
            is_visible=False
        )
        e_ext_profile.wards.add(self.ward)

        # Create and accept work request
        work_request = EExtensionWorkRequest.objects.create(
            e_extension=e_ext,
            super_extension=super_ext,
            status=WorkRequestStatusChoices.PENDING
        )
        work_request.accept()

        self.client.force_authenticate(user=super_ext)

        response = self.client.get('/api/v2/users/')

        assert response.status_code == status.HTTP_200_OK
        user_ids = [user['id'] for user in response.data['results']]

        # Should still see e-extension after acceptance
        assert str(e_ext.id) in user_ids

    def test_rejected_request_does_not_keep_user_visible(self):
        """Test that rejecting a work request doesn't keep user visible if not visible"""
        super_ext = SuperExtensionFactory()
        super_ext_profile = SuperExtensionOfficerProfileFactory(user=super_ext)
        super_ext_profile.counties.add(self.county)

        # Create invisible e-extension
        e_ext = EExtensionFactory()
        e_ext_profile = EExtensionOfficerProfileFactory(
            user=e_ext,
            is_visible=False
        )
        e_ext_profile.wards.add(self.ward)

        # Create and reject work request
        work_request = EExtensionWorkRequest.objects.create(
            e_extension=e_ext,
            super_extension=super_ext,
            status=WorkRequestStatusChoices.PENDING
        )
        work_request.reject()

        self.client.force_authenticate(user=super_ext)

        response = self.client.get('/api/v2/users/')

        assert response.status_code == status.HTTP_200_OK
        user_ids = [user['id'] for user in response.data['results']]

        # Should still see e-extension who sent request (even if rejected)
        assert str(e_ext.id) in user_ids

    def test_unauthenticated_user_cannot_list_users(self):
        """Test unauthenticated users cannot list users"""
        response = self.client.get('/api/v2/users/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_multiple_wards_visibility(self):
        """Test e-extension can see farmers from all their assigned wards"""
        e_ext = EExtensionFactory()
        e_ext_profile = EExtensionOfficerProfileFactory(user=e_ext)

        # Create two wards
        ward1 = self.ward
        ward2 = WardFactory(subcounty=self.subcounty)

        # Assign both wards to e-extension
        e_ext_profile.wards.add(ward1, ward2)

        # Create visible farmers in both wards
        farmer1 = FarmerFactory()
        farmer1_profile = FarmerProfileFactory(user=farmer1, is_visible=True)
        farmer1_profile.wards.add(ward1)

        farmer2 = FarmerFactory()
        farmer2_profile = FarmerProfileFactory(user=farmer2, is_visible=True)
        farmer2_profile.wards.add(ward2)

        self.client.force_authenticate(user=e_ext)

        response = self.client.get('/api/v2/users/')

        assert response.status_code == status.HTTP_200_OK
        user_ids = [user['id'] for user in response.data['results']]

        # Should see farmers from both wards
        assert str(farmer1.id) in user_ids
        assert str(farmer2.id) in user_ids
