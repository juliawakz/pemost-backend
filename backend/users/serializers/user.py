from django.contrib.auth import get_user_model
from rest_framework import serializers
from users.choices import RoleChoices

User = get_user_model()

# hierarchy map: higher number = more powerful
USER_TYPE_HIERARCHY = {
    RoleChoices.SYSTEM_ADMIN: 4,
    RoleChoices.SUPER_EXTENSION: 3,
    RoleChoices.E_EXTENSION: 2,
    RoleChoices.FARMER: 1
}


class UserWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "is_archived",
        )


class UserReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "full_name",
            "email",
            "user_role",
            "phone_number",
            "is_archived",
            "date_joined",
            "last_login",
            "created_at",
            "updated_at",
        )


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "is_archived",
            "user_role"
        )

    def validate(self, attrs):
        request_user = self.context["request"].user
        target_user = self.instance

        new_type = attrs.get("type")

        if new_type:
            if request_user.type == RoleChoices.AGRODEALER:
                raise serializers.ValidationError(
                    {
                        "type": "You cannot assign a user type."
                    }
                )

            if not request_user.is_superuser:
                # current hierarchy levels
                request_level = USER_TYPE_HIERARCHY.get(request_user.type, 0)
                new_level = USER_TYPE_HIERARCHY.get(new_type, 0)

                # Prevent escalating higher than self
                if new_level > request_level and not request_user.is_superuser:
                    raise serializers.ValidationError(
                        {
                            "type": "You cannot assign a user type higher than your own."
                        }
                    )

                # Prevent downgrading peers/higher-level users
                if target_user and USER_TYPE_HIERARCHY.get(target_user.type, 0) >= request_level and not request_user.is_superuser:
                    raise serializers.ValidationError(
                        {
                            "type": "You cannot change the type of a user at the same or higher level."
                        }
                    )

        return attrs
