import pytest
from rest_framework import status
from rest_framework.test import APIClient
from users.factory.user import UserFactory


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_logout_view():
    user = UserFactory.create()
    client = APIClient()
    login_data = {
        "email": user.email,
        "password": "admin",
    }
    response = client.post("/api/v2/users/login/", login_data, format="json")
    assert response.status_code == status.HTTP_200_OK

    client.force_authenticate(user)
    data = {"refresh": response.data["token"]["refresh"]}
    response = client.post("/api/v2/users/logout/", data=data)
    print(response.data)
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"message": "Successful Logout"}


@pytest.mark.django_db
def test_logout_view_with_invalid_token():
    client = APIClient()
    user = UserFactory.create()
    client.force_authenticate(user)
    data = {"refresh": "invalid_token"}
    response = client.post("/api/v2/users/logout/", data=data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Error" in response.data
