from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from locations.filterset.subcounty import SubCountyFilter
from locations.models.subcounty import SubCounty
from locations.serializers.subcounty import SubCountySerializer
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from users.permissions import IsSystemAdminOrSuperUser


@extend_schema(tags=["Locations - Subcounties"])
class SubCountyViewSet(viewsets.ModelViewSet):
    queryset = SubCounty.objects.all().order_by("subcounty_id")
    serializer_class = SubCountySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = SubCountyFilter

    def get_permissions(self):
        """
        Any authenticated user can list/retrieve.
        Only system admin/superuser can create/update/delete.
        """
        if self.action in ["list", "retrieve"]:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsSystemAdminOrSuperUser]
        return [permission() for permission in permission_classes]
