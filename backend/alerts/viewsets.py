from alerts.models import Alert
from alerts.serializers import MiniAlertSerializer, AlertReadSerializer
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication


@extend_schema(tags=["Alerts"])
class AlertViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing and managing alerts.

    Provides:
    - list: Returns a list of alerts using MiniAlertSerializer
    - retrieve: Returns detailed alert information using AlertReadSerializer
    - mark_as_read: Mark a single alert as read (POST)
    - mark_all_as_read: Mark all user's alerts as read (POST)

    Permissions:
    - Authenticated users can view and mark alerts as read
    """
    queryset = Alert.objects.all()
    serializer_class = MiniAlertSerializer
    authentication_classes = [TokenAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['alert_type', 'read', 'farm']

    def get_serializer_class(self):
        """
        Return appropriate serializer based on action.
        - list: MiniAlertSerializer
        - retrieve: AlertReadSerializer
        """
        if self.action == 'retrieve':
            return AlertReadSerializer
        return MiniAlertSerializer

    def get_queryset(self):
        """
        Filter alerts based on user role.

        - System Admin/Superuser: All alerts
        - Farmer: Only alerts for their own farms
        - E-Extension: Alerts for farms they manage
        - Super Extension: Alerts for farms managed by their e-extensions
        """
        user = self.request.user

        if getattr(self, "swagger_fake_view", False):
            return Alert.objects.none()

        # Optimize queries with related data
        base_queryset = self.queryset.select_related(
            'farm',
            'farm__farmer',
            'farm__ward'
        ).filter(is_archived=False).order_by('-created_at')

        # System Admin/Superuser sees all alerts
        if user.is_superuser or user.is_systemadmin():
            return base_queryset

        # Farmer sees only alerts for their own farms
        if user.is_farmer():
            return base_queryset.filter(farm__farmer=user)

        # E-Extension sees alerts for farms they manage
        if user.is_eextension():
            try:
                e_ext_profile = user.e_extension_users
                return base_queryset.filter(
                    farm__e_extensions=e_ext_profile,
                    farm__is_visible=True
                ).distinct()
            except AttributeError:
                return Alert.objects.none()

        # Super Extension sees alerts for farms managed by
        # their e-extensions
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
                return Alert.objects.none()

        return Alert.objects.none()

    @action(detail=True, methods=['post'], url_path='mark-as-read')
    def mark_as_read(self, request, pk=None):
        """
        Mark a single alert as read.
        """
        alert = self.get_object()

        if alert.read:
            return Response(
                {"message": "Alert is already marked as read."},
                status=status.HTTP_200_OK
            )

        alert.read = True
        alert.save()

        return Response(
            {
                "message": "Alert marked as read successfully.",
                "data": MiniAlertSerializer(
                    alert,
                    context={'request': request}
                ).data
            },
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['post'], url_path='mark-all-as-read')
    def mark_all_as_read(self, request):
        """
        Mark all alerts for the current user as read.
        Only marks unread alerts that the user has access to.
        """
        # Get all unread alerts for the current user
        queryset = self.get_queryset().filter(read=False)

        if not queryset.exists():
            return Response(
                {"message": "No unread alerts to mark as read."},
                status=status.HTTP_200_OK
            )

        # Update all unread alerts to read
        updated_count = queryset.update(read=True)

        return Response(
            {
                "message": f"{updated_count} alert(s) marked as read.",
                "count": updated_count
            },
            status=status.HTTP_200_OK
        )
