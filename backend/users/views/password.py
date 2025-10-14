from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.serializers.password import (
    PasswordChangeSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetSerializer,
)
from users.utils.user import UserUtils

User = get_user_model()


@extend_schema(tags=["Password"])
class PasswordResetView(GenericAPIView):
    serializer_class = PasswordResetSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = User.objects.get(email=serializer.data["email"])
            UserUtils().send_email_otp(user.email)
        except User.DoesNotExist:
            pass
        response = {
            "message": "Check your email for reset otp."
        }
        return Response(response, status=status.HTTP_200_OK)


@extend_schema(tags=["Password"])
class PasswordResetConfirmView(GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # serializer handles token + password logic
        serializer.save()

        return Response(
            {
                "message": "Password reset successful."
            },
            status=status.HTTP_200_OK
        )


@extend_schema(tags=["Password"])
class PasswordChangeView(GenericAPIView):
    serializer_class = PasswordChangeSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                "message": "Password changed successfully."
            },
            status=status.HTTP_200_OK
        )
