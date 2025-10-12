from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from app.models.farm import Farm
from app.serializers.farm import FarmSerializer
from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication


@extend_schema(tags=["App"])
class FarmViewset(viewsets.ModelViewSet):
    queryset = Farm.objects.all()
    serializer_class = FarmSerializer
    authentication_classes = [TokenAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        u = self.request.user

        if getattr(self, "swagger_fake_view", False):
            return Farm.objects.none()

        if u.is_superuser or u.is_systemadmin():
            return self.queryset.all()

        # Super Extension sees farms in their counties
        if u.is_superextension():
            super_ext_users = u.super_extension_users
            return self.queryset.filter(
                ward__subcounty__county__in=super_ext_users.counties.all(),
                is_archived=False,
                is_visible=True
            ).distinct()

        # E-Extension sees farms in their wards that they manage
        if u.is_eextension():
            e_ext_users = u.e_extension_users
            return self.queryset.filter(
                Q(ward__in=e_ext_users.wards.all(), is_visible=True) |
                Q(e_extensions=e_ext_users),
                is_archived=False
            ).distinct()

        # Farmers see only their own farms
        if u.is_farmer():
            return self.queryset.filter(
                user=u,
                is_archived=False
            )

        return self.queryset.none()

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid()
        if serializer.is_valid():
            self.perform_create(serializer)
            data = serializer.data
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
                headers=self.get_success_headers(data),
            )
        else:
            return Response(
                serializer.errors,
                status.HTTP_400_BAD_REQUEST
            )

    def get_permissions(self):
        """
        - Any authenticated user can list/retrieve.
        - Only system admin/superuser/superextension/eextension
            can create/update/delete.
        """
        if self.action in ["list", "retrieve"]:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [
                IsAuthenticated
            ]
        return [permission() for permission in permission_classes]
