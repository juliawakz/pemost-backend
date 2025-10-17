from app.models.farmer_work_request import FarmerWorkRequest
from app.permissions import CanManageFarmerWorkRequest
from app.serializers.farmer_work_request import (
    AcceptRejectRequestSerializer,
    FarmerWorkRequestCreateSerializer,
    FarmerWorkRequestReadSerializer,
)
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView
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
        Only show non-archived (pending or active) requests by default.
        """
        if getattr(self, 'swagger_fake_view', False):
            return FarmerWorkRequest.objects.none()

        user = self.request.user

        if not user.is_authenticated:
            return FarmerWorkRequest.objects.none()

        base_qs = (
            FarmerWorkRequest.objects
            .prefetch_related("farms")
            .select_related("e_extension")
            .order_by("-created_at")
            .distinct()
        )

        # System Admins / Superusers
        if user.is_superuser or getattr(
                user, "is_systemadmin", lambda: False)():
            return base_qs

        # E-Extension Officers
        if getattr(user, "is_eextension", lambda: False)():
            return base_qs.filter(e_extension__user=user)

        # Farmers
        # A farmer can see requests for any of their farms
        if hasattr(user, "farm_users"):
            return base_qs.filter(farms__user=user)

        # Default
        return FarmerWorkRequest.objects.none()


@extend_schema(tags=["App - Farmer Work Requests"])
@extend_schema(
    summary="Accept/Reject farm work request",
    request=AcceptRejectRequestSerializer,
    responses={200: FarmerWorkRequestReadSerializer}
)
@action(detail=True, methods=['post'], url_path="accept/reject")
class AcceptRejectFarmWorkRequestView(CreateAPIView):
    """
    Accept or reject a work request (E-Extension only).
    Establishes the relationship between Farmer and E-Extension.
    Archives the request after acceptance.
    """
    serializer_class = AcceptRejectRequestSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        work_request_id = serializer.validated_data["work_request"].id
        status_action = serializer.validated_data["status"]
        response_message = serializer.validated_data["response_message"]

        work_request = FarmerWorkRequest.objects.filter(
            id=work_request_id).first()
        if not work_request:
            return Response(
                {"detail": "Work request not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Accept or reject the request
        if status_action.lower() == "accept":
            work_request.accept(response_message=response_message)
        else:
            work_request.reject(response_message=response_message)

        read_serializer = FarmerWorkRequestReadSerializer(work_request)
        return Response(read_serializer.data, status=status.HTTP_200_OK)
