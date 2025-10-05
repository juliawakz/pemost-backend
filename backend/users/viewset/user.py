from django.contrib.auth import get_user_model
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from users.choices import RoleChoices
from users.filterset import UserFilter
from users.serializers.user import UserUpdateSerializer, UserWriteSerializer

User = get_user_model()


@extend_schema(tags=["Users"])
class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserWriteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = UserFilter

    def get_queryset(self):
        u = self.request.user

        if getattr(self, "swagger_fake_view", False):
            return User.objects.none()

        if u.is_superuser or u.role == RoleChoices.SYSTEM_ADMIN:
            return User.objects.all()

        if u.role == RoleChoices.SUPER_EXTENSION:
            return User.objects.filter(
                Q(role__in=[RoleChoices.SUPER_EXTENSION,
                            RoleChoices.E_EXTENSION, RoleChoices.AGRODEALER]) |
                Q(role=RoleChoices.FARMER, is_managed=True),
                wards__subcounty__county__in=u.counties.all(),
                is_archived=False
            ).distinct()

        if u.role == RoleChoices.E_EXTENSION:
            return User.objects.filter(
                Q(role__in=[RoleChoices.E_EXTENSION, RoleChoices.AGRODEALER]) |
                Q(role=RoleChoices.FARMER, is_managed=True),
                wards__in=u.counties.all(),
                is_archived=False
            ).distinct()

        return User.objects.filter(
            id=u.id, is_archived=False
        )

    def get_serializer_class(self):
        if self.action in ["update", "partial_update"]:
            return UserUpdateSerializer
        return UserWriteSerializer
