from django.contrib.auth import get_user_model
from django.db import transaction
from locations.models import County, SubCounty, Ward
from locations.serializers.subcounty import (
    MinimalCountySerializer,
    MinimalSubCountySerializer,
)
from locations.serializers.ward import MiniWardSerializer
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied, ValidationError
from users.choices import RoleChoices
from users.utils.otp import OtpUtils
from users.utils.user import UserUtils

User = get_user_model()
user_utils = UserUtils()


class BaseUserSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=RoleChoices.choices, required=True)
    counties = serializers.PrimaryKeyRelatedField(
        queryset=County.objects.all(), many=True, required=False
    )
    subcounties = serializers.PrimaryKeyRelatedField(
        queryset=SubCounty.objects.all(), many=True, required=False
    )
    wards = serializers.PrimaryKeyRelatedField(
        queryset=Ward.objects.all(), many=True, required=False
    )

    class Meta:
        model = User
        fields = [
            "id", "email", "first_name", "last_name", "phone_number",
            "id_number", "role", "is_managed", "counties", "subcounties",
            "wards", "created_at", "updated_at", "full_name"
        ]
        read_only_fields = ["id", "created_at", "updated_at", "full_name"]

    def validate(self, attrs):
        request = self.context["request"]
        user = request.user
        role = attrs.get("role")

        if not role and not getattr(self.instance, "role", None):
            raise ValidationError("Role is required.")

        wards = list(attrs.get("wards") or [])
        subcounties = list(attrs.get("subcounties") or [])
        counties = list(attrs.get("counties") or [])

        # --- Role-specific checks ---
        if role == RoleChoices.SUPER_EXTENSION and not counties:
            raise ValidationError(
                "Super E-Extension must be assigned at least one county.")
        if role == RoleChoices.E_EXTENSION and not (wards or subcounties):
            raise ValidationError(
                "E-Extension must be assigned at least one ward or subcounty.")
        if role in [RoleChoices.FARMER, RoleChoices.AGRODEALER] and not wards:
            raise ValidationError(
                "Farmer/Agrodealer must be assigned at least one ward.")

        # --- Permission checks ---
        if not (user.is_superuser or user.role == RoleChoices.SYSTEM_ADMIN):
            if user.role == RoleChoices.SUPER_EXTENSION:
                if role not in [
                    RoleChoices.E_EXTENSION, RoleChoices.AGRODEALER,
                    RoleChoices.FARMER
                ]:
                    raise PermissionDenied(
                        f"Super Extension cannot manage {role} users.")

                if wards:
                    bad_wards = user_utils._ensure_all_wards_in_counties(
                        wards, user.counties.all())
                    if bad_wards:
                        raise ValidationError({
                            "message": "Some wards do not belong to "
                            "your assigned region(s).",
                            "wards": bad_wards
                        })

            elif user.role == RoleChoices.E_EXTENSION:
                if role not in [RoleChoices.FARMER, RoleChoices.AGRODEALER]:
                    raise PermissionDenied(
                        "E-Extension may only manage a Farmer or Agrodealer.")

                if wards:
                    bad_wards = user_utils._ensure_wards_subset(
                        wards, user.wards.all())
                    if bad_wards:
                        raise ValidationError({
                            "message": "Wards outside your scope "
                            "were assigned.",
                            "wards": bad_wards
                        })

            elif role and user.role in [
                    RoleChoices.FARMER, RoleChoices.AGRODEALER]:
                raise PermissionDenied(
                    "You are not allowed to change your role.")

            elif request.user != getattr(self.instance, "user", request.user):
                raise PermissionDenied("You are not allowed to manage users.")

        # --- Location consistency checks ---
        if wards:
            derived_subcounties, derived_counties = \
                user_utils._derive_subcounties_and_counties_from_wards(wards)
            if subcounties and set(sc.id for sc in subcounties) != \
                    set(derived_subcounties.values_list("id", flat=True)):
                raise ValidationError(
                    "Provided subcounties do not match the wards.")
            if counties and set(c.id for c in counties) != \
                    set(derived_counties.values_list("id", flat=True)):
                raise ValidationError(
                    "Provided counties do not match the wards.")

        attrs["is_verified"] = True
        return attrs

    def _sync_locations(self, instance):
        """Ensure subcounties & counties stay coherent with wards."""
        wards = instance.wards.all()
        if wards.exists():
            subcounties, counties = \
                user_utils._derive_subcounties_and_counties_from_wards(wards)
            instance.subcounties.set(subcounties)
            instance.counties.set(counties)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["counties"] = MinimalCountySerializer(
            instance.counties.all(), many=True).data
        data["subcounties"] = \
            MinimalSubCountySerializer(
                instance.subcounties.all(), many=True).data
        data["wards"] = \
            MiniWardSerializer(instance.wards.all(), many=True).data
        return data


# ---------------------------------------------------------------------
# 🟢 WRITE SERIALIZER (Create new user)
# ---------------------------------------------------------------------
class UserWriteSerializer(BaseUserSerializer):
    @transaction.atomic
    def create(self, validated_data):
        wards = validated_data.pop("wards", [])
        subcounties = validated_data.pop("subcounties", [])
        counties = validated_data.pop("counties", [])
        role = validated_data.get("role")

        password = OtpUtils().generate_random_password()
        validated_data["password"] = password

        if role == RoleChoices.FARMER:
            validated_data["is_managed"] = True

        instance = self.Meta.model.objects.create(**validated_data)
        instance.set_password(password)
        instance.save()

        # Set relationships
        if wards:
            instance.wards.set(wards)
        if subcounties:
            instance.subcounties.set(subcounties)
        if counties:
            instance.counties.set(counties)

        # Sync hierarchy (wards → subcounties → counties)
        self._sync_locations(instance)

        # Send credentials
        UserUtils().send_login_credentials_email(
            first_name=instance.first_name,
            email=instance.email,
            password=password
        )

        return instance


# ---------------------------------------------------------------------
# 🟡 UPDATE SERIALIZER (All fields optional + auto-partial)
# ---------------------------------------------------------------------
class UserUpdateSerializer(BaseUserSerializer):
    def __init__(self, *args, **kwargs):
        # Force partial updates automatically
        kwargs["partial"] = True
        super().__init__(*args, **kwargs)

        # Make all fields optional
        for field in self.fields.values():
            field.required = False

    @transaction.atomic
    def update(self, instance, validated_data):
        wards = validated_data.pop("wards", None)
        subcounties = validated_data.pop("subcounties", None)
        counties = validated_data.pop("counties", None)

        instance = super().update(instance, validated_data)

        if wards is not None:
            instance.wards.set(wards)
        if subcounties is not None:
            instance.subcounties.set(subcounties)
        if counties is not None:
            instance.counties.set(counties)

        self._sync_locations(instance)
        return instance
