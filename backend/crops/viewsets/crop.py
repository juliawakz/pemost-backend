from drf_spectacular.utils import extend_schema
from crops.models.crop import Crop
from crops.serializers.crop import CropSerializer
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from users.permissions.user import \
    IsSuperExtensionOrEExtension
from crops.filterset.crop import CropFilterSet


@extend_schema(tags=["Crop"])
class CropViewset(viewsets.ModelViewSet):
    queryset = Crop.objects.all()
    serializer_class = CropSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CropFilterSet

    def get_permissions(self):
        """
        - Any authenticated user can list/retrieve.
        - Only system admin/superuser/superextension/eextension
            can create/update/delete.
        """
        if self.action in ["list", "retrieve"]:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [
                IsSuperExtensionOrEExtension
            ]
        return [permission() for permission in permission_classes]
