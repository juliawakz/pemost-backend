import pytest
from django.contrib.auth import get_user_model
from locations.factory.ward import WardFactory
from notifications.tasks import send_email_task
from rest_framework import status
from rest_framework.test import APIClient
from users.choices import RoleChoices
from users.factory.user import SystemAdminFactory

User = get_user_model()


@pytest.mark.django_db
def test_registration_view_success(mocker):
    mocker.patch("notifications.tasks.send_email_task.delay")
    ward = WardFactory()
    auth_user = SystemAdminFactory()
    client = APIClient()
    client.force_authenticate(user=auth_user)

    user_data = {
        "first_name": "testuser",
        "last_name": "testuser",
        "email": "test@example.com",
        "phone_number": "0705123456",
        "role": RoleChoices.FARMER,
        "wards": [ward.id]
    }
    response = client.post("/api/v2/users/", user_data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert User.objects.filter(email="test@example.com").exists()
    assert User.objects.count() == 2
    assert send_email_task.delay.called


@pytest.mark.django_db
def test_registration_view_invalid_data():
    auth_user = SystemAdminFactory()
    client = APIClient()
    client.force_authenticate(user=auth_user)

    user_data = {
        "first_name": "testuser",
        "last_name": "testuser",
        "email": "test@example",
        "phone_number": "0705123456"
    }
    response = client.post("/api/v2/users/", user_data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert User.objects.count() == 1
