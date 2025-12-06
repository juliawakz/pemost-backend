from django.db import models
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from pest_control.models.pest_report import PestReport
from pest_control.serializers.pest_report import (
    MiniPestReportSerializer,
    PestReportReadSerializer,
    PestReportWriteSerializer
)
from rest_framework import filters, status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication


@extend_schema(tags=["Pest Control"])
class PestReportViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing pest reports.

    Provides full CRUD operations for pest reports.
    Users can report pests they observe in the field.

    Permissions:
    - Authenticated users (except agrodealers) can create reports
    - Users can view all reports or filter by various criteria
    """
    queryset = PestReport.objects.all()
    serializer_class = MiniPestReportSerializer
    authentication_classes = [TokenAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_fields = ['pest', 'farm', 'user']
    search_fields = ['pest__name', 'pest__scientific_name', 'farm__name']
    ordering_fields = ['created_at', 'no_of_pests']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """
        Return appropriate serializer based on action.
        - create/update: PestReportWriteSerializer
        - retrieve: PestReportReadSerializer
        - list: MiniPestReportSerializer
        """
        if self.action in ['create', 'update', 'partial_update']:
            return PestReportWriteSerializer
        elif self.action == 'retrieve':
            return PestReportReadSerializer
        return MiniPestReportSerializer

    def get_queryset(self):
        """
        Filter pest reports based on user role.

        - System Admin/Superuser: All reports
        - Farmer: Reports for their farms + their own reports
        - E-Extension: Reports for farms they manage
        - Super Extension: Reports for farms managed by their e-extensions
        - Agrodealer: No access to reports
        """
        user = self.request.user

        if getattr(self, "swagger_fake_view", False):
            return PestReport.objects.none()

        # Optimize queries with related data
        base_queryset = self.queryset.select_related(
            'pest',
            'farm',
            'farm__farmer',
            'user'
        ).filter(is_archived=False).order_by('-created_at')

        # System Admin/Superuser sees all reports
        if user.is_superuser or user.is_systemadmin():
            return base_queryset

        # Agrodealers cannot access pest reports
        if user.is_agrodealer():
            return PestReport.objects.none()

        # Farmer sees reports for their farms and their own reports
        if user.is_farmer():
            return base_queryset.filter(
                models.Q(farm__farmer=user) | models.Q(user=user)
            ).distinct()

        # E-Extension sees reports for farms they manage
        if user.is_eextension():
            try:
                e_ext_profile = user.e_extension_users
                return base_queryset.filter(
                    farm__e_extensions=e_ext_profile,
                    farm__is_visible=True
                ).distinct()
            except AttributeError:
                return PestReport.objects.none()

        # Super Extension sees reports for farms managed
        # by their e-extensions
        if user.is_superextension():
            try:
                super_ext_profile = user.super_extension_users
                managed_e_extensions = (
                    super_ext_profile.managed_e_extensions.all()
                )
                return base_queryset.filter(
                    farm__e_extensions__in=managed_e_extensions,
                    farm__is_visible=True
                ).distinct()
            except AttributeError:
                return PestReport.objects.none()

        return PestReport.objects.none()

    def perform_create(self, serializer):
        """
        Automatically set the user to the current authenticated user.
        """
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'], url_path='my-reports')
    def my_reports(self, request):
        """
        Get all pest reports submitted by the current user.
        """
        reports = self.get_queryset().filter(user=request.user)
        serializer = self.get_serializer(reports, many=True)

        return Response(
            {
                "count": reports.count(),
                "results": serializer.data
            },
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'], url_path='by-pest/(?P<pest_id>[^/.]+)')
    def by_pest(self, request, pest_id=None):
        """
        Get all pest reports for a specific pest.
        """
        reports = self.get_queryset().filter(pest__id=pest_id)

        if not reports.exists():
            return Response(
                {"message": "No reports found for this pest."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(reports, many=True)

        return Response(
            {
                "count": reports.count(),
                "results": serializer.data
            },
            status=status.HTTP_200_OK
        )
