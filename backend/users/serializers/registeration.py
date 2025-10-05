from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
from locations.models import County, SubCounty, Ward
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from users.choices import RoleChoices
from users.utils.user import UserUtils

User = get_user_model()
user_utils = UserUtils()


class RegisterAccountSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(
        choices=[
            (RoleChoices.FARMER, "Farmer"),
            (RoleChoices.E_EXTENSION, "E-Extension"),
        ],
        required=True
    )
    wards = serializers.PrimaryKeyRelatedField(
        queryset=Ward.objects.all(), many=True, required=True
    )
    password1 = serializers.CharField(
        required=True, write_only=True)
    password2 = serializers.CharField(
        required=True, write_only=True)

    class Meta:
        model = User
        fields = [
            "email", "first_name", "last_name", "phone_number",
            "id_number", "wards", "password1", "password2",
            "id_number", "role"
        ]

    def validate(self, attrs):
        password1 = attrs.get("password1")
        password2 = attrs.get("password2")

        if password1 != password2:
            raise ValidationError(
                "The two password fields didn't match."
            )

        return attrs

    def create(self, validated_data):
        user_data = {
            "first_name": validated_data["first_name"],
            "last_name": validated_data["last_name"],
            "email": validated_data["email"],
            "phone_number": validated_data["phone_number"],
            "password": validated_data["password1"],
            "id_number": validated_data.get("id_number", None),
            "role": validated_data.get("role")
        }

        wards = validated_data.pop("wards", [])

        user = User.objects.create_user(**user_data)

        user_utils.send_email_otp(email=validated_data["email"])

        # --- Set M2M relations ---
        user.wards.set(wards)

        return user


class VerifyAccountSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    token = serializers.CharField(
        required=True,
        min_length=settings.TOKEN_LENGTH,
        max_length=settings.TOKEN_LENGTH,
    )

    def validate(self, attrs):
        email = attrs.get("email")
        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            raise ValidationError(
                "User with this email does not exist."
            )

        return attrs
