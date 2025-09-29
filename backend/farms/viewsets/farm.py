from django.db.models import Q
from drf_spectacular.utils import extend_schema
from farms.filtersets.farm import FarmFilter
from farms.models.farm import Farm
from farms.serializers.farm import FarmSerializer
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.choices import RoleChoices


@extend_schema(tags=["Farms"])
class FarmViewset(viewsets.ModelViewSet):
    queryset = Farm.objects.all()
    serializer_class = FarmSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = FarmFilter

    def get_queryset(self):
        u = self.request.user

        if u.is_superuser or u.role == RoleChoices.SYSTEM_ADMIN:
            return self.queryset.all()

        if u.role == RoleChoices.SUPER_EXTENSION:
            return self.queryset.filter(
                ward__subcounty__county__in=u.counties.all(),
                is_archived=False
            ).distinct()

        if u.role == RoleChoices.E_EXTENSION:
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
