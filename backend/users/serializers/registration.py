from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from users.exceptions import PasswordMismatchException
from users.utils.user import UserUtils

User = get_user_model()


class RegistrationSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=True, write_only=True)
    last_name = serializers.CharField(required=True, write_only=True)
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
    password1 = serializers.CharField(required=True, write_only=True)
    password2 = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        password1 = attrs.get("password1")
        password2 = attrs.get("password2")

        if password1 != password2:
            raise PasswordMismatchException

        return attrs

    def create(self, validated_data):
        user_data = {
            "first_name": validated_data["first_name"],
            "last_name": validated_data["last_name"],
            "email": validated_data["email"],
            "phone_number": validated_data["phone_number"],
            "password": validated_data["password1"],
        }

        user = User.objects.create_user(**user_data)

        UserUtils().send_email_otp(email=validated_data["email"])

        return user
