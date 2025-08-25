from rest_framework import permissions, status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from users.serializers.login import LoginSerializer
from users.utils.user import UserUtils


class UserLoginAPIView(GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SystemAdminLoginAPIView(GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        is_system_admin = UserUtils().check_system_admin(serializer.data["user"]["id"])
        if is_system_admin:
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(
            {"message": "Not authorised"}, status=status.HTTP_400_BAD_REQUEST
        )
