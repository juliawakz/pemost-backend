from drf_spectacular.utils import extend_schema
from farms.serializers.farm_import import FarmsImportSerializer
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


@extend_schema(tags=["Farms"])
class FarmsImportView(generics.GenericAPIView):
    serializer_class = FarmsImportSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        total_farms = serializer.save()

        return Response(
            {
                "message": f"{total_farms} farms uploaded",
                "status": status.HTTP_200_OK
            }
        )
