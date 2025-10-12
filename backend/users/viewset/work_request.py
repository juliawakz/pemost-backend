from django.contrib.auth import get_user_model
from django.db.models import Q
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.models import (
    EExtensionWorkRequest,
    FarmerWorkRequest
)
from users.choices import WorkRequestStatusChoices
from users.serializers.work_request import (
    EExtensionWorkRequestSerializer,
    FarmerWorkRequestSerializer,
    AcceptRejectRequestSerializer,
)
from users.permissions.user import CanManageWorkRequest

User = get_user_model()


@extend_schema(tags=["Work Requests - E-Extension to Super Extension"])
@extend_schema_view(
    list=extend_schema(summary="List E-Extension work requests"),
    create=extend_schema(summary="Send work request to Super Extension"),
    retrieve=extend_schema(summary="Get work request details"),
)
class EExtensionWorkRequestViewSet(viewsets.ModelViewSet):
    """
    ViewSet for E-Extension Officers to send work requests to Super Extension Officers.

    - E-Extensions can create requests to Super Extensions in their county
    - Super Extensions can accept/reject requests sent to them
    - Both parties can view their requests
    """
    serializer_class = EExtensionWorkRequestSerializer
    permission_classes = [IsAuthenticated, CanManageWorkRequest]
    http_method_names = ['get', 'post', 'patch']

    def get_queryset(self):
        # Handle swagger/schema generation
        if getattr(self, 'swagger_fake_view', False):
            return EExtensionWorkRequest.objects.none()

        user = self.request.user

        # Check if user is authenticated
        if not user.is_authenticated:
            return EExtensionWorkRequest.objects.none()

        if user.is_superuser or user.is_systemadmin():
            return EExtensionWorkRequest.objects.all()

        # E-Extensions see their sent requests
        # Super Extensions see requests sent to them
        return EExtensionWorkRequest.objects.filter(
            Q(e_extension=user) | Q(super_extension=user)
        ).select_related('e_extension', 'super_extension').order_by('-created_at')

    @extend_schema(
        summary="Accept work request",
        request=AcceptRejectRequestSerializer,
        responses={200: EExtensionWorkRequestSerializer}
    )
    @action(detail=True, methods=['post'], url_path='accept')
    def accept_request(self, request, pk=None):
        """
        Accept a work request (Super Extension only).
        Establishes the relationship between E-Extension and Super Extension.
        """
        work_request = self.get_object()

        # Only the recipient can accept
        if work_request.super_extension != request.user:
            return Response(
                {"detail": "Only the Super Extension officer can accept this request."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Check if already accepted/rejected
        if work_request.status != WorkRequestStatusChoices.PENDING:
            return Response(
                {"detail": f"This request has already been {work_request.status.lower()}."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = AcceptRejectRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        work_request.accept(response_message=serializer.validated_data.get('response_message'))

        return Response(
            self.get_serializer(work_request).data,
            status=status.HTTP_200_OK
        )

    @extend_schema(
        summary="Reject work request",
        request=AcceptRejectRequestSerializer,
        responses={200: EExtensionWorkRequestSerializer}
    )
    @action(detail=True, methods=['post'], url_path='reject')
    def reject_request(self, request, pk=None):
        """
        Reject a work request (Super Extension only).
        """
        work_request = self.get_object()

        # Only the recipient can reject
        if work_request.super_extension != request.user:
            return Response(
                {"detail": "Only the Super Extension officer can reject this request."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Check if already accepted/rejected
        if work_request.status != WorkRequestStatusChoices.PENDING:
            return Response(
                {"detail": f"This request has already been {work_request.status.lower()}."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = AcceptRejectRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        work_request.reject(response_message=serializer.validated_data.get('response_message'))

        return Response(
            self.get_serializer(work_request).data,
            status=status.HTTP_200_OK
        )


@extend_schema(tags=["Work Requests - Farmer to E-Extension"])
@extend_schema_view(
    list=extend_schema(summary="List Farmer work requests"),
    create=extend_schema(summary="Send work request to E-Extension"),
    retrieve=extend_schema(summary="Get work request details"),
)
class FarmerWorkRequestViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Farmers to send work requests to E-Extension Officers.

    - Farmers can create requests to E-Extensions
    - E-Extensions can accept/reject requests sent to them
    - Both parties can view their requests
    """
    serializer_class = FarmerWorkRequestSerializer
    permission_classes = [IsAuthenticated, CanManageWorkRequest]
    http_method_names = ['get', 'post', 'patch']

    def get_queryset(self):
        # Handle swagger/schema generation
        if getattr(self, 'swagger_fake_view', False):
            return FarmerWorkRequest.objects.none()

        user = self.request.user

        # Check if user is authenticated
        if not user.is_authenticated:
            return FarmerWorkRequest.objects.none()

        if user.is_superuser or user.is_systemadmin():
            return FarmerWorkRequest.objects.all()

        # Farmers see their sent requests
        # E-Extensions see requests sent to them
        return FarmerWorkRequest.objects.filter(
            Q(farmer=user) | Q(e_extension=user)
        ).select_related('farmer', 'e_extension').order_by('-created_at')

    @extend_schema(
        summary="Accept work request",
        request=AcceptRejectRequestSerializer,
        responses={200: FarmerWorkRequestSerializer}
    )
    @action(detail=True, methods=['post'], url_path='accept')
    def accept_request(self, request, pk=None):
        """
        Accept a work request (E-Extension only).
        Establishes the relationship between Farmer and E-Extension.
        """
        work_request = self.get_object()

        # Only the recipient can accept
        if work_request.e_extension != request.user:
            return Response(
                {"detail": "Only the E-Extension officer can accept this request."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Check if already accepted/rejected
        if work_request.status != WorkRequestStatusChoices.PENDING:
            return Response(
                {"detail": f"This request has already been {work_request.status.lower()}."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = AcceptRejectRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        work_request.accept(response_message=serializer.validated_data.get('response_message'))

        return Response(
            self.get_serializer(work_request).data,
            status=status.HTTP_200_OK
        )

    @extend_schema(
        summary="Reject work request",
        request=AcceptRejectRequestSerializer,
        responses={200: FarmerWorkRequestSerializer}
    )
    @action(detail=True, methods=['post'], url_path='reject')
    def reject_request(self, request, pk=None):
        """
        Reject a work request (E-Extension only).
        """
        work_request = self.get_object()

        # Only the recipient can reject
        if work_request.e_extension != request.user:
            return Response(
                {"detail": "Only the E-Extension officer can reject this request."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Check if already accepted/rejected
        if work_request.status != WorkRequestStatusChoices.PENDING:
            return Response(
                {"detail": f"This request has already been {work_request.status.lower()}."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = AcceptRejectRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        work_request.reject(response_message=serializer.validated_data.get('response_message'))

        return Response(
            self.get_serializer(work_request).data,
            status=status.HTTP_200_OK
        )
