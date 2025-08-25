from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import update_last_login
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from users.exceptions import (
    AccountDisabledException,
    AccountNotRegisteredException,
    InactiveAccountException,
    InvalidCredentialsException,
)
from users.serializers.profile import ProfileSerializer

User = get_user_model()


class TokenSerializer(serializers.Serializer):
    refresh_expiry_time = serializers.DateTimeField(read_only=True)
    access_expiry_time = serializers.DateTimeField(read_only=True)
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        allow_blank=False,
        write_only=True,
    )
    password = serializers.CharField(
        write_only=True, style={"input_type": "password"}, allow_blank=False
    )
    user = ProfileSerializer(many=False, read_only=True)
    token = TokenSerializer(read_only=True, required=False)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = User.objects.filter(email=email).first()

        if not user:
            raise AccountNotRegisteredException()

        if user.is_archived:
            raise AccountDisabledException()

        if not user.is_verified:
            raise InactiveAccountException()

        authenticated_user = authenticate(username=email, password=password)

        if not authenticated_user:
            raise InvalidCredentialsException()

        attrs["user"] = authenticated_user
        update_last_login(None, user)
        refresh = RefreshToken.for_user(user)

        user_login_data = {
            "user": user,
            "token": {
                "access": str(refresh.access_token),
                "refresh": str(RefreshToken.for_user(user)),
                "access_expiry_time": user.last_login + refresh.access_token_class.lifetime,
                "refresh_expiry_time": user.last_login + refresh.lifetime,
            },
        }
        return user_login_data


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True, allow_blank=False)
