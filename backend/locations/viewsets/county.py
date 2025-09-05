from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from locations.models.county import County
from locations.serializers.county import CountySerializer
from users.permissions.user import IsSystemAdminOrSuperUser


class CountyViewSet(viewsets.ModelViewSet):
    queryset = County.objects.all().order_by("county_id")
    serializer_class = CountySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        "county_id",
        "name"
    ]  # enable filtering on county_id and name

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
