from datetime import timedelta

import pytest
from django.utils import timezone
from users.factory.otp import OtpFactory
from users.factory.user import UserFactory


@pytest.mark.django_db
def test_otp_creation_and_str():
    user = UserFactory(first_name="Alice", last_name="Smith")
    otp = OtpFactory(user=user, token="123456")

    assert otp.user == user
    assert otp.token == "123456"
    assert str(otp) == f"{user.full_name} - 123456"


@pytest.mark.django_db
def test_is_valid_property_true():
    otp = OtpFactory(expiry_at=timezone.now() + timedelta(minutes=5))
    assert otp.is_valid is True


@pytest.mark.django_db
def test_is_valid_property_false():
    otp = OtpFactory(expiry_at=timezone.now() - timedelta(minutes=1))
    assert otp.is_valid is False


@pytest.mark.django_db
def test_multiple_otps_for_same_user():
    user = UserFactory()
    otp1 = OtpFactory(user=user)
    otp2 = OtpFactory(user=user)

    assert otp1.user == otp2.user
    assert otp1.token != otp2.token  # unique sequence tokens
    assert user.otp_set.count() == 2  # reverse relation works
