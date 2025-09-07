import factory
from locations.models.county import County


class CountyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = County
        django_get_or_create = ("county_id",)

    county_id = factory.Sequence(lambda n: n + 1)
    name = factory.Sequence(lambda n: f"County {n}")
