from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenRefreshView

User = get_user_model()


@extend_schema(tags=["Authentication"])
class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


@extend_schema(tags=["Authentication"])
class ObtainAuthTokenView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        # Check if user is system admin (or adjust field name)
        if not (user.is_superuser or user.is_system_admin()):
            return Response(
                {
                    "detail": "You are not authorized to obtain a token."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # Generate token normally if admin
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})
