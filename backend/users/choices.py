from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class RoleChoices(TextChoices):
    SYSTEM_ADMIN = "SYSTEM_ADMIN", _("system_admin")
    SUPER_EXTENSION = "SUPER_EXTENSION", _("super_extension")
    AGRODEALER = "AGRODEALER", _("agrodealer")
    E_EXTENSION = "E_EXTENSION", _("e_extension")
    FARMER = "FARMER", _("farmer")
