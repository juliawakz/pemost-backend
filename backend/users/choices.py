from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class RoleChoices(TextChoices):
    SYSTEM_ADMIN = "SYSTEM_ADMIN", _("system admin")
    SUPER_EXTENSION = "SUPER_EXTENSION", _("super extension")
    AGRODEALER = "AGRODEALER", _("agrodealer")
    E_EXTENSION = "E_EXTENSION", _("e-extension")
    FARMER = "FARMER", _("farmer")
