import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from users.factory.user import SystemAdminFactory, UserFactory

User = get_user_model()


@pytest.mark.django_db
def test_user_login_api_view_success():
    user = UserFactory.create()
    client = APIClient()
    login_data = {
        "email": user.email,
        "password": "admin",
    }
    response = client.post("/api/v2/users/login/", login_data, format="json")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_user_login_api_view_wrong_credentials():
    user = UserFactory.create()
    client = APIClient()
    login_data = {
        "email": user.email,
        "password": "adminqq",
    }
    response = client.post("/api/v2/users/login/", login_data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_system_admin_login_on_user_login():
    system_admin = SystemAdminFactory.create()
    client = APIClient()
    login_data = {
        "email": system_admin.email,
        "password": "admin",
    }
    response = client.post("/api/v2/users/login/", login_data, format="json")
    assert response.status_code == status.HTTP_200_OK
