from app.choices import WorkRequestStatusChoices
from app.models.work_request import EExtensionWorkRequest, FarmerWorkRequest
from app.permissions import CanManageEExtensionWorkRequest, CanManageFarmerWorkRequest
from app.serializers.work_request import (
    AcceptRejectRequestSerializer,
    EExtensionWorkRequestCreateSerializer,
    EExtensionWorkRequestReadSerializer,
    FarmerWorkRequestCreateSerializer,
    FarmerWorkRequestReadSerializer,
)
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication


@extend_schema(tags=["App - Farmer Work Requests"])
@extend_schema_view(
    list=extend_schema(summary="List farmer work requests"),
    create=extend_schema(summary="Send work request to E-Extension"),
    retrieve=extend_schema(summary="Get work request details"),
)
class FarmerWorkRequestViewset(viewsets.ModelViewSet):
    """
    ViewSet for Farmers to send work requests to E-Extension Officers.

    - Farmers can create requests to E-Extensions
    - E-Extensions can accept/reject requests sent to them
    - Both parties can view their requests
    - Archived requests (accepted/rejected) are not shown
    """
    serializer_class = FarmerWorkRequestReadSerializer
    authentication_classes = [TokenAuthentication, JWTAuthentication]
    permission_classes = [CanManageFarmerWorkRequest]
    http_method_names = ['get', 'post']

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return FarmerWorkRequestCreateSerializer
        return FarmerWorkRequestReadSerializer

    def get_queryset(self):
        """
        Filter work requests based on user role.
        Only show non-archived (pending) requests.
        """
        if getattr(self, 'swagger_fake_view', False):
            return FarmerWorkRequest.objects.none()

        user = self.request.user

        if not user.is_authenticated:
            return FarmerWorkRequest.objects.none()

        if user.is_superuser or user.is_systemadmin():
            return FarmerWorkRequest.objects.filter(
                is_archived=False
            ).select_related('farmer', 'e_extension').order_by('-created_at').distinct()

        # Farmers see their sent requests
        # E-Extensions see requests sent to them
        return FarmerWorkRequest.objects.filter(
            farmer=user
        ).select_related(
            'farmer', 'e_extension'
        ).filter(
            is_archived=False
        ).order_by('-created_at') | FarmerWorkRequest.objects.filter(
            e_extension=user
        ).select_related(
            'farmer', 'e_extension'
        ).filter(
            is_archived=False
        ).order_by('-created_at').distinct()

    @extend_schema(
        summary="Accept work request",
        request=AcceptRejectRequestSerializer,
        responses={200: FarmerWorkRequestReadSerializer}
    )
    @action(detail=True, methods=['post'], url_path='accept')
    def accept_request(self, request, pk=None):  # noqa: ARG002
        """
        Accept a work request (E-Extension only).
        Establishes the relationship between Farmer and E-Extension.
        Archives the request after acceptance.
        """
        work_request = self.get_object()

        # Only the recipient can accept
        if work_request.e_extension != request.user:
            return Response(
                {"detail": "Only the E-Extension officer can "
                           "accept this request."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Check if already accepted/rejected
        if work_request.status != WorkRequestStatusChoices.PENDING:
            return Response(
                {"detail": f"This request has already been "
                           f"{work_request.status.lower()}."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = AcceptRejectRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        work_request.accept(
            response_message=serializer.validated_data.get('response_message')
        )

        return Response(
            self.get_serializer(work_request).data,
            status=status.HTTP_200_OK
        )

    @extend_schema(
        summary="Reject work request",
        request=AcceptRejectRequestSerializer,
        responses={200: FarmerWorkRequestReadSerializer}
    )
    @action(detail=True, methods=['post'], url_path='reject')
    def reject_request(self, request, pk=None):  # noqa: ARG002
        """
        Reject a work request (E-Extension only).
        Archives the request after rejection.
        """
        work_request = self.get_object()

        # Only the recipient can reject
        if work_request.e_extension != request.user:
            return Response(
                {"detail": "Only the E-Extension officer can "
                           "reject this request."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Check if already accepted/rejected
        if work_request.status != WorkRequestStatusChoices.PENDING:
            return Response(
                {"detail": f"This request has already been "
                           f"{work_request.status.lower()}."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = AcceptRejectRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        work_request.reject(
            response_message=serializer.validated_data.get('response_message')
        )

        return Response(
            self.get_serializer(work_request).data,
            status=status.HTTP_200_OK
        )


@extend_schema(tags=["App - E-Extension Work Requests"])
@extend_schema_view(
    list=extend_schema(summary="List E-Extension work requests"),
    create=extend_schema(summary="Send work request to Super Extension"),
    retrieve=extend_schema(summary="Get work request details"),
)
class EExtensionWorkRequestViewset(viewsets.ModelViewSet):
    """
    ViewSet for E-Extension Officers to send work requests to
    Super Extension Officers.

    - E-Extensions can create requests to Super Extensions
    - Super Extensions can accept/reject requests sent to them
    - Both parties can view their requests
    - Archived requests (accepted/rejected) are not shown
    """
    serializer_class = EExtensionWorkRequestReadSerializer
    authentication_classes = [TokenAuthentication, JWTAuthentication]
    permission_classes = [CanManageEExtensionWorkRequest]
    http_method_names = ['get', 'post']

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return EExtensionWorkRequestCreateSerializer
        return EExtensionWorkRequestReadSerializer

    def get_queryset(self):
        """
        Filter work requests based on user role.
        Only show non-archived (pending) requests.
        """
        if getattr(self, 'swagger_fake_view', False):
            return EExtensionWorkRequest.objects.none()

        user = self.request.user

        if not user.is_authenticated:
            return EExtensionWorkRequest.objects.none()

        if user.is_superuser or user.is_systemadmin():
            return EExtensionWorkRequest.objects.filter(
                is_archived=False
            ).select_related(
                'e_extension', 'super_extension'
            ).order_by('-created_at').distinct()

        # E-Extensions see their sent requests
        # Super Extensions see requests sent to them
        return EExtensionWorkRequest.objects.filter(
            e_extension=user
        ).select_related(
            'e_extension', 'super_extension'
        ).filter(
            is_archived=False
        ).order_by('-created_at') | EExtensionWorkRequest.objects.filter(
            super_extension=user
        ).select_related(
            'e_extension', 'super_extension'
        ).filter(
            is_archived=False
        ).order_by('-created_at').distinct()

    @extend_schema(
        summary="Accept work request",
        request=AcceptRejectRequestSerializer,
        responses={200: EExtensionWorkRequestReadSerializer}
    )
    @action(detail=True, methods=['post'], url_path='accept')
    def accept_request(self, request, pk=None):  # noqa: ARG002
        """
        Accept a work request (Super Extension only).
        Establishes the relationship between E-Extension and
        Super Extension.
        Archives the request after acceptance.
        """
        work_request = self.get_object()

        # Only the recipient can accept
        if work_request.super_extension != request.user:
            return Response(
                {"detail": "Only the Super Extension officer can "
                           "accept this request."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Check if already accepted/rejected
        if work_request.status != WorkRequestStatusChoices.PENDING:
            return Response(
                {"detail": f"This request has already been "
                           f"{work_request.status.lower()}."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = AcceptRejectRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        work_request.accept(
            response_message=serializer.validated_data.get('response_message')
        )

        return Response(
            self.get_serializer(work_request).data,
            status=status.HTTP_200_OK
        )

    @extend_schema(
        summary="Reject work request",
        request=AcceptRejectRequestSerializer,
        responses={200: EExtensionWorkRequestReadSerializer}
    )
    @action(detail=True, methods=['post'], url_path='reject')
    def reject_request(self, request, pk=None):  # noqa: ARG002
        """
        Reject a work request (Super Extension only).
        Archives the request after rejection.
        """
        work_request = self.get_object()

        # Only the recipient can reject
        if work_request.super_extension != request.user:
            return Response(
                {"detail": "Only the Super Extension officer can "
                           "reject this request."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Check if already accepted/rejected
        if work_request.status != WorkRequestStatusChoices.PENDING:
            return Response(
                {"detail": f"This request has already been "
                           f"{work_request.status.lower()}."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = AcceptRejectRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        work_request.reject(
            response_message=serializer.validated_data.get('response_message')
        )

        return Response(
            self.get_serializer(work_request).data,
            status=status.HTTP_200_OK
        )
