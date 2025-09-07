import pytest
from django.contrib.auth import authenticate, get_user_model
from django.utils import timezone
from notifications.tasks import send_email_task
from rest_framework import status
from rest_framework.test import APIClient
from users.factory.user import UserFactory
from users.models.otp import Otp

User = get_user_model()


@pytest.mark.django_db
def test_password_reset_view_success(mocker):
    mocker.patch("notifications.tasks.send_email_task.delay")
    client = APIClient()
    user = UserFactory.create()
    data = {"email": user.email}

    response = client.post("/api/v2/users/password/reset/", data=data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"message": "Reset OTP sent to email."}
    assert Otp.objects.filter(user=user).count() == 1
    assert send_email_task.delay.called


@pytest.mark.django_db
def test_password_reset_confirm_view_success():
    client = APIClient()
    user = UserFactory.create()
    otp = Otp.objects.create(
        user=user,
        token="123456",
        expiry_at=timezone.make_aware(
                timezone.datetime.now() + timezone.timedelta(hours=1),
                timezone.get_default_timezone()
        ))
    data = {
        "email": user.email,
        "token": otp.token,
        "new_password1": "pissw0rd!",
        "new_password2": "pissw0rd!",
    }

    response = client.post(
        "/api/v2/users/password/reset/confirm/", data=data, format="json"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"message": "Password reset successful."}
    assert authenticate(username=user.email, password="pissw0rd!") is not None


@pytest.mark.django_db
def test_password_reset_confirm_view_failed():
    client = APIClient()
    user = UserFactory.create()
    data = {
        "email": user.email,
        "token": "253689",
        "new_password1": "pissw0rd!",
        "new_password2": "pissw0rd!",
    }

    response = client.post(
        "/api/v2/users/password/reset/confirm/", data=data, format="json"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {"detail": "The OTP is invalid or expired."}
    assert authenticate(username=user.email, password="pissw0rd!") is None


@pytest.mark.django_db
def test_password_change_view_success():
    client = APIClient()
    user = UserFactory.create()
    data = {
        "current_password": "admin",
        "new_password1": "traincascade",
        "new_password2": "traincascade",
    }
    client.force_authenticate(user)
    response = client.post("/api/v2/users/password/change/", data=data, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"message": "Password changed successfully."}
