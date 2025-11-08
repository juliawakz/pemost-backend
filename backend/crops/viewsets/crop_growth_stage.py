from users.permissions import IsSystemAdminOrSuperUser
from crops.filterset.crop_growth_stage import CropGrowthStageFilterSet
from crops.models.crop_growth_stage import CropGrowthStage
from crops.serializers.growth_stage import CropGrowthStageSerializer
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated



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
                IsSystemAdminOrSuperUser
            ]
        return [permission() for permission in permission_classes]
