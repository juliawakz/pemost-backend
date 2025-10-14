from datetime import datetime

from decouple import config
from django.conf import settings
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.utils import timezone
from locations.models import County, SubCounty
from notifications.tasks import send_email_task
from users.models.otp import Otp
from users.utils.otp import OtpUtils

User = get_user_model()
otp_utils = OtpUtils()


# ---------- User Helpers Functions ----------
class UserUtils:
    def invalidate_token(self, user, token: str):
        Otp.objects.filter(
            user=user,
            token=token
        ).update(
            expiry_at=timezone.now()
        )

    def verify_user(self, email: str):
        user = User.objects.filter(email=email).first()
        user.is_verified = True
        user.save()
        return user

    def check_token_is_valid(self, otp_details: dict):
        user = User.objects.filter(
            email=otp_details["email"]
        ).first()
        return Otp.objects.filter(
            user=user,
            token=otp_details["token"],
            expiry_at__gt=timezone.make_aware(timezone.datetime.now()),
        ).exists()

    def change_password(self, user_data):
        user = User.objects.filter(
            email=user_data["email"]
        ).first()
        user.set_password(user_data["password1"])
        user.save()

    def send_login_credentials_email(
            self, first_name: str, email: str, password: str):
        login_url = f"{config('LOGIN_URL',default='http://127.0.0.1:8000')}/login/"
        template = render_to_string(
            "user_registration.html",
            {
                "first_name": first_name,
                "email": email,
                "password": password,
                "login_url": login_url,
                "current_year": datetime.now().year,
            }
        )
        send_email_task.delay(
            email,
            settings.EMAIL_FROM,
            "Account Login Details",
            "",
            template
        )

    def send_email_otp(self, email: str):
        token_length = getattr(
            settings,
            "TOKEN_LENGTH",
            6
        )
        otp = otp_utils.generate_security_code(
            token_length=token_length
        )
        user = User.objects.filter(email=email).first()
        Otp.objects.create(
            user=user,
            token=otp,
            expiry_at=timezone.make_aware(
                timezone.datetime.now() + timezone.timedelta(hours=1),
                timezone.get_default_timezone()
            )
        )
        template = render_to_string(
            "email_otp.html",
            {
                "otp": otp,
                "user": user.first_name,
                "current_year": datetime.now().year,
            }
        )
        send_email_task.delay(
            email,
            settings.EMAIL_FROM,
            "Pemost Verification Code",
            "",
            template
        )
        return otp
