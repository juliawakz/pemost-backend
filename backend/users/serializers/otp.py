from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import serializers
from users.exceptions import AccountNotRegisteredException, InvalidEmailException

User = get_user_model()


class OtpWriteSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        email = attrs.get("email")

        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            raise AccountNotRegisteredException()

        return attrs


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
            raise InvalidEmailException

        return attrs
