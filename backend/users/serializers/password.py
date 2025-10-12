from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers
from users.exceptions import (
    AccountNotRegisteredException,
    InvalidCurrentPasswordException,
    InvalidOTPException,
    PasswordMismatchException,
)
from users.models.otp import Otp
from users.utils.user import UserUtils

User = get_user_model()
user_utils = UserUtils()


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    token = serializers.CharField(required=True, max_length=6, min_length=6)
    new_password1 = serializers.CharField(required=True, write_only=True)
    new_password2 = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        email = attrs["email"]
        new_password1 = attrs["new_password1"]
        new_password2 = attrs["new_password2"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise AccountNotRegisteredException()

        if new_password1 != new_password2:
            raise PasswordMismatchException()

        # validate OTP
        if not Otp.objects.filter(
            user=user,
            token=attrs["token"],
            expiry_at__gt=timezone.now()
        ).exists():
            raise InvalidOTPException()

        attrs["user"] = user  # attach user for save()
        return attrs

    def save(self, **kwargs):
        user = self.validated_data["user"]
        password = self.validated_data["new_password1"]
        token = self.validated_data["token"]
        user.set_password(password)
        user.save()
        user_utils.invalidate_token(
            user,
            token
        )
        return user


class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True, required=True)
    new_password1 = serializers.CharField(write_only=True, required=True)
    new_password2 = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        user = self.context["request"].user
        current_password = attrs.get("current_password")
        new_password1 = attrs.get("new_password1")
        new_password2 = attrs.get("new_password2")

        if not user.check_password(current_password):
            raise InvalidCurrentPasswordException()

        if new_password1 != new_password2:
            raise PasswordMismatchException()

        attrs["user"] = user
        attrs["new_password"] = new_password1
        return attrs

    def save(self, **kwargs):
        user = self.validated_data["user"]
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user
