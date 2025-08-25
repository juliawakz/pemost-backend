from django.contrib.auth import get_user_model
from rest_framework import serializers
from users.exceptions import (
    AccountNotRegisteredException,
    InvalidCurrentPasswordException,
    PasswordMismatchException,
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
    password1 = serializers.CharField(required=True)
    password2 = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password1 = attrs.get("password1")
        password2 = attrs.get("password2")

        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            raise AccountNotRegisteredException()

        if password1 != password2:
            raise PasswordMismatchException

        return attrs


class PasswordChangeSerializer(serializers.Serializer):
    password = serializers.CharField(required=True, write_only=True)
    password1 = serializers.CharField(required=True, write_only=True)
    password2 = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        user = self.context.get("request").user
        password = attrs.get("password")
        password1 = attrs.get("password1")
        password2 = attrs.get("password2")

        if password1 != password2:
            raise PasswordMismatchException

        if not user.check_password(password):
            raise InvalidCurrentPasswordException
        attrs["email"] = user.email
        return attrs
