from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from locations.filterset.county import CountyFilter
from locations.models.county import County
from locations.serializers.county import CountySerializer
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from users.permissions.user import IsSystemAdminOrSuperUser


@extend_schema(tags=["Locations - Counties"])
class CountyViewSet(viewsets.ModelViewSet):
    queryset = County.objects.all().order_by("county_id")
    serializer_class = CountySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CountyFilter

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
