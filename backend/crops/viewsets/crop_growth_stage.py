from drf_spectacular.utils import extend_schema
from crops.models.crop_growth_stage import CropGrowthStage
from crops.serializers.growth_stage import CropGrowthStageSerializer
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from users.permissions.user import \
    IsSuperExtensionOrEExtension
from crops.filterset.crop_growth_stage import CropGrowthStageFilterSet


@extend_schema(tags=["Crop Growth Stages"])
class CropGrowthStageViewset(viewsets.ModelViewSet):
    queryset = CropGrowthStage.objects.all()
    serializer_class = CropGrowthStageSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CropGrowthStageFilterSet

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
