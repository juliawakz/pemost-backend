from rest_framework.permissions import BasePermission

from users.choices import RoleChoices


class CanManageDescendants(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.is_superuser or user.type == RoleChoices.SYSTEM_ADMIN:
            return True

        return obj == user or obj in user.get_all_descendants()
