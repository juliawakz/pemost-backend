from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils.translation import gettext as _
from locations.models import County, Ward
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from users.choices import RoleChoices
from users.models import (
    EExtensionOfficer,
    SuperExtensionOfficer,
    Agrodealer
)
from users.utils.user import UserUtils

User = get_user_model()
user_utils = UserUtils()


class BaseRegistrationSerializer(serializers.Serializer):
    """Base serializer for user registration with common fields"""
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True, max_length=30)
    last_name = serializers.CharField(required=True, max_length=30)
    phone_number = PhoneNumberField(required=True)
    id_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    password1 = serializers.CharField(required=True, write_only=True, min_length=8)
    password2 = serializers.CharField(required=True, write_only=True, min_length=8)
    profile_photo = serializers.ImageField(required=False, allow_null=True)

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
            "role": self.get_role(),
            "profile_photo": validated_data.get("profile_photo", None),
        }
        return User.objects.create_user(**user_data)

    def get_role(self):
        """Override in subclasses to return the appropriate role"""
        raise NotImplementedError("Subclasses must implement get_role()")


class EExtensionRegistrationSerializer(BaseRegistrationSerializer):
    """Serializer for e-extension officer self-registration"""
    wards = serializers.PrimaryKeyRelatedField(
        queryset=Ward.objects.all(),
        many=True,
        required=True,
        help_text=_("Wards where this e-extension officer operates")
    )
    is_visible = serializers.BooleanField(
        default=False,
        required=False,
        help_text=_("If True, e-extension is visible to super extension officers in their county")
    )

    def get_role(self):
        return RoleChoices.E_EXTENSION

    def validate_wards(self, value):
        if not value:
            raise ValidationError(_("At least one ward must be specified."))
        return value

    @transaction.atomic
    def create(self, validated_data):
        wards = validated_data.pop("wards", [])
        is_visible = validated_data.pop("is_visible", False)

        # Remove password fields from validated_data
        validated_data.pop("password2")

        # Create user
        user = self.create_user(validated_data)

        # Create e-extension profile
        e_extension = EExtensionOfficer.objects.create(
            user=user,
            is_visible=is_visible
        )

        # Set wards
        e_extension.wards.set(wards)

        # Send OTP for email verification
        user_utils.send_email_otp(email=user.email)

        return user


class SuperExtensionRegistrationSerializer(BaseRegistrationSerializer):
    """Serializer for super extension officer registration (admin-only)"""
    counties = serializers.PrimaryKeyRelatedField(
        queryset=County.objects.all(),
        many=True,
        required=False,
        help_text=_("Counties where this super extension officer operates")
    )

    def get_role(self):
        return RoleChoices.SUPER_EXTENSION

    @transaction.atomic
    def create(self, validated_data):
        counties = validated_data.pop("counties", [])

        # Remove password fields from validated_data
        validated_data.pop("password2")

        # Create user
        user = self.create_user(validated_data)

        # Create super extension profile
        super_extension = SuperExtensionOfficer.objects.create(
            user=user
        )

        # Set counties
        if counties:
            super_extension.counties.set(counties)

        # Send OTP for email verification
        user_utils.send_email_otp(email=user.email)

        return user


class AgrodealerRegistrationSerializer(BaseRegistrationSerializer):
    """Serializer for agrodealer registration"""
    ward = serializers.PrimaryKeyRelatedField(
        queryset=Ward.objects.all(),
        required=True,
        help_text=_("Ward where this agrodealer operates"),
    )
    name = serializers.CharField(
        max_length=50,
        required=True,
        help_text=_("Name of the agrovet"),
    )
    location = serializers.CharField(
        required=True,
        allow_blank=False,
        help_text=_("Location of the agrodealer in WKT format e.g. 'POINT (36.0038 -0.4683)'"),
    )

    def get_role(self):
        return RoleChoices.AGRODEALER

    @transaction.atomic
    def create(self, validated_data):
        ward = validated_data.pop("ward", [])
        location = validated_data.pop("location", [])
        name = validated_data.pop("name", [])

        # Remove password fields from validated_data
        validated_data.pop("password2")

        # Create user
        user = self.create_user(validated_data)

        # Create agrodealer profile
        Agrodealer.objects.create(
            user=user,
            location=location,
            name=name,
            ward=ward
        )

        # Send OTP for email verification
        user_utils.send_email_otp(email=user.email)

        return user


class RegisterAccountSerializer(BaseRegistrationSerializer):
    def get_role(self):
        return RoleChoices.FARMER

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
