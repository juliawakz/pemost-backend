from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from users.serializers.user import (
    NotificationPreferencesSerializer,
    UserReadSerializer
)

User = get_user_model()


@extend_schema(tags=["User Notification Preferences"])
class NotificationPreferencesView(APIView):
    """
    API endpoint for managing user notification preferences.

    GET: Retrieve current notification preferences
    PATCH: Update notification preferences
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: NotificationPreferencesSerializer},
        description="Get current notification preferences"
    )
    def get(self, request):
        """Retrieve current notification preferences"""
        serializer = NotificationPreferencesSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=NotificationPreferencesSerializer,
        responses={200: UserReadSerializer},
        description="Update notification preferences"
    )
    def patch(self, request):
        """Update notification preferences"""
        serializer = NotificationPreferencesSerializer(
            request.user,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Notification preferences updated successfully",
                    "data": serializer.data
                },
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
