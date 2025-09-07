from unittest.mock import MagicMock, patch

import pytest
from locations.factory.ward import WardFactory
from rest_framework.exceptions import PermissionDenied, ValidationError
from users.choices import RoleChoices
from users.factory.user import (
    EExtensionFactory,
    FarmerFactory,
    SuperExtensionFactory,
    SystemAdminFactory,
)
from users.serializers.user import UserSerializer

data = {
    "first_name": "test",
    "last_name": "user",
    "email": "testuser@test.com",
    "phone_number": "+254712345678"
}


@pytest.mark.django_db
def test_missing_role_raises():
    admin = SystemAdminFactory()
    request = type("MockRequest", (), {"user": admin})
    serializer = UserSerializer(data=data, context={"request": request})
    assert not serializer.is_valid()
    assert "Role is required." in str(serializer.errors)


@pytest.mark.django_db
def test_super_extension_requires_county():
    admin = SystemAdminFactory()
    request = type("MockRequest", (), {"user": admin})
    data["role"] = RoleChoices.SUPER_EXTENSION
    serializer = UserSerializer(data=data, context={"request": request})
    assert not serializer.is_valid()
    assert "must be assigned at least one county" in str(serializer.errors)


@pytest.mark.django_db
def test_e_extension_requires_ward_or_subcounty():
    admin = SystemAdminFactory()
    request = type("MockRequest", (), {"user": admin})
    data["role"] = RoleChoices.E_EXTENSION
    serializer = UserSerializer(data=data, context={"request": request})
    assert not serializer.is_valid()
    assert "must be assigned at least one ward or subcounty" in str(serializer.errors)


@pytest.mark.django_db
def test_farmer_requires_ward():
    admin = SystemAdminFactory()
    request = type("MockRequest", (), {"user": admin})
    data["role"] = RoleChoices.FARMER
    serializer = UserSerializer(data=data, context={"request": request})
    assert not serializer.is_valid()
    assert "must be assigned at least one ward" in str(serializer.errors)


@pytest.mark.django_db
def test_create_user_with_ward():
    admin = SystemAdminFactory()
    ward = WardFactory()

    data["role"] = RoleChoices.FARMER
    data["wards"] = [ward.id]
    request = type("MockRequest", (), {"user": admin})

    with patch("users.utils.otp.OtpUtils.generate_random_password", return_value="TempPass123!"):
        with patch("users.utils.user.UserUtils.send_login_credentials_email") as mock_email:
            serializer = UserSerializer(data=data, context={"request": request})
            assert serializer.is_valid()
            user = serializer.save()

    user.refresh_from_db()
    assert user.wards.count() == 1
    assert user.check_password("TempPass123!")
    mock_email.assert_called_once()


@pytest.mark.django_db
def test_update_triggers_sync_locations():
    admin = SystemAdminFactory()
    ward = WardFactory()
    user = FarmerFactory()
    user.wards.add(ward)
    data = {"first_name": "Updated"}
    request = type("MockRequest", (), {"user": admin})

    serializer = UserSerializer(
        instance=user,
        data=data,
        context={"request": request},
        partial=True
    )

    assert user.counties.count() == 0
    assert user.subcounties.count() == 0
    assert serializer.is_valid()

    serializer.save()

    user.refresh_from_db()
    assert user.counties.count() == 1
    assert user.subcounties.count() == 1


@pytest.mark.django_db
def test_to_representation_includes_nested():
    ward = WardFactory()
    user = FarmerFactory()
    user.wards.add(ward)

    serializer = UserSerializer(instance=user, context={"request": MagicMock()})
    data = serializer.data

    assert "wards" in data
    assert isinstance(data["wards"], list)
    assert data["wards"][0]["id"] == str(ward.id)


@pytest.mark.django_db
def test_super_extension_cannot_create_system_admin():
    super_extenision = SuperExtensionFactory()
    ward = WardFactory()
    super_extenision.counties.add(ward.subcounty.county)

    request = type("MockRequest", (), {"user": super_extenision})
    data["role"] = RoleChoices.SYSTEM_ADMIN
    data["wards"] = [ward.id]

    serializer = UserSerializer(data=data, context={"request": request})
    with pytest.raises(PermissionDenied, match="cannot create SYSTEM_ADMIN"):
        serializer.is_valid(raise_exception=True)


