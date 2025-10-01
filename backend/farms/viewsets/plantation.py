from django.db.models import Q
from users.permissions.user import IsSuperExtensionOrEExtension
from drf_spectacular.utils import extend_schema
from django_filters.rest_framework import DjangoFilterBackend
from farms.filtersets.farm import FarmFilterSet
from farms.models.plantation import Plantation
from farms.serializers.plantation import PlantationSerializer
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


@extend_schema(tags=["Plantation"])
class PlatationViewset(viewsets.ModelViewSet):
    queryset = Plantation.objects.all()
    serializer_class = PlantationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        u = self.request.user

        if u.is_superuser or u.is_system_admin():
            return self.queryset.all()

        if u.is_super_extension():
            return self.queryset.filter(
                farm__ward__subcounty__county__in=u.counties.all(),
                is_archived=False
            ).distinct()

        if u.is_e_extension():
            return self.queryset.filter(
                farm__ward__in=u.wards.all(),
                is_archived=False
            ).distinct()

        return self.queryset.filter(
            Q(farm__owner=u),
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
