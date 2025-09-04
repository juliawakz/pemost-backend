from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from users.serializers.user import UserReadSerializer, UserWriteSerializer
from users.serializers.registration import RegistrationSerializer
from users.permissions.user import CanManageDescendants
from users.choices import RoleChoices

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserReadSerializer
    permission_classes = (
        IsAuthenticated,
        CanManageDescendants
    )

    filter_backends = [
        DjangoFilterBackend
    ]
    filterset_fields = [
        "first_name",
        "last_name",
        "email"
    ]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            permission_classes = [IsAuthenticated]
        elif self.action in ["update", "partial_update", "destroy"]:
            permission_classes = [IsAuthenticated, CanManageDescendants]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == "create":
            return RegistrationSerializer
        elif self.action in ("update", "partial_update"):
            return UserWriteSerializer
        elif self.action in ("retrieve",):
            return UserReadSerializer
        return self.serializer_class

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser or user.type == RoleChoices.SYSTEM_ADMIN:
            return User.objects.all()

        descendant_users = user.user_descendants.all()
        # descendant_ids = [u.id for u in descendant_users]

        return descendant_users  # User.objects.filter(id__in=descendant_ids + [user.id])
