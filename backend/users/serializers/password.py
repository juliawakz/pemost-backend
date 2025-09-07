from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.utils import timezone
from users.models.otp import Otp
from users.exceptions import (
    AccountNotRegisteredException,
    InvalidCurrentPasswordException,
    PasswordMismatchException,
    InvalidOTPException
)

User = get_user_model()


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        email = attrs.get("email")

        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            raise AccountNotRegisteredException()

        return attrs


class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    token = serializers.CharField(required=True, max_length=6, min_length=6)
    password1 = serializers.CharField(required=True, write_only=True)
    password2 = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        email = attrs["email"]
        password1 = attrs["password1"]
        password2 = attrs["password2"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise AccountNotRegisteredException()

        if password1 != password2:
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
        password = self.validated_data["password1"]
        user.set_password(password)
        user.save()
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
