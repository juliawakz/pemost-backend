from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from users.choices import RoleChoices
from users.serializers.user import user_utils


class LocationChecks:
    def check_ward(self, ward, user):
        # --- Permission checks ---
        if not (user.is_superuser or user.role == RoleChoices.SYSTEM_ADMIN):
            if user.is_super_extension():
                if ward:
                    bad_wards = user_utils._ensure_all_wards_in_counties(
                        [ward], user.counties.all()
                    )
                    if bad_wards:
                        raise serializers.ValidationError({
                            "message": "The ward does not belong to\
                                your assigned region(s).",
                            "wards": bad_wards
                        })
            elif user.is_e_extension():
                if ward:
                    bad_wards = user_utils._ensure_wards_subset(
                        [ward], user.wards.all()
                    )
                    if bad_wards:
                        raise ValidationError({
                            "message": [
                                "Ward outside your scope were assigned."],
                            "wards": bad_wards
                        })
            else:
                raise serializers.ValidationError(
                    "You are not allowed to perform this action."
                )

    def check_ward_farmer(self, ward, user):
        # --- Permission checks ---
        if not (user.is_superuser or user.role == RoleChoices.SYSTEM_ADMIN):
            if user.is_super_extension():
                if ward:
                    bad_wards = user_utils._ensure_all_wards_in_counties(
                        [ward], user.counties.all()
                    )
                    if bad_wards:
                        raise serializers.ValidationError({
                            "message": "The ward does not belong to\
                                your assigned region(s).",
                            "wards": bad_wards
                        })
            elif user.is_e_extension():
                if ward:
                    bad_wards = user_utils._ensure_wards_subset(
                        [ward], user.wards.all()
                    )
                    if bad_wards:
                        raise ValidationError({
                            "message": [
                                "Ward outside your scope were assigned."],
                            "wards": bad_wards
                        })
            elif user.is_farmer():
                if ward:
                    bad_wards = user_utils._ensure_wards_subset(
                        [ward], user.wards.all()
                    )
                    if bad_wards:
                        raise ValidationError({
                            "message": [
                                "Ward outside the registered ward."],
                            "wards": bad_wards
                        })
            else:
                raise serializers.ValidationError(
                    "You are not allowed to perform this action."
                )
