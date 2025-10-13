from app.filtersets.e_extension import EExtensionOfficerFilterSet
from app.models.e_extension import EExtensionOfficer
from app.permissions import CanManageEExtensionOfficer
from app.serializers.e_extension import (
    EExtensionOfficerReadSerializer,
    EExtensionOfficerUpdateSerializer,
    EExtensionOfficerWriteSerializer,
)
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication


@extend_schema(tags=["App - E-Extension Officers"])
class EExtensionOfficerViewset(viewsets.ModelViewSet):
    queryset = EExtensionOfficer.objects.all()
    serializer_class = EExtensionOfficerReadSerializer
    authentication_classes = [TokenAuthentication, JWTAuthentication]
    permission_classes = [CanManageEExtensionOfficer]
    filterset_class = EExtensionOfficerFilterSet

    def get_serializer_class(self):
        """
        Return appropriate serializer class based on action.
        - List/Retrieve: EExtensionOfficerReadSerializer
        - Create: EExtensionOfficerWriteSerializer
        - Update/Partial Update: EExtensionOfficerUpdateSerializer
        """
        if self.action == 'create':
            return EExtensionOfficerWriteSerializer
        elif self.action in ['update', 'partial_update']:
            return EExtensionOfficerUpdateSerializer
        return EExtensionOfficerReadSerializer

    def get_queryset(self):
        """
        Filter E-Extension officers based on user role.

        - System Admin/Superuser: All E-Extension officers
        - Farmers: All E-Extension officers (can see all)
        - E-Extensions: Only themselves
        - Super Extensions: Only their managed E-Extensions
        - Others: None
        """
        u = self.request.user

        if getattr(self, "swagger_fake_view", False):
            return EExtensionOfficer.objects.none()

        # Optimize queries with related data
        base_queryset = self.queryset.select_related(
            'user'
        ).prefetch_related(
            'wards',
            'super_extensions',
            'managed_farms'
        )

        if u.is_superuser or u.is_systemadmin():
            return base_queryset.filter(is_archived=False).distinct()

        # Farmers can see all E-Extension officers
        if u.is_farmer():
            return base_queryset.filter(
                is_archived=False,
                is_visible=True
            ).distinct()

        # E-Extensions can only see themselves
        if u.is_eextension():
            return base_queryset.filter(
                user=u,
                is_archived=False
            ).distinct()

        # Super Extensions can see their managed E-Extensions
        if u.is_superextension():
            super_ext_profile = u.super_extension_users
            return base_queryset.filter(
                super_extensions=super_ext_profile,
                is_archived=False
            ).distinct()

        return EExtensionOfficer.objects.none()

    def create(self, request, *args, **kwargs):  # noqa: ARG002
        """
        Create a new E-Extension officer profile with proper validation.
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
        """Save the E-Extension officer instance."""
        serializer.save()

    def update(self, request, *args, **kwargs):  # noqa: ARG002
        """
        Update an E-Extension officer profile.
        Allows updating: wards, is_visible.
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
        """Partially update an E-Extension officer profile (PATCH)."""
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def perform_update(self, serializer):
        """Save the updated E-Extension officer instance."""
        serializer.save()
