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


class IsSuperadmin(BasePermission):
    """Permission for Superadmin only (alias for System Admin)"""
    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and user.is_systemadmin()
        )


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

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.is_superuser or user.is_systemadmin():
            return True

        if hasattr(obj, 'owner') and obj.owner == user:
            return True

        if hasattr(obj, 'user') and obj.user == user:
            return True

        return False


class IsAgrodealer(BasePermission):
    """Permission for Agrodealer only"""
    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and user.is_agrodealer()
        )


class CanGenerateApiKey(BasePermission):
    """Permission to generate API keys - Superadmin only"""
    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and user.is_systemadmin()
        )


class CanManageWorkRequest(BasePermission):
    """
    Permission to manage work requests.
    - E-Extension can send requests to Super Extension
    - Farmer can send requests to E-Extension
    - Recipients can accept/reject requests sent to them
    """
    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        user = request.user

        # System admins can do anything
        if user.is_superuser or user.is_systemadmin():
            return True

        # Check if user is the sender (can view their own requests)
        if hasattr(obj, 'e_extension') and obj.e_extension == user:
            return True
        if hasattr(obj, 'farmer') and obj.farmer == user:
            return True

        # Check if user is the recipient (can accept/reject)
        if hasattr(obj, 'super_extension') and obj.super_extension == user:
            return True
        if hasattr(obj, 'e_extension') and obj.e_extension == user:
            # This is for FarmerWorkRequest where e_extension is the recipient
            return True

        return False
