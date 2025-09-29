from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from users.serializers.profile import ProfileSerializer

User = get_user_model()


@extend_schema(tags=["Profile"])
class ProfileView(RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_object(self):
        return self.request.user
