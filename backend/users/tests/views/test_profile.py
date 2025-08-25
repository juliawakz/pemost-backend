import uuid

import pytest
from rest_framework import status
from rest_framework.test import APIClient
from users.factory.user import UserFactory


@pytest.mark.django_db
def test_profile_view_success():
    client = APIClient()
    user = UserFactory.create()
    client.force_authenticate(user)
    response = client.get("/api/v2/users/profile/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 8
    assert uuid.UUID(response.data["id"]) == user.id
    assert response.data["first_name"] == user.first_name
    assert response.data["last_name"] == user.last_name
    assert response.data["email"] == user.email
    assert response.data["phone_number"] == user.phone_number
    assert response.data["full_name"] == user.full_name


@pytest.mark.django_db
def test_profile_exists_view_authenticated():
    client = APIClient()
    user1 = UserFactory.create()
    user2 = UserFactory.create()
    data = {"email": user2.email}
    client.force_authenticate(user1)
    response = client.post(
        "/api/v2/users/profile/check-exists/", data=data, format="json"
    )
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_profile_exists_view_unauthenticated():
    client = APIClient()
    data = {"email": "test@example.com"}
    response = client.post(
        "/api/v2/users/profile/check-exists/", data=data, format="json"
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_profile_exists_view_invalid_email():
    data = {"email": "invalid-email"}
    client = APIClient()
    user1 = UserFactory.create()
    client.force_authenticate(user1)
    response = client.post(
        "/api/v2/users/profile/check-exists/", data=data, format="json"
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_profile_exists_view_nonexistent_email():
    data = {"email": "me@gmail.com"}
    client = APIClient()
    user1 = UserFactory.create()
    client.force_authenticate(user1)
    response = client.post(
        "/api/v2/users/profile/check-exists/", data=data, format="json"
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
