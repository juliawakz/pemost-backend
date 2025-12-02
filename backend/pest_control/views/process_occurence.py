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
            201: {
                "type": "object",
                "properties": {
                    "message": {"type": "string"},
                    "summary": {
                        "type": "object",
                        "properties": {
                            "total_submitted": {"type": "integer"},
                            "total_processed": {"type": "integer"},
                            "total_errors": {"type": "integer"}
                        }
                    },
                    "processed_farms": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "errors": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "index": {"type": "integer"},
                                "farm_id": {"type": "string"},
                                "error": {"type": "string"}
                            }
                        }
                    }
                }
            },
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

        result = serializer.get_processing_result()

        if result:
            response_data = {
                "message": "Processing completed",
                "summary": {
                    "total_submitted": result['total_submitted'],
                    "total_processed": result['total_processed'],
                    "total_errors": result['total_errors']
                },
                "processed_farms": result['processed_farms'],
                "errors": result['errors']
            }

            if result['total_errors'] > 0 and result['total_processed'] > 0:
                return Response(
                    response_data, status=status.HTTP_207_MULTI_STATUS)
            elif result['total_errors'] == result['total_submitted']:
                return Response(
                    response_data, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(
                    response_data, status=status.HTTP_201_CREATED)

        return Response(
            {"detail": "Data Accepted"},
            status=status.HTTP_201_CREATED
        )