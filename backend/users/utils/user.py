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
    def _derive_subcounties_and_counties_from_wards(self, wards_qs):
        # wards -> subcounties -> counties
        subcounties = SubCounty.objects.filter(wards__in=wards_qs).distinct()
        counties = County.objects.filter(subcounties__in=subcounties).distinct()
        return subcounties, counties

    def _ensure_all_wards_in_counties(self, wards, counties):
        county_ids = set(counties.values_list("id", flat=True))
        bad_wards = [{"id": str(w.id), "name": w.name} for w in wards if w.subcounty.county_id not in county_ids]
        return bad_wards

    def _ensure_wards_subset(self, wards, allowed_wards):
        allowed_ids = set(allowed_wards.values_list("id", flat=True))
        bad_wards = [
            {"id": str(w.id), "name": w.name}
            for w in wards if w.id not in allowed_ids
        ]
        return bad_wards

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
        login_url = f"{config('LOGIN_URL', default='http://127.0.0.1:8000')}/login/"
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
