import pytest
from django.contrib.auth import get_user_model
from users.exceptions import (
    AccountNotRegisteredException,
    InvalidCurrentPasswordException,
    PasswordMismatchException,
)
from users.factory.user import UserFactory
from users.serializers.password import (
    PasswordChangeSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetSerializer,
)

User = get_user_model()


@pytest.mark.django_db
def test_password_reset_serializer_valid_email():
    user = UserFactory.create()
    data = {"email": user.email}
    serializer = PasswordResetSerializer(data=data)
    assert serializer.is_valid()
    assert serializer.validated_data["email"] == data["email"]


@pytest.mark.django_db
def test_password_reset_serializer_invalid_email():
    data = {"email": "nonexistent@example.com"}
    serializer = PasswordResetSerializer(data=data)
    with pytest.raises(AccountNotRegisteredException):
        serializer.is_valid(raise_exception=True)


@pytest.mark.django_db
def test_password_reset_confirm_serializer_valid_data():
    user = UserFactory.create()
    data = {
        "email": user.email,
        "token": "123456",
        "password1": "newpassword",
        "password2": "newpassword",
    }

    serializer = PasswordResetConfirmSerializer(data=data)
    assert serializer.is_valid()
    assert serializer.validated_data["email"] == data["email"]
    assert serializer.validated_data["token"] == data["token"]
    assert serializer.validated_data["password1"] == data["password1"]
    assert serializer.validated_data["password2"] == data["password2"]


@pytest.mark.django_db
def test_password_reset_confirm_serializer_invalid_email():
    data = {
        "email": "nonexistent@example.com",
        "token": "123456",
        "password1": "newpassword",
        "password2": "newpassword",
    }

    serializer = PasswordResetConfirmSerializer(data=data)
    with pytest.raises(AccountNotRegisteredException):
        serializer.is_valid(raise_exception=True)


@pytest.mark.django_db
def test_password_reset_confirm_serializer_invalid_passwords():
    user = UserFactory.create()
    data = {
        "email": user.email,
        "token": "123456",
        "password1": "newpassword",
        "password2": "differentpassword",
    }

    serializer = PasswordResetConfirmSerializer(data=data)
    with pytest.raises(PasswordMismatchException):
        serializer.is_valid(raise_exception=True)


@pytest.mark.django_db
def test_password_change_serializer_valid_data():
    user = UserFactory.create()
    request = type("MockRequest", (), {"user": user})

    data = {
        "password": "admin",
        "password1": "newpassword",
        "password2": "newpassword",
    }

    serializer = PasswordChangeSerializer(data=data, context={"request": request})
    assert serializer.is_valid()
    assert serializer.validated_data["password"] == data["password"]
    assert serializer.validated_data["password1"] == data["password1"]
    assert serializer.validated_data["password2"] == data["password2"]
    assert serializer.validated_data["email"] == user.email


@pytest.mark.django_db
def test_password_change_serializer_invalid_current_password():
    user = UserFactory.create()
    request = type("MockRequest", (), {"user": user})

    data = {
        "password": "wrongpassword",
        "password1": "newpassword",
        "password2": "newpassword",
    }

    serializer = PasswordChangeSerializer(data=data, context={"request": request})
    with pytest.raises(InvalidCurrentPasswordException):
        serializer.is_valid(raise_exception=True)


@pytest.mark.django_db
def test_password_change_serializer_invalid_passwords():
    user = UserFactory.create()
    request = type("MockRequest", (), {"user": user})

    data = {
        "password": "admin",
        "password1": "newpassword",
        "password2": "differentpassword",
    }

    serializer = PasswordChangeSerializer(data=data, context={"request": request})
    with pytest.raises(PasswordMismatchException):
        serializer.is_valid(raise_exception=True)
