from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from users.choices import RoleChoices
from users.serializers.user import user_utils


class LocationChecks:
    def check_ward(self, ward, user):
        # --- Permission checks ---
        if not (user.is_superuser or user.role == RoleChoices.SYSTEM_ADMIN):
            if user.role == RoleChoices.SUPER_EXTENSION:
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
            elif user.role == RoleChoices.E_EXTENSION:
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
