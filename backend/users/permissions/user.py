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
            and (
                user.is_superuser or
                user.is_system_admin() or
                user.is_super_extension()
            )
        )


class IsSuperExtensionOrEExtension(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        return bool(
            user
            and user.is_authenticated
            and (
                user.is_superuser or
                user.is_system_admin() or
                user.is_super_extension() or
                user.is_e_extension()
            )
        )


class IsSuperExtensionOrEExtensionOwner(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        return bool(
            user
            and user.is_authenticated
            and (
                user.is_superuser or
                user.is_system_admin() or
                user.is_super_extension() or
                user.is_e_extension() or
                user.is_farmer()
            )
        )

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.is_superuser or user.is_system_admin() or \
                user.is_super_extension() or user.is_e_extension():
            return True

        if obj.owner == user:
            return True

        return False
