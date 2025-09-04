from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
from users.serializers.user import UserReadSerializer
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from users.utils.user import UserUtils
from users.choices import RoleChoices

User = get_user_model()


class RegistrationSerializer(serializers.Serializer):
    first_name = serializers.CharField(
        required=True,
        write_only=True
    )
    last_name = serializers.CharField(
        required=True,
        write_only=True
    )
    user_role = serializers.ChoiceField(
        choices=RoleChoices.choices,
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
    user = UserReadSerializer(
        read_only=True
    )

    def create(self, validated_data):
        user_data = {
            "first_name": validated_data["first_name"],
            "last_name": validated_data["last_name"],
            "email": validated_data["email"],
            "phone_number": validated_data["phone_number"],
            "user_role": validated_data["user_role"],
            "created_by": self.context["request"].user
        }

        user = UserUtils()._add_user(**user_data)
        validated_data["user"] = user

        return validated_data
