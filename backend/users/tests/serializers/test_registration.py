import pytest
from django.contrib.auth import get_user_model
from notifications.tasks import send_email_task
from rest_framework.serializers import ValidationError
from users.choices import UserTypeChoices
from users.exceptions import PasswordMismatchException
from users.factory.user import UserFactory
from users.serializers.registration import RegistrationSerializer

User = get_user_model()


@pytest.mark.django_db
def test_registration_serializer_valid_data(mocker):
    mocker.patch("notifications.tasks.send_email_task.delay")
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "phone_number": "+254705571573",
        "email": "john.doe@example.com",
        "password1": "password123",
        "password2": "password123",
    }

    serializer = RegistrationSerializer(data=data)
    assert serializer.is_valid()
    user = serializer.save()
    assert User.objects.filter(email=data["email"]).exists()
    assert user.email == data["email"]
    assert user.first_name == data["first_name"]
    assert user.last_name == data["last_name"]
    assert user.phone_number == "+254705571573"
    assert user.is_verified is False
    assert user.is_staff is False
    assert user.type is UserTypeChoices.FARMER
    assert send_email_task.delay.called


@pytest.mark.django_db
def test_registration_serializer_only_kenyan_numbers():
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "phone_number": "+232705571573",
        "email": "john.doe@example.com",
        "password1": "password123",
        "password2": "password123",
    }

    serializer = RegistrationSerializer(data=data)
    with pytest.raises(ValidationError):
        serializer.is_valid(raise_exception=True)

    assert len(serializer.errors.keys()) == 1
    assert "phone_number" in serializer.errors.keys()


@pytest.mark.django_db
def test_registration_serializer_invalid_passwords():
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "phone_number": "+254705571573",
        "email": "john.doe@example.com",
        "password1": "password123",
        "password2": "differentpassword",
    }
    serializer = RegistrationSerializer(data=data)
    with pytest.raises(PasswordMismatchException):
        serializer.is_valid(raise_exception=True)


@pytest.mark.django_db
def test_registration_serializer_existing_email():
    user = UserFactory.create()
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "phone_number": "+254705571573",
        "email": user.email,
        "password1": "password123",
        "password2": "password123",
    }

    serializer = RegistrationSerializer(data=data)
    with pytest.raises(
        ValidationError, match="A user is already registered with this email."
    ):
        serializer.is_valid(raise_exception=True)


@pytest.mark.django_db
def test_registration_serializer_existing_phone_number():
    user_data = {
        "first_name": "John",
        "last_name": "Doe",
        "phone_number": "+254705571573",
        "email": "john.doe@example.com",
    }
    user = User.objects.create(**user_data)
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "phone_number": user.phone_number,
        "email": "john.doe@example.com",
        "password1": "password123",
        "password2": "password123",
    }

    serializer = RegistrationSerializer(data=data)
    with pytest.raises(
        ValidationError, match="A user is already registered with this phone number."
    ):
        serializer.is_valid(raise_exception=True)
