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
        total_farms = serializer.save()
        return Response(
            {
                "message": f"{total_farms} farms uploaded",
                "status": status.HTTP_200_OK,
            }
        )
