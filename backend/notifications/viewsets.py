from notifications.models import Notification
from notifications.serializers import NotificationSerializer
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response


class NotificationViewSet(viewsets.ModelViewSet):
    """
    Users can fetch their notifications.
    Only update allowed is marking as read (via custom actions).
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(message_to=self.request.user)

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

    @action(detail=True, methods=["post"])
    def mark_as_read(self, request, pk=None):
        """Mark a single notification as read"""
        notification = self.get_object()
        if not notification.is_read:
            notification.is_read = True
            notification.save(update_fields=["is_read"])
        serializer = self.get_serializer(notification)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def mark_all_as_read(self, request):
        """Mark all notifications for the user as read and return them"""
        qs = self.get_queryset().filter(is_read=False)
        qs.update(is_read=True)
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)
