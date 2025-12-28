from decouple import config
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from users.choices import UserTypeChoices
from users.serializers.user import UserReadSerializer
from users.utils.otp import OtpUtils

# from users.utils.user import UserUtils

User = get_user_model()


class UserRegistrationSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=True, write_only=True)
    last_name = serializers.CharField(required=True, write_only=True)
    user_type = serializers.ChoiceField(
        choices=UserTypeChoices.choices,
        required=True,
        write_only=True
    )
    phone_number = PhoneNumberField(
        required=True,
        write_only=True,
        validators=[
            UniqueValidator(
                queryset=User.objects.values_list("phone_number", flat=True),
                message=_("A user is already registered with this phone number."),
            )
        ],
    )
    email = serializers.EmailField(
        required=True,
        write_only=True,
        validators=[
            UniqueValidator(
                queryset=User.objects.values_list("email", flat=True),
                message=_("A user is already registered with this email."),
            )
        ],
    )

    user = UserReadSerializer(read_only=True)

    def create(self, validated_data):
        user_data = {
            "first_name": validated_data["first_name"],
            "last_name": validated_data["last_name"],
            "email": validated_data["email"],
            "phone_number": validated_data["phone_number"],
            "password": OtpUtils().generate_random_password(),
            "type": validated_data["user_type"],
            "is_verified": True
        }

        # user_type_login_urls = {
        #     UserTypeChoices.SYSTEM_ADMIN: config("ADMIN_LOGIN_URL"),
        #     UserTypeChoices.NORMAL: config("LOGIN_URL"),
        # }

        # login_url = user_type_login_urls.get(validated_data["user_type"], config("LOGIN_URL"))

        user = User.objects.create_user(**user_data)

        # UserUtils().send_email_login_credentials(
        #     first_name=user.first_name,
        #     email=user_data["email"],
        #     password=user_data["password"],
        #     login_url=login_url
        # )

        return user
