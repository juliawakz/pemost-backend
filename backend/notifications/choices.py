from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class MessageTypeChoices(TextChoices):
    EMAIL = "EMAIL", _("email")
    PUSH = "PUSH", _("push")
