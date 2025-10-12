from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils.translation import gettext as _
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from users.choices import RoleChoices
from users.utils.user import UserUtils

User = get_user_model()
user_utils = UserUtils()


class RegisterAccountSerializer(serializers.Serializer):
    """Base serializer for user registration with common fields"""
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True, max_length=30)
    last_name = serializers.CharField(required=True, max_length=30)
    phone_number = PhoneNumberField(required=True)
    id_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    password1 = serializers.CharField(required=True, write_only=True, min_length=8)
    password2 = serializers.CharField(required=True, write_only=True, min_length=8)
    profile_photo = serializers.ImageField(required=False, allow_null=True)
    role = serializers.ChoiceField(
        choices=[
            (RoleChoices.SUPER_EXTENSION, "Super Extension Officer'"),
            (RoleChoices.E_EXTENSION, "E-Extension Officer"),
            (RoleChoices.AGRODEALER, "Agrodealer"),
            (RoleChoices.FARMER, "Farmer"),
        ],
        required=True
    )

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise ValidationError(_("A user with this email already exists."))
        return value

    def validate_phone_number(self, value):
        if User.objects.filter(phone_number=value).exists():
            raise ValidationError(_("A user with this phone number already exists."))
        return value

    def validate_id_number(self, value):
        if value and User.objects.filter(id_number=value).exists():
            raise ValidationError(_("A user with this ID number already exists."))
        return value

    def validate(self, attrs):
        password1 = attrs.get("password1")
        password2 = attrs.get("password2")

        if password1 != password2:
            raise ValidationError({"password2": _("The two password fields didn't match.")})

        return attrs

    def create_user(self, validated_data):
        """Create the base user"""
        user_data = {
            "first_name": validated_data["first_name"],
            "last_name": validated_data["last_name"],
            "email": validated_data["email"],
            "phone_number": validated_data["phone_number"],
            "password": validated_data["password1"],
            "id_number": validated_data.get("id_number", None),
            "role": validated_data.get("role", None),
            "profile_photo": validated_data.get("profile_photo", None),
        }
        return User.objects.create_user(**user_data)

    @transaction.atomic
    def create(self, validated_data):
        # Remove password fields from validated_data
        validated_data.pop("password2")

        # Create user
        user = self.create_user(validated_data)

        # Send OTP for email verification
        user_utils.send_email_otp(email=user.email)

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


class UserReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id", "email", "first_name", "last_name", "phone_number",
            "id_number", "role", "is_verified", "full_name",
            "profile_photo", "created_at", "updated_at"
        ]
        extra_kwargs = {
            "id": {"read_only": True},
            "email": {"read_only": True},
            "is_verified": {"read_only": True},
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
            "full_name": {"read_only": True},
            "role": {"read_only": True}
        }
