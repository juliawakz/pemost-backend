import pytest
from django.contrib.auth import get_user_model
from locations.factory.ward import WardFactory
from rest_framework import status
from rest_framework.test import APIClient
from users.choices import RoleChoices
from users.factory.user import SystemAdminFactory, UserFactory
from users.serializers.user import UserSerializer

User = get_user_model()


@pytest.mark.django_db
def test_get_all_users_cannot_be_accessed_by_normal_user():
    user = UserFactory.create()

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get("/api/v2/users/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1


@pytest.mark.django_db
def test_retrieve_user():
    user = UserFactory.create()
    admin = SystemAdminFactory.create()

    client = APIClient()
    client.force_authenticate(user=admin)

    response = client.get(f"/api/v2/users/{user.id}/")

    assert response.status_code == status.HTTP_200_OK
    serialized_user = UserSerializer(instance=user).data
    assert response.data == serialized_user


@pytest.mark.django_db
def test_get_all_users():
    UserFactory.create_batch(15)
    admin = SystemAdminFactory.create()

    client = APIClient()
    client.force_authenticate(user=admin)

    response = client.get("/api/v2/users/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    count = data["count"]
    assert count == User.objects.count()


@pytest.mark.django_db
def test_update_user():
    ward = WardFactory()
    user = UserFactory.create()
    user.wards.add(ward)
    updated_data = {
        "first_name": "Lala",
        "last_name": "hehe",
        "phone_number": "0722567890",
        "email": "haha.lele@example.com",
        "is_archived": True,
        "role": RoleChoices.AGRODEALER,
    }

    admin = SystemAdminFactory.create()

    client = APIClient()
    client.force_authenticate(user=admin)

    response = client.patch(
        f"/api/v2/users/{user.id}/", data=updated_data, format="json"
    )
    assert response.status_code == status.HTTP_200_OK
    user.refresh_from_db()
    assert user.first_name == "Lala"
    assert user.last_name == "hehe"
    assert user.phone_number == "0722567890"
    assert user.email == "haha.lele@example.com"
    assert user.is_staff is False
    assert user.role == RoleChoices.AGRODEALER


@pytest.mark.django_db
def test_filter_by_first_name():
    UserFactory.create_batch(15)
    user = UserFactory.create()
    admin = SystemAdminFactory.create()
    client = APIClient()
    client.force_authenticate(user=admin)
    response = client.get(
        "/api/v2/users/",
        {
            "first_name": user.first_name,
            "last_name": user.last_name
        })
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["count"] == 1


@pytest.mark.django_db
def test_filter_by_first_name_doesnt_exist():
    UserFactory.create_batch(15)
    admin = SystemAdminFactory.create()
    client = APIClient()
    client.force_authenticate(user=admin)
    response = client.get("/api/v2/users/", {"first_name": "123456789"})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["count"] == 0


@pytest.mark.django_db
def test_filter_by_last_name():
    UserFactory.create_batch(15)
    user = UserFactory.create()
    admin = SystemAdminFactory.create()
    client = APIClient()
    client.force_authenticate(user=admin)
    response = client.get(
        "/api/v2/users/",
        {"last_name": user.last_name, "first_name": user.first_name})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["count"] == 1


@pytest.mark.django_db
def test_filter_by_last_name_doesnt_exist():
    UserFactory.create_batch(15)
    admin = SystemAdminFactory.create()
    client = APIClient()
    client.force_authenticate(user=admin)
    response = client.get("/api/v2/users/", {"last_name": "123456789"})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["count"] == 0


@pytest.mark.django_db
def test_filter_by_email():
    UserFactory.create_batch(15)
    user = UserFactory.create()
    admin = SystemAdminFactory.create()
    client = APIClient()
    client.force_authenticate(user=admin)
    response = client.get("/api/v2/users/", {"email": user.email})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["count"] == 1


@pytest.mark.django_db
def test_filter_by_email_doesnt_exist():
    UserFactory.create_batch(15)
    admin = SystemAdminFactory.create()
    client = APIClient()
    client.force_authenticate(user=admin)
    response = client.get("/api/v2/users/", {"email": "bhjubhu@cgvgtt.gbjugu"})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["count"] == 0
