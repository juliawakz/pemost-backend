from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class UserTypeChoices(TextChoices):
    SYSTEM_ADMIN = "SYSTEM ADMIN", _("system admin")
    SUPER_EXTENSION = "SUPER-EXTENSION", _("super-extension")
    AGRODEALER = "AGRODEALER", _("agrodealer")
    E_EXTENSION = "E-EXTENSION", _("e-extension")
    FARMER = "FARMER", _("farmer")
