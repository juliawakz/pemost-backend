from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class RoleChoices(TextChoices):
    FARMER = "FARMER", _("farmer")
    AGRODEALER = "AGRODEALER", _("agrodealer")
    E_EXTENSION = "E_EXTENSION", _("e-extension")
    SUPER_EXTENSION = "SUPER_EXTENSION", _("super extension")
    SYSTEM_ADMIN = "SYSTEM_ADMIN", _("system admin")
