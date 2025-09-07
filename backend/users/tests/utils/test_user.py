import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from notifications.tasks import send_email_task
from users.factory.user import UserFactory
from users.models.otp import Otp
from users.utils.otp import OtpUtils
from users.utils.user import UserUtils

User = get_user_model()
otp_utils = OtpUtils()


@pytest.fixture
def test_user():
    return UserFactory.create()


@pytest.fixture
def test_otp(test_user):
    return Otp.objects.create(
        user=test_user,
        token="123456",
        expiry_at=timezone.make_aware(
            timezone.datetime.now() + timezone.timedelta(hours=1),
            timezone.get_default_timezone()
        )
    )


@pytest.mark.django_db
def test_check_token_is_valid(test_user, test_otp):
    otp_details = {"email": test_user.email, "token": test_otp.token}
    assert UserUtils().check_token_is_valid(otp_details)


@pytest.mark.django_db
def test_check_token_expired(test_user, test_otp):
    otp_details = {"email": test_user.email, "token": test_otp.token}
    otp = Otp.objects.filter(id=test_otp.id).first()
    otp.expiry_at = timezone.make_aware(
        timezone.datetime.now() + timezone.timedelta(hours=-2)
    )
    otp.save()
    assert not UserUtils().check_token_is_valid(otp_details)


@pytest.mark.django_db
def test_change_password():
    user = UserFactory.create()
    user_data = {"email": user.email, "password1": "new_password"}
    UserUtils().change_password(user_data)
    user.refresh_from_db()
    assert user.check_password("new_password")


@pytest.mark.django_db
def test_send_email_otp(mocker):
    user = UserFactory.create()
    mocker.patch("notifications.tasks.send_email_task.delay")
    UserUtils().send_email_otp(user.email)
    assert Otp.objects.filter(user=user).exists()
    assert send_email_task.delay.called
