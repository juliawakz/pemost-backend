from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from users.models import ApiKey
from users.serializers.api_key import ApiKeySerializer, ApiKeyCreateSerializer
from users.permissions.user import CanGenerateApiKey


@extend_schema(tags=["API Keys"])
@extend_schema_view(
    list=extend_schema(summary="List API keys"),
    create=extend_schema(summary="Generate new API key"),
    retrieve=extend_schema(summary="Get API key details"),
    destroy=extend_schema(summary="Revoke API key"),
)
class ApiKeyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Superadmin to manage API keys.

    - Only Superadmin can generate and manage API keys
    - Keys are shown in full only at creation time
    - Keys can be activated/deactivated
    """
    serializer_class = ApiKeySerializer
    permission_classes = [CanGenerateApiKey]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        # Handle swagger/schema generation
        if getattr(self, 'swagger_fake_view', False):
            return ApiKey.objects.none()

        user = self.request.user

        # Check if user is authenticated
        if not user.is_authenticated:
            return ApiKey.objects.none()

        # Superadmins see only their own keys
        if user.is_superadmin():
            return ApiKey.objects.filter(user=user).order_by('-created_at')

        # Superusers see all keys
        if user.is_superuser:
            return ApiKey.objects.all().order_by('-created_at')

        return ApiKey.objects.none()

    def get_serializer_class(self):
        if self.action == 'create':
            return ApiKeyCreateSerializer
        return ApiKeySerializer

    @extend_schema(
        summary="Revoke API key",
        responses={204: None}
    )
    def destroy(self, request, *args, **kwargs):
        """
        Revoke (delete) an API key.
        """
        instance = self.get_object()

        # Only the owner or superuser can revoke
        if instance.user != request.user and not request.user.is_superuser:
            return Response(
                {"detail": "You can only revoke your own API keys."},
                status=status.HTTP_403_FORBIDDEN
            )

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        summary="Deactivate API key",
        responses={200: ApiKeySerializer}
    )
    @action(detail=True, methods=['post'], url_path='deactivate')
    def deactivate(self, request, pk=None):
        """
        Deactivate an API key without deleting it.
        """
        api_key = self.get_object()

        # Only the owner or superuser can deactivate
        if api_key.user != request.user and not request.user.is_superuser:
            return Response(
                {"detail": "You can only deactivate your own API keys."},
                status=status.HTTP_403_FORBIDDEN
            )

        if not api_key.is_active:
            return Response(
                {"detail": "This API key is already inactive."},
                status=status.HTTP_400_BAD_REQUEST
            )

        api_key.is_active = False
        api_key.save(update_fields=['is_active'])

        return Response(
            self.get_serializer(api_key).data,
            status=status.HTTP_200_OK
        )

    @extend_schema(
        summary="Reactivate API key",
        responses={200: ApiKeySerializer}
    )
    @action(detail=True, methods=['post'], url_path='reactivate')
    def reactivate(self, request, pk=None):
        """
        Reactivate a previously deactivated API key.
        """
        api_key = self.get_object()

        # Only the owner or superuser can reactivate
        if api_key.user != request.user and not request.user.is_superuser:
            return Response(
                {"detail": "You can only reactivate your own API keys."},
                status=status.HTTP_403_FORBIDDEN
            )

        if api_key.is_active:
            return Response(
                {"detail": "This API key is already active."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if not expired
        if not api_key.is_valid():
            return Response(
                {"detail": "Cannot reactivate an expired API key."},
                status=status.HTTP_400_BAD_REQUEST
            )

        api_key.is_active = True
        api_key.save(update_fields=['is_active'])

        return Response(
            self.get_serializer(api_key).data,
            status=status.HTTP_200_OK
        )
