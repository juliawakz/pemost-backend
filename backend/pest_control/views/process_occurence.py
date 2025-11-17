from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from pest_control.serializers.pest_occurence import ProcessOccurrenceSerializer

@extend_schema(tags=["Pest Control"])
class ProcessOccurrenceApiView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ProcessOccurrenceSerializer

    @extend_schema(
        request=ProcessOccurrenceSerializer,
        responses={
            201: {"type": "object", "properties": {"detail": {"type": "string"}}},
            400: {"type": "object", "properties": {"detail": {"type": "string"}}}
        }
    )
    def post(self, request, *args, **kwargs):
        if not request.data:
            return Response(
                {"detail": "No data passed"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ProcessOccurrenceSerializer(
            data=request.data,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)

        return Response(
            {"detail": "Data Accepted"},
            status=status.HTTP_201_CREATED
        )