from rest_framework.permissions import SAFE_METHODS, BasePermission


class CanManageFarmerWorkRequest(BasePermission):
    """
    Permission to manage farmer work requests.

    - Read (GET): Farmers (senders) and E-Extensions (recipients)
    - Create (POST): Only farmers
    - Accept/Reject: Only E-Extension recipients
    """
    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        # Everyone authenticated can read
        if request.method in SAFE_METHODS:
            return True

        # Only farmers can create requests
        if view.action == 'create':
            return user.is_farmer()

        # Accept/reject checked at object level
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user

        # System admins can do anything
        if user.is_superuser or user.is_systemadmin():
            return True

        # Read access - farmer (sender) or e-extension (recipient)
        if request.method in SAFE_METHODS:
            return obj.farms.filter(user=user).exists() \
                    or obj.e_extension.user == user

        # Only recipient can accept/reject
        if view.action in ['accept_request', 'reject_request']:
            return obj.e_extension.user == user

        return False


class CanManageEExtensionWorkRequest(BasePermission):
    """
    Permission to manage E-Extension work requests.

    - Read (GET): E-Extensions (senders) and Super Extensions (recipients)
    - Create (POST): Only E-Extensions
    - Accept/Reject: Only Super Extension recipients
    """
    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        # Everyone authenticated can read
        if request.method in SAFE_METHODS:
            return True

        # Only E-Extensions can create requests
        if view.action == 'create':
            return user.is_eextension()

        # Accept/reject checked at object level
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user

        # System admins can do anything
        if user.is_superuser or user.is_systemadmin():
            return True

        # Read access - e-extension (sender) or super-extension (recipient)
        if request.method in SAFE_METHODS:
            return obj.e_extension.user == user or\
                obj.super_extension.user == user

        # Only recipient can accept/reject
        if view.action in ['accept_request', 'reject_request']:
            return obj.super_extension.user == user

        return False


class CanManageFarm(BasePermission):
    """
    Permission to manage farms.

    - Read (GET): Any authenticated user can view farms they have access to
      (access controlled by get_queryset)
    - Create (POST): Only farmers can create their own farms
    - Update (PUT/PATCH): Farm owner (farmer), Super Extensions with
      visibility, or E-Extensions with visibility
    - Delete: Only farm owner or system admins
    """
    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        # Everyone authenticated can read
        if request.method in SAFE_METHODS:
            return True

        # Only farmers can create farms
        if view.action == 'create':
            return user.is_farmer()

        # Update/Delete checked at object level
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user

        # System admins can do anything
        if user.is_superuser or user.is_systemadmin():
            return True

        # Read access - controlled by get_queryset
        if request.method in SAFE_METHODS:
            return True

        # Farm owner can update/delete their farms
        if user.is_farmer() and obj.user == user:
            return True

        # Super Extension can update farms they have visibility to
        if user.is_superextension():
            super_ext_profile = user.super_extension_users
            managed_e_extensions = (
                super_ext_profile.managed_e_extensions.all()
            )
            # Check if any of their E-Extensions manage this farm
            has_visibility = obj.e_extensions.filter(
                id__in=managed_e_extensions
            ).exists()
            if has_visibility and obj.is_visible:
                # Can only update, not delete
                return view.action in ['update', 'partial_update']

        # E-Extension can update farms they manage
        if user.is_eextension():
            e_ext_profile = user.e_extension_users
            # Check if they manage this farm
            has_visibility = obj.e_extensions.filter(
                id=e_ext_profile.id
            ).exists()
            if has_visibility and obj.is_visible:
                # Can only update, not delete
                return view.action in ['update', 'partial_update']

        return False


class CanManageAgrodealer(BasePermission):
    """
    Permission to manage agrodealers.

    - Read (GET): Farmers can see all, agrodealers can only see themselves
    - Create (POST): Only agrodealers can create their profile
    - Update (PUT/PATCH): Only agrodealer owner or system admins
    - Delete: Only system admins
    """
    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        # Everyone authenticated can read
        if request.method in SAFE_METHODS:
            return True

        # Only agrodealers can create profiles
        if view.action == 'create':
            return user.is_agrodealer()

        # Update/Delete checked at object level
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user

        # System admins can do anything
        if user.is_superuser or user.is_systemadmin():
            return True

        # Read access - controlled by get_queryset
        if request.method in SAFE_METHODS:
            return True

        # Agrodealer owner can update their profile
        if user.is_agrodealer() and obj.user == user:
            if view.action in ['update', 'partial_update']:
                return True

        return False


class CanManageEExtensionOfficer(BasePermission):
    """
    Permission to manage E-Extension officers.

    - Read (GET): Farmers can see all, E-Extensions can only see themselves,
      Super Extensions can see their managed E-Extensions
    - Create (POST): Only E-Extensions can create their profile
    - Update (PUT/PATCH): Only E-Extension owner or system admins
    - Delete: Only system admins
    """
    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        # Everyone authenticated can read
        if request.method in SAFE_METHODS:
            return True

        # Only E-Extensions can create profiles
        if view.action == 'create':
            return user.is_eextension()

        # Update/Delete checked at object level
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user

        # System admins can do anything
        if user.is_superuser or user.is_systemadmin():
            return True

        # Read access - controlled by get_queryset
        if request.method in SAFE_METHODS:
            return True

        # E-Extension owner can update their profile
        if user.is_eextension() and obj.user == user:
            if view.action in ['update', 'partial_update']:
                return True

        return False


class CanManageSuperExtensionOfficer(BasePermission):
    """
    Permission to manage Super Extension officers.

    - Read (GET): E-Extensions can see all, Super Extensions can only
      see themselves
    - Create (POST): Only Super Extensions can create their profile
    - Update (PUT/PATCH): Only Super Extension owner or system admins
    - Delete: Only system admins
    """
    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        # Everyone authenticated can read
        if request.method in SAFE_METHODS:
            return True

        # Only Super Extensions can create profiles
        if view.action == 'create':
            return user.is_superextension()

        # Update/Delete checked at object level
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user

        # System admins can do anything
        if user.is_superuser or user.is_systemadmin():
            return True

        # Read access - controlled by get_queryset
        if request.method in SAFE_METHODS:
            return True

        # Super Extension owner can update their profile
        if user.is_superextension() and obj.user == user:
            if view.action in ['update', 'partial_update']:
                return True

        return False
