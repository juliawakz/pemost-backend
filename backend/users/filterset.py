import django_filters
from users.models.user import User


class UserFilter(django_filters.FilterSet):
    # simple field filters
    role = django_filters.CharFilter(field_name="role", lookup_expr="exact")
    email = django_filters.CharFilter(field_name="email", lookup_expr="icontains")
    first_name = django_filters.CharFilter(field_name="first_name", lookup_expr="icontains")
    last_name = django_filters.CharFilter(field_name="last_name", lookup_expr="icontains")
    phone_number = django_filters.CharFilter(field_name="phone_number", lookup_expr="icontains")

    # ManyToMany ID filters
    county = django_filters.NumberFilter(field_name="counties__county_id", lookup_expr="exact")
    subcounty = django_filters.NumberFilter(field_name="subcounties__subcounty_id", lookup_expr="exact")
    ward = django_filters.NumberFilter(field_name="wards__ward_id", lookup_expr="exact")

    # ManyToMany name filters (case-insensitive partial match)
    county_name = django_filters.CharFilter(field_name="counties__name", lookup_expr="icontains")
    subcounty_name = django_filters.CharFilter(field_name="subcounties__name", lookup_expr="icontains")
    ward_name = django_filters.CharFilter(field_name="wards__name", lookup_expr="icontains")

    class Meta:
        model = User
        fields = [
            "role",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "county",
            "county_name",
            "subcounty",
            "subcounty_name",
            "ward",
            "ward_name",
        ]
