from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.response import Response
from users.serializers.user import (
    RegisterAccountSerializer,
    VerifyAccountSerializer
)
from users.utils.user import UserUtils

user_utils = UserUtils()


@extend_schema(tags=["User Registration - Account Registration"])
class RegisterAccountView(CreateAPIView):
    """
    Use role-specific registration
    """
    serializer_class = RegisterAccountSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response_data = {"message": "User registered successfully."}
        return Response(response_data, status=status.HTTP_201_CREATED)


@extend_schema(tags=["User Registration - Account Verification"])
class VerifyAccountView(GenericAPIView):
    """
    API endpoint for email verification using OTP.
    Users must verify their email address using the OTP sent during
    registration. Once verified, users can log in to the system.
    """
    serializer_class = VerifyAccountSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if user_utils.check_token_is_valid(serializer.data):
            user = user_utils.verify_user(serializer.data["email"])
            user_utils.invalidate_token(user, serializer.data["token"])

            response = {
                "message": "Account verified successfully. You can now log in.",
            }
            return Response(response, status=status.HTTP_200_OK)
        else:
            response = {"message": "Invalid or expired OTP. Please request a new one."}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
