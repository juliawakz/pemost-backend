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


class PasswordResetView(GenericAPIView):
    serializer_class = PasswordResetSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        UserUtils().send_email_otp(serializer.data["email"])
        response = {"message": "Reset password OTP  token sent"}
        return Response(response, status=status.HTTP_200_OK)


class PasswordResetConfirmView(GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if UserUtils().check_token_is_valid(serializer.data):
            UserUtils().change_password(serializer.data)
            response = {"message": "Password Changed."}
            return Response(response, status=status.HTTP_200_OK)
        else:
            response = {"message": "Invalid or expired Otp"}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class PasswordChangeView(GenericAPIView):
    serializer_class = PasswordChangeSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        context = {"request": self.request}
        serializer = self.get_serializer(data=request.data, context=context)
        serializer.is_valid(raise_exception=True)
        UserUtils().change_password(serializer.validated_data)
        response = {"message": "Password Changed."}
        return Response(response, status=status.HTTP_200_OK)
