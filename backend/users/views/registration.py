from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.response import Response
from users.serializers.registeration import (
    EExtensionRegistrationSerializer,
    RegisterAccountSerializer,
    SuperExtensionRegistrationSerializer,
    VerifyAccountSerializer,
    AgrodealerRegistrationSerializer
)
from users.serializers.user import UserSerializer
from users.utils.user import UserUtils

user_utils = UserUtils()


@extend_schema(tags=["User Registration - E-Extension Officer"])
class EExtensionRegistrationView(CreateAPIView):
    """
    API endpoint for e-extension officer self-registration.

    E-Extension officers can register themselves and must specify the wards they operate in.
    After registration, an OTP is sent to the provided email for verification.
    By default, they are not visible to super extension officers until approved.
    """
    serializer_class = EExtensionRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        response_data = {
            "message": "E-Extension officer registered successfully. Please check your email for verification code.",
            "user": UserSerializer(user).data
        }
        return Response(response_data, status=status.HTTP_201_CREATED)



@extend_schema(tags=["User Registration - Agrodealer"])
class AgrodealerRegistrationView(CreateAPIView):
    """
    API endpoint for e-extension officer self-registration.

    Agrodealer can register themselves and must specify the wards they operate in.
    After registration, an OTP is sent to the provided email for verification.
    """
    serializer_class = AgrodealerRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        response_data = {
            "message": "Agrodealer registered successfully. Please check your email for verification code.",
            "user": UserSerializer(user).data
        }
        return Response(response_data, status=status.HTTP_201_CREATED)


@extend_schema(tags=["User Registration - Super Extension Officer"])
class SuperExtensionRegistrationView(CreateAPIView):
    """
    API endpoint for super extension officer registration.

    Note: This endpoint should typically be restricted to admins only.
    Super extension officers can specify the counties they operate in.
    After registration, an OTP is sent to the provided email for verification.
    """
    serializer_class = SuperExtensionRegistrationSerializer
    permission_classes = [permissions.IsAdminUser]  # Admin-only access

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        response_data = {
            "message": "Super Extension officer registered successfully. Please check your email for verification code.",
            "user": UserSerializer(user).data
        }
        return Response(response_data, status=status.HTTP_201_CREATED)


@extend_schema(tags=["User Registration - Farmer"])
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

    Users must verify their email address using the OTP sent during registration.
    Once verified, users can log in to the system.
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
                "user": UserSerializer(user).data
            }
            return Response(response, status=status.HTTP_200_OK)
        else:
            response = {"message": "Invalid or expired OTP. Please request a new one."}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
