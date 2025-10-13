import pytest
from locations.factory import CountyFactory, SubCountyFactory, WardFactory
from rest_framework.test import APIRequestFactory
from users.choices import WorkRequestStatusChoices
from users.factory import (
    EExtensionFactory,
    EExtensionOfficerProfileFactory,
    FarmerFactory,
    FarmerProfileFactory,
    SuperExtensionFactory,
    SuperExtensionOfficerProfileFactory,
)
from users.models import EExtensionWorkRequest, FarmerWorkRequest
from users.serializers.work_request import (
    AcceptRejectRequestSerializer,
    EExtensionWorkRequestSerializer,
    FarmerWorkRequestSerializer,
)


@pytest.mark.django_db
class TestEExtensionWorkRequestSerializer:
    """Tests for E-Extension work request serializer"""

    def setup_method(self):
        """Set up test data"""
        self.factory = APIRequestFactory()

        # Create location hierarchy
        self.county = CountyFactory()
        self.subcounty = SubCountyFactory(county=self.county)
        self.ward = WardFactory(subcounty=self.subcounty)

    def test_create_valid_work_request(self):
        """Test creating a valid work request"""
        e_ext = EExtensionFactory()
        super_ext = SuperExtensionFactory()

        # Create profiles with proper location setup
        e_ext_profile = EExtensionOfficerProfileFactory(user=e_ext)
        e_ext_profile.wards.add(self.ward)

        super_ext_profile = SuperExtensionOfficerProfileFactory(user=super_ext)
        super_ext_profile.counties.add(self.county)

        data = {
            'super_extension': super_ext.id,
            'message': 'I would like to work with you'
        }

        request = self.factory.post('/fake-url/')
        request.user = e_ext

        serializer = EExtensionWorkRequestSerializer(
            data=data,
            context={'request': request}
        )

        assert serializer.is_valid(), serializer.errors
        work_request = serializer.save()

        assert work_request.e_extension == e_ext
        assert work_request.super_extension == super_ext
        assert work_request.status == WorkRequestStatusChoices.PENDING

    def test_non_e_extension_cannot_create_request(self):
        """Test that non e-extension user cannot create request"""
        farmer = FarmerFactory()
        super_ext = SuperExtensionFactory()

        data = {
            'super_extension': super_ext.id,
            'message': 'Test'
        }

        request = self.factory.post('/fake-url/')
        request.user = farmer

        serializer = EExtensionWorkRequestSerializer(
            data=data,
            context={'request': request}
        )

        assert not serializer.is_valid()
        assert 'Only E-Extension officers can send work requests' in str(serializer.errors)

    def test_cannot_send_request_outside_county(self):
        """Test that e-extension cannot send request to super extension in different county"""
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

        data = {
            'super_extension': super_ext.id,
            'message': 'Test'
        }

        request = self.factory.post('/fake-url/')
        request.user = e_ext

        serializer = EExtensionWorkRequestSerializer(
            data=data,
            context={'request': request}
        )

        assert not serializer.is_valid()
        assert 'can only send work requests to Super Extension officers in your county' in str(serializer.errors)

    def test_cannot_create_duplicate_pending_request(self):
        """Test that duplicate pending requests are not allowed"""
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

        data = {
            'super_extension': super_ext.id,
            'message': 'Another request'
        }

        request = self.factory.post('/fake-url/')
        request.user = e_ext

        serializer = EExtensionWorkRequestSerializer(
            data=data,
            context={'request': request}
        )

        assert not serializer.is_valid()
        assert 'already have a pending request' in str(serializer.errors)


@pytest.mark.django_db
class TestFarmerWorkRequestSerializer:
    """Tests for Farmer work request serializer"""

    def setup_method(self):
        """Set up test data"""
        self.factory = APIRequestFactory()

    def test_create_valid_work_request(self):
        """Test creating a valid work request"""
        farmer = FarmerFactory()
        e_ext = EExtensionFactory()

        # Create profiles
        FarmerProfileFactory(user=farmer)
        EExtensionOfficerProfileFactory(user=e_ext)

        data = {
            'e_extension': e_ext.id,
            'message': 'I need help with my farm'
        }

        request = self.factory.post('/fake-url/')
        request.user = farmer

        serializer = FarmerWorkRequestSerializer(
            data=data,
            context={'request': request}
        )

        assert serializer.is_valid(), serializer.errors
        work_request = serializer.save()

        assert work_request.farmer == farmer
        assert work_request.e_extension == e_ext
        assert work_request.status == WorkRequestStatusChoices.PENDING

    def test_non_farmer_cannot_create_request(self):
        """Test that non-farmer user cannot create request"""
        e_ext = EExtensionFactory()
        another_e_ext = EExtensionFactory()

        data = {
            'e_extension': another_e_ext.id,
            'message': 'Test'
        }

        request = self.factory.post('/fake-url/')
        request.user = e_ext

        serializer = FarmerWorkRequestSerializer(
            data=data,
            context={'request': request}
        )

        assert not serializer.is_valid()
        assert 'Only Farmers can send work requests' in str(serializer.errors)

    def test_cannot_create_duplicate_pending_request(self):
        """Test that duplicate pending requests are not allowed"""
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

        data = {
            'e_extension': e_ext.id,
            'message': 'Another request'
        }

        request = self.factory.post('/fake-url/')
        request.user = farmer

        serializer = FarmerWorkRequestSerializer(
            data=data,
            context={'request': request}
        )

        assert not serializer.is_valid()
        assert 'already have a pending request' in str(serializer.errors)


@pytest.mark.django_db
class TestAcceptRejectRequestSerializer:
    """Tests for AcceptRejectRequestSerializer"""

    def test_valid_with_message(self):
        """Test serializer is valid with response message"""
        data = {
            'response_message': 'Welcome to the team!'
        }

        serializer = AcceptRejectRequestSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data['response_message'] == 'Welcome to the team!'

    def test_valid_without_message(self):
        """Test serializer is valid without response message"""
        data = {}

        serializer = AcceptRejectRequestSerializer(data=data)
        assert serializer.is_valid()
        assert 'response_message' not in serializer.validated_data

    def test_message_max_length(self):
        """Test that message respects max length"""
        data = {
            'response_message': 'x' * 501  # Over 500 char limit
        }

        serializer = AcceptRejectRequestSerializer(data=data)
        assert not serializer.is_valid()
        assert 'response_message' in serializer.errors
