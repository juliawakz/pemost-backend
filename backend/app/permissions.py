from rest_framework.permissions import BasePermission


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