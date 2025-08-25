from django.db import models
from django.utils.translation import gettext_lazy as _


class GenderChoices(models.TextChoices):
    """
    Various Gender
    """

    M = "M", _("m")
    F = "F", _("f")
    # set in db , human_readable


class GrowthStage(models.TextChoices):
    VEGETATIVE = "vegetative", _("Vegatative")
    FLOWERING = "flowering", _("Flowering")
    FRUITING = "fruiting", _("Fruiting")
    HARVESTING = "harvesting", _("Harvesting")


class SERVERE(models.TextChoices):
    CRITICAL = "critical", _("Critical")
    NOT_CRITICAL = "not_critical", _("Not Critical")
    NONE = "none", _("None")


class PEST_STAGE(models.TextChoices):
    """
    Pest Stage
    """

    LARVAE = "larvae", _("Larvae")
    EGGS = "eggs", _("Eggs")
    NYMPH = "nymph", _("Nymph")
    PUPAE = "pupae", _("Pupae")
    ADULT = "adult", _("Adult")


class ACTION_THRESHOLD_RISK(models.TextChoices):
    HIGH = "high", _("High")
    LOW = "low", _("Low")
    MODERATE = "moderate", _("Moderate")
    NONE = "none", _("None")
