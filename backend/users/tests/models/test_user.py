import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from locations.factory.county import CountyFactory
from locations.factory.subcounty import SubCountyFactory
from locations.factory.ward import WardFactory
from users.choices import RoleChoices
from users.factory.user import (
    AgroDealerFactory,
    EExtensionFactory,
    FarmerFactory,
    SuperExtensionFactory,
    SystemAdminFactory,
    UserFactory,
)

User = get_user_model()


# -------------------------------
# User Creation & Manager
# -------------------------------
@pytest.mark.django_db
def test_user_creation_with_manager():
    user = User.objects.create_user(
        email="user@example.com",
        first_name="Test",
        last_name="User",
        phone_number="+254700000001",
        password="strongpassword123",
    )
    assert user.email == "user@example.com"
    assert user.check_password("strongpassword123")


@pytest.mark.django_db
def test_superuser_creation():
    admin = User.objects.create_superuser(
        email="admin@example.com",
        first_name="Admin",
        last_name="User",
        phone_number="+254700000002",
        password="adminpassword123",
    )
    assert admin.is_superuser is True
    assert admin.is_staff is True
    assert admin.role == RoleChoices.SYSTEMADMIN


# -------------------------------
# Properties & Methods
# -------------------------------
@pytest.mark.django_db
def test_full_name_and_str():
    user = UserFactory(first_name="Jane", last_name="Doe")
    assert user.full_name == "Jane Doe"
    assert str(user) == "Jane Doe"  # matches __str__


@pytest.mark.django_db
def test_profile_photo_url(settings):
    user = UserFactory()
    assert user.profile_photo_url is None

    # simulate photo
    photo = SimpleUploadedFile("avatar.jpg", b"file_content", content_type="image/jpeg")
    user.profile_photo = photo
    user.save()
    assert user.profile_photo_url.startswith(settings.SERVER_HOST)


@pytest.mark.django_db
def test_role_helpers():
    admin = SystemAdminFactory()
    assert admin.is_systemadmin() is True

    super_ext = SuperExtensionFactory()
    assert super_ext.is_superextension() is True
    assert super_ext.is_systemadmin() is False

    e_ext = EExtensionFactory()
    assert e_ext.is_eextension() is True


# -------------------------------
# Many-to-Many Relationships
# -------------------------------
@pytest.mark.django_db
def test_user_with_location_relationships():
    county = CountyFactory(name="Nairobi", county_id=47)
    subcounty = SubCountyFactory(name="Westlands", county=county)
    ward = WardFactory(name="Kangemi", subcounty=subcounty)

    user = UserFactory(counties=[county], subcounties=[subcounty], wards=[ward])

    assert county in user.counties.all()
    assert subcounty in user.subcounties.all()
    assert ward in user.wards.all()


# -------------------------------
# Role factory
# -------------------------------
@pytest.mark.django_db
@pytest.mark.parametrize(
    "factory_class, expected_role",
    [
        (SystemAdminFactory, RoleChoices.SYSTEMADMIN),
        (SuperExtensionFactory, RoleChoices.SUPER_EXTENSION),
        (EExtensionFactory, RoleChoices.E_EXTENSION),
        (AgroDealerFactory, RoleChoices.AGRODEALER),
        (FarmerFactory, RoleChoices.FARMER),
    ],
)
def test_factory_assign_correct_roles(factory_class, expected_role):
    user = factory_class()
    assert user.role == expected_role


# -------------------------------
# Meta & Ordering
# -------------------------------
@pytest.mark.django_db
def test_user_ordering():
    UserFactory(first_name="A", created_at=timezone.now())
    UserFactory(first_name="B", created_at=timezone.now())
    users = list(User.objects.all())
    # should be ordered by -created_at
    assert users[0].created_at >= users[1].created_at
