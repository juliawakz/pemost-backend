import pytest
from rest_framework import status
from rest_framework.test import APIClient
from users.factory import (
    EExtensionFactory,
    SuperExtensionFactory,
    FarmerFactory,
    SystemAdminFactory,
    EExtensionOfficerProfileFactory,
    SuperExtensionOfficerProfileFactory,
    FarmerProfileFactory,
)
from locations.factory.county import CountyFactory
from locations.factory.subcounty import SubCountyFactory
from locations.factory.ward import WardFactory
from users.models import EExtensionWorkRequest, FarmerWorkRequest
from users.choices import WorkRequestStatusChoices


@pytest.mark.django_db
class TestEExtensionWorkRequestViewSet:
    """Tests for E-Extension work request viewset"""

    def setup_method(self):
        """Set up test data"""
        self.client = APIClient()

        # Create location hierarchy
        self.county = CountyFactory()
        self.subcounty = SubCountyFactory(county=self.county)
        self.ward = WardFactory(subcounty=self.subcounty)

    def test_create_work_request_success(self):
        """Test e-extension can create work request to super extension"""
        e_ext = EExtensionFactory()
        super_ext = SuperExtensionFactory()

        # Create profiles with proper location setup
        e_ext_profile = EExtensionOfficerProfileFactory(user=e_ext)
        e_ext_profile.wards.add(self.ward)

        super_ext_profile = SuperExtensionOfficerProfileFactory(user=super_ext)
        super_ext_profile.counties.add(self.county)

        self.client.force_authenticate(user=e_ext)

        data = {
            'super_extension': super_ext.id,
            'message': 'I would like to work with you'
        }

        response = self.client.post('/api/v2/work-requests/e-extension/', data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['e_extension'] == e_ext.id
        assert response.data['super_extension'] == super_ext.id
        assert response.data['status'] == WorkRequestStatusChoices.PENDING
        assert EExtensionWorkRequest.objects.count() == 1

    def test_create_work_request_non_e_extension_fails(self):
        """Test non e-extension user cannot create request"""
        farmer = FarmerFactory()
        super_ext = SuperExtensionFactory()

        self.client.force_authenticate(user=farmer)

        data = {
            'super_extension': super_ext.id,
            'message': 'Test'
        }

        response = self.client.post('/api/v2/work-requests/e-extension/', data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Only E-Extension officers can send work requests' in str(response.data)

    def test_create_work_request_different_county_fails(self):
        """Test cannot send request to super extension in different county"""
        e_ext = EExtensionFactory()
        super_ext = SuperExtensionFactory()

        # Different counties
        county1 = CountyFactory()
        county2 = CountyFactory()
        subcounty1 = SubCountyFactory(county=county1)
        ward1 = WardFactory(subcounty=subcounty1)

        e_ext_profile = EExtensionOfficerProfileFactory(user=e_ext)
        e_ext_profile.wards.add(ward1)

        super_ext_profile = SuperExtensionOfficerProfileFactory(user=super_ext)
        super_ext_profile.counties.add(county2)

        self.client.force_authenticate(user=e_ext)

        data = {
            'super_extension': super_ext.id,
            'message': 'Test'
        }

        response = self.client.post('/api/v2/work-requests/e-extension/', data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'can only send work requests to Super Extension officers in your county' in str(response.data)

    def test_create_duplicate_pending_request_fails(self):
        """Test cannot create duplicate pending requests"""
        e_ext = EExtensionFactory()
        super_ext = SuperExtensionFactory()

        e_ext_profile = EExtensionOfficerProfileFactory(user=e_ext)
        e_ext_profile.wards.add(self.ward)

        super_ext_profile = SuperExtensionOfficerProfileFactory(user=super_ext)
        super_ext_profile.counties.add(self.county)

        # Create existing pending request
        EExtensionWorkRequest.objects.create(
            e_extension=e_ext,
            super_extension=super_ext,
            status=WorkRequestStatusChoices.PENDING
        )

        self.client.force_authenticate(user=e_ext)

        data = {
            'super_extension': super_ext.id,
            'message': 'Another request'
        }

        response = self.client.post('/api/v2/work-requests/e-extension/', data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'already have a pending request' in str(response.data)

    def test_list_work_requests_as_sender(self):
        """Test e-extension can list their sent requests"""
        e_ext = EExtensionFactory()
        super_ext1 = SuperExtensionFactory()
        super_ext2 = SuperExtensionFactory()

        e_ext_profile = EExtensionOfficerProfileFactory(user=e_ext)
        e_ext_profile.wards.add(self.ward)

        # Create multiple requests
        EExtensionWorkRequest.objects.create(
            e_extension=e_ext,
            super_extension=super_ext1,
            status=WorkRequestStatusChoices.PENDING
        )
        EExtensionWorkRequest.objects.create(
            e_extension=e_ext,
            super_extension=super_ext2,
            status=WorkRequestStatusChoices.ACCEPTED
        )

        self.client.force_authenticate(user=e_ext)

        response = self.client.get('/api/v2/work-requests/e-extension/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2

    def test_list_work_requests_as_recipient(self):
        """Test super extension can list received requests"""
        super_ext = SuperExtensionFactory()
        e_ext1 = EExtensionFactory()
        e_ext2 = EExtensionFactory()

        super_ext_profile = SuperExtensionOfficerProfileFactory(user=super_ext)
        super_ext_profile.counties.add(self.county)

        # Create multiple requests to this super extension
        EExtensionWorkRequest.objects.create(
            e_extension=e_ext1,
            super_extension=super_ext,
            status=WorkRequestStatusChoices.PENDING
        )
        EExtensionWorkRequest.objects.create(
            e_extension=e_ext2,
            super_extension=super_ext,
            status=WorkRequestStatusChoices.PENDING
        )

        self.client.force_authenticate(user=super_ext)

        response = self.client.get('/api/v2/work-requests/e-extension/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2

    def test_accept_work_request_success(self):
        """Test super extension can accept work request"""
        e_ext = EExtensionFactory()
        super_ext = SuperExtensionFactory()

        e_ext_profile = EExtensionOfficerProfileFactory(user=e_ext)
        e_ext_profile.wards.add(self.ward)

        super_ext_profile = SuperExtensionOfficerProfileFactory(user=super_ext)
        super_ext_profile.counties.add(self.county)

        work_request = EExtensionWorkRequest.objects.create(
            e_extension=e_ext,
            super_extension=super_ext,
            status=WorkRequestStatusChoices.PENDING
        )

        self.client.force_authenticate(user=super_ext)

        data = {'response_message': 'Welcome to the team!'}
        response = self.client.post(
            f'/api/v2/work-requests/e-extension/{work_request.id}/accept/',
            data
        )

        assert response.status_code == status.HTTP_200_OK
        work_request.refresh_from_db()
        assert work_request.status == WorkRequestStatusChoices.ACCEPTED
        assert work_request.response_message == 'Welcome to the team!'

        # Check relationship established
        e_ext_profile.refresh_from_db()
        assert super_ext_profile in e_ext_profile.super_extensions.all()

    def test_accept_work_request_only_recipient_can_accept(self):
        """Test only recipient can accept work request"""
        e_ext = EExtensionFactory()
        super_ext = SuperExtensionFactory()
        other_super_ext = SuperExtensionFactory()

        work_request = EExtensionWorkRequest.objects.create(
            e_extension=e_ext,
            super_extension=super_ext,
            status=WorkRequestStatusChoices.PENDING
        )

        self.client.force_authenticate(user=other_super_ext)

        response = self.client.post(
            f'/api/v2/work-requests/e-extension/{work_request.id}/accept/'
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_reject_work_request_success(self):
        """Test super extension can reject work request"""
        e_ext = EExtensionFactory()
        super_ext = SuperExtensionFactory()

        work_request = EExtensionWorkRequest.objects.create(
            e_extension=e_ext,
            super_extension=super_ext,
            status=WorkRequestStatusChoices.PENDING
        )

        self.client.force_authenticate(user=super_ext)

        data = {'response_message': 'Sorry, not at this time'}
        response = self.client.post(
            f'/api/v2/work-requests/e-extension/{work_request.id}/reject/',
            data
        )

        assert response.status_code == status.HTTP_200_OK
        work_request.refresh_from_db()
        assert work_request.status == WorkRequestStatusChoices.REJECTED
        assert work_request.response_message == 'Sorry, not at this time'

    def test_accept_already_processed_request_fails(self):
        """Test cannot accept already processed request"""
        e_ext = EExtensionFactory()
        super_ext = SuperExtensionFactory()

        work_request = EExtensionWorkRequest.objects.create(
            e_extension=e_ext,
            super_extension=super_ext,
            status=WorkRequestStatusChoices.ACCEPTED
        )

        self.client.force_authenticate(user=super_ext)

        response = self.client.post(
            f'/api/v2/work-requests/e-extension/{work_request.id}/accept/'
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'already been processed' in str(response.data)

    def test_system_admin_can_view_all_requests(self):
        """Test system admin can view all work requests"""
        admin = SystemAdminFactory()
        e_ext = EExtensionFactory()
        super_ext = SuperExtensionFactory()

        EExtensionWorkRequest.objects.create(
            e_extension=e_ext,
            super_extension=super_ext,
            status=WorkRequestStatusChoices.PENDING
        )

        self.client.force_authenticate(user=admin)

        response = self.client.get('/api/v2/work-requests/e-extension/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1

    def test_unrelated_user_cannot_view_request(self):
        """Test unrelated user cannot view other users' requests"""
        e_ext = EExtensionFactory()
        super_ext = SuperExtensionFactory()
        other_e_ext = EExtensionFactory()

        work_request = EExtensionWorkRequest.objects.create(
            e_extension=e_ext,
            super_extension=super_ext,
            status=WorkRequestStatusChoices.PENDING
        )

        self.client.force_authenticate(user=other_e_ext)

        response = self.client.get(
            f'/api/v2/work-requests/e-extension/{work_request.id}/'
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestFarmerWorkRequestViewSet:
    """Tests for Farmer work request viewset"""

    def setup_method(self):
        """Set up test data"""
        self.client = APIClient()

    def test_create_work_request_success(self):
        """Test farmer can create work request to e-extension"""
        farmer = FarmerFactory()
        e_ext = EExtensionFactory()

        FarmerProfileFactory(user=farmer)
        EExtensionOfficerProfileFactory(user=e_ext)

        self.client.force_authenticate(user=farmer)

        data = {
            'e_extension': e_ext.id,
            'message': 'I need help with my farm'
        }

        response = self.client.post('/api/v2/work-requests/farmer/', data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['farmer'] == farmer.id
        assert response.data['e_extension'] == e_ext.id
        assert response.data['status'] == WorkRequestStatusChoices.PENDING
        assert FarmerWorkRequest.objects.count() == 1

    def test_create_work_request_non_farmer_fails(self):
        """Test non-farmer user cannot create request"""
        e_ext = EExtensionFactory()
        another_e_ext = EExtensionFactory()

        self.client.force_authenticate(user=e_ext)

        data = {
            'e_extension': another_e_ext.id,
            'message': 'Test'
        }

        response = self.client.post('/api/v2/work-requests/farmer/', data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Only Farmers can send work requests' in str(response.data)

    def test_create_duplicate_pending_request_fails(self):
        """Test cannot create duplicate pending requests"""
        farmer = FarmerFactory()
        e_ext = EExtensionFactory()

        FarmerProfileFactory(user=farmer)
        EExtensionOfficerProfileFactory(user=e_ext)

        # Create existing pending request
        FarmerWorkRequest.objects.create(
            farmer=farmer,
            e_extension=e_ext,
            status=WorkRequestStatusChoices.PENDING
        )

        self.client.force_authenticate(user=farmer)

        data = {
            'e_extension': e_ext.id,
            'message': 'Another request'
        }

        response = self.client.post('/api/v2/work-requests/farmer/', data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'already have a pending request' in str(response.data)

    def test_list_work_requests_as_farmer(self):
        """Test farmer can list their sent requests"""
        farmer = FarmerFactory()
        e_ext1 = EExtensionFactory()
        e_ext2 = EExtensionFactory()

        FarmerProfileFactory(user=farmer)

        # Create multiple requests
        FarmerWorkRequest.objects.create(
            farmer=farmer,
            e_extension=e_ext1,
            status=WorkRequestStatusChoices.PENDING
        )
        FarmerWorkRequest.objects.create(
            farmer=farmer,
            e_extension=e_ext2,
            status=WorkRequestStatusChoices.ACCEPTED
        )

        self.client.force_authenticate(user=farmer)

        response = self.client.get('/api/v2/work-requests/farmer/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2

    def test_list_work_requests_as_e_extension(self):
        """Test e-extension can list received requests"""
        e_ext = EExtensionFactory()
        farmer1 = FarmerFactory()
        farmer2 = FarmerFactory()

        EExtensionOfficerProfileFactory(user=e_ext)

        # Create multiple requests to this e-extension
        FarmerWorkRequest.objects.create(
            farmer=farmer1,
            e_extension=e_ext,
            status=WorkRequestStatusChoices.PENDING
        )
        FarmerWorkRequest.objects.create(
            farmer=farmer2,
            e_extension=e_ext,
            status=WorkRequestStatusChoices.PENDING
        )

        self.client.force_authenticate(user=e_ext)

        response = self.client.get('/api/v2/work-requests/farmer/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2

    def test_accept_work_request_success(self):
        """Test e-extension can accept work request"""
        farmer = FarmerFactory()
        e_ext = EExtensionFactory()

        farmer_profile = FarmerProfileFactory(user=farmer)
        e_ext_profile = EExtensionOfficerProfileFactory(user=e_ext)

        work_request = FarmerWorkRequest.objects.create(
            farmer=farmer,
            e_extension=e_ext,
            status=WorkRequestStatusChoices.PENDING
        )

        self.client.force_authenticate(user=e_ext)

        data = {'response_message': 'Happy to help!'}
        response = self.client.post(
            f'/api/v2/work-requests/farmer/{work_request.id}/accept/',
            data
        )

        assert response.status_code == status.HTTP_200_OK
        work_request.refresh_from_db()
        assert work_request.status == WorkRequestStatusChoices.ACCEPTED
        assert work_request.response_message == 'Happy to help!'

        # Check relationship established
        farmer_profile.refresh_from_db()
        assert e_ext_profile in farmer_profile.e_extensions.all()

    def test_accept_work_request_only_recipient_can_accept(self):
        """Test only recipient can accept work request"""
        farmer = FarmerFactory()
        e_ext = EExtensionFactory()
        other_e_ext = EExtensionFactory()

        work_request = FarmerWorkRequest.objects.create(
            farmer=farmer,
            e_extension=e_ext,
            status=WorkRequestStatusChoices.PENDING
        )

        self.client.force_authenticate(user=other_e_ext)

        response = self.client.post(
            f'/api/v2/work-requests/farmer/{work_request.id}/accept/'
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_reject_work_request_success(self):
        """Test e-extension can reject work request"""
        farmer = FarmerFactory()
        e_ext = EExtensionFactory()

        work_request = FarmerWorkRequest.objects.create(
            farmer=farmer,
            e_extension=e_ext,
            status=WorkRequestStatusChoices.PENDING
        )

        self.client.force_authenticate(user=e_ext)

        data = {'response_message': 'Currently at capacity'}
        response = self.client.post(
            f'/api/v2/work-requests/farmer/{work_request.id}/reject/',
            data
        )

        assert response.status_code == status.HTTP_200_OK
        work_request.refresh_from_db()
        assert work_request.status == WorkRequestStatusChoices.REJECTED
        assert work_request.response_message == 'Currently at capacity'

    def test_accept_already_processed_request_fails(self):
        """Test cannot accept already processed request"""
        farmer = FarmerFactory()
        e_ext = EExtensionFactory()

        work_request = FarmerWorkRequest.objects.create(
            farmer=farmer,
            e_extension=e_ext,
            status=WorkRequestStatusChoices.REJECTED
        )

        self.client.force_authenticate(user=e_ext)

        response = self.client.post(
            f'/api/v2/work-requests/farmer/{work_request.id}/accept/'
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'already been processed' in str(response.data)

    def test_system_admin_can_view_all_requests(self):
        """Test system admin can view all work requests"""
        admin = SystemAdminFactory()
        farmer = FarmerFactory()
        e_ext = EExtensionFactory()

        FarmerWorkRequest.objects.create(
            farmer=farmer,
            e_extension=e_ext,
            status=WorkRequestStatusChoices.PENDING
        )

        self.client.force_authenticate(user=admin)

        response = self.client.get('/api/v2/work-requests/farmer/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1

    def test_filter_by_status(self):
        """Test filtering work requests by status"""
        farmer = FarmerFactory()
        e_ext = EExtensionFactory()

        FarmerProfileFactory(user=farmer)

        FarmerWorkRequest.objects.create(
            farmer=farmer,
            e_extension=e_ext,
            status=WorkRequestStatusChoices.PENDING
        )
        FarmerWorkRequest.objects.create(
            farmer=farmer,
            e_extension=e_ext,
            status=WorkRequestStatusChoices.ACCEPTED
        )

        self.client.force_authenticate(user=farmer)

        response = self.client.get(
            '/api/v2/work-requests/farmer/',
            {'status': WorkRequestStatusChoices.PENDING}
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
