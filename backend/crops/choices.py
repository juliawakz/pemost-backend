from django.db import models
from django.utils.translation import gettext_lazy as _


class GrowthStageChoices(models.TextChoices):
    VEGETATIVE = "vegetative", _("Vegatative")
    FLOWERING = "flowering", _("Flowering")
    FRUITING = "fruiting", _("Fruiting")
    HARVESTING = "harvesting", _("Harvesting")


class SeverityChoices(models.TextChoices):
    CRITICAL = "critical", _("Critical")
    NOT_CRITICAL = "not_critical", _("Not Critical")
    NONE = "none", _("None")
