from django.conf import settings
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.utils import timezone
from users.models.otp import Otp
from users.models.role import Role
from notifications.tasks import send_email_task
from users.choices import RoleChoices
from users.utils.otp import OtpUtils

User = get_user_model()
otp_utils = OtpUtils()


class UserUtils:
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

    def _add_user(
            self, email, first_name, last_name, phone_number, created_by, user_role
            ):
        password = otp_utils.generate_random_password()
        user = User.objects.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            created_by=created_by,
            password=password
        )
        user.is_active = True
        user.save()
        if user_role:
            Role.objects.create(
                user=user,
                role=user_role
            )
        self.send_login_credentials_email(
            first_name,
            email,
            password,
            settings.LOGIN_URL
        )
        return user

    def send_login_credentials_email(
            self, first_name: str, email: str, password: str, login_url: str):
        template = render_to_string(
            "user_registration.html",
            {
                "first_name": first_name,
                "email": email,
                "password": password,
                "login_url": login_url
            }
        )
        send_email_task.delay(
            email,
            settings.DEFAULT_EMAIL,
            "Account Login Details",
            "",
            template
        )

    def check_system_admin(self, user_id: str):
        user = User.objects.filter(id=user_id).first()
        if user.type == RoleChoices.SYSTEM_ADMIN:
            return True
        return False

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
            expiry_at=timezone.now() + timezone.timedelta(hours=1)
        )
        template = render_to_string(
            "email_otp.html",
            {
                "otp": otp,
                "user": user.first_name
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
