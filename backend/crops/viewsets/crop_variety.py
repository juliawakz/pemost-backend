from drf_spectacular.utils import extend_schema
from crops.models.crop_variety import CropVariety
from crops.serializers.crop_variety import CropVarietySerializer
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from users.permissions.user import \
    IsSuperExtensionOrEExtension
from crops.filterset.crop_variety import CropVarietyFilterSet


@extend_schema(tags=["Crop Varieties"])
class CropVarietyViewset(viewsets.ModelViewSet):
    queryset = CropVariety.objects.all()
    serializer_class = CropVarietySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CropVarietyFilterSet

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
                IsAuthenticated,
                IsSuperExtensionOrEExtension
            ]
        return [permission() for permission in permission_classes]
