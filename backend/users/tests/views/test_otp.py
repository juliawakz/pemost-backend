import pytest
from notifications.tasks import send_email_task
from rest_framework import status
from rest_framework.test import APIClient
from users.factory.user import UnverifiedUserFactory, UserFactory
from users.models import Otp


@pytest.mark.django_db
def test_otp_generation_view(mocker):
    mocker.patch("notifications.tasks.send_email_task.delay")
    client = APIClient()
    user = UserFactory.create()

    data = {"email": user.email}

    response = client.post("/api/v2/users/otp/generate/", data)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"message": "OTP sent successfully."}
    assert send_email_task.delay.called


@pytest.mark.django_db
def test_otp_verify_view_success_otp(mocker):
    client = APIClient()
    user = UnverifiedUserFactory.create()
    assert user.is_verified is False
    otp = Otp.objects.create(user=user, token="123456")
    data = {"email": user.email, "token": otp.token}

    response = client.post("/api/v2/users/otp/verify/", data)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"message": "Account Activated."}
    user.refresh_from_db()
    assert user.is_verified is True


@pytest.mark.django_db
def test_otp_verify_view_invalid_otp():
    client = APIClient()
    user = UnverifiedUserFactory.create()
    assert user.is_verified is False
    data = {"email": user.email, "token": "202020"}
    response = client.post("/api/v2/users/otp/verify/", data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {"message": "Invalid or expired Otp"}
    user.refresh_from_db()
    assert user.is_verified is False
