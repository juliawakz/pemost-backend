import django_filters
from users.models.user import User
from users.choices import RoleChoices


class UserFilter(django_filters.FilterSet):
    # simple field filters
    role = django_filters.CharFilter(field_name="role", lookup_expr="exact")
    email = django_filters.CharFilter(field_name="email", lookup_expr="icontains")
    first_name = django_filters.CharFilter(field_name="first_name", lookup_expr="icontains")
    last_name = django_filters.CharFilter(field_name="last_name", lookup_expr="icontains")
    phone_number = django_filters.CharFilter(field_name="phone_number", lookup_expr="icontains")
    is_verified = django_filters.BooleanFilter(field_name="is_verified")

    # Profile-specific visibility filters
    # For E-Extensions: filter by is_visible
    e_extension_is_visible = django_filters.BooleanFilter(
        field_name="e_extension_profile__is_visible",
        lookup_expr="exact"
    )

    # For Agrodealers: filter by is_visible
    agrodealer_is_visible = django_filters.BooleanFilter(
        field_name="agrodealers__is_visible",
        lookup_expr="exact"
    )

    # Location filters for Super Extension Officers
    super_extension_county = django_filters.NumberFilter(
        field_name="super_extension_profile__counties__id",
        lookup_expr="exact"
    )
    super_extension_county_name = django_filters.CharFilter(
        field_name="super_extension_profile__counties__name",
        lookup_expr="icontains"
    )

    # Location filters for E-Extension Officers
    e_extension_ward = django_filters.NumberFilter(
        field_name="e_extension_profile__wards__id",
        lookup_expr="exact"
    )
    e_extension_ward_name = django_filters.CharFilter(
        field_name="e_extension_profile__wards__name",
        lookup_expr="icontains"
    )

    # Location filters for Agrodealers
    agrodealer_ward = django_filters.NumberFilter(
        field_name="agrodealers__ward__id",
        lookup_expr="exact"
    )
    agrodealer_ward_name = django_filters.CharFilter(
        field_name="agrodealers__ward__name",
        lookup_expr="icontains"
    )

    class Meta:
        model = User
        fields = [
            "role",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "is_verified",
            "e_extension_is_visible",
            "agrodealer_is_visible",
            "super_extension_county",
            "super_extension_county_name",
            "e_extension_ward",
            "e_extension_ward_name",
            "agrodealer_ward",
            "agrodealer_ward_name",
        ]
