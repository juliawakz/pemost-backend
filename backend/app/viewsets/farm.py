from app.filtersets.farm import FarmFilterSet
from app.models.farm import Farm
from app.permissions import CanManageFarm
from app.serializers.farm import (
    FarmReadSerializer,
    FarmUpdateSerializer,
    FarmWriteSerializer,
)
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication


@extend_schema(tags=["App - Farms"])
class FarmViewset(viewsets.ModelViewSet):
    queryset = Farm.objects.all()
    serializer_class = FarmReadSerializer
    authentication_classes = [TokenAuthentication, JWTAuthentication]
    permission_classes = [CanManageFarm]
    filter_backends = [DjangoFilterBackend]
    filterset_class = FarmFilterSet

    def get_serializer_class(self):
        """
        Return appropriate serializer class based on action.
        - List/Retrieve: FarmReadSerializer
          (full data with nested objects)
        - Create: FarmWriteSerializer (for creating new farms)
        - Update/Partial Update: FarmUpdateSerializer
          (only name, boundary, user_size)
        """
        if self.action == 'create':
            return FarmWriteSerializer
        elif self.action in ['update', 'partial_update']:
            return FarmUpdateSerializer
        return FarmReadSerializer

    def get_queryset(self):
        """
        Filter farms based on user role and optimize queries.

        - System Admin/Superuser: All farms
        - Super Extension: Farms managed by their E-Extensions
          (where visibility is enabled)
        - E-Extension: Farms they manage (where visibility is enabled)
        - Farmer: Only their own farms
        """
        u = self.request.user

        if getattr(self, "swagger_fake_view", False):
            return Farm.objects.none()

        # Optimize queries with related data
        base_queryset = self.queryset.select_related(
            'user',
            'ward',
            'ward__subcounty',
            'ward__subcounty__county'
        ).prefetch_related('e_extensions')

        if u.is_superuser or u.is_systemadmin():
            return base_queryset.filter(is_archived=False).distinct()

        # Super Extension sees farms managed by their E-Extensions
        if u.is_superextension():
            super_ext_profile = u.super_extension_users
            # Get all E-Extensions managed by this Super Extension
            managed_e_extensions = super_ext_profile.managed_e_extensions.all()
            return base_queryset.filter(
                e_extensions__in=managed_e_extensions,
                is_archived=False,
                is_visible=True
            ).distinct()

        # E-Extension sees farms they manage
        if u.is_eextension():
            e_ext_profile = u.e_extension_users
            return base_queryset.filter(
                e_extensions=e_ext_profile,
                is_archived=False,
                is_visible=True
            ).distinct()

        # Farmers see only their own farms
        if u.is_farmer():
            return base_queryset.filter(
                user=u,
                is_archived=False
            ).distinct()

        return Farm.objects.none()

    def create(self, request, *args, **kwargs):  # noqa: ARG002
        """
        Create a new farm with proper validation.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=self.get_success_headers(serializer.data)
        )

    def perform_create(self, serializer):
        """
        Save the farm instance.
        Can be overridden to add custom logic.
        """
        serializer.save()

    def update(self, request, *args, **kwargs):  # noqa: ARG002
        """
        Update a farm (full update).
        Only name, boundary, and user_size can be updated.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        """
        Partially update a farm (PATCH).
        Only name, boundary, and user_size can be updated.
        """
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def perform_update(self, serializer):
        """
        Save the updated farm instance.
        """
        serializer.save()
