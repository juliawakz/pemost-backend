from django_filters.rest_framework import DjangoFilterBackend
from locations.models.ward import Ward
from locations.serializers.ward import WardSerializer
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from users.permissions.user import IsSystemAdminOrSuperUser


class WardViewSet(viewsets.ModelViewSet):
    queryset = Ward.objects.all().order_by("ward_id")
    serializer_class = WardSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        "ward_id",
        "name",
        "subcounty__county",
        "subcounty__county__name",
        "subcounty",
        "subcounty__name"
    ]  # enable filtering

    def get_permissions(self):
        """
        Any authenticated user can list/retrieve.
        Only system admin/superuser can create/update/delete.
        """
        if self.action in ["list", "retrieve"]:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated, IsSystemAdminOrSuperUser]
        return [permission() for permission in permission_classes]
