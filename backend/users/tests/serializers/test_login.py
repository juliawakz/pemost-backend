import pytest
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from users.exceptions import (
    AccountDisabledException,
    AccountNotRegisteredException,
    InvalidCredentialsException,
)
from users.factory.user import UserFactory
from users.serializers.login import LoginSerializer, LogoutSerializer

User = get_user_model()


@pytest.mark.django_db
def test_login_valid_user():
    user = UserFactory.create()
    data = {
        "email": str(user.email),
        "password": "admin",
    }

    serializer = LoginSerializer(data=data)
    serializer.is_valid(raise_exception=True)

    user_login_data = serializer.validated_data
    assert "token" in user_login_data
    assert "user" in user_login_data
    assert "access" in user_login_data["token"]
    assert "refresh" in user_login_data["token"]
    assert "access_expiry_time" in user_login_data["token"]
    assert "refresh_expiry_time" in user_login_data["token"]


@pytest.mark.django_db
def test_login_invalid_accounts():
    data = {
        "email": "noaccount@eexample.com",
        "password": "wrongpassword",
    }
    serializer = LoginSerializer(data=data)
    with pytest.raises(AccountNotRegisteredException):
        serializer.is_valid(raise_exception=True)


@pytest.mark.django_db
def test_login_is_archived_accounts():
    user_data = {
        "first_name": "John",
        "last_name": "Doe",
        "phone_number": "+123456789",
        "email": "john.doe@example.com",
        "is_archived": True,
    }

    user = User.objects.create(**user_data)

    data = {
        "email": user.email,
        "password": "pass",
    }
    serializer = LoginSerializer(data=data)
    with pytest.raises(AccountDisabledException):
        serializer.is_valid(raise_exception=True)


@pytest.mark.django_db
def test_login_invalid_credentials():
    user = UserFactory.create()
    data = {
        "email": user.email,
        "password": "wrongpassword",
    }

    serializer = LoginSerializer(data=data)
    with pytest.raises(InvalidCredentialsException):
        serializer.is_valid(raise_exception=True)


def test_logout_serializer_valid_data():
    data = {"refresh": "valid_refresh_token"}
    serializer = LogoutSerializer(data=data)
    assert serializer.is_valid()
    assert serializer.validated_data == {"refresh": "valid_refresh_token"}


def test_logout_serializer_missing_refresh_token():
    data = {"refresh": ""}
    serializer = LogoutSerializer(data=data)
    with pytest.raises(ValidationError) as exc_info:
        serializer.is_valid(raise_exception=True)

    assert "refresh" in exc_info.value.detail
