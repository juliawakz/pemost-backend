from drf_spectacular.utils import extend_schema
from pest_control.models.pest_occurence import PestOccurrence
from pest_control.serializers.pest_occurence import PestOccurrenceSerializer
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication


@extend_schema(tags=["Pest Control"])
class PestOccurrenceListView(ListAPIView):
    queryset = PestOccurrence.objects.all()
    serializer_class = PestOccurrenceSerializer
    authentication_classes = [TokenAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return PestOccurrence.objects.none()

        return self.queryset.filter(is_archived=False)
