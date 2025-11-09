from app.models.plantation import Plantation
from app.permissions import CanManagePlantation
from app.serializers.plantation import (
    PlantationReadSerializer,
    PlantationWriteSerializer,
)
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Q


@extend_schema(tags=["App - Plantations"])
class PlantationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing plantations.

    Permissions:
    - System Admin/Superuser: Full CRUD on all plantations
    - Farmer: CRUD on their own farm's plantations
    - E-Extension: CRUD on plantations for farms they manage
    - Super Extension: Read-only access to plantations of managed e-extensions
    """
    queryset = Plantation.objects.all()
    serializer_class = PlantationReadSerializer
    authentication_classes = [TokenAuthentication, JWTAuthentication]
    permission_classes = [CanManagePlantation]

    def get_serializer_class(self):
        """
        Return appropriate serializer based on action.
        """
        if self.action in ['create', 'update', 'partial_update']:
            return PlantationWriteSerializer
        return PlantationReadSerializer

    def get_queryset(self):
        """
        Filter plantations based on user role and farm access.

        - System Admin/Superuser: All plantations
        - Farmer: Only their own farm's plantations
        - E-Extension: Plantations for farms they manage
        - Super Extension: Plantations for farms managed by their e-extensions
        """
        user = self.request.user

        if getattr(self, "swagger_fake_view", False):
            return Plantation.objects.none()

        # Optimize queries with related data
        base_queryset = self.queryset.select_related(
            'farm',
            'farm__farmer',
            'farm__ward',
            'crop_variety',
            'crop_variety__crop'
        ).filter(is_archived=False)

        # System Admin/Superuser sees all plantations
        if user.is_superuser or user.is_systemadmin():
            return base_queryset

        # Farmer sees only their own farm's plantations
        if user.is_farmer():
            return base_queryset.filter(farm__farmer=user)

        # E-Extension sees plantations for farms they manage
        if user.is_eextension():
            try:
                e_ext_profile = user.e_extension_users
                return base_queryset.filter(
                    farm__e_extensions=e_ext_profile,
                    farm__is_visible=True
                ).distinct()
            except AttributeError:
                return Plantation.objects.none()

        # Super Extension sees plantations for farms managed by their e-extensions
        if user.is_superextension():
            try:
                super_ext_profile = user.super_extension_users
                managed_e_extensions = super_ext_profile.managed_e_extensions.all()
                return base_queryset.filter(
                    farm__e_extensions__in=managed_e_extensions,
                    farm__is_visible=True
                ).distinct()
            except AttributeError:
                return Plantation.objects.none()

        return Plantation.objects.none()

    def perform_destroy(self, instance):
        """
        Soft delete by archiving instead of hard delete.
        """
        instance.is_archived = True
        instance.save()

    @action(detail=True, methods=['post'], url_path='mark-matured')
    def mark_matured(self, request, pk=None):
        """
        Manually mark a plantation as matured.
        Only accessible by the farm owner, e-extension managing the farm, or admin.
        """
        plantation = self.get_object()

        # Check permissions
        user = request.user
        if not (user.is_superuser or user.is_systemadmin()):
            if user.is_farmer() and plantation.farm.farmer != user:
                return Response(
                    {"message": "You do not have permission to modify this plantation."},
                    status=status.HTTP_403_FORBIDDEN
                )
            elif user.is_eextension():
                try:
                    e_ext_profile = user.e_extension_users
                    if e_ext_profile not in plantation.farm.e_extensions.all():
                        return Response(
                            {"message": "You are not managing this farm."},
                            status=status.HTTP_403_FORBIDDEN
                        )
                except AttributeError:
                    return Response(
                        {"message": "E-Extension profile not found."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

        plantation.is_matured = True
        plantation.save()

        return Response(
            {
                "message": f"Plantation for {plantation.crop_variety.name} has been marked as matured.",
                "data": PlantationReadSerializer(plantation, context={'request': request}).data
            },
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'], url_path='active')
    def active_plantations(self, request):
        """
        Get all active (non-matured) plantations accessible to the user.
        """
        queryset = self.get_queryset().filter(is_matured=False)
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='matured')
    def matured_plantations(self, request):
        """
        Get all matured plantations accessible to the user.
        """
        queryset = self.get_queryset().filter(is_matured=True)
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
