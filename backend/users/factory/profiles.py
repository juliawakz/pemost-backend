import factory
from users.models import (
    EExtensionOfficer,
    SuperExtensionOfficer,
    Agrodealer,
)
from users.factory.user import (
    FarmerFactory,
    EExtensionFactory,
    SuperExtensionFactory,
    AgroDealerFactory,
)


class EExtensionOfficerProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EExtensionOfficer
        django_get_or_create = ("user",)

    user = factory.SubFactory(EExtensionFactory)
    is_visible = False

    @factory.post_generation
    def wards(self, create, extracted, **kwargs):
        if create and extracted:
            self.wards.add(*extracted)

    @factory.post_generation
    def super_extensions(self, create, extracted, **kwargs):
        if create and extracted:
            self.super_extensions.add(*extracted)


class SuperExtensionOfficerProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SuperExtensionOfficer
        django_get_or_create = ("user",)

    user = factory.SubFactory(SuperExtensionFactory)

    @factory.post_generation
    def counties(self, create, extracted, **kwargs):
        if create and extracted:
            self.counties.add(*extracted)


class AgrodealerProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Agrodealer
        django_get_or_create = ("user",)

    user = factory.SubFactory(AgroDealerFactory)
    is_visible = True
