from app.filtersets.agrodealer import AgrodealerFilterSet
from app.models.agrodealer import Agrodealer
from app.permissions import CanManageAgrodealer
from app.serializers.agrodealer import (
    AgrodealerReadSerializer,
    AgrodealerUpdateSerializer,
    AgrodealerWriteSerializer,
)
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication


@extend_schema(tags=["App - Agrodealers"])
class AgrodealerViewset(viewsets.ModelViewSet):
    queryset = Agrodealer.objects.all()
    serializer_class = AgrodealerReadSerializer
    authentication_classes = [TokenAuthentication, JWTAuthentication]
    permission_classes = [CanManageAgrodealer]
    filterset_class = AgrodealerFilterSet

    def get_serializer_class(self):
        """
        Return appropriate serializer class based on action.
        - List/Retrieve: AgrodealerReadSerializer
        - Create: AgrodealerWriteSerializer
        - Update/Partial Update: AgrodealerUpdateSerializer
        """
        if self.action == 'create':
            return AgrodealerWriteSerializer
        elif self.action in ['update', 'partial_update']:
            return AgrodealerUpdateSerializer
        return AgrodealerReadSerializer

    def get_queryset(self):
        """
        Filter agrodealers based on user role.

        - System Admin/Superuser: All agrodealers
        - Farmers: All agrodealers (can see all)
        - Agrodealers: Only themselves
        - Others: None
        """
        u = self.request.user

        if getattr(self, "swagger_fake_view", False):
            return Agrodealer.objects.none()

        # Optimize queries with related data
        base_queryset = self.queryset.select_related(
            'user',
            'ward',
            'ward__subcounty',
            'ward__subcounty__county'
        )

        if u.is_superuser or u.is_systemadmin():
            return base_queryset.filter(is_archived=False).distinct()

        # Farmers can see all agrodealers
        if u.is_farmer():
            return base_queryset.filter(
                is_archived=False,
                is_visible=True
            ).distinct()

        # Agrodealers can only see themselves
        if u.is_agrodealer():
            return base_queryset.filter(
                user=u,
                is_archived=False
            ).distinct()

        return Agrodealer.objects.none()

    def create(self, request, *args, **kwargs):  # noqa: ARG002
        """
        Create a new agrodealer profile with proper validation.
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
        """Save the agrodealer instance."""
        serializer.save()

    def update(self, request, *args, **kwargs):  # noqa: ARG002
        """
        Update an agrodealer profile.
        Allows updating: name, ward, location, is_visible.
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
        """Partially update an agrodealer profile (PATCH)."""
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def perform_update(self, serializer):
        """Save the updated agrodealer instance."""
        serializer.save()
