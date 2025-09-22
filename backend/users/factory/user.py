import factory
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from users.choices import RoleChoices

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ("email",)

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    phone_number = factory.Sequence(lambda n: f"+254700000{n:03d}")
    id_number = factory.Faker("bothify", text="??########")
    password = factory.LazyAttribute(lambda _: make_password("admin"))
    role = RoleChoices.FARMER
    is_staff = False
    last_login = factory.LazyFunction(timezone.now)

    @factory.post_generation
    def set_custom_password(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            self.password = make_password("admin")

    @factory.post_generation
    def counties(self, create, extracted, **kwargs):
        if create and extracted:
            self.counties.add(*extracted)

    @factory.post_generation
    def subcounties(self, create, extracted, **kwargs):
        if create and extracted:
            self.subcounties.add(*extracted)

    @factory.post_generation
    def wards(self, create, extracted, **kwargs):
        if create and extracted:
            self.wards.add(*extracted)


# -----------------------------
# Specialized User Factories
# -----------------------------
class SystemAdminFactory(UserFactory):
    role = RoleChoices.SYSTEM_ADMIN
    is_staff = True
    is_superuser = True


class SuperExtensionFactory(UserFactory):
    role = RoleChoices.SUPER_EXTENSION


class EExtensionFactory(UserFactory):
    role = RoleChoices.E_EXTENSION


class AgroDealerFactory(UserFactory):
    role = RoleChoices.AGRODEALER


class FarmerFactory(UserFactory):
    role = RoleChoices.FARMER
