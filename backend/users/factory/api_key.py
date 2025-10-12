import factory
from django.utils import timezone
from datetime import timedelta
from users.models import ApiKey
from users.factory.user import SuperadminFactory


class ApiKeyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ApiKey

    user = factory.SubFactory(SuperadminFactory)
    name = factory.Sequence(lambda n: f"API Key {n}")
    is_active = True
    expires_at = factory.LazyFunction(lambda: timezone.now() + timedelta(days=365))
