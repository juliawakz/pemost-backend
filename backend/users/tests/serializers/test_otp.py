import pytest
from django.contrib.auth import get_user_model
from users.exceptions import AccountNotRegisteredException, InvalidEmailException
from users.factory.user import UserFactory
from users.models import Otp
from users.serializers.otp import OtpVerifySerializer, OtpWriteSerializer

User = get_user_model()


@pytest.mark.django_db
def test_otp_write_serializer_valid_data():
    user = UserFactory.create()
    data = {"email": user.email}
    serializer = OtpWriteSerializer(data=data)
    assert serializer.is_valid()
    assert serializer.validated_data["email"] == user.email


@pytest.mark.django_db
def test_otp_write_serializer_nonexistent_user():
    data = {"email": "nonexistent@example.com"}
    serializer = OtpWriteSerializer(data=data)
    with pytest.raises(AccountNotRegisteredException):
        serializer.is_valid(raise_exception=True)


@pytest.mark.django_db
def test_otp_verify_serializer_valid_data():
    user = UserFactory.create()
    otp = Otp.objects.create(user=user, token="123456")
    data = {"email": user.email, "token": otp.token}
    serializer = OtpVerifySerializer(data=data)
    assert serializer.is_valid()


@pytest.mark.django_db
def test_otp_verify_serializer_nonexistent_user():
    data = {"email": "nonexistent@example.com", "token": "123456"}
    serializer = OtpVerifySerializer(data=data)
    with pytest.raises(InvalidEmailException):
        serializer.is_valid(raise_exception=True)
