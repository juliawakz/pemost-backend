from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from fcm_django.models import FCMDevice
from notifications.filterset import NotificationFilterSet
from notifications.models import Notification
from notifications.serializers import (
    FCMDeviceSerializer,
    NotificationSerializer
)
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from firebase_admin.messaging import Message
from firebase_admin.messaging import Notification as FCMNotification


@extend_schema(tags=["Notifications"])
class NotificationViewSet(viewsets.ModelViewSet):
    """
    Users can fetch their notifications.
    Only update allowed is marking as read (via custom actions).
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = NotificationFilterSet
    queryset = Notification.objects.all()

    def get_queryset(self):
        u = self.request.user

        if getattr(self, "swagger_fake_view", False):
            return Notification.objects.none()

        if u.is_superuser or u.is_systemadmin():
            return self.queryset.distinct()
        return self.queryset.filter(message_to=u)

    # Disable DELETE
    def destroy(self, request, *args, **kwargs):
        return Response(
            {"detail": "Deleting notifications is not allowed."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    # Disable PATCH
    def partial_update(self, request, *args, **kwargs):
        return Response(
            {"detail": "Partial update is not allowed."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    # Optional: also disable full PUT updates if you don’t want them
    def update(self, request, *args, **kwargs):
        return Response(
            {"detail": "Direct update is not allowed."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    @action(detail=True, methods=["post"], url_path="mark-as-read")
    def mark_as_read(self, request, pk=None):
        """Mark a single notification as read"""
        notification = self.get_object()
        if not notification.is_read:
            notification.is_read = True
            notification.save(update_fields=["is_read"])
        serializer = self.get_serializer(notification)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], url_path="mark-all-as-read")
    def mark_all_as_read(self, request):
        """Mark all notifications for the user as read and return them"""
        qs = self.get_queryset().filter(is_read=False)
        qs.update(is_read=True)
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], url_path="register/device")
    def register_device(self, request):
        """
        Register FCM device for push notifications.
        For mobile web, use device_type='web'
        """
        serializer = FCMDeviceSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            device = serializer.save()
            return Response(
                {
                    "detail": "Device registered successfully",
                    "device": FCMDeviceSerializer(device).data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], url_path="unregister/device")
    def unregister_device(self, request):
        """
        Unregister FCM device
        """
        registration_id = request.data.get("registration_id")
        if not registration_id:
            return Response(
                {"detail": "registration_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        deleted_count, _ = FCMDevice.objects.filter(
            user=request.user,
            registration_id=registration_id
        ).delete()

        if deleted_count > 0:
            return Response(
                {"detail": "Device unregistered successfully"},
                status=status.HTTP_200_OK
            )
        return Response(
            {"detail": "Device not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    @action(detail=False, methods=["get"], url_path="devices")
    def my_devices(self, request):
        """
        Get all registered devices for the authenticated user
        """
        devices = FCMDevice.objects.filter(user=request.user)
        serializer = FCMDeviceSerializer(devices, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], url_path="test/push")
    def test_push_notification(self, request):
        """
        Test endpoint to send push notifications to authenticated user's
        devices. For testing purposes only - should be removed or
        restricted in production.

        Body params:
        - title: Notification title
        - body: Notification body
        - data: Optional dict of additional data
        """
        title = request.data.get("title", "Test Notification")
        body = request.data.get("body", "This is a test notification")
        data = request.data.get("data", {})

        # Get all active devices for the user
        devices = FCMDevice.objects.filter(user=request.user, active=True)

        if not devices.exists():
            return Response(
                {"detail": "No active devices found for this user"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Send notification to all user devices
        try:
            # Construct FCM message
            message = Message(
                notification=FCMNotification(
                    title=title,
                    body=body
                ),
                data=data
            )

            result = devices.send_message(message)

            # Handle different response types
            response_data = {
                "detail": "Notification sent successfully",
                "devices_count": devices.count(),
            }

            # Result can be different types depending on single/batch send
            if hasattr(result, 'success_count'):
                # BatchResponse for multiple devices
                response_data.update({
                    "success_count": result.success_count,
                    "failure_count": result.failure_count
                })
            elif isinstance(result, dict):
                # Dict response
                response_data["result"] = result
            else:
                # String message ID for single device
                response_data["message_id"] = str(result)

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"detail": f"Error sending notification: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
