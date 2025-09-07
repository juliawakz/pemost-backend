import factory
from locations.factory.subcounty import SubCountyFactory
from locations.models.ward import Ward


class WardFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Ward
        django_get_or_create = ("ward_id",)

    ward_id = factory.Sequence(lambda n: n + 1)
    name = factory.Sequence(lambda n: f"Ward {n}")
    subcounty = factory.SubFactory(SubCountyFactory)
