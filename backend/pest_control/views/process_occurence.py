# Ensure these imports exist in your file
from drf_spectacular.utils import extend_schema
from pest_control.serializers.pest_occurence import ProcessOccurrenceSerializer
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


@extend_schema(tags=["Pest Control"])
class ProcessOccurrenceApiView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ProcessOccurrenceSerializer

    def post(self, request, *args, **kwargs):
        if not request.data:
            return Response(
                {
                    "detail": "No data passed"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(
            data=request.data,
            context={"request": request}
        )

        if serializer.is_valid():
            message = {"detail": "Data Accepted"}
            return Response(message, status=status.HTTP_201_CREATED)
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
