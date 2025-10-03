from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
from django.conf import settings
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers, ValidationError
from locations.models import Ward, SubCounty, County
from users.utils.user import UserUtils

User = get_user_model()
user_utils = UserUtils()


class RegistrationSerializer(serializers.ModelSerializer):
    county = serializers.PrimaryKeyRelatedField(
        queryset=County.objects.all(), required=True
    )
    subcounty = serializers.PrimaryKeyRelatedField(
        queryset=SubCounty.objects.all(), required=True
    )
    ward = serializers.PrimaryKeyRelatedField(
        queryset=Ward.objects.all(), required=True
    )
    password1 = serializers.CharField(
        required=True, write_only=True)
    password2 = serializers.CharField(
        required=True, write_only=True)

    def validate(self, attrs):
        password1 = attrs.get("password1")
        password2 = attrs.get("password2")

        ward = attrs.pop("ward")
        subcounty = attrs.pop("subcounty")
        county = attrs.pop("county")

        wards = list(ward or [])
        subcounties = list(subcounty or [])
        counties = list(county or [])

        if password1 != password2:
            raise ValidationError("The two password fields didn't match.")

        # --- Location consistency checks ---
        if wards:
            derived_subcounties, derived_counties = \
                user_utils._derive_subcounties_and_counties_from_wards(wards)
            if subcounties and set(sc.id for sc in subcounties) != \
                    set(derived_subcounties.values_list("id", flat=True)):
                raise ValidationError(
                    "Provided subcounty does not match the ward.")
            if counties and set(c.id for c in counties) != \
                    set(derived_counties.values_list("id", flat=True)):
                raise ValidationError(
                    "Provided county does not match the ward.")

        attrs["counties"] = counties
        attrs["subcounties"] = subcounties
        attrs["wards"] = wards

        return attrs

    def create(self, validated_data):
        user_data = {
            "first_name": validated_data["first_name"],
            "last_name": validated_data["last_name"],
            "email": validated_data["email"],
            "phone_number": validated_data["phone_number"],
            "password": validated_data["password1"]
        }

        user = User.objects.create_user(**user_data)

        user_utils.send_email_otp(email=validated_data["email"])

        return user


class OtpVerifySerializer(serializers.Serializer):
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
                "User with this email does not exist.")

        return attrs
