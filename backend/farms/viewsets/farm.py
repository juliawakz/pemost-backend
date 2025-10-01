from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from farms.filtersets.farm import FarmFilterSet
from farms.models.farm import Farm
from farms.serializers.farm import FarmSerializer
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.permissions.user import\
    IsSuperExtensionOrEExtension, IsSystemAdminOrSuperUser


@extend_schema(tags=["Farm"])
class FarmViewset(viewsets.ModelViewSet):
    queryset = Farm.objects.all()
    serializer_class = FarmSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = FarmFilterSet

    def get_queryset(self):
        u = self.request.user

        if u.is_superuser or u.is_system_admin():
            return self.queryset.all()

        if u.is_super_extension():
            return self.queryset.filter(
                ward__subcounty__county__in=u.counties.all(),
                is_archived=False
            ).distinct()

        if u.is_e_extension():
            return self.queryset.filter(
                ward__in=u.wards.all(),
                is_archived=False
            ).distinct()

        return self.queryset.filter(
            Q(owner=u),
            is_archived=False
        )

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid()
        if serializer.is_valid():
            self.perform_create(serializer)
            data = serializer.data
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
                headers=self.get_success_headers(data),
            )
        else:
            return Response(
                serializer.errors,
                status.HTTP_400_BAD_REQUEST
            )

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
