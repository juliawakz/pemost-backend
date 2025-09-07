import factory
from locations.factory.county import CountyFactory
from locations.models.subcounty import SubCounty


class SubCountyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SubCounty
        django_get_or_create = ("subcounty_id",)

    subcounty_id = factory.Sequence(lambda n: n + 1)
    name = factory.Sequence(lambda n: f"SubCounty {n}")
    county = factory.SubFactory(CountyFactory)
