import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from users.factory.user import UserFactory
from users.models.otp import Otp

User = get_user_model()


@pytest.mark.django_db
def test_create_otp():
    user = UserFactory.create()
    otp = Otp.objects.create(token="123456", user=user)

    assert otp.token == "123456"
    assert otp.user == user
    assert timezone.now() < otp.expiry_at


@pytest.mark.django_db
def test_otp_str_method():
    user = UserFactory.create()
    otp = Otp.objects.create(token="654321", user=user)

    assert str(otp) == "654321"
