from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from app.serializers.farm_import import FarmsImportSerializer
from users.permissions import IsSystemAdminOrSuperUser


class FarmsImportView(generics.GenericAPIView):
    queryset = None
    serializer_class = FarmsImportSerializer
    permission_classes = [IsSystemAdminOrSuperUser]

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = self.get_serializer(
            data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        result = serializer.save()

        # Handle both old and new return formats
        if isinstance(result, dict):
            message = (
                f"{result['created']} farms created, "
                f"{result['updated']} updated, "
                f"{result['skipped']} skipped"
            )
            response_data = {
                "message": message,
                "status": status.HTTP_200_OK,
                "details": result
            }
        else:
            # Backward compatibility for old format
            response_data = {
                "message": f"{result} farms uploaded",
                "status": status.HTTP_200_OK,
            }

        return Response(response_data)
