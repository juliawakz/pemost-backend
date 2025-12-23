from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils.translation import gettext as _
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from users.choices import LicenceChoices, RoleChoices
from users.utils.user import UserUtils

User = get_user_model()
user_utils = UserUtils()


class RegisterAccountSerializer(serializers.Serializer):
    """Base serializer for user registration with common fields"""
    email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)
    first_name = serializers.CharField(required=True, max_length=30)
    last_name = serializers.CharField(required=True, max_length=30)
    phone_number = PhoneNumberField(required=True)
    id_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    password1 = serializers.CharField(required=True, write_only=True, min_length=8)
    password2 = serializers.CharField(required=True, write_only=True, min_length=8)
    profile_photo = serializers.ImageField(required=False, allow_null=True)
    agree_to_terms = serializers.BooleanField(required=True)
    role = serializers.ChoiceField(
        choices=[
            (RoleChoices.SYSTEM_ADMIN, "System Admin"),
            (RoleChoices.SUPER_EXTENSION, "Super Extension Officer"),
            (RoleChoices.E_EXTENSION, "E-Extension Officer"),
            (RoleChoices.AGRODEALER, "Agrodealer"),
            (RoleChoices.FARMER, "Farmer"),
        ],
        required=True
    )
    license_type = serializers.ChoiceField(
        choices=[
            (LicenceChoices.FREE, "Free"),
            (LicenceChoices.PREMIUM, "Premium"),
        ],
        required=True
    )

    def validate_email(self, value):
        if value and User.objects.filter(email=value).exists():
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
        if attrs.get("password1") != attrs.get("password2"):
            raise ValidationError({"password2": _("The two password fields didn't match.")})
        return attrs

    def create_user(self, validated_data):
        """Create a user correctly handling password and license_type"""
        password = validated_data.pop("password1")
        validated_data.pop("password2", None)

        user = User.objects.create_user(
            phone_number=validated_data["phone_number"],
            password=password,
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            email=validated_data.get("email"),
            id_number=validated_data.get("id_number"),
            role=validated_data.get("role"),
            profile_photo=validated_data.get("profile_photo"),
            agree_to_terms=validated_data.get("agree_to_terms"),
            license_type=validated_data.get("license_type", LicenceChoices.FREE)
        )
        return user

    @transaction.atomic
    def create(self, validated_data):
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
            "profile_photo", "enable_email_notifications",
            "enable_push_notifications", "created_at", "updated_at"
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


class MiniUserReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "full_name",
            "role"
        ]
        extra_kwargs = {
            "id": {"read_only": True},
            "full_name": {"read_only": True},
            "role": {"read_only": True}
        }


class NotificationPreferencesSerializer(serializers.ModelSerializer):
    """Serializer for updating user notification preferences"""
    class Meta:
        model = User
        fields = [
            "enable_email_notifications",
            "enable_push_notifications"
        ]

    def update(self, instance, validated_data):
        instance.enable_email_notifications = validated_data.get(
            'enable_email_notifications',
            instance.enable_email_notifications
        )
        instance.enable_push_notifications = validated_data.get(
            'enable_push_notifications',
            instance.enable_push_notifications
        )
        instance.save()
        return instance
