from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from crops.choices import SeverityChoices
from users.serializers.choices import RoleChoiceSerializer


@extend_schema(tags=["Growth Stages"])
class SeverityChoicesView(APIView):
    """
    Endpoint to fetch Severitys.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = RoleChoiceSerializer

    def get(self, request, *args, **kwargs):
        choices = [
            {"value": choice.value, "label": choice.label}
            for choice in SeverityChoices
        ]
        serializer = RoleChoiceSerializer(choices, many=True)
        return Response(serializer.data)
