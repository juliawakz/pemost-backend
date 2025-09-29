from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from users.choices import RoleChoices
from users.serializers.choices import RoleChoiceSerializer


@extend_schema(tags=["Users"])
class RoleChoicesView(APIView):
    """
    Endpoint to fetch all RoleChoices.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = RoleChoiceSerializer

    def get(self, request, *args, **kwargs):
        u = request.user
        choices = [
            {"value": choice.value, "label": choice.label}
            for choice in RoleChoices
        ]
        if u.role == RoleChoices.SUPER_EXTENSION:
            choices = choices[:-2]
        elif u.role == RoleChoices.E_EXTENSION:
            choices = choices[:-3]
        elif u.role == RoleChoices.AGRODEALER or u.role == RoleChoices.FARMER:
            return Response(
                {
                    "Error": "You are not allowed to access this resource"
                },
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = RoleChoiceSerializer(choices, many=True)
        return Response(serializer.data)
