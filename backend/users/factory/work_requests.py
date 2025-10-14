import factory
from users.choices import WorkRequestStatusChoices
from users.factory.user import EExtensionFactory, FarmerFactory, SuperExtensionFactory
from users.models import EExtensionWorkRequest, FarmerWorkRequest


class EExtensionWorkRequestFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EExtensionWorkRequest

    e_extension = factory.SubFactory(EExtensionFactory)
    super_extension = factory.SubFactory(SuperExtensionFactory)
    status = WorkRequestStatusChoices.PENDING
    notification_sent = False
    message = factory.Faker("text", max_nb_chars=200)


class FarmerWorkRequestFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FarmerWorkRequest

    farmer = factory.SubFactory(FarmerFactory)
    e_extension = factory.SubFactory(EExtensionFactory)
    status = WorkRequestStatusChoices.PENDING
    notification_sent = False
    message = factory.Faker("text", max_nb_chars=200)
