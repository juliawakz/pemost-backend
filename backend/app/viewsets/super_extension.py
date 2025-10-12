from drf_spectacular.utils import extend_schema
from app.models.super_extension import SuperExtensionOfficer
from app.permissions import CanManageSuperExtensionOfficer
from app.serializers.super_extension import (
    SuperExtensionOfficerReadSerializer,
    SuperExtensionOfficerWriteSerializer,
    SuperExtensionOfficerUpdateSerializer
)
from app.filtersets.super_extension import SuperExtensionOfficerFilterSet
from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication


@extend_schema(tags=["App - Super Extension Officers"])
class SuperExtensionOfficerViewset(viewsets.ModelViewSet):
    queryset = SuperExtensionOfficer.objects.all()
    serializer_class = SuperExtensionOfficerReadSerializer
    authentication_classes = [TokenAuthentication, JWTAuthentication]
    permission_classes = [CanManageSuperExtensionOfficer]
    filterset_class = SuperExtensionOfficerFilterSet

    def get_serializer_class(self):
        """
        Return appropriate serializer class based on action.
        - List/Retrieve: SuperExtensionOfficerReadSerializer
        - Create: SuperExtensionOfficerWriteSerializer
        - Update/Partial Update: SuperExtensionOfficerUpdateSerializer
        """
        if self.action == 'create':
            return SuperExtensionOfficerWriteSerializer
        elif self.action in ['update', 'partial_update']:
            return SuperExtensionOfficerUpdateSerializer
        return SuperExtensionOfficerReadSerializer

    def get_queryset(self):
        """
        Filter Super Extension officers based on user role.

        - System Admin/Superuser: All Super Extension officers
        - E-Extensions: All Super Extension officers (can see all)
        - Super Extensions: Only themselves
        - Others: None
        """
        u = self.request.user

        if getattr(self, "swagger_fake_view", False):
            return SuperExtensionOfficer.objects.none()

        # Optimize queries with related data
        base_queryset = self.queryset.select_related(
            'user'
        ).prefetch_related(
            'counties',
            'managed_e_extensions'
        )

        if u.is_superuser or u.is_systemadmin():
            return base_queryset.filter(is_archived=False)

        # E-Extensions can see all Super Extension officers
        if u.is_eextension():
            return base_queryset.filter(
                is_archived=False
            )

        # Super Extensions can only see themselves
        if u.is_superextension():
            return base_queryset.filter(
                user=u,
                is_archived=False
            )

        return SuperExtensionOfficer.objects.none()

    def create(self, request, *args, **kwargs):  # noqa: ARG002
        """
        Create a new Super Extension officer profile.
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
        """Save the Super Extension officer instance."""
        serializer.save()

    def update(self, request, *args, **kwargs):  # noqa: ARG002
        """
        Update a Super Extension officer profile.
        Allows updating: counties.
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
        """Partially update a Super Extension officer profile (PATCH)."""
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def perform_update(self, serializer):
        """Save the updated Super Extension officer instance."""
        serializer.save()
