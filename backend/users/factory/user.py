import factory
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from users.choices import UserTypeChoices

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Faker("email")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    phone_number = factory.Faker("phone_number")
    is_verified = True
    type = UserTypeChoices.FARMER
    password = factory.LazyAttribute(lambda _: make_password("admin"))

    @factory.post_generation
    def set_custom_password(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            self.password = make_password("admin")


class UnverifiedUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Faker("email")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    phone_number = factory.Faker("phone_number")
    is_verified = False
    type = UserTypeChoices.FARMER
    password = factory.LazyAttribute(lambda _: make_password("admin"))

    @factory.post_generation
    def set_custom_password(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            self.password = make_password("admin")


class SystemAdminFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Faker("email")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    phone_number = factory.Faker("phone_number")
    is_verified = True
    type = UserTypeChoices.SYSTEM_ADMIN
    password = factory.LazyAttribute(lambda _: make_password("admin"))

    @factory.post_generation
    def set_custom_password(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            self.password = make_password("admin")
