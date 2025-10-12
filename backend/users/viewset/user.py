from django.contrib.auth import get_user_model
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from users.models import EExtensionOfficer, EExtensionWorkRequest
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from users.choices import RoleChoices
from users.filterset import UserFilter
from users.serializers.user import UserSerializer
from rest_framework.response import Response
from rest_framework import status

User = get_user_model()


@extend_schema(tags=["Users"])
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = UserFilter

    def create(self, request, *args, **kwargs):
        return Response(
            {"detail": "Creation of users is not allowed via this endpoint."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def get_queryset(self):
        u = self.request.user

        if getattr(self, "swagger_fake_view", False):
            return User.objects.none()

        # System Admin and Superuser see everything
        if u.is_superuser or u.role == RoleChoices.SYSTEMADMIN:
            return User.objects.all()

        # Superadmin sees everything (business-level admin)
        if u.role == RoleChoices.SUPERADMIN:
            return User.objects.all()

        # Super Extension Officer
        if u.role == RoleChoices.SUPER_EXTENSION:
            super_ext_profile = u.super_extension_profile

            # Get e-extensions who:
            # 1. Are visible (is_visible=True) OR
            # 2. Have sent work requests to this super extension
            e_ext_with_requests = EExtensionWorkRequest.objects.filter(
                super_extension=u
            ).values_list('e_extension_id', flat=True)

            visible_e_extensions = Q(
                role=RoleChoices.E_EXTENSION,
                e_extension_profile__is_visible=True,
                e_extension_profile__wards__subcounty__county__in=super_ext_profile.counties.all()
            )

            requested_e_extensions = Q(
                role=RoleChoices.E_EXTENSION,
                id__in=e_ext_with_requests
            )

            # Can see:
            # - E-extensions (visible OR have sent requests)
            # - Farmers managed by their e-extensions (through farms)
            # - Cannot see agrodealers
            # Get farmers whose farms are managed by e-extensions under this super extension
            managed_farmers = User.objects.filter(
                role=RoleChoices.FARMER,
                farms__e_extensions__super_extensions=super_ext_profile
            ).distinct()

            return User.objects.filter(
                visible_e_extensions |
                requested_e_extensions |
                Q(id__in=managed_farmers.values_list('id', flat=True)),
                is_archived=False
            ).distinct()

        # E-Extension Officer
        if u.role == RoleChoices.E_EXTENSION:
            e_ext_profile = u.e_extension_profile

            # Get farmers who have sent work requests to this e-extension
            from users.models import FarmerWorkRequest

            farmers_with_requests = FarmerWorkRequest.objects.filter(
                e_extension=u
            ).values_list('farmer_id', flat=True)

            # Get farmers whose farms are managed by this e-extension
            managed_farmers = User.objects.filter(
                role=RoleChoices.FARMER,
                farms__e_extensions=e_ext_profile
            ).distinct()

            # Can see:
            # - Farmers who have sent work requests OR are managed
            #  by them (through farms)
            # - Cannot see agrodealers
            return User.objects.filter(
                Q(role=RoleChoices.FARMER, id__in=farmers_with_requests) |
                Q(id__in=managed_farmers.values_list('id', flat=True)),
                is_archived=False
            ).distinct()

        # Farmer
        if u.role == RoleChoices.FARMER:
            # Get e-extensions managing any of this farmer's farms
            managed_e_extensions = EExtensionOfficer.objects.filter(
                managed_farmers__owner=u
            ).values_list('id', flat=True)

            # Can see:
            # - Their managing e-extensions (through farms)
            # - All agrodealers (visible ones)
            return User.objects.filter(
                Q(role=RoleChoices.E_EXTENSION,
                  e_extension_profile__id__in=managed_e_extensions) |
                Q(role=RoleChoices.AGRODEALER, agrodealers__is_visible=True),
                is_archived=False
            ).distinct()

        # Agrodealer - can only see themselves
        if u.role == RoleChoices.AGRODEALER:
            return User.objects.filter(id=u.id, is_archived=False)

        # Default: users can only see themselves
        return User.objects.filter(
            id=u.id, is_archived=False
        )

    def get_serializer_class(self):
        if self.action in ["update", "partial_update"]:
            return UserSerializer
        return UserSerializer
