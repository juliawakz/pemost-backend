from django.contrib.auth import get_user_model
from django.contrib.auth.models import update_last_login
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from users.serializers.user import MiniUserReadSerializer

User = get_user_model()


class TokenSerializer(serializers.Serializer):
    refresh_expiry_time = serializers.DateTimeField(read_only=True)
    access_expiry_time = serializers.DateTimeField(read_only=True)
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)


class LoginSerializer(serializers.Serializer):
    phone_number = PhoneNumberField(write_only=True, required=True)
    username = serializers.CharField(write_only=True, required=False)
    email = serializers.EmailField(write_only=True, required=False)
    password = serializers.CharField(max_length=128, write_only=True)
    user = MiniUserReadSerializer(many=False, read_only=True)
    message = serializers.CharField(read_only=True)
    token = TokenSerializer(read_only=True, required=False)

    def validate(self, data):
        email = data.get("email", None)
        password = data.get("password", None)
        phone_number = data.get("phone_number", None)
        if not any([email, phone_number]):
            raise serializers.ValidationError(
                "Unable to login with provided credentials"
            )
        try:
            user_filter = {}
            if email:
                user_filter.update({"email": str(email)})
            else:
                user_filter.update({"phone_number": str(phone_number)})
            user = User.objects.get(**user_filter)
        except (User.DoesNotExist, User.MultipleObjectsReturned) as e:
            raise serializers.ValidationError(
                _("Unable to login with provided credentials")
            ) from e
        if not user.check_password(password):
            raise serializers.ValidationError(_("Invalid login credentials"))
        try:
            is_enabled = user.is_active
            refresh = RefreshToken.for_user(user)
            refresh_token = str(refresh)
            access_token = str(refresh.access_token)
            update_last_login(None, user)
            validation = {
                "user": user,
                "message": "Login Successful"
                if is_enabled
                else "Verify your account to retrieve token.",
            }
            if is_enabled:
                validation["token"] = {
                    "access": access_token,
                    "refresh": refresh_token,
                    "lifetime": refresh.lifetime,
                    "expiry_time": user.last_login + refresh.lifetime,
                }
            return validation
        except User.DoesNotExist as e:
            raise serializers.ValidationError(("Invalid login credentials")) from e

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(
        required=True,
        allow_blank=False
    )
