from rest_framework.permissions import BasePermission


class IsSystemAdminOrSuperUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and (
            request.user.is_system_admin
        )
