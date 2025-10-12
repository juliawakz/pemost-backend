from rest_framework.permissions import BasePermission


class IsSystemAdminOrSuperUser(BasePermission):
    """Permission for System Admin or Superuser only"""
    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (user.is_superuser or user.is_systemadmin())
        )


class IsSystemAdminOrSuperUserOwner(BasePermission):
    """Permission for System Admin or Superuser only"""
    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (user.is_superuser or user.is_systemadmin())
        )

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.is_superuser or user.is_systemadmin():
            return True

        if hasattr(obj, 'owner') and obj.owner == user:
            return True

        if hasattr(obj, 'user') and obj.user == user:
            return True

        return False


class IsSuperExtension(BasePermission):
    """Permission for Super Extension Officer only"""
    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and user.is_super_extension()
        )


class IsEExtension(BasePermission):
    """Permission for E-Extension Officer only"""
    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and user.is_e_extension()
        )


class IsFarmer(BasePermission):
    """Permission for Farmer only"""
    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and user.is_farmer()
        )


class IsAgrodealer(BasePermission):
    """Permission for Agrodealer only"""
    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and user.is_agrodealer()
        )
