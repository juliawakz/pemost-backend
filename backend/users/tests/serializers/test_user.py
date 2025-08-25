import uuid

import pytest
from django.contrib.auth import get_user_model
from users.choices import UserTypeChoices
from users.exceptions import AccountNotRegisteredException
from users.factory.user import UserFactory
from users.serializers.user import (
    UserReadSerializer,
    UserWriteSerializer,
)
from users.serializers.profile import (
    ProfileExistsSerializer,
    ProfileSerializer,
)

User = get_user_model()


@pytest.mark.django_db
def test_user_write_serializer():
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone_number": "+254701234567",
        "type": UserTypeChoices.FARMER,
        "is_verified": True,
        "is_archived": False,
    }

    serializer = UserWriteSerializer(data=data)
    assert serializer.is_valid()
    user_instance = serializer.save()
    assert user_instance.first_name == "John"
    assert user_instance.last_name == "Doe"
    assert user_instance.email == "john.doe@example.com"
    assert user_instance.phone_number == "+254701234567"
    assert user_instance.is_verified is True
    assert user_instance.is_archived is False


@pytest.mark.django_db
def test_user_read_serializer():
    user = User.objects.create(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone_number="+254701234567",
        type=UserTypeChoices.FARMER,
        is_verified=True,
        is_archived=False,
    )

    serializer = UserReadSerializer(instance=user)
    assert len(serializer.data.keys()) == 13
    assert uuid.UUID(serializer.data["id"]) == user.id
    assert serializer.data["first_name"] == "John"
    assert serializer.data["last_name"] == "Doe"
    assert serializer.data["email"] == "john.doe@example.com"
    assert serializer.data["phone_number"] == "+254701234567"
    assert serializer.data["type"] == UserTypeChoices.FARMER
    assert serializer.data["is_verified"] is True
    assert serializer.data["is_archived"] is False
    assert serializer.data["full_name"] == "John Doe"
    assert "date_joined" in serializer.data.keys()
    assert "last_login" in serializer.data.keys()
    assert "created_at" in serializer.data.keys()
    assert "updated_at" in serializer.data.keys()


@pytest.mark.django_db
def test_profile_serializer():
    user = User.objects.create(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone_number="1234567890",
        type="user",
    )

    serializer = ProfileSerializer(instance=user)
    assert len(serializer.data.keys()) == 8
    assert uuid.UUID(serializer.data["id"]) == user.id
    assert serializer.data["first_name"] == "John"
    assert serializer.data["last_name"] == "Doe"
    assert serializer.data["email"] == "john.doe@example.com"
    assert serializer.data["phone_number"] == "1234567890"
    assert serializer.data["full_name"] == "John Doe"


@pytest.mark.django_db
def test_profile_exists_serializer_valid():
    user = UserFactory.create()
    data = {"email": user.email}
    serializer = ProfileExistsSerializer(data=data)
    assert serializer.is_valid()


@pytest.mark.django_db
def test_profile_exists_serializer_invalid():
    data = {"email": "nonexistent@example.com"}
    serializer = ProfileExistsSerializer(data=data)
    with pytest.raises(AccountNotRegisteredException):
        serializer.is_valid()
