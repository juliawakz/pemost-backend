from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from users.serializers.user import UserSerializer
from users.choices import RoleChoices

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        u = self.request.user

        if u.is_superuser or u.role == RoleChoices.SYSTEM_ADMIN:
            return User.objects.all()

        if u.role == RoleChoices.SUPER_EXTENSION:
            return User.objects.filter(
                role__in=[RoleChoices.E_EXTENSION, RoleChoices.FARMER, RoleChoices.AGRODEALER],
                wards__subcounty__county__in=u.counties.all(), is_archived=False
            ).distinct()

        if u.role == RoleChoices.E_EXTENSION:
            return User.objects.filter(
                role__in=[RoleChoices.FARMER, RoleChoices.AGRODEALER],
                wards__in=u.wards.all(), is_archived=False
            ).distinct()

        return User.objects.filter(id=u.id, is_archived=False)
