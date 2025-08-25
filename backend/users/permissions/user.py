from rest_framework.permissions import BasePermission

from users.utils.user import UserUtils
from users.choices import UserTypeChoices


class CanManageDescendants(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.is_superuser or user.type == UserTypeChoices.SYSTEM_ADMIN:
            return True

        return obj == user or obj in UserUtils().get_all_descendants(user)
