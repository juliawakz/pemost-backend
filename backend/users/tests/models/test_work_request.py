import pytest
from django.utils import timezone
from users.choices import WorkRequestStatusChoices
from users.factory import (
    EExtensionFactory,
    EExtensionOfficerProfileFactory,
    EExtensionWorkRequestFactory,
    FarmerFactory,
    FarmerProfileFactory,
    FarmerWorkRequestFactory,
    SuperExtensionFactory,
    SuperExtensionOfficerProfileFactory,
)
from users.models import EExtensionWorkRequest, FarmerWorkRequest


@pytest.mark.django_db
class TestEExtensionWorkRequest:
    """Tests for E-Extension to Super Extension work requests"""

    def test_create_work_request(self):
        """Test creating a work request"""
        e_ext = EExtensionFactory()
        super_ext = SuperExtensionFactory()

        work_request = EExtensionWorkRequestFactory(
            e_extension=e_ext,
            super_extension=super_ext,
            message="I would like to work with you"
        )

        assert work_request.status == WorkRequestStatusChoices.PENDING
        assert work_request.notification_sent is False
        assert work_request.responded_at is None
        assert str(work_request) == f"{e_ext.full_name} → {super_ext.full_name} (PENDING)"

    def test_accept_work_request(self):
        """Test accepting a work request establishes relationship"""
        e_ext = EExtensionFactory()
        super_ext = SuperExtensionFactory()

        # Create profiles
        e_ext_profile = EExtensionOfficerProfileFactory(user=e_ext)
        super_ext_profile = SuperExtensionOfficerProfileFactory(user=super_ext)

        work_request = EExtensionWorkRequestFactory(
            e_extension=e_ext,
            super_extension=super_ext
        )

        # Accept the request
        work_request.accept(response_message="Welcome to the team!")

        # Refresh from DB
        work_request.refresh_from_db()
        e_ext_profile.refresh_from_db()

        assert work_request.status == WorkRequestStatusChoices.ACCEPTED
        assert work_request.response_message == "Welcome to the team!"
        assert work_request.responded_at is not None
        assert e_ext_profile.is_visible is True
        assert super_ext_profile in e_ext_profile.super_extensions.all()

    def test_reject_work_request(self):
        """Test rejecting a work request"""
        e_ext = EExtensionFactory()
        super_ext = SuperExtensionFactory()

        # Create profiles
        e_ext_profile = EExtensionOfficerProfileFactory(user=e_ext)
        super_ext_profile = SuperExtensionOfficerProfileFactory(user=super_ext)

        work_request = EExtensionWorkRequestFactory(
            e_extension=e_ext,
            super_extension=super_ext
        )

        # Reject the request
        work_request.reject(response_message="Sorry, I'm at capacity")

        # Refresh from DB
        work_request.refresh_from_db()
        e_ext_profile.refresh_from_db()

        assert work_request.status == WorkRequestStatusChoices.REJECTED
        assert work_request.response_message == "Sorry, I'm at capacity"
        assert work_request.responded_at is not None
        # Relationship should NOT be established
        assert super_ext_profile not in e_ext_profile.super_extensions.all()


@pytest.mark.django_db
class TestFarmerWorkRequest:
    """Tests for Farmer to E-Extension work requests"""

    def test_create_work_request(self):
        """Test creating a work request"""
        farmer = FarmerFactory()
        e_ext = EExtensionFactory()

        work_request = FarmerWorkRequestFactory(
            farmer=farmer,
            e_extension=e_ext,
            message="I need help with my farm"
        )

        assert work_request.status == WorkRequestStatusChoices.PENDING
        assert work_request.notification_sent is False
        assert work_request.responded_at is None
        assert str(work_request) == f"{farmer.full_name} → {e_ext.full_name} (PENDING)"

    def test_accept_work_request(self):
        """Test accepting a work request establishes relationship"""
        farmer = FarmerFactory()
        e_ext = EExtensionFactory()

        # Create profiles
        farmer_profile = FarmerProfileFactory(user=farmer)
        e_ext_profile = EExtensionOfficerProfileFactory(user=e_ext)

        work_request = FarmerWorkRequestFactory(
            farmer=farmer,
            e_extension=e_ext
        )

        # Accept the request
        work_request.accept(response_message="Happy to help!")

        # Refresh from DB
        work_request.refresh_from_db()
        farmer_profile.refresh_from_db()

        assert work_request.status == WorkRequestStatusChoices.ACCEPTED
        assert work_request.response_message == "Happy to help!"
        assert work_request.responded_at is not None
        assert farmer_profile.is_visible is True
        assert e_ext_profile in farmer_profile.e_extensions.all()

    def test_reject_work_request(self):
        """Test rejecting a work request"""
        farmer = FarmerFactory()
        e_ext = EExtensionFactory()

        # Create profiles
        farmer_profile = FarmerProfileFactory(user=farmer)
        e_ext_profile = EExtensionOfficerProfileFactory(user=e_ext)

        work_request = FarmerWorkRequestFactory(
            farmer=farmer,
            e_extension=e_ext
        )

        # Reject the request
        work_request.reject(response_message="Outside my coverage area")

        # Refresh from DB
        work_request.refresh_from_db()
        farmer_profile.refresh_from_db()

        assert work_request.status == WorkRequestStatusChoices.REJECTED
        assert work_request.response_message == "Outside my coverage area"
        assert work_request.responded_at is not None
        # Relationship should NOT be established
        assert e_ext_profile not in farmer_profile.e_extensions.all()
