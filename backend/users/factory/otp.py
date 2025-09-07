from datetime import timedelta

import factory
from django.utils import timezone
from users.factory.user import UserFactory
from users.models.otp import Otp


class OtpFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Otp

    token = factory.Sequence(lambda n: f"{n:06d}")  # 000001, 000002, etc.
    user = factory.SubFactory(UserFactory)
    expiry_at = factory.LazyFunction(lambda: timezone.now() + timedelta(minutes=10))
