from rest_framework import permissions, status
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.response import Response
from users.serializers.otp import OtpVerifySerializer, OtpWriteSerializer
from users.utils.user import UserUtils


class OtpGenerationView(CreateAPIView):
    serializer_class = OtpWriteSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        UserUtils().send_email_otp(serializer.data["email"])
        return Response(
            {"message": "OTP sent successfully."},
            status=200,
        )


class OtpVerifyOtpView(GenericAPIView):
    serializer_class = OtpVerifySerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if UserUtils().check_token_is_valid(serializer.data):
            UserUtils().verify_user(serializer.data["email"])
            response = {"message": "Account Activated."}
            return Response(response, status=status.HTTP_200_OK)
        else:
            response = {"message": "Invalid or expired Otp"}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
