from rest_framework.permissions import BasePermission


class IsSystemAdminOrSuperUser(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (user.is_superuser or user.is_system_admin())
        )


class IsSuperExtension(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        return bool(
            user
            and user.is_authenticated
            and user.is_super_extension()
        )


class IsEExtension(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        return bool(
            user
            and user.is_authenticated
            and user.is_e_extension()
        )


class IsFarmer(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        return bool(
            user
            and user.is_authenticated
            and user.is_farmer()
        )

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.is_superuser or user.is_system_admin():
            return True

        if obj.owner == user:
            return True

        return False
