from rest_framework import permissions, status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.serializers.registration import RegistrationSerializer
from users.serializers.user import UserReadSerializer
from users.serializers.user_registration import UserRegistrationSerializer


class RegistrationView(CreateAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response_data = {"message": "User registered successfully."}
        return Response(response_data, status=status.HTTP_201_CREATED)


class UserRegistrationView(CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        response_data = UserReadSerializer(instance)
        return Response(response_data.data, status=status.HTTP_201_CREATED)