@pytest.mark.django_db
def test_super_extension_can_create_farmer_within_county():
    super_extenision = SuperExtensionFactory()
    ward = WardFactory()
    super_extenision.counties.add(ward.subcounty.county)

    request = type("MockRequest", (), {"user": super_extenision})
    data["role"] = RoleChoices.FARMER
    data["wards"] = [ward.id]

    serializer = UserSerializer(data=data, context={"request": request})
    assert serializer.is_valid(), serializer.errors


@pytest.mark.django_db
def test_super_extension_cannot_assign_outside_county():
    super_extenision = SuperExtensionFactory()
    ward = WardFactory()
    other_ward = WardFactory()
    super_extenision.counties.add(ward.subcounty.county)

    request = type("MockRequest", (), {"user": super_extenision})
    data["role"] = RoleChoices.FARMER
    data["wards"] = [other_ward.id]

    serializer = UserSerializer(data=data, context={"request": request})
    with pytest.raises(ValidationError, match="Some wards do not belong"):
        serializer.is_valid(raise_exception=True)


@pytest.mark.django_db
def test_e_extension_cannot_assign_outside_wards():
    e_extenision = EExtensionFactory()
    ward = WardFactory()
    other_ward = WardFactory()
    e_extenision.wards.add(ward)

    request = type("MockRequest", (), {"user": e_extenision})
    data["role"] = RoleChoices.FARMER
    data["wards"] = [other_ward.id]

    serializer = UserSerializer(data=data, context={"request": request})
    with pytest.raises(ValidationError, match="Wards outside your scope"):
        serializer.is_valid(raise_exception=True)


@pytest.mark.django_db
def test_e_extension_agrodealer_requires_exactly_one_ward():
    e_extenision = EExtensionFactory()
    ward = WardFactory()
    other_ward = WardFactory(subcounty=ward.subcounty)
    e_extenision.wards.add(ward)
    e_extenision.wards.add(other_ward)

    request = type("MockRequest", (), {"user": e_extenision})
    data["role"] = RoleChoices.AGRODEALER
    data["wards"] = [other_ward.id, ward.id]

    serializer = UserSerializer(data=data, context={"request": request})
    with pytest.raises(ValidationError, match="Agrodealer must have exactly one ward"):
        serializer.is_valid(raise_exception=True)


@pytest.mark.django_db
def test_e_extension_can_create_farmer_in_assigned_ward():
    e_extenision = EExtensionFactory()
    ward = WardFactory()
    e_extenision.wards.add(ward)

    request = type("MockRequest", (), {"user": e_extenision})
    data["role"] = RoleChoices.FARMER
    data["wards"] = [ward.id]

    serializer = UserSerializer(data=data, context={"request": request})
    assert serializer.is_valid(), serializer.errors


@pytest.mark.django_db
def test_regular_user_cannot_manage_others():
    farmer_one = FarmerFactory()
    farmer_two = FarmerFactory()
    ward = WardFactory()
    farmer_one.wards.add(ward)
    farmer_two.wards.add(ward)

    data = {
        "first_name": "FarmerTwo"
    }

    request = type("MockRequest", (), {"user": farmer_one})

    serializer = UserSerializer(instance=farmer_two, data=data, context={"request": request}, partial=True)
    with pytest.raises(PermissionDenied, match="not allowed to manage users"):
        serializer.is_valid(raise_exception=True)


@pytest.mark.django_db
def test_e_extension_cannot_create_super_extension():
    e_extenision = EExtensionFactory()
    ward = WardFactory()
    e_extenision.wards.add(ward)

    request = type("MockRequest", (), {"user": e_extenision})
    data["role"] = RoleChoices.SUPER_EXTENSION
    data["counties"] = [ward.subcounty.county.id]
    data["subcounties"] = [ward.subcounty.id]
    data["wards"] = [ward.id]

    serializer = UserSerializer(data=data, context={"request": request})
    with pytest.raises(PermissionDenied, match="E-Extension may only create Farmer or Agrodealer."):
        serializer.is_valid(raise_exception=True)
