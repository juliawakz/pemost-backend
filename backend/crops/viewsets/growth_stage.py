from drf_spectacular.utils import extend_schema
from crops.models.growth_stage import GrowthStage
from crops.serializers.growth_stage import GrowthStageSerializer
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from users.permissions.user import \
    IsSuperExtensionOrEExtension
from crops.filterset.growth_stage import GrowthStageFilterSet


@extend_schema(tags=["Growth Stages"])
class GrowthStageViewset(viewsets.ModelViewSet):
    queryset = GrowthStage.objects.all()
    serializer_class = GrowthStageSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = GrowthStageFilterSet

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
