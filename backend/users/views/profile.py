from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.generics import GenericAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.serializers.profile import ProfileExistsSerializer, ProfileSerializer

User = get_user_model()


class ProfileView(RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = "id"

    def get_object(self):
        return self.request.user


class ProfileExitsView(GenericAPIView):
    serializer_class = ProfileExistsSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
