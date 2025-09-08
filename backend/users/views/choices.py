from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from users.choices import RoleChoices
from users.serializers.choices import RoleChoiceSerializer


class RoleChoicesView(APIView):
    """
    Endpoint to fetch all RoleChoices.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = RoleChoiceSerializer

    def get(self, request, *args, **kwargs):
        choices = [
            {"value": choice.value, "label": choice.label}
            for choice in RoleChoices
        ]
        serializer = RoleChoiceSerializer(choices, many=True)
        return Response(serializer.data)
