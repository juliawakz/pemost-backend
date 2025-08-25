import pytest
from django.contrib.auth import get_user_model
from users.choices import UserTypeChoices
from users.factory.user import SystemAdminFactory, UserFactory

User = get_user_model()


@pytest.mark.django_db
def test_user_creation():
    user_data = {
        "first_name": "John",
        "last_name": "Doe",
        "phone_number": "+123456789",
        "email": "john.doe@example.com",
        "is_verified": True,
        "is_staff": False,
        "type": UserTypeChoices.FARMER,
    }

    user = User.objects.create(**user_data)

    assert user.first_name == "John"
    assert user.last_name == "Doe"
    assert user.phone_number == "+123456789"
    assert user.email == "john.doe@example.com"
    assert user.is_verified is True
    assert user.is_staff is False
    assert user.type is UserTypeChoices.FARMER


@pytest.mark.django_db
def test_full_name_property():
    user_data = {
        "first_name": "Jane",
        "last_name": "Doe",
        "phone_number": "+987654321",
        "email": "jane.doe@example.com",
        "is_verified": False,
        "is_staff": True,
        "type": UserTypeChoices.SYSTEM_ADMIN,
    }

    user = User.objects.create(**user_data)
    assert user.full_name == "Jane Doe"
    assert str(user) == "Jane Doe"


@pytest.mark.django_db
def test_normal_user_factory():
    user = UserFactory.create()
    assert user.type == UserTypeChoices.FARMER


@pytest.mark.django_db
def test_system_admin_factory():
    user = SystemAdminFactory.create()
    assert user.type == UserTypeChoices.SYSTEM_ADMIN
