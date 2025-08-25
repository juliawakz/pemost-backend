from django.conf import settings
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.utils import timezone
from notifications.tasks import send_email_task
from users.choices import UserTypeChoices
from users.models.otp import Otp
from users.utils.otp import OtpUtils

User = get_user_model()
otp_utils = OtpUtils()


class UserUtils:
    def check_token_is_valid(self, otp_details: dict):
        user = User.objects.filter(email=otp_details["email"]).first()
        return Otp.objects.filter(
            user=user,
            token=otp_details["token"],
            expiry_at__gt=timezone.make_aware(timezone.datetime.now()),
        ).exists()

    def verify_user(self, email: str):
        user = User.objects.filter(email=email).first()
        user.is_verified = True
        user.email_verified = True
        user.save()

    def send_email_otp(self, email: str):
        token_length = getattr(settings, "TOKEN_LENGTH", 6)
        otp = otp_utils.generate_security_code(token_length=token_length)
        user = User.objects.filter(email=email).first()
        Otp.objects.create(
            user=user,
            token=otp,
            expiry_at=timezone.now() + timezone.timedelta(hours=1)

        )
        template = render_to_string(
            "email_otp.html",
            {"otp": otp, "user": user.first_name}
        )
        send_email_task.delay(
            email,
            settings.EMAIL_FROM,
            "Pemost Verification Code",
            "",
            template
        )
        return otp

    def send_email_login_credentials(
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
            "Account Registration Details",
            "",
            template
        )

    def check_system_admin(self, user_id: str):
        user = User.objects.filter(id=user_id).first()
        if user.type == UserTypeChoices.SYSTEM_ADMIN:
            return True
        return False

    def change_password(self, user_data):
        user = User.objects.filter(
            email=user_data["email"]
        ).first()
        user.set_password(user_data["password1"])
        user.save()

    def get_all_descendants(self, user):
        descendants = []
        for child in user.created_users.all():
            descendants.append(child)
            descendants.extend(self.get_all_descendants(child))
        return descendants

    def get_all_farmers_under(self, user):
        all_descendants = self.get_all_descendants(user)
        return [u for u in all_descendants if u.role == "farmer"]
