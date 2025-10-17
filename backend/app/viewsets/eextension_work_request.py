from app.choices import WorkRequestStatusChoices
from app.models.eextension_work_request import EExtensionWorkRequest
from app.permissions import CanManageEExtensionWorkRequest
from app.serializers.eextension_work_request import (
    AcceptRejectRequestSerializer,
    EExtensionWorkRequestCreateSerializer,
    EExtensionWorkRequestReadSerializer,
)
from django.db.models import Q
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication


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
            return EExtensionWorkRequest.objects.select_related(
                'e_extension', 'super_extension'
            ).order_by('-created_at').distinct()

        # E-Extensions see their sent requests
        # Super Extensions see requests sent to them
        return (
            EExtensionWorkRequest.objects.filter(
                Q(super_extension__user=user) | Q(e_extension__user=user)
            )
            .select_related('e_extension', 'super_extension')
            .order_by('-created_at')
            .distinct()
        )

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
        if work_request.super_extension.user != request.user:
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
    summary="Reject/Accept work request",
    request=AcceptRejectRequestSerializer,
    responses={200: EExtensionWorkRequestReadSerializer}
)
@action(detail=True, methods=['post'], url_path="accept/reject")
class AcceptRejectEExtensionWorkRequestView(CreateAPIView):
    """
    Accept or reject a work request (Super-Extension only).
    Establishes the relationship between Super-Extension and E-Extension.
    Archives the request after acceptance.
    """
    serializer_class = AcceptRejectRequestSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        work_request_id = serializer.validated_data["work_request"].id
        status_action = serializer.validated_data["status"]
        response_message = serializer.validated_data["response_message"]

        work_request = EExtensionWorkRequest.objects.filter(
            id=work_request_id).first()

        if not work_request:
            return Response(
                {"message": "Work request not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Accept or reject the request
        if status_action.lower() == "accept":
            work_request.accept(response_message=response_message)
        else:
            work_request.reject(response_message=response_message)

        read_serializer = EExtensionWorkRequestReadSerializer(work_request)
        return Response(read_serializer.data, status=status.HTTP_200_OK)
