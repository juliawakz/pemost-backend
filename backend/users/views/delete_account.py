from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import DestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

User = get_user_model()


@extend_schema(tags=["Account Management"])
class DeleteAccountView(DestroyAPIView):
    """
    Delete the authenticated user's account.

    This will set all related resources (farms, agrodealers, extension officers)
    to have null user references instead of deleting them.
    """
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        user_email = user.email

        # Delete the user - related objects will be set to null based on SET_NULL
        user.delete()

        return Response(
            {
                "message": f"Account {user_email} has been successfully deleted. "
                          "All related resources have been preserved with user set to null."
            },
            status=status.HTTP_200_OK
        )
